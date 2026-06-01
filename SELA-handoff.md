# SELA-handoff.md｜CCM Manual V4.0.0 首次對齊 Kit V1.9.0

> **本檔給 Kit Claude 用**——升 Kit 時看這份就能高效規畫，不用挖整份 CLAUDE.md（4,500+ 行）。
>
> **產出時機**：CCM Manual V4.0.0 首次對齊 Kit（鐵律 #0 + 第二章「對齊既有專案」必含）。
>
> **本專案背景**：MkDocs + Material Theme 文檔網站、給彰濱秀傳癌症中心個管師使用、Sela 個人帳號（sela1227）維護、GitHub Pages 私有 repo 部署、V1.x 起累積 28 個版本（V3.4.28→V4.0.0）、52 個坑、15 條規則。

---

## 一、用 Kit 的整體感受（給 Kit Claude 校準）

### 預期外的順利

- **章法手冊「踩過的坑要編號累積、永不重排」**：CCM 從 V1.x 起就在做這件事（累積 #1-#52）、跟 Kit 章法一完全吻合——表示這原則跨專案有共識
- **章法手冊「下版候選工作按優先序排」**：CCM 從 V3.4.x 起把候選工作分「驗證/最重要/等醫師/老手剩餘/等資料/雜項」六層、跟 Kit 章法五接近，但**少了「第 1 名要解釋為什麼」**這個細節——本版（V4.0.0）已補
- **章法手冊「版本歷程留近期 6-10 版」**：CCM 累積到 V3.4.28 後版本歷程保持 8 版滾動、跟 Kit 章法七一致——這原則跨專案直觀
- **章法手冊「一句話總結放最末」**：CCM 早就這麼做、但**寫得太長**（350 字 vs Kit 範例 ~80 字）——本版已縮短

### 預期外的卡住

- **Kit 鐵律 #0「每版評估 handoff」CCM 從未做過**：V3.4.16 起累積 13 版（每版踩坑 + 大改動）、按 Kit 標準早該產出 2-3 份 handoff。直到 Sela 上傳 Kit V1.9.0 才意識到。**Kit 對「既有專案首次接 Kit 時該怎麼補回歷史 handoff」沒明確指引**
- **Kit 預設「Python / Flet / HTML 」三條 reference 路徑沒覆蓋 MkDocs 文檔網站專案**——CCM 對齊時走「對齊既有專案 SOP」第二章但無 reference 可參考，所有規則要自己判斷適不適用
- **Kit 章法手冊「業務對映表 / 升版必讀 / 煙霧測試指令 / 關鍵路徑」4 個段落對純文檔網站幾乎不適用**——本版進「✗ 不做」級且明寫理由

### 對 Kit 的整體評價

- ✓ **章法手冊 10 條規則品質非常高、直接可用**——CCM 自己摸索出來的「規則 1 版本同步、規則 14 single source of truth、規則 15 時效性」跟 Kit 章法核心精神吻合
- ✓ **坑 #40「對齊既有專案 SOP」四級分類法非常實用**——本版完全照做、清楚把 7 件做 vs 5 件不做分開
- ✗ **Kit 沒覆蓋「文檔網站」這條技術棧路徑**——MkDocs / Sphinx / Docusaurus 這類純文檔網站有獨特挑戰（nav 巢狀、cross-ref 完整性、build --strict 防呆等）
- ✗ **章法手冊舉的範例都是有資料庫的應用**（schema、Alembic、bcrypt 等）——文檔網站專案讀完會覺得「這跟我不太相關」、需要自己翻譯

---

## 二、發現的「跨專案通用坑」（建議進 Kit）

### 強烈建議加坑

#### 1. **str_replace 改既有內容前要先看實際格式、不要憑記憶猜 old_str**

- **症狀**：`str_replace` 拋例外（old_str not found）或更糟——`if old in text` 靜默漏掉、build 才報錯
- **原因**：不同檔的格式有微妙差異（編號清單 vs 條列、全形空格 vs 半形、anchor slug 漢字編碼）、憑記憶寫 old_str 容易猜錯
- **做法**：
  - 動 str_replace 前先 `grep -n` 看實際格式
  - Python 批次改用 `assert old in text` 而非 `if old in text`——靜默漏掉是 anti-pattern
  - **build --strict 是最後防線**（CCM 規則 6：mkdocs build --strict 0 warning）
- **影響範圍**：所有有大量 markdown / 配置檔的專案
- **證據**：CCM 坑 #51（V3.4.27 C0 目錄格式不一致漏改）、坑 #48（V3.4.24 A3 anchor 寫錯沒先 build 看 slug）
- **檢查結果**：grep Kit「str_replace」「old_str」→ 無重複，但 Kit 章法八「測試指令」精神接近

#### 2. **歷史註解不該寫死版本號（避免 sed 升版誤動）**

