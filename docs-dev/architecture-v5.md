# V5 架構細節（原 CLAUDE.md 一、二節）

> 本檔由 V5.5.0（內審 R12）從舊 CLAUDE.md 原文搬出，內容未改寫。現行規範以根目錄 CLAUDE.md 為準；這裡是決策脈絡與歷史。

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

## 二、Nav 結構與分類（V5.1.0 起）

**分類的唯一來源是每頁開頭的 front matter**：

```yaml
---
category: cancer      # learn | daily | cancer | lookup | admin
---
```

| category | 側欄組名（＝hub 名）| hub 頁 | 底部導覽鈕 |
|---|---|---|---|
| learn | 學習中心 | hub_learning | 學習 |
| daily | 日常工作 | hub_daily | 工作 |
| cancer | 癌別照護 | hub_cancer | 癌別 |
| lookup | 臨床速查 | hub_lookup | （無，不亮）|
| admin | 系統與管理 | hub_admin | （無，不亮）|

側欄：頂層是首頁＋五個 hub，「完整資料庫」底下依上表分 5 組；A1／C3／H3 這些代碼保留在頁面標題裡。分類定義在 `hooks.py` 的 `CATS`。

**新增一頁（3 步）**：
1. 建 `docs/<英文檔名>.md`，開頭寫 front matter `category:`
2. `mkdocs.yml` 的「完整資料庫」對應組加一行
3. `mkdocs build --strict`——忘了寫 category、放錯組、沒進 nav，都會被擋下

### 癌別檔固定章節 ID（V5.2.0 起）

13 份癌別檔（C1–C13）的章節標題後面都掛固定英文 ID，**標題文字、章號可以改，ID 不能改**。連到癌別章節一律寫 `C3_colorectal-cancer.md#redflags` 這種形式，不要再用中文 slug。

| ID | 章節 | 必備？ |
|---|---|---|
| `overview` | 疾病概述 | ✓ |
| `staging` | 診斷與分期 | ✓ |
| `treatment` | 治療指引 | ✓ |
| `nhi` | 健保給付（C6／C7／C8／C10 有獨立一章）| 選配 |
| `notes` | 本癌別特殊注意事項 | 選配 |
| `followup` | 個管師日常追蹤重點 | ✓ |
| `care` | 個管照護重點 | 選配 |
| `redflags` | 🚩 紅旗表 | 選配（C2／C9／C11–C13 尚未建立）|
| `faq` | 常見問題與處理 | ✓ |
| `edu` | 衛教資源 | ✓ |

- front matter `template_kind: cancer` → hook 檢查必備 ID 是否齊全；C10 用 `template_kind: cancer-split`（`rcc`／`bladder` 兩部，另有 `rcc-*`、`bladder-*`、`turbt`、`nmibc`、`mibc`、`metastatic`、`cystectomy`、`intake`）。
- 寫法：`## 七、常見問題與處理 { #faq }`。
- 各檔不再自寫 `## 目錄`（hook 會擋），右側自動 TOC 與頂部快捷列已足夠。

### 文件審閱欄位（V5.4.0 起，內審 R6）

「最後更新」＝該檔最後一次 git commit 的日期，Material 自動顯示在頁底，**不再手寫**。審閱相關的狀態寫在 front matter，模板把它畫成頁底的審閱資訊列：

| 欄位 | 值 | 誰要寫 |
|---|---|---|
| `guideline` | 依據的治療準則（文字）| 癌別檔必填 |
| `guideline_level` | 1–4（① 原文全文／② 官方摘要／③ 二手解讀／④ 未查證）| 癌別檔必填 |
| `nhi_level` | 1–4，健保給付內容的來源層級 | 選填（C6／C7／C8／C10 = 1）|
| `guideline_note` | 備註 | 選填 |
| `review_status` | `draft`／`pending`（待醫師團隊確認）／`reviewed` | 癌別檔必填 |
| `review_due` | 下次檢視期限 `YYYY-MM-DD`，**過期 build 就失敗** | 癌別檔必填；C0、D2 也有 |

- 欄位名刻意避開 Material 內建的 `status`。
- **C0「治療準則版本對照 → 現況盤點」表由這些欄位在 build 時產生**（`<!-- ccm:guideline-table -->`），改來源層級只改該癌別檔。
- `review_due` 過期＝內容該重看了：重新檢視後把日期往後改，不要只改日期不看內容。
