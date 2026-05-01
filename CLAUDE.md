# CLAUDE.md｜彰濱秀傳癌症個管師手冊網站

**專案**：MkDocs + Material Theme，部署在 GitHub Pages（私有 Repo + GitHub Pro）
**當前版本**：V3.0.2
**網站用途**：彰濱秀傳癌症中心個管師工作手冊，供新進個管師隨時查詢，含中文搜尋
**對話脈絡**：V3.0.0 從零重做，把 V2.x 的 17 份巢狀分類 MD 收斂成 4 篇平鋪主檔（工作 / 養成 / 工具 / 指標），架構上消除 V2.x 的 sidebar 標題重複問題。V3.0.2 主色換 #25506b、sidebar 永久顯示。

---

## ⚠️ 永久規則（每版必遵守）

> **Claude 自我檢查機制**：每次升版（包含改坑記錄、改下版候選工作）之前，逐條重新確認以下規則是否依然有效並已執行。

### 🔁 每次升版前的自我確認清單

- [ ] **規則 1**：版本號在五個地方全部同步（JS / CSS / README / CLAUDE.md / ZIP 檔名）？
- [ ] **規則 2**：03_tools.md 第 5–8 章（院內系統說明）有沒有出現明文帳號密碼？
- [ ] **規則 3**：mkdocs.yml 的 `nav:` 是否仍是 5 個平鋪頂層、沒有任何巢狀？
- [ ] **規則 4**：03_tools.md 院內系統章節有填「放射腫瘤科 林伯儒 醫師」維護單位？
- [ ] **規則 5**：手機底部導覽列的 `getSiteRoot()` 有沒有被改成依賴 base.href？（不能）
- [ ] **規則 6**：`mkdocs build --strict` 過了？（0 warning）
- [ ] **規則 7**：主色用 `:root` 強制覆蓋（不是 `palette: custom`，坑 #18）？
- [ ] **規則 8**：sidebar 內第二層 `.md-nav` 有 `display: none`（坑 #19，避免左右側 TOC 重複）？
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
old, new = "V3.0.2", "V3.0.2"
for p in ["docs/javascripts/extra.js", "docs/stylesheets/extra.css",
          "README.md", "CLAUDE.md"]:
    f = pathlib.Path(p)
    f.write_text(f.read_text().replace(old, new))
```

### 規則 2：院內系統說明不寫明文帳密

03_tools.md 第 5–8 章（院內個管追蹤系統 / MDT / 抗癌藥物 / 病歷互審）以及未來任何院內系統說明，一律不得出現：
- 具體帳號代碼（員工編號、系統代碼）
- 具體密碼
- 帳號密碼對照表

**正確寫法**：「使用你自己的帳號和密碼登入。如忘記，請洽系統管理員。」

### 規則 3：nav 必須平鋪 5 個頂層、無巢狀

```yaml
# ✅ 正確（V3 平鋪）
nav:
  - 首頁: index.md
  - 工作: 01_work.md
  - 養成: 02_training.md
  - 工具: 03_tools.md
  - 指標: 04_metrics.md
