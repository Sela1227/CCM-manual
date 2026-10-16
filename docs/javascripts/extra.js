/* ======================================================
   彰濱秀傳癌症中心 - 個管師訓練系統 V4.22.0
   - 版本號 footer + header 雙處顯示（SPEC §10.6 UI 版號鐵律）
   - 手機底部導覽列（首頁／學習／工作／癌別／搜尋，SVG 圖示）
   - 單一導航分類對照表 PAGE_CAT + 麵包屑（底部導覽與麵包屑共用）
   - getSiteRoot() 從 window.location.pathname 推算（規則 5）
   ====================================================== */

(function () {
  "use strict";

  var CCM_VERSION = "V4.22.0";

  // ---- 推算 site root（不依賴 base.href）----
  function getSiteRoot() {
    var path = window.location.pathname;
    var m = path.match(/^(\/[^\/]+\/)/);
    return m ? m[1] : "/";
  }

  // ---- SVG 圖示庫（Material Symbols 風格，24×24 viewBox）----
  // 現行：5 個一級分類（首頁/學習/工作/癌別/搜尋）
  var ICONS = {
    search: '<svg viewBox="0 0 24 24"><path d="M15.5 14h-.79l-.28-.27a6.5 6.5 0 1 0-.7.7l.27.28v.79l5 4.99L20.49 19zm-6 0A4.5 4.5 0 1 1 14 9.5 4.5 4.5 0 0 1 9.5 14z"/></svg>',
    home:    '<svg viewBox="0 0 24 24"><path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/></svg>',
    tracker: '<svg viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-2 11h-3v3h-4v-3H7v-4h3V7h4v3h3z"/></svg>',
    mdt:     '<svg viewBox="0 0 24 24"><path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/></svg>',
    drugs:   '<svg viewBox="0 0 24 24"><path d="M4.22 11.29 11.29 4.22a5 5 0 0 1 7.07 7.07l-7.07 7.07a5 5 0 0 1-7.07-7.07zm1.41 1.42a3 3 0 0 0 0 4.24 3 3 0 0 0 4.24 0l3.54-3.53-4.24-4.25z"/></svg>',
    metrics: '<svg viewBox="0 0 24 24"><path d="M3 13h2v-2H3zm0 4h2v-2H3zm0-8h2V7H3zm4 4h14v-2H7zm0 4h14v-2H7zM7 7v2h14V7z"/></svg>',
    kb:      '<svg viewBox="0 0 24 24"><path d="M18 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM6 4h5v8l-2.5-1.5L6 12V4z"/></svg>'
  };

  // ---- 版本徽章注入到 footer 右下角 ----
  function injectVersionBadge() {
    // 先清掉舊的（避免 instant-nav 重複）
    var olds = document.querySelectorAll(".ccm-ver-footer");
    olds.forEach(function (n) { n.remove(); });

    var badge = document.createElement("div");
    badge.className = "ccm-ver-footer";
    badge.textContent = CCM_VERSION;
    document.body.appendChild(badge);
  }

  // ---- header 版號注入到站名右側（SPEC §10.6 UI 版號鐵律、footer + header 雙包）----
  function injectHeaderVersion() {
    var olds = document.querySelectorAll(".ccm-ver-inline");
    olds.forEach(function (n) { n.remove(); });

    // Material Theme header 站名容器（優先 .md-header__topic 首個 .md-ellipsis）
    var host = document.querySelector(".md-header__title .md-header__topic:first-child .md-ellipsis");
    if (!host) host = document.querySelector(".md-header__title .md-ellipsis");
    if (!host) return;

    var tag = document.createElement("span");
    tag.className = "ccm-ver-inline";
    tag.textContent = CCM_VERSION;
    tag.title = "目前版本 " + CCM_VERSION;
    host.appendChild(tag);
  }

  // ---- SELA 歸屬印記注入（Kit V1.21.0 雙軌 logo 系統、本版加入）----
  function injectSelaCredit() {
    var olds = document.querySelectorAll(".ccm-sela-credit");
    olds.forEach(function (n) { n.remove(); });

    var credit = document.createElement("a");
    credit.className = "ccm-sela-credit";
    credit.href = "https://github.com/Sela1227";
    credit.target = "_blank";
    credit.rel = "noopener";
    credit.title = "本系統由 SELA 維護";
    credit.innerHTML = '<img src="' + getSiteRoot() + 'assets/sela-logo/sela.svg" alt="SELA"/>by SELA';
    document.body.appendChild(credit);
  }

  // ---- 搜尋觸發（UI/IA 改版加入：首頁搜尋框 + 底部「搜尋」鈕共用）----
  window.ccmOpenSearch = function () {
    var cb = document.getElementById("__search");      // Material 手機搜尋 overlay 開關
    if (cb) cb.checked = true;
    var inp = document.querySelector(".md-search__input");
    if (inp) setTimeout(function () { inp.focus(); }, 60);
  };

  // ---- 單一導航分類對照表（外部審核 P1：側欄、底部導覽、麵包屑共用同一套分類）----
  // 鍵＝頁面 slug（docs/ 下的檔名去 .md）。歸屬以這張表為準，不靠 URL regex 猜。
  // 新增 docs/*.md 時必須在這裡登記——tools/check_js_runtime.py 會檢查全部 md 都有分類。
  var CATS = {
    learn:  { label: "學習中心",   hub: "hub_learning/" },
    daily:  { label: "日常工作",   hub: "hub_daily/" },
    cancer: { label: "癌別照護",   hub: "hub_cancer/" },
    lookup: { label: "臨床速查",   hub: "hub_lookup/" },
    admin:  { label: "系統與管理", hub: "hub_admin/" }
  };
  var PAGE_CAT = {
    "hub_learning": "learn", "A_work-guide": "learn", "A_training-plan": "learn",
    "hub_daily": "daily", "D_forms": "daily", "D2_education": "daily",
    "D3_phone-scripts": "daily", "D4_letters": "daily", "E_advanced": "daily",
    "hub_cancer": "cancer", "C0_general": "cancer", "C1_lung-cancer": "cancer",
    "C2_breast-cancer": "cancer", "C3_colorectal-cancer": "cancer", "C4_liver-cancer": "cancer",
    "C5_head-neck-cancer": "cancer", "C6_prostate-cancer": "cancer", "C7_esophageal-cancer": "cancer",
    "C8_gastric-cancer": "cancer", "C9_biliary-pancreatic-cancer": "cancer",
    "C10_urological-cancer": "cancer", "C11_gynecologic-cancer": "cancer",
    "C12_hematologic-cancer": "cancer", "C13_other-cancers": "cancer",
    "hub_lookup": "lookup", "D1_assessment-tools": "lookup", "F_clinical-kb": "lookup",
    "F1_lab": "lookup", "F2_pathology": "lookup", "F3_imaging": "lookup",
    "F4_treatment": "lookup", "F5_followup": "lookup", "H3_cancer-drugs": "lookup",
    "hub_admin": "admin", "A3_team": "admin", "B1_HIS-manual": "admin", "B2_other-tools": "admin",
    "H1_ccm-tracker-guide": "admin", "H2_mdt-guide": "admin", "H4_peer-review-guide": "admin",
    "G_quality-index": "admin", "G2_114-quality-report": "admin"
  };

  // 目前頁面 slug（/repo/C6_prostate-cancer/ → "C6_prostate-cancer"；首頁 → ""）
  function currentSlug() {
    var rest = window.location.pathname.slice(getSiteRoot().length);
    rest = rest.replace(/index\.html$/, "").replace(/\/$/, "");
    return rest.split("/")[0] || "";
  }

  // 底部導覽：臨床速查、系統與管理沒有專屬鈕，這兩類頁面不亮任何鈕（麵包屑會標出所在分類）
  var NAV_ITEMS = [
    { path: "",              label: "首頁", icon: ICONS.home,    isHome: true },
    { path: "hub_learning/", label: "學習", icon: ICONS.kb,      cat: "learn" },
    { path: "hub_daily/",    label: "工作", icon: ICONS.tracker, cat: "daily" },
    { path: "hub_cancer/",   label: "癌別", icon: ICONS.mdt,     cat: "cancer" },
    { path: "#ccm-search",   label: "搜尋", icon: ICONS.search,  onclick: true }
  ];

  // ---- 麵包屑：深層頁頂端顯示「首頁 › 所在分類」，可點回上層 ----
  function injectBreadcrumb() {
    document.querySelectorAll(".ccm-crumb").forEach(function (n) { n.remove(); });
    var slug = currentSlug();
    if (!slug || slug.indexOf("hub_") === 0) return;      // 首頁與 hub 本身不需要
    var cat = CATS[PAGE_CAT[slug]];
    var host = document.querySelector(".md-content__inner");
    if (!cat || !host) return;
    var root = getSiteRoot();
    var nav = document.createElement("nav");
    nav.className = "ccm-crumb";
    nav.setAttribute("aria-label", "所在位置");
    nav.innerHTML = '<a href="' + root + '">首頁</a><span aria-hidden="true">›</span>' +
                    '<a href="' + root + cat.hub + '">' + cat.label + '</a>';
    host.insertBefore(nav, host.firstChild);
  }

  function setMobileNavActive() {
    var nav = document.getElementById("ccm-mobile-nav");
    if (!nav) return;
    var root = getSiteRoot();
    var current = window.location.pathname;
    var slug = currentSlug();
    nav.querySelectorAll("a").forEach(function (a, idx) {
      var item = NAV_ITEMS[idx];
      var on = false;
      if (item) {
        if (item.isHome) on = (current === root || current === root + "index.html");
        else if (item.cat) on = (PAGE_CAT[slug] === item.cat);
      }
      if (on) a.classList.add("active");
      else a.classList.remove("active");
    });
  }

  // ---- 手機底部導覽列 ----
  function injectMobileNav() {
    if (document.getElementById("ccm-mobile-nav")) return;

    var root = getSiteRoot();

    var nav = document.createElement("nav");
    nav.id = "ccm-mobile-nav";

    NAV_ITEMS.forEach(function (item) {
      var a = document.createElement("a");
      a.href = item.path.charAt(0) === "#" ? item.path : root + item.path;
      if (item.onclick) {
        a.addEventListener("click", function (e) { e.preventDefault(); window.ccmOpenSearch(); });
      }
      a.innerHTML = item.icon + '<span>' + item.label + '</span>';
      nav.appendChild(a);
    });

    document.body.appendChild(nav);
    setMobileNavActive();
  }

  function init() {
    injectVersionBadge();
    injectHeaderVersion();
    injectSelaCredit();
    injectMobileNav();
    injectBreadcrumb();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  // 處理 instant navigation（站名會被重建，badge 要重新插入）
  if (typeof document$ !== "undefined" && document$.subscribe) {
    document$.subscribe(function () {
      injectVersionBadge();
      injectHeaderVersion();
      injectSelaCredit();
      injectBreadcrumb();

      var nav = document.getElementById("ccm-mobile-nav");
      if (!nav) {
        injectMobileNav();
        return;
      }
      setMobileNavActive();
    });
  }
})();
