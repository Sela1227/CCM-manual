#!/usr/bin/env python3
"""獨立教材 HTML 的 CCM 整合層套用工具

**為什麼需要**：教材（肺淋巴圖譜、頸部 Level 圖譜…）是從別的工作流產出的
獨立 HTML，上傳進來時是「原始檔」——沒有 CCM 版號、沒有返回連結、沒有 SELA
歸屬印記。每次上游更新教材，整合層就會被沖掉、要重套一次。手工重套會漏東西
（V4.4.0 那次就漏了 title 錨點對不上）。

**用法**：
    # 上游更新了教材 → 放進 uploads → 重套整合層
    python3 tools/integrate_teaching.py lung-nodal-map /path/to/new_lung.html
    python3 tools/integrate_teaching.py head-neck-levels /path/to/new_hn.html

    # 只升版號（不換教材內容）——規則 1 升版時用
    python3 tools/integrate_teaching.py --bump V4.5.0

    # 檢查現有教材整合層完不完整
    python3 tools/integrate_teaching.py --check

**新增一份教材時**：在下方 REGISTRY 加一筆，並記得同步更新
    - 規則 1 的版號位置表（+1 列）
    - 對應癌別檔 / F2 / G / G2 的 cross-ref
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# ── 教材登記表：新增教材時在這裡加一筆 ────────────────────────────────
# eyebrow / meta_last / title 是「上游檔裡的原文」，上游改字就要跟著改
REGISTRY: dict[str, dict[str, str]] = {
    "lung-nodal-map": {
        "back_href": "../C1_lung-cancer/",
        "back_label": "C1 肺癌照護指引",
        "back_label_short": "C1 肺癌",
        "eyebrow": '<div class="eyebrow">IASLC Nodal Map · AJCC 9th ed.</div>',
        "meta_last": "<span>圖為示意，非等比解剖圖</span>",
        "title_new": "<title>肺癌淋巴分區圖譜 — 個管師教學 | 彰濱秀傳癌症中心</title>",
        "foot_note": (
            "分區依據 IASLC 淋巴結圖譜；分期依據 AJCC Cancer Staging System: Lung, "
            "Version 9（2025/1/1 生效）。圖為示意，非等比解剖圖。"
        ),
    },
    "head-neck-levels": {
        "back_href": "../C5_head-neck-cancer/",
        "back_label": "C5 頭頸癌照護指引",
        "back_label_short": "C5 頭頸癌",
        "eyebrow": '<div class="eyebrow">Surgical Neck Levels I–VII · AJCC 8th ed.</div>',
        "meta_last": "<span>右頸側面觀，投影示意</span>",
        "title_new": "<title>頸部淋巴 Level 圖譜 — 個管師教學 | 彰濱秀傳癌症中心</title>",
        "foot_note": (
            "分區依據 2013 Neck Level Consensus；N 分期版本依部位不同"
            "（鼻咽／p16+ 口咽為 Version 9，口腔・喉・下咽為第 8 版）。右頸側面觀，投影示意。"
        ),
    },
    # mHSPC/mCRPC 教材：獨立模板（A4 列印導向、自帶 style、非 eyebrow 結構）。
    # integrate() 的錨點對它不適用——它的整合層是 V4.18.0 手工套的（見 CLAUDE.md 坑 #76）。
    # 但 --bump / --check 只依 slug 掃 docs/<slug>/index.html，不依 integrate 錨點，
    # 所以登記在此即可讓版號同步（規則 1）與煙霧測試（規則 6 第三道）涵蓋它。
    "prostate-mhspc-mcrpc": {
        "back_href": "../C6_prostate-cancer/",
        "back_label": "C6 攝護腺癌照護指引",
        "back_label_short": "C6 攝護腺癌",
        "_manual_layer": True,  # 標記：整合層為手工套用，integrate() 不適用（錨點不同源）
    },
}

DOCS = Path("docs")
C0_ANCHOR = "../C0_general/#分期系統版本對照ajcc-已改逐部位滾動更新"

CCM_CSS = """*{box-sizing:border-box;margin:0;padding:0}