```

**不可改成巢狀**（坑 #16）。V2.x 的所有 sidebar 標題重複問題、9 組 CSS 補丁、760px viewport hack，根源都是巢狀 nav。V3 從架構上消除這個問題，加回巢狀就是回到 V2.x 那個地獄。

如果未來內容真的太大需要再切細，**砍成更多平鋪頂層**（例如 9 個），不要做巢狀分類。

### 規則 4：院內系統章節維護單位

03_tools.md 的第 5–8 章（H1–H4 系列），維護單位欄位統一填寫：

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

V3 平鋪結構，5 個頂層頁面對應 5 個檔案，**沒有任何巢狀**：

| Nav 顯示 | 對應檔案 | 內容範圍 |
|---------|---------|---------|
| 首頁 | `docs/index.md` | 4 篇導覽卡片 |
| 工作 | `docs/01_work.md` | 13 章：認識工作 / 工作職責 / 工作工具箱 / C0 通論 / C1–C6 各癌別 / D 表單 / F 臨床知識庫 / E1 困難個案 / E2 安寧 / E4 必要事件 / 聯絡資訊 |
| 養成 | `docs/02_training.md` | 3 章：12 個月養成路線圖 / 培訓計畫書養成章 / E3 品質改善專案 |
| 工具 | `docs/03_tools.md` | 8 章：軟體上手 / 培訓計畫書工具章 / B1 HIS / B2 其他工具 / H1 個管追蹤 / H2 MDT / H3 抗癌藥物 / H4 病歷互審 |
| 指標 | `docs/04_metrics.md` | 3 章：品質指標概念入門 / 績效指標總則 / G 60 項速查 |

**改 nav 名稱要動兩處**：`mkdocs.yml` 的 `nav:` 區段、`docs/index.md` 的 4 個卡片連結。

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
| **V3.0.0** | **從零重做**：17 份巢狀 MD → 4 篇平鋪主檔（工作 / 養成 / 工具 / 指標）+ 首頁，nav 完全無巢狀，從架構上消除坑 #16 |
| V3.0.1 | 嘗試主色 #25506b（用 `palette: custom` + attribute selector，**失敗，主色沒換**）+ sidebar 永久顯示（造成左右兩側 TOC 重複）→ 兩個問題都記成坑 #18、#19 |
| **V3.0.2** | **修補 V3.0.1 兩個 bug**：主色改用 `:root` 強制覆蓋變數（坑 #18 做法）+ 加一條 CSS 隱藏 sidebar 內嵌 TOC（坑 #19 做法）。CLAUDE.md 規則 1 從「四處」擴充為「五處」 |

---

## 五、關鍵路徑

```
# 內容修改（最常動的）
docs/01_work.md         # 5067 行：工作篇 13 章
docs/02_training.md     # 589 行：養成篇 3 章
docs/03_tools.md        # 2017 行：工具篇 8 章（含 H1–H4 院內系統）
docs/04_metrics.md      # 729 行：指標篇 3 章
docs/index.md           # 首頁 4 卡片

# 框架（規則 3：nav 動之前先看規則）
mkdocs.yml              # nav / theme / plugins / markdown_extensions

# 樣式
docs/stylesheets/extra.css     # 主色 + sidebar 永久顯示 4 條規則 + 表格 / h1-h3
docs/javascripts/extra.js      # CCM_VERSION（規則 1）+ getSiteRoot（規則 5）

# 版本同步五處（規則 1）
docs/javascripts/extra.js      # var CCM_VERSION = "V?.?.?"
docs/stylesheets/extra.css     # 頂部 comment
README.md                      # 「當前版本：V?.?.?」
CLAUDE.md                      # 頂部「當前版本：V?.?.?」
ZIP 檔名                       # CCM Manual V?.?.?.zip

# 部署（不常動）
.github/workflows/deploy.yml
requirements.txt
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

1. **驗證 V3.0.2 sidebar 永久顯示在 MacBook Air（885px viewport）正常** — Sela 部署後第一件事，需要截圖確認 (a) 左邊 sidebar 跟主內容並排不浮動 (b) 主色 #25506b 視覺對 (c) 手機底部 4 鍵正常
2. 評估右側 TOC 要不要拿掉 — Sela 反映「側欄在右邊不習慣」，但對 5067 行的工作篇實際很有用，看實況決定。拿掉只要一行 `.md-sidebar--secondary { display: none !important; }`
3. 補 03_tools.md 第 3 章 HIS 系統的操作截圖（B1 五大系統）— 系統陸續上線後補入，新人最需要
4. 抗癌藥物速查若有新版（H3 章節），替換內容
5. 子宮頸癌 / 子宮體癌 / 卵巢癌完治率定義補入 04_metrics.md（待各團隊討論）
6. 評估 4 篇主檔是否需要再切細（特別是工作篇 5067 行）— 但要遵守規則 3，**只能切成更多平鋪頂層**，不可巢狀

---

## 八、一句話總結

V3.0.2：修補 V3.0.1 的兩個 bug——主色 #25506b 改用 `:root` 強制覆蓋 CSS 變數（坑 #18，`palette: custom` 行不通），sidebar 加一條 `display: none` 隱藏內嵌的當前頁 TOC（坑 #19，避免左右兩側 TOC 重複）。連續 8 版（V2.0.x → V3.0.x）打地鼠的「sidebar 與 TOC 各種重複」終於從架構上 + CSS 上都收乾淨。下版可以開始做內容（HIS 截圖、藥物速查更新），不必再動框架。
