# CLAUDE.md｜彰濱秀傳癌症個管師手冊網站

**專案**：MkDocs + Material Theme，部署在 GitHub Pages（私有 Repo + GitHub Pro）
**當前版本**：V3.1.0
**網站用途**：彰濱秀傳癌症中心個管師工作手冊，供新進個管師隨時查詢，含中文搜尋
**對話脈絡**：
- V2.0.x：17 份 MD + 巢狀 nav，連續打地鼠 sidebar 標題重複
- V3.0.0：把 17 份合併成 4 份平鋪主檔，從架構上消除巢狀
- V3.0.1–V3.0.2：修主色與內嵌 TOC bug（坑 #18、#19）
- **V3.1.0（本版）**：發現 V2.0.3 的 17 份 MD 內容是「討論很多次後改出來的精修版」，比合併過程做的 strip/demote 結果好。本版**內容回退到 V2.0.3 原檔**，**框架沿用 V3**（平鋪 nav，但改成 17 條而非 5 條）。坑 #20 記錄這個教訓

---

## ⚠️ 永久規則（每版必遵守）

> **Claude 自我檢查機制**：每次升版（包含改坑記錄、改下版候選工作）之前，逐條重新確認以下規則是否依然有效並已執行。

### 🔁 每次升版前的自我確認清單

- [ ] **規則 1**：版本號在五個地方全部同步（JS / CSS / README / CLAUDE.md / ZIP 檔名）？
- [ ] **規則 2**：H1–H4 院內系統說明書有沒有出現明文帳號密碼？
- [ ] **規則 3**：mkdocs.yml 的 `nav:` 是否仍是平鋪、沒有任何巢狀？（V3.1.0 是 17 條 + 首頁）
- [ ] **規則 4**：H1–H4 院內系統說明書有填「放射腫瘤科 林伯儒 醫師」維護單位？
- [ ] **規則 5**：手機底部導覽列的 `getSiteRoot()` 有沒有被改成依賴 base.href？（不能）
- [ ] **規則 6**：`mkdocs build --strict` 過了？（0 warning）
- [ ] **規則 7**：主色用 `:root` 強制覆蓋（不是 `palette: custom`，坑 #18）？
- [ ] **規則 8**：sidebar 內第二層 `.md-nav` 有 `display: none`（坑 #19，避免左右側 TOC 重複）？
- [ ] **規則 9**：drug-lookup/ 子資料夾有複製到 docs/（坑 #21，H3 抗癌藥物速查的本體）？
- [ ] **版本歷程**：這版做了什麼已補進版本歷程表？
- [ ] **下版候選工作**：重新排序、砍掉已做的？
- [ ] **一句話總結**：最後一段已更新？

---

### 規則 1：版本號五處必須同步

| 位置 | 改什麼 |
|------|--------|
| `docs/javascripts/extra.js` | `var CCM_VERSION = "V?.?.?"` |
| `docs/stylesheets/extra.css` | 頂部版本說明 comment |
| `README.md` | 頂部「當前版本：V?.?.?」 |
| `CLAUDE.md` | 頂部「當前版本：V?.?.?」 |
| ZIP 打包名稱 | `CCM Manual V?.?.?.zip` |

不同步的後果：右下角徽章顯示舊版號，使用者無法確認自己看的是哪版。

```python
# 升版時用 Python replace 批次處理，不用 sed 逐行（坑 #14 教訓）
import re, pathlib
old, new = "V3.1.0", "V3.1.0"
for p in ["docs/javascripts/extra.js", "docs/stylesheets/extra.css",
          "README.md", "CLAUDE.md"]:
    f = pathlib.Path(p)
    f.write_text(f.read_text().replace(old, new))
```

### 規則 2：院內系統說明書不寫明文帳密

H1–H4 系列（個管追蹤系統 / MDT / 抗癌藥物 / 病歷互審）以及未來任何 H 系列檔，一律不得出現：
- 具體帳號代碼（員工編號、系統代碼）
- 具體密碼
- 帳號密碼對照表