- **症狀**：sed 升版（`s/V3.4.X/V3.4.Y/g`）把歷史註解內的版本號一併替換成新版號
- **原因**：歷史註解本意是紀錄「過去某版做了什麼」、寫死版本號就會被 sed 當成「當前版本」誤改
- **做法**：
  - 歷史描述用「本版」「上一版」「美編 7 件之一」等版本中性敘述
  - 版本號只該出現在 4 處：程式版本變數（CCM_VERSION）、CSS 開頭版本標記、README、CLAUDE.md 頂部
  - 註解內絕對不寫死版本號
- **影響範圍**：所有用 sed 批次升版的專案（多數 SELA 專案符合）
- **證據**：CCM 坑 #46（V3.4.22 美編版踩到、訂規則 1 修訂；V4.0.0 再補充規則 1 澄清）
- **檢查結果**：grep Kit「sed 升版」「歷史註解」→ 無重複

#### 3. **環境重置時要從 outputs 解壓最新 zip 重建工作目錄**

- **症狀**：長對話中環境重置、`/home/claude/work` 不見、bash 報 `cd: can't cd to`
- **原因**：Anthropic 平台跨對話 / 長時間後可能重置工作環境、但 `/mnt/user-data/outputs/` 是持久的
- **做法**：
  - 每次新對話開頭驗證工作目錄存在
  - 不存在則 `unzip /mnt/user-data/outputs/<最新版>.zip` 重建
  - 把這條寫進專案 CLAUDE.md 開頭「接手第一件事」
- **影響範圍**：所有跨多日 / 多對話迭代的長期專案
- **證據**：CCM 坑 #52（V3.4.28 環境重置 /home/claude/work 不見、從 outputs 解壓 V3.4.27 zip 重建）
- **檢查結果**：grep Kit「環境重置」「outputs 解壓」→ 無重複

### 可加但等更多證據確認

- **編號清單 vs 條列清單格式不一致導致 str_replace 漏掉**：CCM 內部問題、但其他大型 markdown 專案可能也遇到——等第 2 個專案踩到再進坑庫

---

## 三、發現的「跨專案設計模式」（建議進 sela-philosophy / 規範）

### 1. Single Source of Truth + Cross-ref（CCM 規則 14）

- **本案發生情境**：CCM 早期同一概念散在多檔（個管師分工散在 A1/H2/H3、ECOG 評估散在 A1/D1、補助專案散在 4 處），改一處忘改別處導致版本不一致
- **可推廣的原則**：每個業務概念有「**單一權威源**」（A3 是醫師清單權威、D2 是衛教資源權威），其他檔用 cross-ref 連到權威源 anchor、不重寫內容
- **代價 / 取捨**：cross-ref 需維護 anchor slug 一致、anchor 改變時所有引用失效（CCM 坑 #48 就是 anchor 寫錯）
- **建議寫入**：`conventions/sela-philosophy.md` 或 `start-project-decisions.md`——「多檔關聯時建立 single source of truth」

### 2. 時效性內容三類標記（CCM 規則 15）

- **本案發生情境**：CCM 內出現三類有時效的資料——EGFR 補助有截止日（2026/12/31）、五癌篩檢推廣每年改版、健保藥物給付不定期更新——以前混在一起寫
- **可推廣的原則**：時效性資料按三類標記：
  - **明確截止日**：⚠️ + 年月日 + 「請於申請前以官網為準」
  - **年度更新**：📅 「每年改版提醒」框 + 「當您讀到此段時請確認是否為當年度版本」
  - **不定期更新**：ⓘ + 版本日期 + 「實際以最新公告為準」
- **代價 / 取捨**：寫文件時要評估時效類型、增加思考負擔
- **建議寫入**：`conventions/CLAUDE-MD-章法.md` 章法十一（新增）或業務文件寫作規範

### 3. 多視角 QA 試用（CCM 累積 7 個視角）

- **本案發生情境**：CCM V3.4.16-V3.4.28 期間用 7 個不同視角審視（新人 28 天試用 / 老手日常 / 醫師審視 / PM 跳頁體驗 / 美編 UI / 第四輪 QA 退化檢查 / 規則對齊）、每輪都找出獨特問題
- **可推廣的原則**：「**結構工程做完不等於可用**——需要不同視角的審視才能找到結構盲點」
- **代價 / 取捨**：每輪審視 30-60 分鐘 + 累積版本號、但找出來的問題遠超「自審」
- **建議寫入**：`conventions/start-project-decisions.md` 或新增「QA 視角清單」conventions

---

## 四、Kit 該瘦身或調整的地方

### Kit 規範修改建議

#### 1. claude-init.md 加「文檔網站」reference 路徑

- **現狀**：Kit V1.9.0 只有 Flet / CLI / 靜態 HTML 三個 reference，沒有 MkDocs / Sphinx / Docusaurus 這類文檔網站
- **建議改成**：加 `reference-docs-site/`（從 CCM Manual 萃取）或在 claude-init.md 加說明「文檔網站走純靜態 HTML 路徑 + 加 MkDocs 特定坑」
- **理由**：MkDocs 跟靜態 HTML 不一樣（有 build step、nav 結構、anchor slug、jieba 中文分詞配置等），靜態 HTML reference 不夠用

