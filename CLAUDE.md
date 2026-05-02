# CLAUDE.md｜彰濱秀傳癌症中心 - 個管師訓練系統

**當前版本**：V3.4.7
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

> 規則 1–11 是**部署/技術規則**（破了會壞 build 或翻車）。
> 規則 12–13 是**內容寫作規範**（破了不會壞 build，但會影響使用者導航體驗）。

### 規則 12：標題層級設計語言

**先決條件（內容編排）**：分層之前先確認內容編排合理——**同類的東西放一起、有邏輯順序**（時間／重要性／工作流程）。內容亂排再怎麼分層都救不回來。**編排穩定後才動層級**。如果分層時發現「同類東西散在文件四處」，回去整理內容順序，再來分層。

**層級用途**：

| 層級 | 用途 | 內容份量門檻 | 是否上 TOC |
|------|------|----------|----------|
| **H1** | 檔名／頁面標題（每檔唯一）| — | — |
| **H2** | 頁面內主要分區（5–10 個為宜，最多 12 個）| — | ✓ 必上 |
| **H3** | H2 之下的子章節 | **≥ 20 行** | ✓ 必上 |
| 邊緣 | 結構性章節但內容偏短 | 15–19 行 | 看狀況（傾向 H3）|
| **H4** | 細層或內容短到 TOC 上不需要獨立列 | **< 15 行** | ✗（toc_depth=3 蓋住，可改用粗體段落）|

**設計原則**：

1. **TOC 是「快速到附近」、不是「精準到小點」**——錨點之間距離太近、使用者點過去一頁就看到兩三個錨點，TOC 反而難掃描。內容短的子段直接用 H4 或粗體段落，不要塞進 TOC
2. **內容份量決定層級**：用「< 15 行 / 15–19 行 / ≥ 20 行」三段分。邊緣段（15–19 行）原則上升 H3，但若是「情感段落」「結尾話」「重複別處的簡介」這類非結構性內容，降 H4
3. **不再使用 H2 的「## 目錄」區塊**——Material 右側自動 TOC 已提供同樣導航，自寫「## 目錄」H2 會跟自動 TOC 視覺重複（且自寫的不會自動更新）
4. **作者主動判斷 H3 vs H4**：規則告訴你閾值，但作者要自己看「這段內容值不值得 TOC 獨立導航」。寧可少不要多

**寫作時自我檢查**：

- 一個檔的 H2 數量超過 12 個 → 多半是「層級壓平」（把子章節寫成 H2 並列）
- 完全沒 H3 → 同組 H2 該收成「一個 H2 + 多個 H3」
- 大量 H4 → 內容寫得細，但確認 H4 不依賴 TOC 導航是否 OK
- TOC 條目（H2+H3 加總）超過 ~30 項 → 太細，回頭看哪些 H3 該降 H4

**坑 #31（V3.4.7+）盤點**：V3.4.6 後 17 份 MD 中違反規則 12 的有四檔——`A_work-guide`（40 H2，模式 1：層級壓平）、`C3-C6_other-cancers`（12 H2、0 H3，模式 2：完全沒 H3）、`G_quality-index`（22 H2、11 H3，模式 4：H3 偏少）、`F_clinical-kb`（40 H4，模式 3：H4 太多）。

**A_work-guide 修法已決議（V3.4.7 候選）**：保守版方案——5 H2（4 部分 + 附錄）+ 28 H3（≥ 20 行的 20 個 + 邊緣 8 個全升）+ 7 個 < 15 行的子段降 H4。砍 `## 目錄` H2。預期 TOC 33 項（vs. 現在 104 項）。**動手前**：先確認內容編排合理（規則 12 先決條件），有發現「同類東西散在四處」就先重整內容、不要急著降層級。

### 規則 13：拆檔與巢狀門檻

何時用單檔平鋪 vs 拆多檔巢狀的決策依據：