**正確寫法**：「使用你自己的帳號和密碼登入。如忘記，請洽系統管理員。」

### 規則 3：nav 必須平鋪、無巢狀

```yaml
# ✅ 正確（V3.1.0 平鋪 17 條，視覺用 emoji + 編號做分組暗示）
nav:
  - 首頁: index.md
  - 📋 A1 工作指導手冊: A_work-guide.md
  - 🎓 A2 培訓計畫書: A_training-plan.md
  - 💻 B1 HIS 系統操作手冊: B1_HIS-manual.md
  # ... 共 17 條
```

```yaml
# ❌ 錯誤（V2.x 的巢狀，禁止）
nav:
  - A｜新人通則:
    - 工作指導手冊: A_work-guide.md
    - 培訓計畫書: A_training-plan.md
```

V2.x 的所有 sidebar 標題重複問題、9 組 CSS 補丁、760px viewport hack，根源都是巢狀 nav（坑 #16）。V3 從架構上消除這個問題，加回巢狀就是回到 V2.x 那個地獄。

**平鋪 nav 的條目數量沒有上限**——V3.1.0 是 17 條（含首頁），sidebar 可滾動，使用者照常瀏覽。如果未來需要分組視覺感，用 emoji + 編號（A1/A2/B1...）暗示分類，但 yaml 結構必須是平的。

### 規則 4：院內系統說明書（H 系列）的維護單位

`H1_ccm-tracker-guide.md`、`H2_mdt-guide.md`、`H3_cancer-drugs.md`、`H4_peer-review-guide.md` 以及未來任何 H 系列檔，維護單位欄位統一填寫：

> 放射腫瘤科 林伯儒 醫師

### 規則 5：手機導覽列 getSiteRoot() 不可依賴 base.href

`docs/javascripts/extra.js` 的 `getSiteRoot()` **必須從 `window.location.pathname` 推算 site root**，不可使用 `base.href`、`document.querySelector("base").href` 或任何依賴 `<base>` tag 的寫法。

原因：Android Chrome + MkDocs instant navigation 下，`base.href` 解析成目前頁面 URL 而非 site root，導致路徑疊加跳 404。已在坑 #4（V1.3.0）和坑 #13（V1.9.6）兩度犯過，第三次直接砍掉這個寫法。

```javascript
// ✅ 正確（從 pathname 推算）
function getSiteRoot() {
  var path = window.location.pathname;
  var m = path.match(/^(\/[^\/]+\/)/);
  return m ? m[1] : "/";
}

// ❌ 錯誤（Android 會給錯誤的路徑）
function getSiteRoot() {
  return document.querySelector("base[href]").href;
}
```

### 規則 6：升版前必須通過 `mkdocs build --strict`

```bash
cd /path/to/repo
mkdocs build --strict 2>&1 | tail -10
```

**期待結果**：`Documentation built in X seconds`，0 warning、0 error。

如果出 warning（特別是「target is not found among documentation files」），多半是內部跨檔連結失效（坑 #17）。修法見坑 #17。

---

## 一、Repo 結構對映

| 我要改的事 | 動這些檔案 |
|-----------|-----------|
| 內容修改（工作 / 養成 / 工具 / 指標） | `docs/01_work.md` / `02_training.md` / `03_tools.md` / `04_metrics.md` |
| 首頁卡片或文案 | `docs/index.md` |
| Nav 結構（先讀規則 3） | `mkdocs.yml` 的 `nav:` |
| 主色 / 全站樣式 | `docs/stylesheets/extra.css` |
| 版本徽章 / 手機底部導覽列 | `docs/javascripts/extra.js` |
| 搜尋分隔符 / 中文分詞 | `mkdocs.yml` 的 `plugins.search` |
| 部署設定 | `.github/workflows/deploy.yml` |
| 套件版本 | `requirements.txt` |
| 版本號（5 處，規則 1） | extra.js / extra.css / README / CLAUDE / ZIP |

---