/* ===== CCM Manual 整合層（版號 + 返回 + SELA 印記）===== */
.ccm-ver-inline{
  display:inline-block;margin-left:8px;padding:1px 7px;
  font-family:var(--mono);font-size:11px;font-weight:500;letter-spacing:.02em;
  vertical-align:middle;border:1px solid var(--line);border-radius:8px;
  background:var(--surface-2);color:var(--ink-2);user-select:none;white-space:nowrap;
}
.ccm-back{
  display:inline-flex;align-items:center;gap:5px;
  font-family:var(--mono);font-size:12px;color:var(--ink-2);text-decoration:none;
  padding:4px 10px;border:1px solid var(--line);border-radius:var(--r,8px);
  background:var(--surface);transition:all .15s;
}
.ccm-back:hover{border-color:var(--ink-2);color:var(--ink);}
.ccm-foot{
  border-top:1px solid var(--line);background:var(--surface);
  padding:22px 0 26px;margin-top:8px;
}
.ccm-foot .wrap{display:flex;flex-wrap:wrap;gap:14px;align-items:center;justify-content:space-between;}
.ccm-foot .note{font-size:12px;color:var(--muted);line-height:1.7;max-width:640px;}
.ccm-sela{
  display:inline-flex;align-items:center;gap:5px;
  font-family:var(--mono);font-size:11px;color:var(--muted);text-decoration:none;
  opacity:.75;transition:opacity .15s;
}
.ccm-sela:hover{opacity:1;}
.ccm-sela img{width:15px;height:15px;display:block;}
@media(max-width:600px){
  .ccm-ver-inline{font-size:10px;padding:0 5px;margin-left:5px;}
  .ccm-foot .wrap{gap:10px;}
}"""

CSS_ANCHOR = "*{box-sizing:border-box;margin:0;padding:0}"
BODY_ANCHOR = "</script>\n</body>"


def current_version() -> str:
    """從 extra.js 讀當前版號（規則 1 的第一順位來源）"""
    js = (DOCS / "javascripts" / "extra.js").read_text(encoding="utf-8")
    m = re.search(r'var CCM_VERSION = "(V[\d.]+)"', js)
    if not m:
        raise RuntimeError("讀不到 extra.js 的 CCM_VERSION")
    return m.group(1)


def integrate(slug: str, src: Path, version: str) -> None:
    cfg = REGISTRY[slug]
    h = src.read_text(encoding="utf-8")

    # 已整合過的檔就不要再套一次（避免重複注入）
    if "ccm-ver-inline" in h:
        raise RuntimeError(f"{src} 看起來已經有整合層了——請用上游的原始檔")

    # 1. CSS
    assert CSS_ANCHOR in h, "CSS 錨點對不上（上游改了 reset 寫法？）"
    h = h.replace(CSS_ANCHOR, CCM_CSS, 1)

    # 2. masthead：返回連結 + 版號徽章
    eyebrow = cfg["eyebrow"]
    assert eyebrow in h, f"eyebrow 錨點對不上（上游改字了？）：{eyebrow}"
    new_eyebrow = eyebrow.replace(
        "</div>", '<span class="ccm-ver-inline" id="ccmVer">V0.0.0</span></div>'
    )
    h = h.replace(
        eyebrow,
        f'<div style="margin-bottom:14px">'
        f'<a class="ccm-back" href="{cfg["back_href"]}">← 回 {cfg["back_label"]}</a></div>\n    '
        + new_eyebrow,
        1,
    )

    # 3. meta 末尾加 C0 版本對照 cross-ref
    meta_last = cfg["meta_last"]
    assert meta_last in h, f"meta 錨點對不上：{meta_last}"
    c0_ref = (
        f'<span>其他癌別分期版本對照見 '
        f'<a href="{C0_ANCHOR}" style="color:inherit">C0 → 分期系統版本對照表</a></span>'
    )
    h = h.replace(meta_last, meta_last + "\n      " + c0_ref, 1)

    # 4. footer + 版號常數
    assert BODY_ANCHOR in h, "body 結尾錨點對不上"
    h = h.replace(
        BODY_ANCHOR,
        f"""</script>