| 情境 | 處理 |
|------|------|
| **單檔 < 500 行** | 平鋪頂層（TOC 處理頁內導航夠用）|
| **單檔 500–1000 行** | 邊緣，看內容性質決定 |
| **單檔 > 1000 行** | 拆檔 + 巢狀（單檔太長，TOC 滑不完）|
| **頁面數 = 1** | 平鋪頂層（沒得巢）|
| **頁面數 2–3** | 看單檔長度決定 |
| **頁面數 ≥ 4** | 巢狀（避免 nav 太散）|

**規則 13 跟規則 3 的關係**：規則 3 講「巢狀**怎麼寫**才不翻車」（CSS 條件），規則 13 講「**何時該**巢狀」（內容門檻）。兩條都要過才動巢狀。

**V3.4.6 現況檢查**：

| 章 | 行數 | 巢狀 | 規則 13 判斷 |
|---|---|---|---|
| A（A1+A2）| 982+731 | 巢狀 | ✓ 一致 |
| B（B1+B2）| 624+255 | 巢狀 | ✓ 一致 |
| C（C0–C6）| 4 檔 | 巢狀 | ✓ 一致 |
| H（H1–H4）| 4 檔 | 巢狀 | ✓ 一致 |
| **D**（1 檔 1479 行）| 平鋪 | **✗ 該拆** |
| E（1 檔 525）| 平鋪 | 邊緣，可不拆 |
| **F**（1 檔 1302 行）| 平鋪 | **✗ 該拆**（V3.4.5 內容已重排為 5 段、拆檔線天然存在）|
| G（1 檔 470）| 平鋪 | ✓ 一致 |

D 與 F 列為「規則 13 遺留任務」，先把規則 12 的內容修完再回頭拆。

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
| F 臨床知識庫 | `F_clinical-kb.md` | F1–F5（單檔不巢狀，V3.4.5 重排為檢驗／分子病理／影像／治療／追蹤五段，**巢狀化尚未評估**）|
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

**#26（V3.4.1）logo 三處出現太亂、內文左邊太貼邊框、Stage IV 概念過度簡化**

V3.4.0 部署後 Sela 反映三件事：

1. **logo 散在三個位置** — header（對）、index.md hero 內文（多餘）、行動裝置 drawer 邊欄頂部（多餘）。應該只在 header 一處
   - 內文：`docs/index.md` 的 `<img src="assets/logo.png" class="home-logo">` 整段砍掉，連帶 `.home-logo` 的 CSS 規則也砍乾淨
   - drawer 邊欄：CSS 隱藏 `.md-nav--primary > .md-nav__title .md-logo`（保留站名與關閉鈕）

2. **內文左邊太貼邊框，閱讀不易** — 截圖 2 證實「文件資訊」h3 與表格幾乎貼到 viewport 左緣
   - 做法：`.md-content__inner` 加 `padding-left/right` 1rem（手機）/ 1.5rem（≥768px），不動 sidebar 行為（規則 8 不破）

3. **Stage IV ≠ 一定轉移**（C0 通論內容修訂） — 原版表格寫「Stage IV ＝ 遠端轉移（M1）」一刀切，但頭頸癌、子宮頸癌、子宮體癌、膀胱癌的 IVA／IVB 仍是局部晚期（仍可根治），只有 IVC 才是 M1
   - 做法：改 Stage 主表格 IV 那一列、改 tip 框文字、新增子章節〈Stage IV ≠ 一定轉移：細分亞期的癌別〉含頭頸癌 AJCC 第 8 版亞期表 + 為什麼這樣切（解剖位置、治療意圖、預後差距）+ 其他細分亞期癌別清單 + 個管師為什麼要懂

- 教訓：**內容是反覆討論的成果**（坑 #20）——醫療概念的精確度比版面美觀重要，發現用詞會誤導臨床判斷就要立刻補

**#27（V3.4.2）V3.4.1 修 drawer logo 的副作用：tablet viewport logo 完全消失**

V3.4.1 部署後 Sela 反映「logo 沒出現」。截圖看是寬桌面但有漢堡按鈕（tablet 範圍 768–1219px）。