## 二、Nav 結構對映表

V3.1.0 平鋪 17 條 + 首頁，**沒有任何巢狀**：

| Nav 顯示 | 對應檔案 | 內容範圍 |
|---------|---------|---------|
| 首頁 | `docs/index.md` | 8 個快速導覽卡片（home-grid） |
| 📋 A1 工作指導手冊 | `A_work-guide.md` | 工作職責、日常流程、五大部分 |
| 🎓 A2 培訓計畫書 | `A_training-plan.md` | 四階段培訓、帶人指引 |
| 💻 B1 HIS 系統操作手冊 | `B1_HIS-manual.md` | 12 個 HIS 子系統 |
| 🔧 B2 其他工具使用說明 | `B2_other-tools.md` | LINE / 信箱 / 雲端 / 視訊 |
| 🏥 C0 癌症照護通論 | `C0_general.md` | 各癌別前言通論 |
| 🫁 C1 肺癌照護指引 | `C1_lung-cancer.md` | 肺癌專科 |
| 🎀 C2 乳癌照護指引 | `C2_breast-cancer.md` | 乳癌專科 |
| 🩺 C3–C6 其他癌別 | `C3-C6_other-cancers.md` | 大腸 / 肝 / 頭頸 / 攝護腺 |
| 📑 D 表單與範本 | `D_forms.md` | 評估表單、追蹤腳本、書信範本 |
| ⭐ E 專題與進階 | `E_advanced.md` | 困難個案、安寧、品質改善、必要事件提報 |
| 📚 F 臨床知識庫 | `F_clinical-kb.md` | 檢驗 / 藥物 / 副作用 / 放療 |
| 📊 G 品質指標速查 | `G_quality-index.md` | 13 癌 60 項指標、個管三大追蹤指標 |
| 🗂️ H1 個管追蹤系統 | `H1_ccm-tracker-guide.md` | 院內自製系統 |
| 👥 H2 MDT 會議管理系統 | `H2_mdt-guide.md` | 院內自製系統 |
| 💊 H3 抗癌藥物速查 | `H3_cancer-drugs.md` + `drug-lookup/` | 145 種藥物，本體在 `docs/drug-lookup/index.html` |
| 🔍 H4 病歷互審系統 | `H4_peer-review-guide.md` | 院內自製系統 |

**改 nav 顯示名要動兩處**：`mkdocs.yml` 的 `nav:` 區段、`docs/index.md` 的卡片連結。
**改 nav 結構（增刪檔案）要動三處**：上述兩處，加上 `docs/javascripts/extra.js` 的 mobile nav `items` 陣列（如果動到那 4 個常用入口的話）。

---

## 三、踩過的坑

> 編號從 V1.0.0 連續累積，永不重排。新坑往下加。

**#1（V1.0.0）私有 Repo + GitHub Pages 需要 GitHub Pro**
- 症狀：Settings → Pages 找不到 GitHub Actions 選項
- 原因：私有 Repo 的 GitHub Pages 功能需付費方案
- 做法：升級 GitHub Pro

**#2（V1.0.0）MD 檔名含中文在 Linux 伺服器編碼壞掉**
- 症狀：build 時 nav 找不到中文檔名 MD，顯示亂碼路徑
- 做法：所有 docs/ 下的 MD 一律英文檔名（V3 是 `01_work.md` 等）

**#3（V1.0.0）中文搜尋 separator 設定錯誤**
- 症狀：搜尋任何中文關鍵字都找不到結果
- 原因：`[\u3000-\u9FFF]` 把所有中文字當分隔符
- 做法：separator 只切標點符號，加 jieba 套件做中文斷詞

**#4（V1.3.0）手機底部導覽列點了路徑疊加跳錯頁**
- 原因：`document.baseURI` 在子頁返回子頁路徑
- 做法：當時改用 `base.href`，後來坑 #13 證明這還是錯的，正解見規則 5

**#5（V1.4.0）CSS content 變數版本徽章跨頁不穩定**
- 做法：改用 JS 直接 `createElement` 注入