#### 2. 章法手冊舉例補「文檔網站」場景

- **現狀**：章法手冊範例都是 web app（schema、Alembic、bcrypt、6 基準品質報表）、文檔網站讀者需翻譯
- **建議改成**：每條章法多舉一個「文檔網站」範例，如：
  - 章法二「業務對映表」→ 文檔網站範例可用 CCM 規則 1「版本號五處同步表」
  - 章法八「測試指令」→ 文檔網站範例可用 `mkdocs build --strict`
- **理由**：跨技術棧的範例會讓 Kit 更通用

### Kit 結構性建議

- **claude-init.md 第二章「對齊既有專案 SOP」**很實用但缺一個情境：「**累積 N 個版本後首次接 Kit 時、過去 handoff 沒做的怎麼補**」。CCM V3.4.16-V3.4.28 共 13 版每版都該評估 handoff（按 Kit 標準）但都沒做、本檔等於「13 版補回的第一份 handoff」。建議 Kit 補一段「歷史補回流程」指引

---

## 五、留在這個專案、不要回流 Kit 的東西

> 這節避免 Kit Claude 把本專案特定的東西當通用坑收進去。

- **CCM 規則 1（版本號五處同步）**：本專案 MkDocs + JS + CSS + README + CLAUDE.md 特化結構、跟其他專案版本號位置不同——**設計原則「版本號位置要列舉」可進 Kit、具體 5 處清單留專案**
- **CCM 規則 2-12**（H 系列說明書帳密、nav 巢狀、林伯儒醫師掛名、getSiteRoot 從 pathname 推算、主色 :root 覆蓋、760px sidebar override 砍除等）：全部 MkDocs / Material Theme / 醫療文檔特定
- **CCM 規則 13 拆檔策略**：本專案 30+ md 檔的特殊狀況、其他專案少有
- **C 系列 13 個癌別檔結構**（疾病概述 / 診斷分期 / 治療指引 / 特殊注意事項 / 品質指標 / 個管照護 / 常見問題 / 衛教資源 八段）：醫療專業內容
- **MDT 主檔對齊**（A3 跟 MDT 系統匯出資料同步）：醫院內部運作
- **個管師分工 A/B/C 匿名**（H 系列改 A/B/C 寫法）：醫療隱私處理
- **G2 品質指標報告**（114 年度 13 癌別 63 指標）：本院年度監測

---

## 六、Kit Claude 的建議行動清單

### 建議升 Kit 版本

**Kit V1.10.0**——加新 conventions + 補 reference（理由：第二、三節提案是新內容、b+1 等級）

### 必做

- [ ] 新增「str_replace 改既有內容前先看實際格式」進 Kit `cross-project-pitfalls.md`（CCM 坑 #51 + #48 萃取）
- [ ] 新增「歷史註解不該寫死版本號」進 Kit `cross-project-pitfalls.md`（CCM 坑 #46 + V4.0.0 規則 1 補充澄清萃取）
- [ ] 新增「環境重置從 outputs 解壓 zip 重建」進 Kit `cross-project-pitfalls.md`（CCM 坑 #52 萃取）
- [ ] 章法手冊加章法十一「時效性內容三類標記」（從 CCM 規則 15 推廣）
- [ ] `start-project-decisions.md` 或 `sela-philosophy.md` 加「Single Source of Truth + Cross-ref」原則
- [ ] `claude-init.md` 加 MkDocs / 文檔網站閱讀路徑

### 暫緩

- [ ] 「文檔網站 reference」（建議萃取自 CCM Manual）——等 Sela 確認要不要做這個 reference
- [ ] 「多視角 QA 試用」進 conventions——再看一個專案是否也有類似累積

### 不做

- [ ] CCM 規則 1-15 整套進 Kit（全部本專案特定）
- [ ] CCM 13 癌別 C 系列檔模板（醫療專業）
- [ ] G2 品質指標報告結構（本院年度監測）

---

## 七、給 Kit Claude 的最後備註

CCM Manual 是「**長期演化 + 文檔網站**」兩個 Kit 較少覆蓋的情境，本份 handoff 反饋偏向「Kit 沒覆蓋的盲點」。

CCM 自己摸索出來的 15 條規則跟 Kit 章法手冊有約 60% 重疊（規則 14 ↔ 章法二、規則 1 ↔ 章法二、規則 15 是 Kit 沒有的、規則 6 ↔ 章法八）——表示**獨立演化的成熟專案會自然趨向類似的章法**、Kit 的章法手冊抓對了核心精神。

未來 CCM 升 V4.1.0+ 時會繼續產出 handoff（依鐵律 #0 評估流程）、累積證據後可決定要不要把「文檔網站 reference」加進 Kit。

---

**文件資訊**

| 項目 | 內容 |
|------|------|
| handoff 版本 | 1.0（首份）|
| 對應專案版本 | CCM Manual V4.0.0 |
| 對應 Kit 版本 | V1.9.0 |
| 產出日期 | 2026 年 6 月 |
| 維護單位 | Sela（個人）|