- 真因：**Material 預設行為**——header 在 < 1220px 不顯示 logo 圖示（給漢堡 + 站名空間），只在 drawer 開啟時才顯示 logo。V3.4.1 把 drawer logo 砍了，這個 viewport 範圍兩處都沒 logo，等於完全消失
- 教訓：**動 Material 預設前要先確認該樣式在每個 viewport 的行為**（不是只在 wide-mode 看 OK 就推上去）。Sela 的滿屏 viewport 是 2160px（坑 #22），但實際使用可能拉小視窗到 tablet 範圍
- 做法：CSS 強制 `.md-header__button.md-logo { display: inline-flex !important; padding: 0.4rem !important }`，在所有 viewport 都顯示 header logo。Drawer 內仍隱藏（V3.4.1 那條保留）
- 同步處理：內文 padding 也再加大（V3.4.1 用 1/1.5rem，V3.4.2 改 1.4/2.5rem，Sela 反映「再遠一點點」）
- 同步補：F 檔 NGS 章節新增**健保給付 NGS 適用癌別**（19 種、14 實體 + 5 血液）、**醫院執行資格三條件**（區域級／LDTs 表列／MTB）、**檢測結果上傳義務**、**個管師對話要點**——依國健署 NGS 懶人包 PDF 補入

**#28（V3.4.3）首頁卡片在手機變空白方框 + TOC 太寬**

V3.4.2 部署後 Sela 反映兩件事（連同 TOC 縮窄一起做）：

1. **手機版首頁的 8 張快速導覽卡片變空白方框**——卡片框線在但裡面什麼都沒有（截圖證實）
   - 真因：`docs/index.md` 的 home-card 結構是
     ```html
     <div class="home-card" markdown>
     <a href="...">
     <svg .../>
     工作指導手冊</a>
     <p>新人必讀。日常...</p>
     </div>
     ```
     Markdown 渲染會把「圖示+標題+連結」那行**自動包進 `<p>`**（看 build 後的 site/index.html 的實際 DOM 證實）。V3.4.0 的 mobile CSS 寫 `.home-card p { display: none }` 想砍描述，結果連標題那個 `<p>` 也一起砍了
   - 教訓：寫 CSS 砍 markdown 渲染出來的元素，要先 `mkdocs build` 看實際 DOM 長相，不能只看原始 .md 檔判斷選擇器是否安全
   - 做法：選擇器改 `.home-card > p:nth-of-type(2) { display: none }`，只砍第二個 `<p>`（描述），第一個 `<p>`（含 `<a>` + SVG + 標題）保留。`:nth-of-type` 是經典 CSS、所有手機瀏覽器都吃；不用 `:has()` 避免相容性風險

2. **右側 TOC 太寬，內文擠**——Material 預設 `.md-sidebar--secondary` 寬 12.1rem
   - 做法：`.md-sidebar--secondary { width: 10rem }`，少 35px 給內文。不動 grid 結構，純改子元素 width，Material 自動把空間給其他 cells
   - 副作用：較長的 H3（如「Stage IV ≠ 一定轉移：細分亞期的癌別」、「健保給付 NGS 適用癌別」）在 TOC 內會折成兩行——可接受，仍可讀；不到 9rem 不會擠到全部標題折行
   - 跟規則 8 不衝突：規則 8 講的是「用 760px CSS 強迫 primary sidebar 在窄 viewport 顯示」（違背 Material 行為）。改 secondary sidebar width 是純樣式調整，性質完全不同

**#29（V3.4.5）F 檔重排：原 F1/F2 兩段名實不符 → 改成 F1–F5 五段**

Sela V3.4.4 提「臨床知識庫的分項不是很好」。讀完原檔結構，問題是：

1. **F1「常見檢驗項目」名實不符**：CBC、生化、腫瘤指數、基因/NGS、IHC 都算檢驗，但**影像（CT/MRI/PET-CT/超音波/骨掃）不是「檢驗」**——硬塞在 F1
2. **F2「治療方式與副作用」塞太多東西**：第九「個管師追蹤問題速查」是電話追蹤腳本（不是治療概念）；第十二「抗癌藥物速查表」是藥物副作用警示查表（也不是治療概念）；F2 體量 942 行
3. **抗癌藥物速查表跟 H3 web app 的關係不清楚**：個管師看到不知道是 H3 重複還是不同東西