**#6（V1.4.0）navigation.expand 強制展開所有側欄**
- 做法：移除 `navigation.expand`，加 `navigation.prune`

**#7（V1.7.0）軟體說明 MD 出現明文帳密** → 永久規則 2

**#8（V1.7.0）版本號分散沒同步** → 永久規則 1（V3 擴充為五處）

**#9（V1.7.1）A_work-guide.md 多個 h1 導致錨點失效**
- 原因：MkDocs 對非第一個 h1 行為不穩定
- 做法：部分標題改 h2

**#10（V1.8.4）mkdocs.yml 缺 markdown_extensions 導致 !!! 區塊不渲染**
- 做法：補回完整 markdown_extensions（admonition / pymdownx / superfences / highlight / tabbed / emoji / tasklist / tables / toc / attr_list）

**#11（V1.8.6）F 章節索引不見 + 移除 navigation.sections**
- 此次同時誤刪 toc.integrate
- 為 V2.x 一連串問題的源頭

**#12（V1.8.9）toc.integrate 再度被誤刪**
- 此規則在 V2.x 是「必保留」，但 V3 平鋪結構下已不需要
- V3 的等效規則是規則 3（nav 不可巢狀）

**#13（V1.9.6）Android 手機底部導覽列 404（第三度）**
- 原因：MkDocs instant nav 下 `base.href` 在 Android 解析錯誤
- 做法：`getSiteRoot()` 完全不用 base.href，改 pathname 推算 → 永久規則 5

**#14（V2.0.3）navigation.indexes 導致頂端 tab 消失 + 版本號散落**
- 兩個獨立問題同版踩到
- 做法：移除 navigation.indexes；版本號改用 Python replace 批次處理

**#15（V2.0.3）navigation.sections 漏加回 + 中文錨點全壞**
- 症狀：60+ 個 broken anchor + 跨檔連結失效
- 做法：加回 navigation.sections、toc 改用 pymdownx.slugs.slugify(case=lower) 支援中文錨點

**#16（V2.0.x → V3.0.0）巢狀 nav 在 < 76.25em viewport 永遠 sidebar 標題重複**
- 症狀：sidebar 中每個 section 名稱（A｜新人通則 等）重複出現兩次，第一個還帶 `>` 箭頭
- 原因：Material 對 nested section 渲染兩次（一次當分類器、一次當第一個子頁），CSS 怎麼蓋都不乾淨
- V2.0.3 試了 9 組 CSS 規則，蓋掉重複還是會破壞別的（pointer-events: none、強制 font-size 等）
- 做法：V3.0.0 從零重做，5 個平鋪頂層頁面 + 0 巢狀，**從架構上消除問題** → 永久規則 3
- 教訓：**CSS override 蓋不過架構問題，要從架構解**

**#17（V3.0.0）合併 MD 後跨檔連結失效**
- 症狀：`mkdocs build --strict` 報「target is not found among documentation files」7 條警告
- 原因：把 17 份 MD 合併成 4 份時，原檔內部的 `[xxx](G_quality-index.md)`、`[xxx](E_advanced.md)`、`[xxx](H?_xxx.md)` 全部指向不存在的目標
- 做法：合併腳本後做一次 sed 批次替換，全部改指向新檔錨點：
  ```bash
  sed -i 's|](G_quality-index\.md)|](04_metrics.md)|g' 01_work.md
  sed -i 's|](E_advanced\.md)|](01_work.md#10-困難個案處理)|g' 01_work.md
  sed -i 's|](H1_ccm-tracker-guide\.md)|](03_tools.md#5-院內個管追蹤系統)|g' 03_tools.md
  # ...H2/H3/H4 同理
  ```

