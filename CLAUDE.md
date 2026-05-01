# CLAUDE.md｜彰濱秀傳癌症個管師手冊網站

**專案**：MkDocs + Material Theme 部署在 GitHub Pages（私有 Repo + GitHub Pro）
**當前版本**：V1.8.6
**網站用途**：彰濱秀傳癌症中心個管師工作手冊，供新進個管師隨時查詢，含即時搜尋功能

---

## ⚠️ 永久規則（每版必遵守）

### 規則 1：版本號四處必須同步

每次升版，下列四個地方**全部同步更新**，缺一不可：

| 位置 | 改什麼 |
|------|--------|
| `docs/javascripts/mobile-nav.js` | `var CCM_VERSION = "V?.?.?"` |
| `docs/stylesheets/extra.css` | 頂部版本說明 comment |
| `README.md` | 頂部「當前版本：V?.?.?」 |
| ZIP 打包名稱 | `CCM Manual V?.?.?.zip` |

版本不一致會讓 header 顯示舊版號，使用者無法確認自己看的是哪版。

### 規則 2：軟體說明 MD 絕對不能明文寫帳號密碼

任何軟體說明文件（H1、H2、H3... 未來任何 H 章節），一律不得出現：
- 具體帳號代碼（員工編號、系統代碼）
- 具體密碼
- 帳號密碼對照表

**正確寫法**：「使用你自己的帳號和密碼登入。如忘記帳號密碼，請洽系統管理員。」

### 規則 3：所有專用軟體說明書的維護單位

`H1_`、`H2_`、`H3_`、`H4_` 等所有軟體說明文件，維護單位欄位統一填寫：

> 放射腫瘤科 林伯儒 醫師

原因：這份手冊部署在公開 URL，任何人都能看到。

---

## 一、Repo 結構對映

| 我要改的事 | 動這些檔案 |
|-----------|-----------|
| 導覽結構 | `mkdocs.yml` 的 `nav:` 區段 |
| 自動部署設定 | `.github/workflows/deploy.yml` |
| 網站外觀、字型、顏色 | `mkdocs.yml` + `docs/stylesheets/extra.css` |
| 手機底部導覽列、版本徽章 | `docs/javascripts/mobile-nav.js` |
| 首頁卡片 | `docs/index.md` |
| 品質指標 | `docs/G_quality-index.md` |
| 培訓計畫書 | `docs/A_training-plan.md` |
| HIS + 五大系統說明 | `docs/B1_HIS-manual.md` |
| 各癌別照護指引 | `docs/C1_lung-cancer.md`、`docs/C2_breast-cancer.md`、`docs/C3-C6_other-cancers.md` |
| 個管追蹤系統說明 | `docs/H1_ccm-tracker-guide.md` |
| MDT 會議系統說明 | `docs/H2_mdt-guide.md` |
| 抗癌藥物速查說明 | `docs/H3_cancer-drugs.md` |
| 病歷互審系統說明 | `docs/H4_peer-review-guide.md` |
| 抗癌藥物速查系統本體 | `docs/drug-lookup/index.html` |

---

## 二、Nav 結構對映表

| 頂部 Tab | 左側項目 | MD 檔 |
|---------|---------|-------|
| A｜新人通則 | 工作指導手冊 | `A_work-guide.md` |
| A｜新人通則 | 培訓計畫書 | `A_training-plan.md` |
| B｜軟體操作 | B1. HIS 系統操作手冊 | `B1_HIS-manual.md` |
| B｜軟體操作 | B2. 其他工具使用說明 | `B2_other-tools.md` |
| C｜各癌別照護指引 | C1. 肺癌 | `C1_lung-cancer.md` |
| C｜各癌別照護指引 | C2. 乳癌 | `C2_breast-cancer.md` |
| C｜各癌別照護指引 | C3–C6. 其他癌別 | `C3-C6_other-cancers.md` |
| D｜表單與範本 | 表單與範本 | `D_forms.md` |
| E｜專題與進階 | 專題與進階 | `E_advanced.md` |
| F｜臨床知識庫 | 臨床知識庫 | `F_clinical-kb.md` |
| G｜品質指標 | 品質指標速查 | `G_quality-index.md` |
| H｜專用軟體 | 個管追蹤系統 | `H1_ccm-tracker-guide.md` |
| H｜專用軟體 | MDT 會議管理系統 | `H2_mdt-guide.md` |
| H｜專用軟體 | 抗癌藥物速查系統 | `H3_cancer-drugs.md` |
| H｜專用軟體 | 病歷互審系統 | `H4_peer-review-guide.md` |