Sela 確認方案 A 變體（IHC + 基因獨立成 F2，總共 5 段）：

- **F1 檢驗判讀**：CBC、生化、腫瘤指數
- **F2 分子與病理檢測**（新拆出）：IHC、單一基因、NGS——拆出來的理由是這類「決定能不能用標靶/免疫」的依據跟普通驗血是不同情境
- **F3 影像判讀**：影像段獨立
- **F4 癌症治療**：治療方式（一-八）+ 局部介入 + 院內精準設備 + **抗癌藥物簡介（H3 簡易版）**——Sela 明確說藥物速查表是「H3 提取出來的簡易版，讓個管先了解這些」，所以加開頭定位說明、跟 H3 連結
- **F5 個管師追蹤速查**：原 F2 第九的追蹤問題速查獨立

**做法**：
- 用 Python 腳本切原檔行 range（不用逐段 str_replace 避免斷段風險），按新順序拼接、重編 F4 內部「一-十一」（原九搬走後填補空缺）、改檔頭章節架構表、改檔尾文件資訊
- F4 第十一段「抗癌藥物簡介」開頭加段定位說明：「本表定位：H3〔抗癌藥物速查 web app〕的簡易版——讓個管師先建立 145 種藥物整體輪廓，完整健保給付條件請查 H3」
- 行數從 1284 → 1302（多 18 行，新加章節 H2/lead + F4 第十一定位說明 + 新文件資訊）——沒丟內容
- 教訓：1000 行以上的檔重組用 Python 切片＋拼接比逐段 str_replace 安全，但**前提是先用 grep 抓清楚每個 H3 的精確行號**才能切；切片用 list slicing 不要用正則（坑 #20 教訓——精修內容不能在合併過程中模糊掉）

**#30（V3.4.6）A1/B1 重複嚴重：方案 C 完整重切**

Sela V3.4.5 提「A1/B1 太多東西重覆，集中討論」。盤點後問題：

1. **A1 第三部分「軟體上手指南」（line 686-952，267 行）跟 B1 全本（570 行）重複嚴重**：兩邊都寫 12 個 HIS 子系統介紹、都「待補充：操作畫面」「待補充：操作步驟」，等於各寫一半的同一份文件
2. **A1 自我重複**：line 932「系統問題找誰？」跟 line 943「軟體問題找誰？」H2 並列、表格內容完全相同
3. **A1 把工作流程跟系統工具混在一起**：第三部分既有 HIS 子系統、又有帳號申請、LINE/Email/雲端、求救對象——其實後三項才是「系統工具」，前面是 B1 的範圍

Sela 選方案 C（最徹底）：完整重切，A1 變「**個管師工作流程**」純粹版，B1 變「**個管師會用到的所有系統與工具**」。

**做法**：
- A1：砍掉第三部分整段（line 686-952），把「第四部分：工作工具箱」「第五部分：品質指標概念」改編號為「第三部分」「第四部分」，目錄重寫為 4 個部分；line 1247 → 983 行（砍 264 行）
- B1：保留原 15 章框架 + 加 3 個新章節從 A1 搬入：
  - 新第 2 章「帳號申請與權限」（A1 line 898-908）
  - 新第 16 章「LINE Email 雲端工具」（A1 line 912-929）
  - 新第 18 章「遇到問題找誰」（A1 line 932-940，A1 line 943-950 自重複那份直接砍）
- B1 原第 2-15 章編號全部 +1 或 +2（第 2 變 3、第 15 變 17 因為中間插了 16）
- B1 目錄重寫為 18 章；行數 570 → 625
- 兩檔都用 Python 切片＋拼接重組（仿 V3.4.5 F 檔做法）