**#18（V3.0.1）palette: custom + attribute selector 沒生效**
- 症狀：mkdocs.yml 設 `primary: custom`、extra.css 用 `[data-md-color-primary="custom"]` selector 設變數，header 仍顯示預設 indigo（截圖證實主色完全沒換）
- 原因：Material 對 custom palette 的支援需要更深的 theme override（partial 或 hooks），光在 extra.css 用 attribute selector 不夠——這個 attribute 沒被 inject 到 html 元素上
- 做法：**放棄 custom palette**，extra.css 改用 `:root` 強制覆蓋變數，無視 mkdocs.yml palette 設定。mkdocs.yml palette 留 `primary: indigo` 當佔位
  ```css
  :root,
  [data-md-color-scheme="default"] {
    --md-primary-fg-color:        #25506b;
    --md-primary-fg-color--light:  #3a6e8c;
    --md-primary-fg-color--dark:   #173a52;
    --md-accent-fg-color:          #25506b;
  }
  ```
- 教訓：CSS 變數覆蓋要用最高優先級 selector（`:root`），不要依賴 Material 注入特定 attribute

**#19（V3.0.1）強制 sidebar 顯示時，內嵌的當前頁 TOC 跟著被顯示**
- 症狀：sidebar 同時顯示 (a) 5 個主 nav item 和 (b) 當前頁的 TOC（本書架構 / 1.認識這份工作 / 個管師是什麼角色 ...），TOC 同時也在右側 secondary sidebar，**左右兩邊一模一樣的 TOC**
- 原因：Material drawer 模式下，`.md-nav--primary` 的 HTML 結構**內嵌**當前頁 TOC（為了 drawer 展開時能看到）。V3.0.1 用 `.md-nav--primary .md-nav { display: block !important }` 強制顯示所有子層 nav，這個內嵌 TOC 也跟著被顯示
- 做法：sidebar override 加一條明確隱藏：
  ```css
  @media screen and (min-width: 760px) {
    .md-sidebar--primary .md-nav .md-nav { display: none !important; }
  }
  ```
  V3 平鋪 nav 下，sidebar 內第二層 `.md-nav` 唯一來源就是當前頁 TOC，安全可全隱藏
- 教訓：「強制顯示 sidebar」≠「強制顯示 sidebar 內所有元素」。drawer 與 wide 兩種模式的 HTML 內部結構不同——drawer 模式下嵌入的東西，必須在強制顯示 sidebar 時針對性隱藏

**#20（V3.0.0–V3.0.2 → V3.1.0）合併 MD 會丟失原檔精修內容**
- 症狀：V3.0.0 把 V2.0.3 的 17 份 MD 用腳本合併成 4 份（工作 / 養成 / 工具 / 指標），過程做了 strip_first_h1、demote、strip_doc_meta、strip_part_header 等處理。Sela 反映「2.03 版的內容是討論很多次後改出來的，比 files 夾裡的好，你應該要以 2.03 為主，只能改排版框架」
- 原因：V2.0.3 的 17 份 MD 是經過反覆討論精修的版本，每一份都有獨立的章節編號、目錄、副標籤、文件資訊區塊；合併過程的 strip / demote 雖然產出乾淨大檔，但隱性丟失了一些細節（章節編號層次、原始排版意圖）
- 做法：V3.1.0 把 docs/ 下的 4 份合併 MD 全砍，改回 V2.0.3 的 17 份原檔；nav 從 5 條平鋪改成 17 條平鋪（仍遵守規則 3 無巢狀）；index.md 用 V2.0.3 的 home-grid 卡片版（也是精修過的）；framework 部分（mkdocs.yml / extra.css / extra.js）保留 V3 的設計
- 教訓：**內容是反覆討論的成果，框架是技術選擇**。下次做大規模重構時，要區分清楚「我在動內容還是動框架」——動框架可以激進，動內容要極度保守，能保留原檔就保留原檔

