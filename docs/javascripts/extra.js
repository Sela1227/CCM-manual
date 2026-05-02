/* ======================================================
   彰濱秀傳癌症中心 - 個管師訓練系統 V3.4.15
   - 版本徽章改 inline，注入到 header 站名旁（不再右下角浮動）
   - 手機底部導覽列（V3.4.4 從 4 個改 6 個進階員工常用入口，SVG 圖示）
   - getSiteRoot() 從 window.location.pathname 推算（規則 5）
   ====================================================== */

(function () {
  "use strict";

  var CCM_VERSION = "V3.4.15";

  // ---- 推算 site root（不依賴 base.href）----
  function getSiteRoot() {
    var path = window.location.pathname;
    var m = path.match(/^(\/[^\/]+\/)/);
    return m ? m[1] : "/";
  }

  // ---- SVG 圖示庫（Material Symbols 風格，24×24 viewBox）----
  // V3.4.4 改 6 個進階員工常用入口：首頁 / H1 個管 / H2 MDT / H3 藥物 / G 指標 / F 知識
  var ICONS = {
    home:    '<svg viewBox="0 0 24 24"><path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/></svg>',
    tracker: '<svg viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-2 11h-3v3h-4v-3H7v-4h3V7h4v3h3z"/></svg>',
    mdt:     '<svg viewBox="0 0 24 24"><path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/></svg>',
    drugs:   '<svg viewBox="0 0 24 24"><path d="M4.22 11.29 11.29 4.22a5 5 0 0 1 7.07 7.07l-7.07 7.07a5 5 0 0 1-7.07-7.07zm1.41 1.42a3 3 0 0 0 0 4.24 3 3 0 0 0 4.24 0l3.54-3.53-4.24-4.25z"/></svg>',
    metrics: '<svg viewBox="0 0 24 24"><path d="M3 13h2v-2H3zm0 4h2v-2H3zm0-8h2V7H3zm4 4h14v-2H7zm0 4h14v-2H7zM7 7v2h14V7z"/></svg>',
    kb:      '<svg viewBox="0 0 24 24"><path d="M18 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM6 4h5v8l-2.5-1.5L6 12V4z"/></svg>'
  };

  // ---- 版本徽章注入到 header 站名旁 ----
  function injectVersionBadge() {
    // 先清掉舊的（避免 instant-nav 重複）
    var olds = document.querySelectorAll(".ccm-ver-inline");
    olds.forEach(function (n) { n.remove(); });

    // 找站名 ellipsis（Material 把站名放這）
    var titleEllipsis = document.querySelector(
      ".md-header__title .md-header__topic:first-child .md-ellipsis"
    );
    if (!titleEllipsis) {
      titleEllipsis = document.querySelector(".md-header__title .md-header__topic");
    }
    if (!titleEllipsis) return;

    var badge = document.createElement("span");
    badge.className = "ccm-ver-inline";
    badge.textContent = CCM_VERSION;
    titleEllipsis.appendChild(badge);
  }

  // ---- 手機底部導覽列 ----
  function injectMobileNav() {
    if (document.getElementById("ccm-mobile-nav")) return;

    var root = getSiteRoot();
    var current = window.location.pathname;

    var items = [
      { href: root,                          label: "首頁", icon: ICONS.home,    match: /^\/[^\/]*\/?$|\/index\.html?$/ },
      { href: root + "H1_ccm-tracker-guide/", label: "個管", icon: ICONS.tracker, match: /\/H1_ccm-tracker-guide\// },
      { href: root + "H2_mdt-guide/",        label: "MDT",  icon: ICONS.mdt,     match: /\/H2_mdt-guide\// },
      { href: root + "H3_cancer-drugs/",     label: "藥物", icon: ICONS.drugs,   match: /\/H3_cancer-drugs\/|\/drug-lookup\// },
      { href: root + "G_quality-index/",     label: "指標", icon: ICONS.metrics, match: /\/G_quality-index\// },
      { href: root + "F_clinical-kb/",       label: "知識", icon: ICONS.kb,      match: /\/F_clinical-kb\// }
    ];

    var nav = document.createElement("nav");
    nav.id = "ccm-mobile-nav";

    items.forEach(function (item) {
      var a = document.createElement("a");
      a.href = item.href;
      if (item.match.test(current)) a.className = "active";
      a.innerHTML = item.icon + '<span>' + item.label + '</span>';
      nav.appendChild(a);
    });

    document.body.appendChild(nav);
  }

  function init() {
    injectVersionBadge();
    injectMobileNav();
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

      var nav = document.getElementById("ccm-mobile-nav");
      if (!nav) {
        injectMobileNav();
        return;
      }
      var current = window.location.pathname;
      var links = nav.querySelectorAll("a");
      links.forEach(function (a) {
        var href = a.getAttribute("href");
        var slug = (href.match(/\/([^\/]+)\/?$/) || [])[1] || "";
        if (slug && current.indexOf("/" + slug + "/") >= 0) {
          a.classList.add("active");
        } else if (!slug && current.match(/\/[^\/]*\/?$/)) {
          a.classList.add("active");
        } else {
          a.classList.remove("active");
        }
      });
    });
  }
})();