**踩過的小坑（不獨立列為大坑）**：B1 新第 16 章原本想叫「LINE / Email / 雲端工具」，但 ` / ` 在 mkdocs slugify 下會產生 `--`（雙 dash） slug，目錄連結 `#16-line-email-雲端工具`（單 dash）對不上實際 anchor `#16-line--email--雲端工具`，build 出 INFO 警告。修法：章節名簡化為「LINE Email 雲端工具」（空格分隔），slug 變單 dash 自然對上。教訓：**章節名含 ` / `、` & ` 等特殊字元時要先想 slug 會被怎麼處理**

- 教訓：方案 C 重切兩個檔同時動，**要在動之前確認跨檔錨點連結沒有人引用**（這次跑 `grep "A_work-guide\\|B1_HIS-manual" docs/` 確認只有 index.md 連根 URL、無人連 anchor，所以可放手重排）

**#31（V3.4.7）規則 12 制定 + A 檔第一個套用範例：層級降級 + 內容重整 + 砍目錄**

V3.4.6 部署後 Sela 提兩個觀察：

1. **不同檔的 TOC 觀感不一致**：A1 滑下去 TOC 超長（40 H2 + 64 H3 = 104 項），C3-C6 只有 12 個 H2 沒層次，F 內容很細但 TOC 看不到，G 的 H3 偏少。**作者用 H2/H3 的習慣每檔不一**
2. **內容多到什麼地步才該拆檔做巢狀？**——目前 A/B/C/H 巢狀 vs D/E/F/G 平鋪是「歷史結果」不是「設計決策」

**規則 12 + 13 訂下**（CLAUDE.md 規則段）：

- **規則 12**：標題層級設計語言。**先決條件**：分層之前先確認內容編排合理（同類放一起）。**層級用途**：H1 檔名／H2 主分區（5–10）／H3 子章節（≥ 20 行）／H4 細層（< 15 行不上 TOC）／邊緣（15–19 行視結構性決定）。**設計原則**：TOC 是「快速到附近」、不是「精準到小點」（Sela 觀感）。**「## 目錄」H2 不再用**（跟 Material 自動 TOC 撞）
- **規則 13**：拆檔與巢狀門檻。< 500 行平鋪 / 500–1000 邊緣 / > 1000 拆檔。D 檔（1479 行）和 F 檔（1302 行）按規則該拆，列為遺留任務

**Sela 的關鍵洞察**（直接寫進規則）：
- 「TOC 快速導航是要快速到附近，不一定要精準到小點」
- 「分層不宜過細，有時導過去一頁就看到兩三個錨點」→ 啟發 H4 的「< 15 行」門檻
- 「在內容編排上就要先優化，同類的東西放一起，有規律，才好分層」→ 規則 12 的先決條件

**A 檔（V3.4.7 第一個套用範例）做法**：

1. **內容重整**（規則 12 先決條件）——掃出第一部分主題切換 8 次，三個明顯的「同類散在四處」：
   - 個管師角色：L26+L36（頭）vs L432（尾，跳 400 行）
   - 常規工作：L52+L68 vs L347（中間，跳 280 行）
   - 其他特殊：L275 vs L415（中間插了常規工作完整清單）
   - 重整成 5 個主題塊（個管師角色 / 常規工作 / 會議與評鑑 / 工作節奏 / 其他特殊），主題切換從 8 次降為 4 次
   - 第二/三/四部分編排已合理，內容順序不動

2. **層級降級**（按規則 12 內容份量門檻）：
   - 5 H2（4 部分 + 附錄）保留
   - 27 H3（20 個 ≥ 20 行 + 7 個邊緣 15–19 行升 H3）
   - 7 H4（< 15 行的極短段降）：個管師是什麼角色？(10)、補休說明(13)、學習路線圖(13)、什麼時候要轉介？(14)、什麼是品質指標？(10)、為什麼要追蹤指標？(8)、各癌別的詳細指標(14)
   - 64 個原 H3 → H4（連帶降）
   - 結果：5 H2 + 27 H3 + 71 H4，**TOC 從 104 項降到 32 項**

3. **砍 ## 目錄 H2**：規則 12 第三條，自寫目錄跟 Material 自動 TOC 撞名重複

4. **行數變化**：983 → 978（內容沒丟，只是重排+重編層級+砍目錄）

