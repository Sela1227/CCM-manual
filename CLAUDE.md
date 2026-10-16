# CLAUDE.md｜彰濱秀傳癌症中心 - 個管師訓練系統

給接手的 Claude：先讀完這頁（約 200 行）。決策脈絡、坑、歷史都在 `docs-dev/`，需要時再查。

## 0. 定位與 Kit 對齊

- 已對齊 SELA Starter Kit V1.26.0 的成熟專案（V4 系列起點首次對齊，之後隨 Kit 跳版只評估落差）。**以本檔為主、Kit 為輔**；不要為對齊 Kit 動既有設計。
- 刻意不對齊 Kit 的部分：header 用 `logo-header.png`（SELA logo 只當 footer 歸屬印記）、主色 `#25506b`、不另做 app logo、坑 #1–#52 保留敘述體。完整仲裁與 CCM 回流 Kit 的坑清單：`docs-dev/kit-alignment.md`。
- 版號規則照 Kit（a、b 不設上限，c 逢十進位）。完成版本時評估 `SELA-handoff.md`（Kit 鐵律 #0）。
- **交付閉環（規則 18）**：交付訊息附「Kit §3 鐵律逐條核對 ✓」，純靜態 MkDocs 所以程式組多數不適用。
- **Sela 自己 git push**。不要 push；交付方式是 zip（見 §6）。

**Stack**：MkDocs 1.6.1 + Material 9.7.7 + pymdown 12.3 + jieba + git-revision-date-localized 1.5.4（`requirements.txt` 精確鎖版）。GitHub Pages（私有 repo `Sela1227/CCM-manual`），CI 在 `.github/workflows/deploy.yml`。

## 1. 唯一閘門

```bash
rm -rf site && mkdocs build --strict 2>&1 | grep -E "WARNING|ERROR|Aborted|Documentation built"
# 只該看到 "Documentation built in X seconds"
```

本機與 CI 跑同一條。所有規範檢查都寫在 `hooks.py`，違規一律 `log.warning` → `--strict` 中止。**build 需要 git 歷史**；沒有 `.git` 的目錄預覽用 `CCM_GIT_DATES=false mkdocs build --strict`。

hooks.py 會擋下的事：

| 類別 | 檢查 |
|---|---|
| 分類 | 每頁 front matter 要有合法 `category`；所在側欄組要等於 category；每個 md 都要進 nav |
| 癌別檔 | `template_kind` 的必備章節 ID；審閱欄位齊全且合法；`review_due` 過期 |
| 寫作 | 不得自寫 `## 目錄`；不得手寫 `<svg>`；`:ccm-圖示:` 必須存在 |
| 樣式 | extra.css 不得有強迫 sidebar 的 override（規則 8）；token 區以外不得寫死色碼 |
| 站台 | 站名、logo、favicon（規則 11）|
| 教材 | `teaching_src/` 原始檔存在、整合層注入成功、drug-lookup sha256 相符、`docs/<教材>/` 不得殘留 |
| 連結 | build 後掃 `site/` 每個站內 href 與 #anchor（含 raw HTML、模板、教材、404 頁）|

mkdocs 本身另驗：同檔／跨檔 anchor、`unrecognized_links: warn`、snippet 不存在（`check_paths`）。

**負面測試**：改動檢查時要故意弄壞一次確認會中止。**先把檔案備份到 scratch，用備份還原，不要用 `git checkout`**（會把未 commit 的改動一起還原，踩過兩次）。

## 2. 永久規則（完整說明見 `docs-dev/rules.md`）

