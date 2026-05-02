# CLAUDE.md｜彰濱秀傳癌症中心 - 個管師訓練系統

**當前版本**：V3.4.0
**Stack**：MkDocs + Material Theme（jieba 中文分詞），GitHub Pages（私有 Repo + GitHub Pro）
**Repo**：Sela1227/CCM-manual（部署不顯示連結，header repo 已拿掉）
**部署工具**：Sela 自製 Git Pusher V1.5.5（匯入 Zip 自動 push）

**這份文件給下次接手的 Claude**：
- 想動框架前先看「永久規則」全部過一遍（11 條）
- 想動內容前先看「Nav 結構對映表」確認改哪個檔
- 想知道「為什麼這版是這樣」看「踩過的坑」#1–#25
- 對話脈絡見「版本歷程」最近 6 版
- 接手第一件事：問 Sela 上次部署狀態，**不要瞎改**

---

## ⚠️ 永久規則（11 條）

> **升版前必跑這份清單**。任何一條沒過 = 這版不可發。

### 🔁 升版自我確認清單

- [ ] **規則 1**：版本號五處同步（JS / CSS / README / CLAUDE.md / ZIP 檔名）
- [ ] **規則 2**：H 系列說明書沒有明文帳密
- [ ] **規則 3**：nav 巢狀條件全滿足（見規則內文）
- [ ] **規則 4**：H 系列維護單位填「放射腫瘤科 林伯儒 醫師」
- [ ] **規則 5**：`getSiteRoot()` 從 pathname 推算，不依賴 base.href
- [ ] **規則 6**：`mkdocs build --strict` 過了（0 warning）
- [ ] **規則 7**：主色用 `:root` 強制覆蓋（不用 `palette: custom`）
- [ ] **規則 8**：extra.css 沒有 `@media min-width: 760px` 大段 sidebar override
- [ ] **規則 9**：drug-lookup/ 子目錄有複製到 docs/
- [ ] **規則 10**：框架元素（nav / 卡片 / 底部導覽）用 SVG，無 emoji
- [ ] **規則 11**：site_name 是「彰濱秀傳癌症中心 - 個管師訓練系統」，logo 三檔在 docs/assets/ 都在
- [ ] 版本歷程已加新行
- [ ] 下版候選工作砍掉已做的、重排優先序
- [ ] 一句話總結已更新
- [ ] 部署後實測：footer 沒有黑色橫條（坑 #25）、4 組巢狀沒翻車

### 規則 1：版本號五處必須同步

| 位置 | 改什麼 |
|------|--------|
| `docs/javascripts/extra.js` | `var CCM_VERSION = "V?.?.?"` |
| `docs/stylesheets/extra.css` | 頂部版本說明 comment |
| `README.md` | 頂部「當前版本：V?.?.?」 |
| `CLAUDE.md` | 頂部「當前版本：V?.?.?」 |
| ZIP 檔名 | `CCM Manual V?.?.?.zip` |

```python
# 用 Python 批次處理，不用 sed 逐行（坑 #14 教訓）
import pathlib
old, new = "V3.4.0", "V3.4.1"  # 假設下版
for p in ["docs/javascripts/extra.js", "docs/stylesheets/extra.css",
          "README.md", "CLAUDE.md"]:
    f = pathlib.Path(p)
    f.write_text(f.read_text().replace(old, new))
```

### 規則 2：H 系列說明書不寫明文帳密

H1–H4（個管追蹤 / MDT / 抗癌藥物 / 病歷互審），未來任何 H 系列檔，禁止：
- 具體帳號代碼
- 具體密碼
- 帳號密碼對照表

**正確寫法**：「使用你自己的帳號和密碼登入。如忘記，請洽系統管理員。」

### 規則 3：Nav 巢狀有條件允許（V3.3.0 起）

**舊規則（V3.0–V3.2）**：「禁止任何巢狀」——是因為 V2.x 巢狀 + 760px CSS override 雙重作用造成 sidebar 標題重複（坑 #16）。

**新規則（V3.3.0 起）**：viewport 真相揭露後（坑 #22，實測 2160px），Material wide-mode 處理巢狀 nav 是設計過的。但加回巢狀**必須同時滿足三個條件**：