**做法**：用 Python 腳本切原檔行 range（仿 V3.4.5/V3.4.6），第一部分按新主題塊重組，二三四部分順序不動但降級。`demote()` 函式按 H2 動作（to_h3/to_h4/keep）+ H3→H4 自動處理。`get_h_level()` 用 `#` 數量精準判斷層級避免 startswith 誤判（`#### foo`.startswith(`### `) = True 的陷阱）

**遺留**：規則 12 還有三個檔要修——C3-C6（模式 2 完全沒 H3）、G_quality-index（模式 4 H3 偏少）、F_clinical-kb（模式 3 H4 太多）。等 A 檔部署實測 OK 再逐個動。Sela 提的下一階段（A1 第二部分 vs A2 重複、A1 附錄整理）也都還沒動

---

## 四、版本歷程

> 留最近 6 版（章法 7：過期上下文等於垃圾）。完整在 README.md。

| 版本 | 主要異動 |
|------|---------|
| V3.4.2 | 修 V3.4.1 的副作用——強制 header logo 在所有 viewport 顯示（坑 #27）；內文 padding 再加大到 1.4/2.5rem；F 檔 NGS 章節補健保給付 19 癌別 + 醫院資格三條件 + 結果上傳義務 |
| V3.4.3 | TOC 縮窄 12.1rem → 10rem（內文每邊多 17px）；修首頁卡片手機變空白方框 bug（CSS 選擇器把標題 `<p>` 也砍了，坑 #28）|
| V3.4.4 | 手機底部導覽從 4 個改 6 個進階員工常用入口（首頁／個管 H1／MDT H2／藥物 H3／指標 G／知識 F）；砍掉 A 工作、B1 HIS（新人入門才用、不適合底部快速進入）|
| V3.4.5 | **純內容版本**：F 檔（臨床知識庫）從原 F1/F2 兩段重排為 F1–F5 五段（檢驗／分子病理／影像／治療／追蹤），F4 內部一-十一重編，F4 第十一「抗癌藥物簡介」明確標示是 H3 簡易版（坑 #29）|
| V3.4.6 | **純內容版本**：A1/B1 重排（方案 C），A1 砍第三部分「軟體上手指南」（267 行）、B1 從 15 章變 18 章（加帳號申請 / LINE Email 雲端工具 / 遇到問題找誰三章）；A1 line 1247→983、B1 line 570→625（坑 #30）|
| **V3.4.7** | **純內容版本**：規則 12（標題層級設計語言）+ 規則 13（拆檔巢狀門檻）訂下；A 檔第一個套用——內容重整（5 主題塊收攏，散亂主題切換 8→4 次）+ 層級降級（5 H2+27 H3+71 H4，TOC 從 104 項降到 32 項）+ 砍 `## 目錄`（坑 #31）|

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

