"""CCM Manual build hooks（V5 架構）

原則：能在 build 時算出來的，就不存在原始碼裡；能被機器檢查的規則，就寫成 hook。
所有違規一律 log.warning → `mkdocs build --strict` 失敗 → CI 不部署（唯一閘門）。

本檔負責：
  1. 版號：讀 VERSION（唯一來源）→ config.extra.version、CSS/JS cache-busting、教材版號
  2. 分類：每頁 front matter 的 category（learn/daily/cancer/lookup/admin）→ 模板畫麵包屑與底部導覽；
     側欄分組必須與 category 一致
  3. 規範檢查：分類合法、規則 8、規則 11、癌別章節 ID
  4. 獨立教材：teaching_src/ 的上游原始檔在 build 時注入整合層（返回、版號、SELA、自帶字型）；
     inject=false 的（drug-lookup）原樣發布並比對 sha256
  5. build 結尾：掃 site/ 每一個站內連結與 anchor（含 raw HTML 與教材）
  6. 文件元資料（V5.4.0）：「最後更新」由 git-revision-date-localized 依 git 日期產生；
     審閱狀態、來源層級、下次檢視期限寫在 front matter，過期即 WARNING；C0 的來源層級表由 front matter 產生
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import logging
import posixpath
import re
from html import escape
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml

log = logging.getLogger("mkdocs.hooks.ccm")
ROOT = Path(__file__).parent
VERSION = "V" + (ROOT / "VERSION").read_text(encoding="utf-8").strip()

# ---- 分類（單一定義；模板與檢查都讀這裡）----
CATS = {
    "learn":  {"label": "學習中心",   "hub": "hub_learning/"},
    "daily":  {"label": "日常工作",   "hub": "hub_daily/"},
    "cancer": {"label": "癌別照護",   "hub": "hub_cancer/"},
    "lookup": {"label": "臨床速查",   "hub": "hub_lookup/"},
    "admin":  {"label": "系統與管理", "hub": "hub_admin/"},
}

# 分類的唯一來源是各頁 front matter 的 `category:`（V5.1.0 起）。
# 側欄「完整資料庫」底下的 5 組，組名對應這裡的 label；頁面放的組必須等於它的 category。
NAV_GROUP = {v["label"]: k for k, v in CATS.items()}
_nav_cat: dict[str, str] = {}

# 癌別檔固定章節 ID（V5.2.0，內審 R4）：標題文字與章號可改，ID 不變；跨檔連結一律用這些 ID。
#   必備：overview staging treatment followup faq edu
#   選配：nhi（健保給付）notes（特殊注意）care（個管照護）redflags（紅旗）appendix
CANCER_IDS = {
    "cancer":       {"overview", "staging", "treatment", "followup", "faq", "edu"},
    "cancer-split": {"rcc", "bladder", "followup", "faq", "edu", "redflags"},   # C10：兩部強分隔
}

# 圖示（V5.5.0，內審 R10）：icons/<名稱>.svg 是唯一來源。
#   內文寫 :ccm-名稱:（行內小圖示）、:ccm-名稱.big:（首頁任務鈕大圖示）、:ccm-名稱.plain:（不加 class）、
#   :ccm-名稱.其他class:（附加 class）；模板用 config.extra.icon_svg.名稱。docs/*.md 不得再手寫 <svg>。
ICONS = {f.stem: re.search(r"<svg[^>]*>(.*)</svg>", f.read_text(encoding="utf-8"), re.S)[1]
         for f in sorted((ROOT / "icons").glob("*.svg"))}
ICON_CODE = re.compile(r":ccm-([a-z0-9-]+?)((?:\.[a-z0-9-]+)*):")


def _icon(m: re.Match, src: str) -> str:
    name, mods = m[1], [c for c in m[2].split(".") if c]
    if name not in ICONS:
        log.warning("%s：圖示 :ccm-%s: 不存在（icons/ 底下沒有 %s.svg）", src, name, name)
        return m[0]
    if "plain" in mods:
        cls = ""
    else:
        base = "ccm-icon" if "big" in mods else "ccm-icon-inline"
        cls = f' class="{" ".join([base] + [c for c in mods if c != "big"])}"'
    return f'<svg{cls} viewBox="0 0 24 24" aria-hidden="true">{ICONS[name]}</svg>'


# 文件元資料（V5.4.0，內審 R6／D-3）。欄位名避開 Material 內建的 `status`。
REVIEW_STATUS = {"draft": "草稿", "pending": "待醫師團隊確認", "reviewed": "已審閱"}
LEVELS = {1: "① 原文全文", 2: "② 官方摘要", 3: "③ 二手解讀", 4: "④ 未查證"}
CANCER_META = ("guideline", "guideline_level", "review_status", "review_due")
TODAY = dt.date.today()


def _front_matter(path: Path) -> dict:
    s = path.read_text(encoding="utf-8")
    if not s.startswith("---\n"):
        return {}
    return yaml.safe_load(s[4:s.index("\n---\n", 4)]) or {}


def _guideline_table() -> str:
    rows, n1 = [], 0
    files = sorted((ROOT / "docs").glob("C*_*.md"), key=lambda f: int(re.match(r"C(\d+)", f.name)[1]))
    for f in files:
        m = _front_matter(f)
        if m.get("template_kind") not in CANCER_IDS:
            continue
        code = re.match(r"(C\d+)", f.name)[1]
        title = re.search(r"^# C\d+\.\s*(.+?)(?:照護指引)?\s*$", f.read_text(encoding="utf-8"), re.M)
        lvl = m.get("guideline_level")
        nhi = m.get("nhi_level")
        n1 += (lvl == 1 or nhi == 1)
        rows.append(f"| [**{code}** {title[1].replace("照護指引", "") if title else ''}]({f.name}) | {m.get('guideline', '')} "
                    f"| **{LEVELS.get(lvl, '?')}** | {LEVELS.get(nhi, '—')} | {m.get('guideline_note', '')} |")
    head = ("| 檔 | 依據的準則 | **治療準則來源層級** | 健保給付來源層級 | 備註 |\n"
            "|---|---|:---:|:---:|---|\n")
    return head + "\n".join(rows) + (
        f"\n\n> **{len(rows)} 個癌別檔，目前 {n1} 個至少有一部分達「① 原文全文」。**")


# 獨立教材（V5.3.0 起）：上游原始檔放 teaching_src/<slug>.html，登記在 teaching_src/registry.json
TEACHING_SRC = ROOT / "teaching_src"
TEACHING = {k: v for k, v in json.loads((TEACHING_SRC / "registry.json").read_text(encoding="utf-8")).items()
            if not k.startswith("_")}
GOOGLE_FONTS = re.compile(r'[ \t]*<link[^>]+fonts\.(?:googleapis|gstatic)\.com[^>]*>\n?')


def _teaching_html(slug: str, cfg: dict, raw: str) -> str | None:
    """把整合層注入上游原始檔。只依賴 </head>、<body…>、</body> 三個錨點——任何模板都能套。"""
    v = VERSION[1:]
    back = "../" + cfg["back"].removesuffix(".md") + "/"
    head = f'<link rel="stylesheet" href="../assets/ccm-teaching/ccm-teaching.css?v={v}">\n'
    if cfg.get("fonts") == "ibm-plex":
        raw, n = GOOGLE_FONTS.subn("", raw)
        if n == 0:
            log.warning("教材 %s：登記了自帶字型，但原始檔裡沒有 Google Fonts 連結可換", slug)
        head = f'<link rel="stylesheet" href="../assets/ccm-teaching/fonts.css?v={v}">\n' + head
    if "fonts.googleapis.com" in raw:
        log.warning("教材 %s：仍引用 Google Fonts（醫院內網可能擋外部字型）——registry 設 fonts", slug)
    if cfg.get("page_title"):
        raw, n = re.subn(r"<title>[^<]*</title>", f"<title>{escape(cfg['page_title'])}</title>", raw, count=1)
        if n == 0:
            log.warning("教材 %s：找不到 <title>", slug)
    bar = (f'<div class="ccm-t-bar"><a class="ccm-t-back" href="{back}">← 回 {escape(cfg["back_label"])}</a>'
           f'<span class="ccm-t-site">彰濱秀傳癌症中心 · 個管師訓練系統</span>'
           f'<span class="ccm-t-ver" title="個管師訓練系統 {VERSION}">{VERSION}</span></div>\n')
    foot = (f'<footer class="ccm-t-foot"><p><strong>彰濱秀傳癌症中心 · 個管師訓練系統</strong>　教學用途。'
            f'{escape(cfg.get("foot_note", ""))}<br>其他癌別分期版本對照見 '
            f'<a href="../C0_general/#分期系統版本對照ajcc-已改逐部位滾動更新">C0 → 分期系統版本對照表</a></p>'
            f'<div class="ccm-t-links"><a class="ccm-t-back" href="{back}">← 回 {escape(cfg["back_label"])}</a>'
            f'<a class="ccm-t-sela" href="https://github.com/Sela1227" target="_blank" rel="noopener" title="本系統由 SELA 維護">'
            f'<img src="../assets/sela-logo/sela.svg" alt="SELA">by SELA</a></div></footer>\n')
    for tag in ("</head>", "</body>"):
        if raw.count(tag) != 1:
            log.warning("教材 %s：%s 應該剛好一個，實際 %d 個", slug, tag, raw.count(tag))
            return None
    m = re.search(r"<body[^>]*>\n?", raw)
    if not m:
        log.warning("教材 %s：找不到 <body>", slug)
        return None
    raw = raw[:m.end()] + bar + raw[m.end():]
    return raw.replace("</head>", head + "</head>").replace("</body>", foot + "</body>")


def on_files(files, config):
    from mkdocs.structure.files import File
    for slug, cfg in TEACHING.items():
        src = TEACHING_SRC / f"{slug}.html"
        if not src.exists():
            log.warning("教材 %s：teaching_src/%s.html 不存在", slug, slug)
            continue
        if (ROOT / "docs" / slug).exists():
            log.warning("教材 %s：docs/%s/ 不該存在——原始檔放 teaching_src/，build 時產生", slug, slug)
        data = src.read_bytes()
        if not cfg.get("inject", True):
            if hashlib.sha256(data).hexdigest() != cfg.get("sha256"):
                log.warning("教材 %s：內容與 registry 的 sha256 不符——這是外部專案的複本，"
                            "不要手改；換新版請同時更新 upstream_version 與 sha256", slug)
            files.append(File.generated(config, f"{slug}/index.html", content=data))
            continue
        back = cfg.get("back", "")
        if not files.get_file_from_path(back):
            log.warning("教材 %s：返回目標 %r 不存在", slug, back)
        html = _teaching_html(slug, cfg, data.decode("utf-8"))
        if html is not None:
            files.append(File.generated(config, f"{slug}/index.html", content=html))
    return files


def _bust(path: str) -> str:
    return re.sub(r"\?v=[^&]*$", "", path) + f"?v={VERSION[1:]}"


def on_config(config):
    config.extra["version"] = VERSION
    config.extra["cats"] = CATS
    config.extra["icon_svg"] = {k: f'<svg viewBox="0 0 24 24" aria-hidden="true">{v}</svg>' for k, v in ICONS.items()}
    config.extra_css = [_bust(str(c)) for c in config.extra_css]
    for i, js in enumerate(config.extra_javascript):          # str 或 ExtraScriptValue
        if isinstance(js, str):
            config.extra_javascript[i] = _bust(js)
        else:
            js.path = _bust(js.path)

    # 規則 8：不得加回 760px sidebar override
    css = (ROOT / "docs/stylesheets/extra.css").read_text(encoding="utf-8")
    # （760px 的 media query 本身可以用，例如首頁任務鈕排版；禁止的是強迫 sidebar 顯示的那組 override）
    if re.search(r"__drawer\]\s*\{[^}]*display:\s*none|md-sidebar--primary\s*\{[^}]*position:\s*sticky", css):
        log.warning("extra.css 出現強迫 sidebar 顯示的 override（規則 8，坑 #22）")

    # R11（V5.5.0）：顏色只能寫在檔頭的 token 區；之後寫死色碼（#fff 除外）→ WARNING
    tail = css.split("中文字體閱讀感", 1)[-1]
    if hexes := sorted(set(re.findall(r"#[0-9a-fA-F]{3,8}\b", tail)) - {"#fff", "#FFF"}):
        log.warning("extra.css 在 token 區之外寫死色碼 %s——改用 var(--ccm-…)", "、".join(hexes))

    # 規則 11：站名與 logo
    if config.site_name != "彰濱秀傳癌症中心 - 個管師訓練系統":
        log.warning("site_name 被改動（規則 11）：%r", config.site_name)
    for key in ("logo", "favicon"):
        rel = config.theme.get(key)
        if not rel or not (ROOT / "docs" / rel).exists():
            log.warning("theme.%s 檔案不存在（規則 11）：%r", key, rel)
    return config


def on_page_markdown(markdown, page, config, files):
    src = page.file.src_uri
    if "<svg" in markdown:
        log.warning("%s：不要手寫 <svg>，改用 :ccm-圖示名稱:（圖示放 icons/）", src)
    markdown = ICON_CODE.sub(lambda m: _icon(m, src), markdown)
    if src == "index.md":
        return markdown
    cat = page.meta.get("category")
    if cat not in CATS:
        log.warning("%s：沒有合法的 category（%r）——在 front matter 寫 category: learn|daily|cancer|lookup|admin", src, cat)
    kind = page.meta.get("template_kind")
    if kind:
        if kind not in CANCER_IDS:
            log.warning("%s：template_kind %r 不認得", src, kind)
        else:
            ids = set(re.findall(r"\{\s*#([\w-]+)\s*\}", markdown))
            if missing := CANCER_IDS[kind] - ids:
                log.warning("%s：癌別模板缺章節 ID %s", src, sorted(missing))
    meta = page.meta
    if kind in CANCER_IDS:
        for key in CANCER_META:
            if key not in meta:
                log.warning("%s：癌別檔 front matter 缺 %s", src, key)
        for key in ("guideline_level", "nhi_level"):
            if key in meta and meta[key] not in LEVELS:
                log.warning("%s：%s 只能是 1–4（%r）", src, key, meta[key])
    if "review_status" in meta and meta["review_status"] not in REVIEW_STATUS:
        log.warning("%s：review_status 只能是 %s（%r）", src, "/".join(REVIEW_STATUS), meta["review_status"])
    if "review_due" in meta:
        due = meta["review_due"]
        if not isinstance(due, dt.date):
            log.warning("%s：review_due 要寫成日期 YYYY-MM-DD（%r）", src, due)
        elif due < TODAY:
            log.warning("%s：已過下次檢視期限 %s——請重新檢視內容後把 review_due 往後改", src, due)
    info = []
    if meta.get("review_status") in REVIEW_STATUS:
        info.append(("審閱狀態", REVIEW_STATUS[meta["review_status"]]))
    if meta.get("guideline_level") in LEVELS:
        info.append(("治療準則來源", LEVELS[meta["guideline_level"]]))
    if meta.get("nhi_level") in LEVELS:
        info.append(("健保給付來源", LEVELS[meta["nhi_level"]]))
    if isinstance(meta.get("review_due"), dt.date):
        info.append(("下次檢視期限", meta["review_due"].isoformat()))
    meta["ccm_review"] = info
    if "<!-- ccm:guideline-table -->" in markdown:
        markdown = markdown.replace("<!-- ccm:guideline-table -->", _guideline_table())
    if re.search(r"^## 目錄\s*$", markdown, re.M):
        log.warning("%s：不得自寫『## 目錄』（規則 12，右側 TOC 已提供）", src)
    want = _nav_cat.get(src)
    if want and cat != want:
        log.warning("%s：側欄放在「%s」組，但 front matter category=%r", src, CATS[want]["label"], cat)
    return markdown


def on_nav(nav, config, files):
    """記下每頁在「完整資料庫」裡所屬的組，並檢查每個 .md 都有進 nav。"""
    _nav_cat.clear()
    in_nav: set[str] = set()

    def walk(items, group=None):
        for it in items:
            if it.is_section:
                walk(it.children, NAV_GROUP.get(it.title, group))
            elif it.is_page:
                in_nav.add(it.file.src_uri)
                if group:
                    _nav_cat[it.file.src_uri] = group

    walk(nav.items)
    for f in files.documentation_pages():
        if f.src_uri not in in_nav:
            log.warning("%s：沒有放進 mkdocs.yml 的 nav", f.src_uri)
    return nav



HREF = re.compile(r'\shref="([^"]*)"')
IDS = re.compile(r'\s(?:id|name)="([^"]+)"')
SKIP_SCHEMES = ("http:", "https:", "mailto:", "tel:", "javascript:", "data:")
SKIP_PAGES = {"drug-lookup/index.html"}   # 外部專案的 web app，不檢查它的內部連結


def check_site_links(site: Path, prefix: str = "/") -> list[str]:
    """掃 site/ 每一頁的每個站內 href：目標檔案要存在、#anchor 要存在。
    涵蓋 markdown 連結、raw HTML、教材與模板——mkdocs 本身只驗 markdown 連結。"""
    pages = {p.relative_to(site).as_posix(): p for p in site.rglob("*.html")}
    ids_cache: dict[str, set[str]] = {}

    def ids_of(rel: str) -> set[str]:
        if rel not in ids_cache:
            ids_cache[rel] = set(IDS.findall(pages[rel].read_text(encoding="utf-8")))
        return ids_cache[rel]

    bad = []
    for rel, path in pages.items():
        if rel in SKIP_PAGES:
            continue
        html = path.read_text(encoding="utf-8")
        base = posixpath.dirname(rel)
        for href in set(HREF.findall(html)):
            if not href or href.startswith(SKIP_SCHEMES) or href.startswith("//"):
                continue
            parts = urlsplit(href)
            target_path = unquote(parts.path)
            if target_path.startswith("/"):        # 404.html 用絕對路徑（site_url 前綴）
                if not target_path.startswith(prefix):
                    bad.append(f"{rel} → {href}（絕對路徑不在站台前綴 {prefix} 底下）")
                    continue
                target_path, base_ = target_path[len(prefix):] or "./", ""
            else:
                base_ = base
            if target_path:
                tgt = posixpath.normpath(posixpath.join(base_, target_path))
                if tgt.startswith(".."):
                    bad.append(f"{rel} → {href}（超出站台根目錄）")
                    continue
                if target_path.endswith("/") or (site / tgt).is_dir():
                    tgt = posixpath.join(tgt, "index.html") if tgt != "." else "index.html"
                if not (site / tgt).exists():
                    bad.append(f"{rel} → {href}（目標不存在）")
                    continue
            else:
                tgt = rel
            frag = unquote(parts.fragment)
            if frag and tgt in pages and tgt not in SKIP_PAGES and frag not in ids_of(tgt):
                bad.append(f"{rel} → {href}（anchor 不存在）")
    return sorted(set(bad))


def on_post_build(config):
    site = Path(config.site_dir)
    prefix = urlsplit(config.site_url or "/").path or "/"
    bad = check_site_links(site, prefix if prefix.endswith("/") else prefix + "/")
    if bad:
        log.warning("站內連結失效 %d 個：\n  %s", len(bad), "\n  ".join(bad))