1. **規則 8 必須遵守**：extra.css 不可加回 `@media min-width: 760px` 大段 override
2. **部署後實測 sidebar 視覺正常**：不可有重複標題、不可有箭頭錯位
3. **出問題就 git revert**：絕對不要再走「用 CSS 蓋」的路（V2.0.3 的 9 條補丁就是這樣堆出來的）

**演進**：
- V3.3.0 路線 B 試水溫：只巢狀 A 組（A1+A2），其他平鋪。Sela 截圖實測通過，無重複無翻車
- **V3.4.0 路線 C 全推**：A/B/C/H 四組全巢狀；D/E/F/G 各只有 1 個檔，仍是平鋪頂層

### 規則 4：H 系列維護單位

H1–H4 及未來任何 H 系列檔，維護單位欄位填：

> 放射腫瘤科 林伯儒 醫師

### 規則 5：getSiteRoot() 從 pathname 推算

`docs/javascripts/extra.js` 必須這樣寫：

```javascript
// ✅ 正確
function getSiteRoot() {
  var path = window.location.pathname;
  var m = path.match(/^(\/[^\/]+\/)/);
  return m ? m[1] : "/";
}

// ❌ 錯誤（坑 #4、#13 已踩兩次）
function getSiteRoot() {
  return document.querySelector("base[href]").href;
}
```

Android Chrome + MkDocs instant navigation 下，`base.href` 解析成目前頁面 URL 而非 site root，導致路徑疊加跳 404。

### 規則 6：升版前必跑 `mkdocs build --strict`

```bash
cd /path/to/repo
mkdocs build --strict 2>&1 | tail -10
# 期待：Documentation built in X seconds，0 warning
```

### 規則 7：主色用 :root，不用 palette: custom

mkdocs.yml palette 留 `primary: indigo` 當佔位（坑 #18、#19 證實 `palette: custom` + attribute selector 不可靠），extra.css 直接覆蓋變數：

```css
:root,
[data-md-color-scheme="default"] {
  --md-primary-fg-color:        #25506b;
  --md-primary-fg-color--light:  #3a6e8c;
  --md-primary-fg-color--dark:   #173a52;
  --md-accent-fg-color:          #25506b;
}
```

### 規則 8：extra.css 不可加回 sidebar override

**禁止這段**：

```css
@media screen and (min-width: 760px) {
  .md-header__button[for=__drawer] { display: none !important; }
  .md-sidebar--primary { position: sticky !important; ... }
  /* ... 一堆 override */
}
```

V2.x → V3.0.x 連續 8 版打地鼠的真兇（坑 #22）。Material 預設 wide-mode 門檻 1525px，但 Sela 滿屏 viewport 是 2160px，**Material 自己會處理一切**。任何「強迫 sidebar 顯示」的衝動都該被勒住——除非你能用 `javascript:alert(innerWidth)` 證明使用者 viewport 真的 < 1525px。

### 規則 9：drug-lookup/ 子目錄

`docs/drug-lookup/index.html` 是 H3 抗癌藥物速查的本體（不是 .md，是自成一體的 web app）。重組 docs/ 結構時必帶。煙霧測試一定要驗 `ls site/drug-lookup/index.html`（坑 #21）。

### 規則 10：框架元素用 SVG，無 emoji

emoji 跨平台渲染不穩（坑 #23）。框架層級的圖示（mkdocs.yml nav、index.md 卡片、extra.js 手機底部導覽）一律 inline SVG。**內文 emoji 不管**——個管師寫文章用「✅」「⚠️」是修辭，那是內容不是框架。

### 規則 11：站名與 logo

- `site_name`：「彰濱秀傳癌症中心 - 個管師訓練系統」（V3.4.0 確定）
- `theme.logo`：`assets/logo-header.png`
- `theme.favicon`：`assets/favicon.png`
- 首頁 hero 大 logo：`assets/logo.png`
- 三個 PNG 不可遺失，否則 build --strict 會 fail

---

## 一、Repo 結構對映