1. **版號只寫在根目錄 `VERSION`**。header／footer 徽章、教材頂部列、CSS／JS 的 `?v=` 全由 build 產生。任何檔案都不寫當前版號；歷史敘述用版本中性寫法（坑 #46、#53）。
2. H 系列說明書不寫明文帳密（「使用你自己的帳號和密碼登入」）。
3. nav 巢狀可以，但不得靠 CSS 強迫 sidebar；出問題就 revert。
4. H 系列維護單位填「放射腫瘤科 林伯儒 醫師」。
5. （退役）JS 不再組站內路徑；若日後恢復，路徑一律從站根推算。
6. 唯一閘門＝`mkdocs build --strict`（§1）。
7. 主色用 `:root, [data-md-color-primary]` 覆蓋變數，不用 `palette: custom`。
8. extra.css 不加回 760px sidebar override（坑 #22：使用者 viewport 2160px，Material 自己處理）。
9. drug-lookup 是外部 SELA 專案的複本，不手改；換版＝整檔替換＋更新 registry 的 `upstream_version` 與 `sha256`。
10. 框架元素（nav、首頁、快捷列、底部導覽）用 SVG 不用 emoji；內文 emoji 不管。
11. 站名「彰濱秀傳癌症中心 - 個管師訓練系統」；`logo-header.png`、`favicon.png` 必須存在。
12. 標題層級：H2 5–10 個；H3 給 ≥20 行的子章節；更短用 H4 或粗體；不自寫目錄。
13. 單檔 >1000 行考慮拆檔；頁數 ≥4 才巢狀。
14. 跨檔資料單一來源：完整版只寫一處，其他地方連過去。數字型資料要標明源頭與連動關係（坑 #62）。
15. 時效性內容標明類型與查證時點；準則版本標到版本號、設單一對照表、不默默升版。
16. 新坑用「症狀／原因／做法」三段式，接在 `docs-dev/pitfalls.md` 檔尾。
17. 優化體檢 OPT-1/2/3 不適用（純靜態站）；OPT-4「生成後驗證」由閘門落實。
18. 交付前逐條核對 Kit §3 並在交付訊息回報。

**內容寫作的硬原則**（坑 #64、#66、#68–#71、#74）：審稿建議＝診斷＋解方，診斷收下、解方先驗證；「待確認」前先真的查五分鐘；來源要分層（① 原文全文 → ④ 未查證）；健保條文以專案內 `chap9_*.pdf` 原文為準（是 zip 偽裝，`unzip` 後有 OCR 全文；目前最新 1150922）；台灣健保 ≠ FDA／國際準則。

## 3. 架構速覽

| 東西 | 位置 | 說明 |
|---|---|---|
| 版號 | `VERSION` | 唯一來源 |
| 規範檢查 | `hooks.py` | 見 §1 |
| 模板 | `overrides/main.html`、`partials/header.html`、`partials/ccm-mobile-nav.html` | 麵包屑、版號徽章、SELA 印記、底部導覽、審閱資訊列。header.html 複製自 Material 9.7.7，升級前要 diff |
| 樣式 | `docs/stylesheets/extra.css` | 檔頭是色彩 token（淺色／深色兩組），其餘只用 `var(--ccm-…)` |
| JS | `docs/javascripts/extra.js` | 只剩 `ccmOpenSearch()` |
| 圖示 | `icons/<名稱>.svg` | 內文寫 `:ccm-名稱:`；`.big` 首頁大圖示、`.plain` 不加 class、其他 `.class` 附加；模板用 `config.extra.icon_svg.名稱` |
| 共用片段 | `snippets/*.md` | 內文寫 `--8<-- "檔名.md"`（可縮排放進 admonition）。緊急處理口袋卡、健保查證註記、來源層級④ 註記、追蹤重點引言 |
| 教材 | `teaching_src/<slug>.html` + `registry.json` | build 時注入返回列、版號、footer、自帶字型；簡介頁 `docs/T<n>_<slug>.md` |
| 字型 | `docs/assets/ccm-teaching/fonts/` | IBM Plex（OFL），只含 latin |
| 開發文件 | `docs-dev/` | 不發布。rules、pitfalls、history、backlog、kit-alignment、architecture-v5 |

### 分類（front matter `category`）

| category | 側欄組名＝hub | 底部導覽鈕 |
|---|---|---|
| learn | 學習中心（hub_learning）| 學習 |
| daily | 日常工作（hub_daily）| 工作 |
| cancer | 癌別照護（hub_cancer）| 癌別 |
| lookup | 臨床速查（hub_lookup）| 不亮 |
| admin | 系統與管理（hub_admin）| 不亮 |

定義在 `hooks.py` 的 `CATS`。側欄頂層是首頁＋五個 hub，「完整資料庫」底下依上表分組。

### 癌別檔（C1–C13）

