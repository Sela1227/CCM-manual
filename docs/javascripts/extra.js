/* ======================================================
   癌症個管師指導書 V3.0.0
   版本徽章 + 手機底部導覽列
   ====================================================== */

(function () {
  "use strict";

  // 版本號（單一來源；CSS、README、CLAUDE.md 各自記錄即可）
  var CCM_VERSION = "V3.1.0";

  // ---- 推算 site root（不依賴 base.href，從 pathname 推）----
  function getSiteRoot() {
    // 例如 /CCM-manual/01_work/ -> /CCM-manual/
    // 例如 /CCM-manual/         -> /CCM-manual/
    var path = window.location.pathname;
    // 找出第一段資料夾（GitHub Pages 的 repo 名）
    var m = path.match(/^(\/[^\/]+\/)/);
    if (m) {
      // 但如果是 user/org page (https://x.github.io/)，第一段就是頁面，要回 "/"
      // 用一個簡單的偵測：如果 hostname 是 *.github.io，且 path 第一段不是 'tags' 之類預期路徑，就用 m[1]
      // 實務上 CCM-manual 是 project page，肯定有 repo 名，所以這條 OK
      return m[1];
    }
    return "/";
  }

  // ---- 版本徽章 ----
  function injectVersionBadge() {
    if (document.getElementById("ccm-ver")) return;
    var el = document.createElement("div");
    el.id = "ccm-ver";
    el.textContent = CCM_VERSION;
    document.body.appendChild(el);
  }

  // ---- 手機底部導覽列 ----
  function injectMobileNav() {
    if (document.getElementById("ccm-mobile-nav")) return;

    var root = getSiteRoot();
    var current = window.location.pathname;

    var items = [
      { href: root,                          label: "首頁", icon: "🏠", match: /^\/[^\/]*\/?$|\/index\.html?$/ },
      { href: root + "A_work-guide/",        label: "工作", icon: "📋", match: /\/A_work-guide\// },
      { href: root + "B1_HIS-manual/",       label: "HIS",  icon: "💻", match: /\/B1_HIS-manual\// },
      { href: root + "G_quality-index/",     label: "指標", icon: "📊", match: /\/G_quality-index\// }
    ];

    var nav = document.createElement("nav");
    nav.id = "ccm-mobile-nav";

    items.forEach(function (item) {
      var a = document.createElement("a");
      a.href = item.href;
      if (item.match.test(current)) a.className = "active";
      a.innerHTML =
        '<span class="ccm-icon">' + item.icon + "</span>" +
        '<span class="ccm-label">' + item.label + "</span>";
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

  // 處理 instant navigation（Material 的 navigation.instant 即使沒開也保險加）
  if (typeof document$ !== "undefined" && document$.subscribe) {
    document$.subscribe(function () {
      // 重新計算 active 狀態
      var nav = document.getElementById("ccm-mobile-nav");
      if (!nav) {
        init();
        return;
      }
      var current = window.location.pathname;
      var links = nav.querySelectorAll("a");
      links.forEach(function (a) {
        var href = a.getAttribute("href");
        // 簡化判定：href 跟 current 是否包含對應 slug
        var slug = (href.match(/\/([^\/]+)\/?$/) || [])[1] || "";
        if (slug && current.indexOf("/" + slug + "/") >= 0) {
          a.classList.add("active");
        } else if (!slug && current.match(/\/[^\/]*\/?$/)) {
          // 首頁
          a.classList.add("active");
        } else {
          a.classList.remove("active");
        }
      });
    });
  }
})();