| 我要改的事 | 動這些檔案 |
|-----------|-----------|
| 內容修改（17 份 MD 之一） | `docs/X_xxx.md`（看「Nav 對映表」對應） |
| 首頁卡片或 logo | `docs/index.md` |
| Nav 結構（先讀規則 3、8） | `mkdocs.yml` 的 `nav:` |
| 主色 / 全站樣式 | `docs/stylesheets/extra.css` |
| 版本徽章 / 手機底部導覽列 | `docs/javascripts/extra.js` |
| 搜尋分隔符 | `mkdocs.yml` 的 `plugins.search.separator` |
| 部署設定 | `.github/workflows/deploy.yml` |
| 套件版本 | `requirements.txt` |
| Logo / Favicon | `docs/assets/{logo,logo-header,favicon}.png` |
| 版本號（5 處，規則 1） | extra.js / extra.css / README / CLAUDE / ZIP |

---

## 二、Nav 結構對映表

V3.4.0 = 4 巢狀組（A/B/C/H）+ 4 平鋪頂層（D/E/F/G）+ 首頁。

| Nav 顯示 | 檔案 | 內容 |
|---------|------|------|
| 首頁 | `index.md` | hero logo + 8 張卡片導覽 |
| **A 新人通則**（巢狀） | — | — |
| └ A1 工作指導手冊 | `A_work-guide.md` | 工作職責、日常流程 |
| └ A2 培訓計畫書 | `A_training-plan.md` | 四階段培訓、帶人指引 |
| **B HIS 與通用工具**（巢狀） | — | — |
| └ B1 HIS 系統操作手冊 | `B1_HIS-manual.md` | 12 個 HIS 子系統 |
| └ B2 其他工具使用說明 | `B2_other-tools.md` | LINE / 信箱 / 雲端 |
| **C 各癌別照護指引**（巢狀） | — | — |
| └ C0 癌症照護通論 | `C0_general.md` | 各癌別前言通論 |
| └ C1 肺癌照護指引 | `C1_lung-cancer.md` | 肺癌 |
| └ C2 乳癌照護指引 | `C2_breast-cancer.md` | 乳癌 |
| └ C3–C6 其他癌別照護指引 | `C3-C6_other-cancers.md` | 大腸 / 肝 / 頭頸 / 攝護腺 |
| D 表單與範本 | `D_forms.md` | D1–D4（單檔不巢狀） |
| E 專題與進階 | `E_advanced.md` | E1–E4（單檔不巢狀） |
| F 臨床知識庫 | `F_clinical-kb.md` | F1–F4（單檔不巢狀） |
| G 品質指標速查 | `G_quality-index.md` | 13 癌 60 項（單檔不巢狀） |
| **H 癌症中心專用軟體**（巢狀） | — | — |
| └ H1 個管追蹤系統 | `H1_ccm-tracker-guide.md` | 院內 |
| └ H2 MDT 會議管理系統 | `H2_mdt-guide.md` | 院內 |
| └ H3 抗癌藥物速查 | `H3_cancer-drugs.md` + `drug-lookup/` | 145 種藥物，本體在 `docs/drug-lookup/index.html` |
| └ H4 病歷互審系統 | `H4_peer-review-guide.md` | 院內 |

**改 nav 顯示名動兩處**：`mkdocs.yml` 的 `nav:`、`docs/index.md` 卡片連結。
**改 nav 結構動三處**：上述兩處 + `docs/javascripts/extra.js` 的 mobile nav `items` 陣列（如果動到那 4 個常用入口的話）。

---

## 三、踩過的坑

> 編號從 V1.0.0 連續累積，永不重排。

**#1（V1.0.0）私有 Repo + GitHub Pages 需要 GitHub Pro**
- 症狀：Settings → Pages 找不到 GitHub Actions 選項
- 做法：升級 GitHub Pro

**#2（V1.0.0）MD 檔名含中文在 Linux 編碼壞**
- 做法：所有 docs/ 下的 MD 一律英文檔名

**#3（V1.0.0）中文搜尋 separator 設定錯誤**
- 原因：`[\u3000-\u9FFF]` 把所有中文當分隔符，搜不到任何中文
- 做法：separator 只切標點符號 + 加 jieba 套件做中文斷詞

**#4（V1.3.0）手機底部導覽列路徑疊加（base.href 第一次踩）**
- 做法：當時改用 base.href，後來坑 #13 證明這還是錯的，正解見規則 5

**#5（V1.4.0）CSS content 變數版本徽章跨頁不穩**
- 做法：改用 JS createElement 注入

**#6（V1.4.0）navigation.expand 強制展開所有側欄**
- 做法：移除 `navigation.expand`，加 `navigation.prune`