- 章節固定 ID：`overview staging treatment followup faq edu`（必備）＋ `nhi notes care redflags appendix`（選配）。寫法 `## 七、常見問題與處理 { #faq }`。連結一律 `C3_colorectal-cancer.md#faq`，不用中文 slug。C10 用 `template_kind: cancer-split`（`rcc`／`bladder` 兩部）。
- 審閱欄位（front matter）：`guideline`、`guideline_level`（1–4）、`nhi_level`（選填）、`guideline_note`、`review_status`（draft／pending／reviewed）、`review_due`（YYYY-MM-DD，過期 build 失敗）。欄位名避開 Material 的 `status`。
- C0「治療準則版本對照 → 現況盤點」表由上述欄位自動產生（`<!-- ccm:guideline-table -->`）。
- 「最後更新」＝git 最後 commit 日期，自動顯示在頁底；文件資訊表不再寫最後更新。
- `redflags` 尚未建立：C2、C9、C11–C13（這幾檔快捷列沒有「立即升級」鈕，建立真紅旗段時再加）。

## 4. 常見操作

**新增一頁**：建 `docs/<英文檔名>.md`（front matter 寫 `category`）→ `mkdocs.yml`「完整資料庫」對應組加一行 → build。

**新增教材**：上游原始檔原封不動放 `teaching_src/<slug>.html` → `registry.json` 加一筆（`back`、`back_label`、`foot_note`、用 Google Fonts 的設 `fonts`）→ 寫簡介頁 `docs/T<n>_<slug>.md` 放進「互動教材」→ 站內連結寫 `<slug>/index.html`。

**新增圖示**：放 `icons/<名稱>.svg`（viewBox 0 0 24 24），內文用 `:ccm-名稱:`。

**加共用片段**：放 `snippets/<名稱>.md`，各處用 `--8<-- "<名稱>.md"`。改片段＝所有引用處一起變。

**跨檔 anchor**：不要手打，從 build 產物撈：`grep -oE 'id="關鍵字[^"]*"' site/<頁>/index.html`。標題不要放日期或斜線。

**批次改檔**：每個 replace 都要 assert 命中次數（坑 #77）；改前先看實際格式（坑 #57）。

**版面改動**：用 Playwright 對產物截圖驗收（桌機 1280／手機 390，淺色＋深色）。本機起站：把 `site/` 複製到任一目錄的 `CCM-Manual/` 底下，`python3 -m http.server`。

## 5. 升版清單

1. 改 `VERSION`。
2. 癌別檔內容重看過就把 `review_due` 往後改（只改日期不看內容等於沒做）。
3. `mkdocs build --strict` 零 warning；有改檢查就做負面測試。
4. `docs-dev/history.md` 加一行；`docs-dev/backlog.md` 刪掉做完的；新坑寫進 `docs-dev/pitfalls.md`。
5. 本檔 §7 的「現況」改成新版一句話（只留最近 3 版）。
6. commit（訊息結尾附 Co-Authored-By 與 Claude-Session 行）→ 打包 zip（§6）。

## 6. 交付

- `git archive HEAD --format=zip -o "CCM Manual V<VERSION>.zip"`：檔名空格分隔、無外層資料夾。
- Sela 用自製 Git Pusher 匯入 zip 或自己 git push → GitHub Actions（Python 3.12、`fetch-depth: 0`）build 並部署。
- 部署後實測：footer 沒有黑色橫條（坑 #25）、側欄巢狀沒有重複標題、深色模式正常。

## 7. 現況（最近 3 版）

- **V5.5.0** 內審重構 P6（收尾）：共用片段（snippets）、圖示短碼與 `icons/` 單一來源、CSS 色彩 token 與深色模式修正（主色在深色模式原本被 Material 的 indigo 蓋掉、表頭是刺眼的淺灰）、本檔精簡到 200 行內，坑與歷史移到 `docs-dev/`。
- **V5.4.0** P5：「最後更新」改 git 日期；審閱欄位進 front matter，`review_due` 過期即擋；C0 來源層級表自動產生。
- **V5.3.0** P4：站內連結全面驗證；教材 build 時注入整合層；drug-lookup sha256；自帶字型；教材簡介頁。

**接下來**（細節見 `docs-dev/backlog.md`）：C9 肝膽胰改寫（建真紅旗段、試 ESMO）；C2／C11–C13 紅旗段；健保第九節已有 1150922 新版，比對各癌別檔的 115/6/23 註記（改 `snippets/nhi-*.md` 一處即可）；品管師待定事項（帶教者、時效與正確率門檻）；🅑 待醫師／病理科回答的項目。
