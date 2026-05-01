# CCM Manual｜癌症個管師指導書

彰濱秀傳癌症中心癌症個案管理師工作資源平台。

**當前版本：V3.0.1**

---

## V3.0.1 更新

- 主色改為 #C9C8C7（淺灰色系）
- sidebar 永久顯示在左側（>= 760px viewport），主內容並排排版，不再 drawer 浮動覆蓋
- 沿用 V2.0.2 那 4 條已驗證的核心 sidebar 規則（V3 平鋪 nav 不需要 V2.0.3 的 5-9 條補丁）

---

## 內容

- **首頁**：四篇導覽
- **工作篇**：日常職責、各癌別照護、表單範本、臨床知識、困難個案處理
- **養成篇**：12 個月分階段培訓、品質改善專案
- **工具篇**：HIS 系統、院內自製工具操作手冊
- **指標篇**：60 項強制申報指標、13 癌別速查

---

## 本地預覽

```bash
pip install -r requirements.txt
mkdocs serve
```

開啟 http://127.0.0.1:8000

---

## 部署

推到 main 分支後，GitHub Actions 自動 build + deploy 到 GitHub Pages。

部署網址：https://Sela1227.github.io/CCM-manual/

---

## 設計原則（V3.0.0 重做）

V3.0.0 是從零開始重做的版本，**完全不延用 V2.x 的任何 CSS override**：

- **5 個平鋪頂層頁面**，nav 沒有任何巢狀結構（V2.x sidebar 標題重複的根源就是巢狀 section，V3 直接從架構上消除）
- **mkdocs-material 預設行為**：在窄螢幕用 drawer 模式（漢堡選單），寬螢幕自動 wide mode，不寫任何 viewport override
- **中文搜尋**：用 jieba 分詞，搜「乳癌篩檢」可以同時找到「乳癌」和「篩檢」
- **手機底部導覽列**：4 個快速切換按鈕，配合自製 JS（不依賴 base.href，從 pathname 推算）

---

## 永久規則

1. **不要把 4 篇主檔再拆成巢狀**——這是 V2.x 出問題的根本原因
2. **toc.integrate 不要用**（V2.x 已踩過兩次）
3. **getSiteRoot() 從 pathname 推算**，不依賴 base.href
4. H 章節維護單位：放射腫瘤科 林伯儒 醫師
5. 內容修改在四份主檔裡做：`docs/01_work.md`、`02_training.md`、`03_tools.md`、`04_metrics.md`