1. **驗證 V3.4.7 A 檔層級重排視覺** — 部署後第一件事，確認 (a) A 檔 TOC 從 104 項降到 32 項，5 個 H2 + 27 個 H3 (b) 第一部分內容順序正確：「個管師角色 → 常規工作 → 會議與評鑑 → 工作節奏 → 其他特殊」五個主題塊收攏 (c) ## 目錄已砍 (d) 第二/三/四部分內容順序不變、層級降級正確 (e) 邊緣降 H4 的 7 段（個管師是什麼角色／補休／學習路線圖／什麼時候要轉介／什麼是品質指標／為什麼要追蹤／各癌別詳細指標）正常顯示但不上 TOC
2. **驗證 V3.4.5 + V3.4.6 內容重排視覺與內容**（如未實測）— (a) F 檔頁首章節架構表是 F1–F5 五段、F4 內部一-十一連續無跳號 (b) A1 是 4 個部分（不再有第三部分軟體上手）(c) B1 是 18 章 + 附錄 + 癌症中心專用軟體 (d) B1 第 2/16/18 章是新加的內容
3. **修 C3-C6 模式 2（規則 12 遺留）** — C3-C6 12 H2、0 H3，4 癌別 × 3 子段全用 H2 並列。改成 4 癌別 H2 + 各 3 子段 H3。230 行小工程
4. **修 G_quality-index 模式 4（規則 12 遺留）** — 22 H2、11 H3 偏少。要看 22 H2 怎麼分組重整
5. **修 F_clinical-kb 模式 3（規則 12 遺留）** — 6/18/40，H4 太多但 toc_depth=3 看不到。視性質決定升 H3 或保留 H4
6. **驗證 V3.4.4 手機底部導覽 6 個鈕視覺**（如未實測）— 部署後第一件事，確認 (a) 6 個鈕在 360px 寬手機都能塞下圖示+標籤 (b) active 狀態正確 (c) 在較窄手機會不會擠到變形
7. **A1 第二部分 vs A2 培訓計畫書是否重複（下一階段）** — A1 line ~464-685「新人養成指引」（學習路線圖、四階段培訓、checklist）跟 A2 主題正面對撞。需先讀 A2 完整結構。**等 Sela 主動提**
8. **A1 附錄是否要動（下一階段）** — A1 末尾「附錄」含「重要聯絡資訊」「相關文件索引」，內容是 placeholder（待填）。**等 Sela 主動提**
9. **B1 「## 目錄」也要砍**（規則 12 第三條）— A 檔已砍，B1 跟 F 檔的「## 目錄/章節架構」也適用同規則。下次動 B1/F 檔時順手
10. 補 B1 各 HIS 子系統的操作截圖（V3.4.6 後 B1 集中為單一系統手冊，新人最需要）
11. **F 檔巢狀化（規則 13 該拆）** — F 檔 1302 行 > 1000 行門檻，按規則 13 該拆 5 檔。但因為 V3.4.5 已內容重整完、單檔仍可讀，**優先序低**，等 Sela 主動提
12. **D 檔巢狀化（規則 13 該拆）** — D 檔 1479 行 > 1000 行門檻，按規則 13 該拆。需先看 D1-D4 內部結構
13. 抗癌藥物速查若有新版，整個 `docs/drug-lookup/` 資料夾原地替換 + 改 H3 版本說明（規則 9）
14. 子宮頸癌 / 子宮體癌 / 卵巢癌完治率定義補入 G_quality-index.md（待各團隊討論）
15. **logo.png（首頁大 logo 600px）是否還需要？** V3.4.1 起所有引用都移除了，下次清理時可考慮砍
16. NGS 內容後續更新時注意：健保給付癌別會擴增（目前 19 種是 113 年 5 月版），補入時記得同步改 F2 NGS 段表格

---

## 八、一句話總結

V3.4.7：**規則 12（標題層級設計語言）+ 規則 13（拆檔巢狀門檻）正式訂下**，A 檔成為**第一個套用範例**。Sela 兩個關鍵洞察直接寫進規則 12：「TOC 是快速到附近不是精準到小點」「分層不宜過細，導過去一頁就看到兩三個錨點」「同類東西放一起、有規律才好分層」。A 檔做了三件事：(1) **內容重整**——掃出第一部分主題切換 8 次、有三組同類散在四處（個管師角色、常規工作、其他特殊），重整成 5 個主題塊收攏，主題切換降為 4 次 (2) **層級降級**——5 H2（4 部分+附錄）+ 27 H3（≥ 20 行的 20 個 + 邊緣 8 個）+ 7 H4（< 15 行極短段降為內文段落、不上 TOC），加上原 64 H3 連帶降 H4，**TOC 從 104 項降到 32 項** (3) **砍 ## 目錄**（規則 12 第三條，跟 Material 自動 TOC 撞名）。Python 切片重組，mkdocs --strict 0 warning。**接手第一件事**：Sela 部署實測 A 檔 TOC 規模、第一部分主題塊收攏視覺、邊緣 7 個 H4 在內文是否仍清楚可讀。規則 12 還有 C3-C6（模式 2）/ G（模式 4）/ F（模式 3）三檔要修，列為下版候選 #3-5；規則 13 的 D 檔（1479 行）F 檔（1302 行）拆檔列為候選 #11-12，等 A 檔實測 OK 再動。
