/* ======================================================
   癌症個管師指導書 V3.2.0
   - 版本徽章 + 手機底部導覽列（SVG 圖示，無 emoji）
   - getSiteRoot() 從 window.location.pathname 推算（坑 #4/#13/規則 5）
   ====================================================== */

(function () {
  "use strict";

  var CCM_VERSION = "V3.2.0";

  // ---- 推算 site root（不依賴 base.href）----
  function getSiteRoot() {
    var path = window.location.pathname;
    var m = path.match(/^(\/[^\/]+\/)/);
    return m ? m[1] : "/";
  }

  // ---- SVG 圖示庫（Material Symbols 風格，24×24 viewBox）----
  // 全部用 path，無 emoji，無外部依賴
  var ICONS = {
    home:    '<svg viewBox="0 0 24 24"><path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/></svg>',
    work:    '<svg viewBox="0 0 24 24"><path d="M19 3h-4.18C14.4 1.84 13.3 1 12 1c-1.3 0-2.4.84-2.82 2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 0c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zm2 14H7v-2h7zm3-4H7v-2h10zm0-4H7V7h10z"/></svg>',
    his:     '<svg viewBox="0 0 24 24"><path d="M20 18c1.1 0 1.99-.9 1.99-2L22 6c0-1.1-.9-2-2-2H4c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2H0v2h24v-2zM4 6h16v10H4z"/></svg>',
    metrics: '<svg viewBox="0 0 24 24"><path d="M3 13h2v-2H3zm0 4h2v-2H3zm0-8h2V7H3zm4 4h14v-2H7zm0 4h14v-2H7zM7 7v2h14V7z"/></svg>'
  };

  // ---- 版本徽章 ----
  function injectVersionBadge() {
    if (document.getElementById("ccm-ver")) return;
    var el = document.createElement("div");
    el.id = "ccm-ver";
    el.textContent = CCM_VERSION;
    document.body.appendChild(el);
  }

  // ---- 手機底部導覽列（4 個常用入口）----
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

  // ---- DOM 就緒就跑 ----
  function init() {
    injectVersionBadge();
    injectMobileNav();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  // 處理 instant navigation
  if (typeof document$ !== "undefined" && document$.subscribe) {
    document$.subscribe(function () {
      var nav = document.getElementById("ccm-mobile-nav");
      if (!nav) {
        init();
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
