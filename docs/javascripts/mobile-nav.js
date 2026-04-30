/* ============================================================
   手機底部導覽列
   只在 ≤ 960px 視窗顯示
   ============================================================ */

(function () {
  // 導覽項目定義
  const NAV_ITEMS = [
    { icon: "🏠", label: "首頁",   href: "/CCM-manual/" },
    { icon: "📋", label: "新人通則", href: "/CCM-manual/A_work-guide/" },
    { icon: "🏥", label: "癌別指引", href: "/CCM-manual/C1_lung-cancer/" },
    { icon: "💻", label: "軟體操作", href: "/CCM-manual/H1_ccm-tracker-guide/" },
    { icon: "📊", label: "品質指標", href: "/CCM-manual/G_quality-index/" },
  ];

  const MOBILE_BREAKPOINT = 960; // px

  function isMobile() {
    return window.innerWidth <= MOBILE_BREAKPOINT;
  }

  function getCurrentPath() {
    return window.location.pathname;
  }

  function isActive(href) {
    const path = getCurrentPath();
    // 首頁只精確比對
    if (href.endsWith("/CCM-manual/")) {
      return path === href || path === "/CCM-manual/index.html";
    }
    return path.startsWith(href.replace(/\/$/, ""));
  }

  function buildNav() {
    const existing = document.getElementById("ccm-bottom-nav");
    if (existing) existing.remove();

    if (!isMobile()) return;

    const nav = document.createElement("nav");
    nav.id = "ccm-bottom-nav";
    nav.setAttribute("aria-label", "底部導覽");

    NAV_ITEMS.forEach(item => {
      const a = document.createElement("a");
      a.href = item.href;
      a.className = "ccm-nav-item" + (isActive(item.href) ? " ccm-nav-active" : "");
      a.innerHTML = `<span class="ccm-nav-icon">${item.icon}</span><span class="ccm-nav-label">${item.label}</span>`;
      nav.appendChild(a);
    });

    document.body.appendChild(nav);
  }

  // 初次建立
  document.addEventListener("DOMContentLoaded", buildNav);

  // MkDocs instant navigation — 每次換頁重建
  document.addEventListener("DOMContentSwitch", buildNav);

  // 視窗大小改變時重建
  let resizeTimer;
  window.addEventListener("resize", function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(buildNav, 150);
  });
})();