**#7（V1.7.0）軟體說明出現明文帳密** → 規則 2

**#8（V1.7.0）版本號分散沒同步** → 規則 1

**#9（V1.7.1）多個 h1 導致錨點失效**
- 做法：部分標題改 h2

**#10（V1.8.4）markdown_extensions 缺漏導致 admonition 不渲染**
- 做法：補回完整擴充清單（admonition / pymdownx / superfences / 等）

**#11（V1.8.6）誤刪 navigation.sections + 誤刪 toc.integrate**
- V2.x 一連串問題的源頭

**#12（V1.8.9）toc.integrate 第二度被誤刪**
- V2.x 必保留，但 V3 平鋪結構下不需要——V3 的等效規則是規則 3 + 8

**#13（V1.9.6）Android 底部導覽 404（base.href 第三度）**
- 做法：getSiteRoot() 完全不用 base.href → 規則 5

**#14（V2.0.3）navigation.indexes 導致頂端 tab 消失 + 版本號散落**
- 做法：移除 navigation.indexes；版本號改用 Python replace 批次處理

**#15（V2.0.3）navigation.sections 漏加 + 中文錨點全壞**
- 做法：加回 navigation.sections、toc 改用 pymdownx.slugs.slugify(case=lower)

**#16（V2.0.x → V3.0.0）巢狀 nav 在窄 viewport 永遠 sidebar 標題重複**
- 症狀：sidebar 中每個 section 名稱重複出現兩次
- 真因（坑 #22 揭露）：不是巢狀本身的問題，是「巢狀 + 760px CSS override 強迫窄 viewport 顯示 sidebar」雙重作用
- V3.0 解法：合併成 4 篇平鋪
- V3.3 修訂：viewport 真相揭露後可以巢狀，但必遵守規則 3、8

**#17（V3.0.0）合併 MD 後跨檔連結失效**
- 做法：sed 批次替換錨點

**#18（V3.0.1）palette: custom + attribute selector 不生效**
- 做法：放棄 `palette: custom`，extra.css 用 `:root` 強制覆蓋變數 → 規則 7

**#19（V3.0.1）強制 sidebar 顯示時內嵌 TOC 跟著被顯示**
- 症狀：sidebar 同時顯示主 nav 和當前頁 TOC，左右兩側 TOC 重複
- V3.0.2 做法：加一條 `.md-sidebar--primary .md-nav .md-nav { display: none }`
- V3.2.0 改動：整段 sidebar override 砍掉後，這條也跟著砍——沒有強迫顯示 sidebar 就沒有重複問題 → 規則 8

**#20（V3.0.0–V3.0.2 → V3.1.0）合併 MD 會丟失原檔精修內容**
- 真相：V2.0.3 的 17 份 MD 是反覆討論精修的版本，合併過程的 strip / demote 隱性丟失細節
- 做法：V3.1.0 把 4 份合併 MD 全砍，回到 V2.0.3 的 17 份原檔
- 教訓：**內容是反覆討論的成果（保守對待），框架是技術選擇（可以激進）**

**#21（V3.1.0）H3 抗癌藥物速查的本體在 docs/drug-lookup/ 子目錄**
- 症狀：V3.0.0 重做時忘了帶 `docs/drug-lookup/index.html`，H3 連結 404
- 做法：每次重組 docs/ 必帶 drug-lookup/，煙霧測試驗 `ls site/drug-lookup/index.html` → 規則 9

**#22（V2.0.x → V3.2.0，連續 9 版重大教訓）「viewport 885px」是錯誤的測量前提**
- 症狀：V2.x 整段 760px sidebar override 建立在「Sela 的 MacBook Air viewport 是 885px」這個前提
- 真相（V3.2.0 揭露）：滿屏 + DevTools 拖出獨立視窗後實測 **2160px**，遠超 Material wide-mode 門檻 1525px。**之前所有 760px 補丁從一開始就建在錯誤前提上**
- 量法：網址列貼 `javascript:alert("CSS寬度: " + innerWidth + " / DPR: " + devicePixelRatio)`，DevTools 不會干擾
- 做法：V3.2.0 砍掉整段 sidebar override，回歸 Material 預設行為 → 規則 8
- 教訓：
  - 量 viewport 要在「實際使用情境」量，不是「DevTools 開著的情境」
  - **錯誤前提下的解法只會堆積技術債**——任何「框架預設不對」的判斷之前，先確認自己量的數字對不對

