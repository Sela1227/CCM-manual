# 彰濱秀傳癌症中心 — 個管師教育訓練指導書

> 彰濱秀傳癌症中心個案管理師工作手冊、培訓資源與專用軟體操作說明

**當前版本：V1.9.8**

---

## 網站

部署於 GitHub Pages：

```
https://sela1227.github.io/CCM-manual/
```

---

## 內容架構

| 章節 | 內容 |
|------|------|
| A｜新人通則 | 工作指導手冊、四階段培訓計畫書 |
| B｜軟體操作 | HIS 子系統、癌症中心五大自建系統 |
| C｜各癌別照護指引 | 肺癌、乳癌、其他癌別照護要點 |
| D｜表單與範本 | 評估表單、追蹤腳本、書信範本 |
| E｜專題與進階 | 困難個案、安寧銜接、品質改善 |
| F｜臨床知識庫 | 常用臨床知識快速查詢 |
| G｜品質指標 | 國健署 115 年 60 項強制申報指標 |
| H｜專用軟體 | 個管追蹤系統、MDT 會議系統、抗癌藥物速查 |

---

## 專案結構

```
CCM-manual/
├── README.md
├── CLAUDE.md                        ← AI 接手工作上下文
├── mkdocs.yml                       ← 網站設定
├── requirements.txt                 ← Python 套件
├── .github/
│   └── workflows/
│       └── deploy.yml               ← 自動部署到 GitHub Pages
└── docs/
    ├── index.md                     ← 首頁
    ├── stylesheets/extra.css        ← 自訂樣式
    ├── javascripts/mobile-nav.js   ← 手機底部導覽列 + 版本徽章
    ├── drug-lookup/index.html       ← 抗癌藥物速查系統（獨立 HTML）
    ├── A_work-guide.md
    ├── A_training-plan.md
    ├── B1_HIS-manual.md
    ├── B2_other-tools.md
    ├── C1_lung-cancer.md
    ├── C2_breast-cancer.md
    ├── C3-C6_other-cancers.md
    ├── D_forms.md
    ├── E_advanced.md
    ├── F_clinical-kb.md
    ├── G_quality-index.md
    ├── H1_ccm-tracker-guide.md
    ├── H2_mdt-guide.md
    └── H3_cancer-drugs.md
```

---

## 更新內容

更新 MD 檔後推送到 main，GitHub Actions 自動重建網站（約 1-2 分鐘）。

更新版本號時需同步修改：
1. `docs/javascripts/mobile-nav.js` 的 `CCM_VERSION`
2. `docs/stylesheets/extra.css` 頂部版本說明
3. `README.md` 頂部「當前版本」
4. ZIP 打包名稱 `CCM Manual V{版本號}.zip`
5. `CLAUDE.md` 版本歷程

---

## 技術

- [MkDocs](https://www.mkdocs.org/) + [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- GitHub Pages（私有 Repo + GitHub Pro）
- GitHub Actions 自動部署
- Jieba 中文斷詞（搜尋優化）