<footer class="ccm-foot">
  <div class="wrap">
    <div class="note">
      <strong>彰濱秀傳癌症中心 · 個管師訓練系統</strong>　教學用途，臨床判讀請以主治醫師與病理報告為準。<br>
      {cfg["foot_note"]}
    </div>
    <div style="display:flex;align-items:center;gap:12px">
      <a class="ccm-back" href="{cfg["back_href"]}">← 回 {cfg["back_label_short"]}</a>
      <a class="ccm-sela" href="https://github.com/Sela1227" target="_blank" rel="noopener" title="本系統由 SELA 維護">
        <img src="../assets/sela-logo/sela.svg" alt="SELA"/>by SELA
      </a>
    </div>
  </div>
</footer>

<script>
/* CCM Manual 版號同步（SPEC §10.6：UI 版號 = zip 檔名版號；規則 1 同步位置之一） */
var CCM_VERSION = "{version}";
document.getElementById("ccmVer").textContent = CCM_VERSION;
document.getElementById("ccmVer").title = "個管師訓練系統 " + CCM_VERSION;
</script>
</body>""",
        1,
    )

    # 5. title
    old_title = re.search(r"<title>[^<]*</title>", h)
    assert old_title, "找不到 <title>"
    h = h.replace(old_title.group(0), cfg["title_new"], 1)

    dst = DOCS / slug / "index.html"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(h, encoding="utf-8")
    print(f"✓ {slug}：整合層套用完成（{len(h.splitlines())} 行，版號 {version}）")


def bump(version: str) -> int:
    bad = 0
    for slug in REGISTRY:
        f = DOCS / slug / "index.html"
        if not f.exists():
            print(f"✗ {slug}：檔案不存在")
            bad += 1
            continue
        h = f.read_text(encoding="utf-8")
        h2 = re.sub(r'var CCM_VERSION = "V[\d.]+"', f'var CCM_VERSION = "{version}"', h)
        f.write_text(h2, encoding="utf-8")
        print(f"✓ {slug}：版號 → {version}")
    return bad


def check() -> int:
    ver = current_version()
    bad = 0
    for slug in REGISTRY:
        f = DOCS / slug / "index.html"
        if not f.exists():
            print(f"✗ {slug}：檔案不存在")
            bad += 1
            continue
        h = f.read_text(encoding="utf-8")
        missing = [
            k
            for k, pat in {
                "版號常數": f'var CCM_VERSION = "{ver}"',
                "版號徽章": 'id="ccmVer"',
                "返回連結": 'class="ccm-back"',
                "SELA 印記": "assets/sela-logo/sela.svg",
                "C0 版本對照": "C0_general",
                "footer": "ccm-foot",
            }.items()
            if pat not in h
        ]
        if missing:
            print(f"✗ {slug}：缺 {', '.join(missing)}")
            bad += 1
        else:
            print(f"✓ {slug}：整合層完整（{ver}）")
    return bad


def main() -> int:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0

    if args[0] == "--check":
        return 1 if check() else 0

    if args[0] == "--bump":
        if len(args) < 2:
            print("✗ 用法：--bump V4.5.0")
            return 1
        return 1 if bump(args[1]) else 0

    if len(args) < 2:
        print("✗ 用法：integrate_teaching.py <slug> <上游原始檔路徑>")
        print(f"  可用 slug：{', '.join(REGISTRY)}")
        return 1

    slug, src = args[0], Path(args[1])
    if slug not in REGISTRY:
        print(f"✗ 未登記的教材：{slug}（可用：{', '.join(REGISTRY)}）")
        print("  新增教材請先在本檔 REGISTRY 加一筆，並更新規則 1 的版號位置表")
        return 1
    if not src.exists():
        print(f"✗ 找不到來源檔：{src}")
        return 1

    integrate(slug, src, current_version())
    return 0


if __name__ == "__main__":
    sys.exit(main())