新增軟體說明時命名規則：`H4_`、`H5_` 依序遞增，全英文小寫加連字號。

---

## 三、踩過的坑

**#1（V1.0.0）私有 Repo + GitHub Pages 需要 GitHub Pro**
- 症狀：Settings → Pages 找不到 GitHub Actions 選項
- 原因：私有 Repo 的 GitHub Pages 功能需要付費方案
- 做法：升級 GitHub Pro（$4/月）

**#2（V1.0.0）MD 檔名含中文在 Linux 伺服器編碼壞掉**
- 症狀：build 時 nav 找不到中文檔名的 MD 檔，顯示亂碼路徑
- 做法：所有 docs/ 下的 MD 檔一律英文檔名（A_、B1_、C1_ 等）

**#3（V1.0.0）中文搜尋 separator 設定錯誤導致索引完全壞掉**
- 症狀：搜尋任何中文關鍵字都找不到結果
- 原因：`[\u3000-\u9FFF]` 把所有中文字都當分隔符
- 做法：separator 只切標點符號，加 jieba 套件做中文斷詞

**#4（V1.3.0）手機底部導覽列點了路徑疊加跳錯頁**
- 原因：`document.baseURI` 在子頁面返回子頁路徑，不是網站根目錄
- 做法：改用 `document.querySelector('base').href` 取得 MkDocs 注入的 base tag

**#5（V1.4.0）CSS content 變數版本徽章跨頁不穩定**
- 原因：CSS pseudo-element `content: var()` 跨頁行為不一致
- 做法：改用 JS 直接 `createElement('span')` 注入 header

**#6（V1.4.0）navigation.expand 強制展開所有側欄**
- 做法：移除 `navigation.expand`，改加 `navigation.prune`

**#7（V1.7.0）軟體說明 MD 出現明文帳號密碼**
- 症狀：H1 登入章節含帳號代碼和密碼
- 做法：永久規則 2（見頂部）— 任何軟體說明 MD 一律只寫「使用自己帳密，忘記請洽管理員」

**#8（V1.7.0）版本號分散在多個檔案沒有同步**
- 症狀：JS 顯示舊版號，ZIP 是新版號
- 做法：永久規則 1（見頂部）— 升版時四個地方必須同步

**#9（V1.7.1）A_work-guide.md 多個 h1 導致錨點失效**
- 症狀：A_work-guide.md 的部分標題（第一部分至第五部分）用 h1，MkDocs 錨點對非第一個 h1 行為不穩定
- 做法：部分標題改為 h2（## 第X部分），保留第一個 h1 作為頁面標題

**#10（V1.8.4）mkdocs.yml 遺失 markdown_extensions 導致全站 !!! 區塊不渲染**
- 症狀：所有 `!!! warning`、`!!! tip`、`!!! note`、`!!! info` 顯示為純文字
- 原因：mkdocs.yml 從未加入 `markdown_extensions` 區塊，admonition 和 pymdownx 套件沒有啟用
- 做法：補回完整的 markdown_extensions 區塊（admonition、pymdownx.details、superfences、highlight、tabbed、emoji、tasklist、tables、toc、attr_list）

**#11（V1.8.6）F 章節索引不見 + 全站表格破版**
- F 索引不見：`# F1.`/`# F2.` 是 h1，MkDocs TOC 從 h2 開始，所以不進索引。修法：降為 h2，子節依序降級。
- 側欄收合：`navigation.sections` 讓章節標頭變固定不可收合。移除後預設收合。同時移除 `toc.integrate`（TOC 回右側獨立面板，左側欄更乾淨）。
- 表格破版：各欄 `white-space: nowrap` 互相競爭導致某些欄過寬。全站加 CSS：`word-break: break-word` + `max-width` 限制。