**#23（V3.2.0）框架 emoji 跨平台渲染不穩**
- 風險：醫院電腦多半舊版 Windows，emoji 在某些終端可能變方框
- 做法：框架層級 emoji 全改 inline SVG → 規則 10
- 注意：**內文 emoji 不管**，那是文章作者的修辭

**#24（V3.3.0）巢狀 nav 路線 B 試水溫做法**
- 背景：V3.0–V3.2 規則 3 是「禁止巢狀」，V3.3 viewport 真相後想加回。直接 8 組全巢狀風險高
- 做法：先巢狀 A 組（只 A1 + A2），其他 15 條仍平鋪。實測 OK 再逐步推到 B、C、H 組
- 回退：如果 sidebar 視覺翻車（標題重複、箭頭錯位等），不要試圖用 CSS 蓋（V2.0.3 的 9 條補丁路線），直接 git revert
- 結果：**V3.3.0 部署實測通過**，截圖證實 sidebar 「A 新人通則」可展開、無重複、無錯位。V3.4.0 推到全巢狀（路線 C）成功

**#25（V3.4.0）footer 底部黑色橫條**
- 症狀：頁面拉到底會看到一條深色橫條（介於主內容和 footer 之間，截圖 1 證實）
- 原因：Material 的 `.md-footer` 預設是深色背景，wide-mode 下會在主色 footer 之外多顯示一段深色
- 做法：extra.css 強制 footer 背景對齊主色 dark 變體
  ```css
  .md-footer { background-color: var(--md-primary-fg-color--dark); }
  .md-footer-meta.md-typeset { background-color: var(--md-primary-fg-color--dark); }
  ```
- 注意：用 `--md-primary-fg-color--dark`（#173a52）而非主色本身，視覺上 footer 比 header 略深，有層次感

---

## 四、版本歷程

> 留最近 6 版（章法 7：過期上下文等於垃圾）。完整在 README.md。

| 版本 | 主要異動 |
|------|---------|
| V3.0.0 | **從零重做框架**：17 份巢狀 → 4 篇平鋪，nav 完全無巢狀（坑 #16） |
| V3.0.1–V3.0.2 | 修主色（坑 #18）+ 修內嵌 TOC（坑 #19） |
| V3.1.0 | **內容回到 V2.0.3 原檔**（17 份精修 + drug-lookup/，坑 #20、#21） |
| V3.2.0 | **重大轉折**：viewport 885px 是錯誤前提（坑 #22），砍掉所有 sidebar override；框架 emoji 改 SVG（坑 #23） |
| V3.3.0 | 巢狀 A 組試水溫（坑 #24）；正式名稱「彰濱秀傳癌症中心 - 個管師訓練系統」；加 SELA logo 三檔；拿掉 header GitHub repo 連結；CLAUDE.md 統整成 11 條規則 |
| **V3.4.0** | 路線 C 全巢狀（A/B/C/H 四組巢狀，D/E/F/G 因單檔仍平鋪）；版本徽章從右下角浮動移到 header 站名旁；修 footer 底部黑色橫條（坑 #25） |

---

## 五、關鍵路徑

```
# 內容（17 份精修 MD，V2.0.3 沿用）
docs/A_work-guide.md          # 工作指導手冊
docs/A_training-plan.md       # 培訓計畫書
docs/B1_HIS-manual.md         # HIS 12 子系統
docs/B2_other-tools.md        # LINE / 信箱 / 雲端
docs/C0_general.md            # 癌症照護通論
docs/C1_lung-cancer.md        # 肺癌
docs/C2_breast-cancer.md      # 乳癌
docs/C3-C6_other-cancers.md   # 其他四癌
docs/D_forms.md               # 表單範本（D1–D4）
docs/E_advanced.md            # E1 困難個案 / E2 安寧 / E3 品質改善 / E4 必要事件
docs/F_clinical-kb.md         # 臨床知識庫
docs/G_quality-index.md       # 60 項指標
docs/H1_ccm-tracker-guide.md  # 院內個管追蹤
docs/H2_mdt-guide.md          # 院內 MDT
docs/H3_cancer-drugs.md       # 抗癌藥物說明
docs/drug-lookup/index.html   # 抗癌藥物速查本體（規則 9）
docs/H4_peer-review-guide.md  # 院內病歷互審
docs/index.md                 # 首頁（hero logo + home-grid 卡片）

# 框架
mkdocs.yml                    # nav / theme / plugins / markdown_extensions
docs/stylesheets/extra.css    # 主色 + 表格 + home-hero/home-grid + 手機底部導覽
docs/javascripts/extra.js     # CCM_VERSION（規則 1）+ getSiteRoot（規則 5）+ 4 個 SVG 入口
docs/assets/logo.png          # 首頁大 logo（600px）
docs/assets/logo-header.png   # 左上角 header logo（96px）
docs/assets/favicon.png       # 瀏覽器分頁 favicon（128px）

# 部署
.github/workflows/deploy.yml
requirements.txt              # mkdocs / mkdocs-material / pymdown-extensions / jieba
.gitignore
```