**#21（V3.1.0）H3 抗癌藥物速查的本體在 docs/drug-lookup/ 子目錄**
- 症狀：V3.0.0 重做時忘了把 `docs/drug-lookup/index.html` 帶過來，部署後 H3 的「點此查藥物」連結變 404
- 原因：H3_cancer-drugs.md 只是「說明書」，實際 145 種藥物的查詢介面是獨立的 HTML（`docs/drug-lookup/index.html`），MkDocs 會把這個資料夾原封不動複製到 `site/drug-lookup/`
- 做法：每次重組 docs/ 結構時，drug-lookup/ 子目錄一定要一起搬（V3.1.0 已修正，加入煙霧測試 step 2「drug-lookup 有複製？」）
- 注意：drug-lookup 是 `<index.html>` 不是 `.md`，是個自成一體的單頁 web app（含 145 種藥物的健保給付條件）。未來有新版時，整個資料夾原地替換即可

---

## 四、版本歷程

> 只留最近 6–10 版（章法 7：過期上下文等於垃圾）。完整歷程在 README.md。

| 版本 | 主要異動 |
|------|---------|
| V1.9.6 | Android 底部導覽 404 徹底修（坑 #13），永久規則 5 寫入 |
| V1.9.7–V1.9.9 | 表格樣式、搜尋微調、760px CSS override 第一版（門檻 960px 太高） |
| V2.0.0 | navigation.sections 漏加回 + 中文錨點全壞（坑 #15） |
| V2.0.1–V2.0.2 | 760px override 反覆調整，V2.0.2 首次成功 sidebar 永久顯示，但巢狀 nav 標題重複 |
| V2.0.3 | 9 組 CSS 規則嘗試修標題重複，太激進可能改壞別的；deploy.yml 一度被誤刪 |
| **V3.0.0** | **從零重做框架**：17 份巢狀 MD → 4 篇平鋪主檔（工作 / 養成 / 工具 / 指標）+ 首頁，nav 完全無巢狀，從架構上消除坑 #16 |
| V3.0.1 | 嘗試主色 #25506b（用 `palette: custom` + attribute selector，**失敗，主色沒換**）+ sidebar 永久顯示（造成左右兩側 TOC 重複）→ 兩個問題都記成坑 #18、#19 |
| V3.0.2 | **修補 V3.0.1 兩個 bug**：主色改用 `:root` 強制覆蓋變數（坑 #18）+ 加一條 CSS 隱藏 sidebar 內嵌 TOC（坑 #19）。CLAUDE.md 規則 1 從「四處」擴充為「五處」 |
| **V3.1.0** | **內容回到 V2.0.3 原檔**（17 份精修 MD + drug-lookup/）：發現合併版會丟失原檔精修內容（坑 #20）、補回 H3 抗癌藥物速查本體（坑 #21）。nav 從 5 條平鋪改 17 條平鋪（仍遵守規則 3 無巢狀），首頁用 V2.0.3 的 home-grid 卡片設計 |

---

## 五、關鍵路徑