---

## 四、版本歷程

| 版本 | 主要異動 |
|------|---------|
| V1.0.0 | MkDocs 骨架，GitHub Actions 部署，MD 改英文檔名 |
| V1.1.0 | 程式名稱定案，H｜專用軟體章節（H1、H2），手機底部導覽列 |
| V1.2.0 | 手機表格換行，桌機表格欄寬，底部導覽列樣式 |
| V1.3.0 | 底部導覽列路徑修正（坑#4），版本徽章改 JS（坑#5），側欄改可收合（坑#6） |
| V1.4.0 | 表格欄寬改 auto，toc.integrate 消除右側欄 |
| V1.5.0 | 中文搜尋根本修正（坑#3），所有錨點連結驗證通過 |
| V1.6.0 | G_quality-index 依 115 年版更新至 60 項指標 |
| V1.7.0 | H3 抗癌藥物速查（drug-lookup/index.html，145 種），刪明文帳密（坑#7），版本號同步規則（坑#8），README.md |
| V1.7.1 | 修 deploy.yml 移除 --strict，移除無效 jieba_dict:auto，修 A_work-guide.md 多個 h1（坑#9） |
| V1.8.0 | 所有 H 章節補維護單位（放射腫瘤科 林伯儒 醫師），新增 H4 病歷互審系統說明書，CLAUDE.md 加規則 3 |
| V1.8.1 | F5 癌症三大治療方式基礎（手術/化療/放療），連結至 A_training-plan.md 第 3.3 節 |
| V1.8.2 | F_clinical-kb.md 全面整合重組：原 F1–F5 合為 F1（查表）+ F2（概念），消除重疊 |
| V1.8.3 | F2 新增第十節藥物速查表（健保署 139 種抗癌藥物，依化療/標靶/免疫/荷爾蒙分類，含副作用與警示） |
| V1.8.4 | 修 mkdocs.yml 補上遺失的 markdown_extensions（admonition、pymdownx 系列），修正全站 !!! 區塊無法渲染問題（坑#10）|
| V1.8.5 | 藥物速查表排版改善：5 欄精簡、癌別縮寫、橫向滾動容器（.drug-table-wrapper）、斑馬紋、縮小字體 0.75rem |
| V1.8.6 | 三大系統性修正：①F heading 降級（F1/F2 h1→h2）②移除 navigation.sections 和 toc.integrate（側欄收合 + TOC 回右側）③全站表格 CSS 強制換行防破版（坑#11）|

---

## 五、關鍵路徑

```
docs/drug-lookup/index.html    # 抗癌藥物速查本體，MkDocs 原封不動複製
                               # 網址：/CCM-manual/drug-lookup/
                               # 更新：直接替換此檔 + 改 H3_cancer-drugs.md 版本說明

docs/javascripts/mobile-nav.js # CCM_VERSION 在此改（規則 1）
docs/stylesheets/extra.css     # 版本說明 comment 在此改（規則 1）
README.md                      # 當前版本在此改（規則 1）
```

---

## 六、部署

```bash
git add .
git commit -m "V1.X.0：xxx"
git push origin main
# → GitHub Actions 自動 build + deploy，約 1–2 分鐘後上線
```

---

## 七、下版候選工作

按優先序：

1. **補 B1 五大系統操作截圖** — 系統陸續上線後補入，新人最需要
2. 抗癌藥物速查有新版時替換 `docs/drug-lookup/index.html`
3. 子宮頸癌、子宮體癌、卵巢癌完治率定義補入 G_（待各團隊討論）
4. 評估 C3–C6 是否需要拆成獨立 MD 檔

---

## 八、一句話總結

V1.8.6 三大修正：F 索引恢復（heading 降級）、側欄改為收合式（移除 navigation.sections + toc.integrate）、全站表格系統性 CSS 修正。