---

## 六、部署

### 本地驗證

```bash
cd /path/to/repo
pip install -r requirements.txt
mkdocs build --strict 2>&1 | tail -10
# 期待：Documentation built in X seconds，0 warning
```

### 推上線

Sela 用自製 Git Pusher V1.5.5：
1. ZIP 命名：`CCM Manual V?.?.?.zip`（空格分隔、點號版本）
2. 內部結構：**無外層資料夾**（mkdocs.yml、docs/、.github/ 直接在根）
3. Git Pusher 「匯入 Zip 並上傳」→ 自動 commit + push
4. 看 https://github.com/Sela1227/CCM-manual/actions 確認 Actions 跑成功
5. 開 https://Sela1227.github.io/CCM-manual/ 看畫面

### 煙霧測試（每次升版必跑）

```bash
mkdocs build --strict                           # 0 warning
ls site/A_work-guide/index.html [...] site/H4_peer-review-guide/index.html  # 17 個檔
ls site/drug-lookup/index.html                  # 規則 9
ls site/assets/logo.png site/assets/logo-header.png site/assets/favicon.png  # 規則 11
grep -c "#25506b" site/stylesheets/extra.css    # 主色（>= 1）
grep -c "min-width: 760" site/stylesheets/extra.css  # 規則 8（== 0）
grep -c "彰濱秀傳癌症中心 - 個管師訓練系統" site/index.html  # 規則 11（>= 1）
```

---

## 七、下版候選工作

按優先序：

1. **驗證 V3.4.0 全巢狀（路線 C）視覺** — 部署後第一件事，確認 (a) sidebar 4 組（A/B/C/H）都能展開、無重複標題、無箭頭錯位 (b) header 站名旁有 V3.4.0 徽章 (c) 頁面拉到底沒有黑色橫條（坑 #25 修補檢查）(d) D/E/F/G 仍是平鋪頂層。如果某組翻車，**只 git revert 那一組回平鋪**，不要試圖用 CSS 蓋
2. 處理「目錄／目錄」重複（截圖 2 那個 H2 章節 + Material 自動 TOC 撞名）— 17 份 MD 中有「## 目錄」H2 的（A_work-guide.md L3887 確認），考慮砍掉那個 H2 章節
3. 補 B1 五大 HIS 系統的操作截圖（系統陸續上線後補入，新人最需要）
4. 抗癌藥物速查若有新版，整個 `docs/drug-lookup/` 資料夾原地替換 + 改 H3 版本說明（規則 9）
5. 子宮頸癌 / 子宮體癌 / 卵巢癌完治率定義補入 G_quality-index.md（待各團隊討論）
6. 評估 D/E/F/G 是否要拆檔（如果拆，可以也巢狀化做成 D1/D2... 等）

---

## 八、一句話總結

V3.4.0：V3.3.0 的巢狀 A 組試水溫部署實測通過後，這版推路線 C——A/B/C/H 四組全巢狀，D/E/F/G 因單檔仍是平鋪頂層。同時把版本徽章從右下角浮動改成 inject 到 header 站名旁（更符合「所有頁都看到」）、修了 footer 底部黑色橫條（坑 #25）。CSS 仍維持 V3.2.0 的乾淨基底（沒有 sidebar override，規則 8 不破）。**接手第一件事**：Sela 部署實測 4 組巢狀視覺有沒有翻車（特別是 C 組 4 個檔最複雜），翻車就 git revert 那一組，不要 CSS 蓋。