```
# 內容（17 份精修 MD，V2.0.3 沿用，本版只改框架不改內容）
docs/A_work-guide.md          # 1247 行：工作指導手冊（5 大部分）
docs/A_training-plan.md       # 培訓計畫書（4 章）
docs/B1_HIS-manual.md         # HIS 12 子系統
docs/B2_other-tools.md        # LINE / 信箱 / 雲端
docs/C0_general.md            # 癌症照護通論
docs/C1_lung-cancer.md        # 肺癌
docs/C2_breast-cancer.md      # 乳癌
docs/C3-C6_other-cancers.md   # 大腸 / 肝 / 頭頸 / 攝護腺
docs/D_forms.md               # 表單範本（D1–D4）
docs/E_advanced.md            # 困難個案 / 安寧 / 品質改善 / 必要事件提報（E1–E4）
docs/F_clinical-kb.md         # 臨床知識庫（F1–F4）
docs/G_quality-index.md       # 60 項指標速查
docs/H1_ccm-tracker-guide.md  # 院內個管追蹤系統
docs/H2_mdt-guide.md          # 院內 MDT 會議系統
docs/H3_cancer-drugs.md       # 抗癌藥物速查（說明）
docs/drug-lookup/index.html   # 抗癌藥物速查本體（145 種）— MkDocs 原封不動複製
docs/H4_peer-review-guide.md  # 院內病歷互審系統
docs/index.md                 # 首頁（home-grid 卡片導覽）

# 框架（V3 沿用，本版不動）
mkdocs.yml                    # nav / theme / plugins / markdown_extensions
docs/stylesheets/extra.css    # 主色 + sidebar 永久顯示 + home-grid 卡片
docs/javascripts/extra.js     # CCM_VERSION（規則 1）+ getSiteRoot（規則 5）+ mobile nav 4 個入口

# 版本同步五處（規則 1）
docs/javascripts/extra.js     # var CCM_VERSION = "V?.?.?"
docs/stylesheets/extra.css    # 頂部 comment
README.md                     # 「當前版本：V?.?.?」
CLAUDE.md                     # 頂部「當前版本：V?.?.?」
ZIP 檔名                      # CCM Manual V?.?.?.zip

# 部署
.github/workflows/deploy.yml
requirements.txt
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

使用 Sela 自製的 Git Pusher（V1.5.5）：
1. ZIP 命名：`CCM Manual V?.?.?.zip`（空格分隔、點號版本）
2. 內部結構：**無外層資料夾**（`mkdocs.yml`、`docs/`、`.github/` 直接在根）
3. Git Pusher 「匯入 Zip 並上傳」→ 自動清空舊資料夾（保留 `.git`、`.gitignore` 項目）→ commit + push
4. 看 https://github.com/Sela1227/CCM-manual/actions 確認 Actions 跑成功
5. 開 https://Sela1227.github.io/CCM-manual/ 看畫面

### 煙霧測試（每次升版必跑）

```bash
# 1. build 過 strict
mkdocs build --strict

# 2. 確認 5 個頂層頁面都 build 出來
ls site/01_work/index.html site/02_training/index.html \
   site/03_tools/index.html site/04_metrics/index.html site/index.html

# 3. 確認 sidebar 是平鋪（no nested）
grep -c "md-nav__item--nested" site/index.html
# 期待：0
```

---

## 七、下版候選工作

按優先序：

1. **驗證 V3.1.0 sidebar 顯示與配色實際效果** — Sela 部署後第一件事，需要截圖確認 (a) 左邊 sidebar 是 17 條平鋪、跟主內容並排不浮動 (b) 主色 #25506b 確實生效（不是 indigo）(c) 右側 TOC 不再跟左側重複 (d) 手機底部 4 鍵正常
2. 評估右側 TOC 要不要拿掉 — 如果 sidebar 17 條已經夠用、TOC 反而干擾，加一行 `.md-sidebar--secondary { display: none !important; }` 就拿掉
3. 評估 sidebar 17 條是否擠 — 如果 sidebar 太長，可以縮小 nav `font-size`、或拿掉 emoji 簡化視覺
4. 補 B1 五大 HIS 系統的操作截圖（系統陸續上線後補入，新人最需要）
5. 抗癌藥物速查若有新版，整個 `docs/drug-lookup/` 資料夾原地替換 + 改 H3 版本說明（坑 #21）
6. 子宮頸癌 / 子宮體癌 / 卵巢癌完治率定義補入 G_quality-index.md（待各團隊討論）
7. 評估 C3–C6 是否需要拆成獨立 MD（如果拆，nav 平鋪變 20 條，仍遵守規則 3）

---

## 八、一句話總結

V3.1.0：把 V3.0.x 的「合併版 4 份」全砍，內容回到 V2.0.3 那 17 份精修 MD（包含 drug-lookup/ 子目錄），nav 改 17 條平鋪（仍無巢狀，遵守規則 3），首頁用 V2.0.3 的 home-grid 卡片設計。框架（主色 #25506b、sidebar 永久顯示、隱藏內嵌 TOC、手機底部導覽）沿用 V3.0.2。坑 #20 教訓：**內容是反覆討論的成果（保守對待），框架是技術選擇（可以激進）**。下版可以開始補 HIS 截圖、藥物速查更新等實際內容，不必再動框架。
