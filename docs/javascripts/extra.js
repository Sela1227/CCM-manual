/* ======================================================
   彰濱秀傳癌症中心 - 個管師訓練系統 V3.4.1
   - 版本徽章改 inline，注入到 header 站名旁（不再右下角浮動）
   - 手機底部導覽列（SVG 圖示，無 emoji）
   - getSiteRoot() 從 window.location.pathname 推算（規則 5）
   ====================================================== */

(function () {
  "use strict";

  var CCM_VERSION = "V3.4.1";

  // ---- 推算 site root（不依賴 base.href）----
  function getSiteRoot() {
    var path = window.location.pathname;
    var m = path.match(/^(\/[^\/]+\/)/);
    return m ? m[1] : "/";
  }

  // ---- SVG 圖示庫（Material Symbols 風格，24×24 viewBox）----
  var ICONS = {
    home:    '<svg viewBox="0 0 24 24"><path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/></svg>',
    work:    '<svg viewBox="0 0 24 24"><path d="M19 3h-4.18C14.4 1.84 13.3 1 12 1c-1.3 0-2.4.84-2.82 2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 0c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zm2 14H7v-2h7zm3-4H7v-2h10zm0-4H7V7h10z"/></svg>',
    his:     '<svg viewBox="0 0 24 24"><path d="M20 18c1.1 0 1.99-.9 1.99-2L22 6c0-1.1-.9-2-2-2H4c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2H0v2h24v-2zM4 6h16v10H4z"/></svg>',
    metrics: '<svg viewBox="0 0 24 24"><path d="M3 13h2v-2H3zm0 4h2v-2H3zm0-8h2V7H3zm4 4h14v-2H7zm0 4h14v-2H7zM7 7v2h14V7z"/></svg>'
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
      { href: root,                       label: "首頁", icon: ICONS.home,    match: /^\/[^\/]*\/?$|\/index\.html?$/ },
      { href: root + "A_work-guide/",     label: "工作", icon: ICONS.work,    match: /\/A_work-guide\// },
      { href: root + "B1_HIS-manual/",    label: "HIS",  icon: ICONS.his,     match: /\/B1_HIS-manual\// },
      { href: root + "G_quality-index/",  label: "指標", icon: ICONS.metrics, match: /\/G_quality-index\// }
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
