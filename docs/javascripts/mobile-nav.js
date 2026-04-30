/* ============================================================
   手機底部導覽列 — 動態偵測 base URL
   ============================================================ */
(function () {
  var NAV_ITEMS = [
    { icon: "🏠", label: "首頁",    path: "" },
    { icon: "📋", label: "新人通則", path: "A_work-guide/" },
    { icon: "🏥", label: "癌別指引", path: "C1_lung-cancer/" },
    { icon: "💻", label: "軟體操作", path: "H1_ccm-tracker-guide/" },
    { icon: "📊", label: "品質指標", path: "G_quality-index/" },
  ];

  function getBase() {
    /* MkDocs Material 會在 <head> 產生 <base href="...">
       baseURI 就是這個值，例如 https://sela1227.github.io/CCM-manual/ */
    return document.baseURI.replace(/[^/]*$/, "");
  }

  function buildNav() {
    var old = document.getElementById("ccm-bottom-nav");
    if (old) old.remove();

    var nav = document.createElement("nav");
    nav.id = "ccm-bottom-nav";
    nav.setAttribute("aria-label", "底部快速導覽");

    var base = getBase();
    var cur  = window.location.pathname;

    NAV_ITEMS.forEach(function (item) {
      var href = base + item.path;
      var targetPath = new URL(href, window.location.origin).pathname;

      var active = item.path === ""
        ? (cur === targetPath || cur === targetPath + "index.html")
        : cur.indexOf(item.path.replace(/\/$/, "")) !== -1;

      var a = document.createElement("a");
      a.href = href;
      a.className = "ccm-nav-item" + (active ? " ccm-nav-active" : "");
      a.innerHTML =
        '<span class="ccm-nav-icon">' + item.icon + "</span>" +
        '<span class="ccm-nav-label">' + item.label + "</span>";
      nav.appendChild(a);
    });

    document.body.appendChild(nav);
  }

  /* 策略 1：DOM 準備好就執行 */
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", buildNav);
  } else {
    buildNav();
  }

  /* 策略 2：MkDocs Material instant navigation observable */
  if (typeof document$ !== "undefined") {
    document$.subscribe(buildNav);
  }

  /* 策略 3：保險用 — 頁面完全載入後再執行一次 */
  window.addEventListener("load", buildNav);

  /* 策略 4：MkDocs 自訂事件（部分版本） */
  document.addEventListener("DOMContentSwitch", buildNav);

  /* resize */
  var resizeTimer;
  window.addEventListener("resize", function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(buildNav, 150);
  });
})();
