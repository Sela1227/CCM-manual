/* ============================================================
   手機底部導覽列 V1.4.0
   修正：用 <base> tag 取得網站根目錄，避免子頁路徑疊加
   ============================================================ */
(function () {
  var NAV = [
    { icon: "🏠", label: "首頁",    path: "" },
    { icon: "📋", label: "新人通則", path: "A_work-guide/" },
    { icon: "🏥", label: "癌別指引", path: "C1_lung-cancer/" },
    { icon: "💻", label: "軟體操作", path: "H1_ccm-tracker-guide/" },
    { icon: "📊", label: "品質指標", path: "G_quality-index/" },
  ];

  /* MkDocs Material 在每頁 <head> 注入 <base href="../../"> 之類的相對路徑
     瀏覽器解析後 .href 就是網站根目錄的絕對 URL
     例：https://sela1227.github.io/CCM-manual/                         */
  function getSiteRoot() {
    var el = document.querySelector("base[href]");
    if (el) return el.href;                       // 正確：網站根目錄
    return window.location.origin + "/";          // fallback
  }

  function curPath() { return window.location.pathname; }

  function isActive(siteRoot, path) {
    var target = new URL(siteRoot + path).pathname;
    var cur    = curPath();
    if (path === "") {
      return cur === target || cur === target + "index.html";
    }
    return cur.indexOf(path.replace(/\/$/, "")) !== -1;
  }

  function build() {
    var old = document.getElementById("ccm-bnav");
    if (old) old.remove();

    var nav  = document.createElement("nav");
    nav.id   = "ccm-bnav";
    nav.setAttribute("aria-label", "快速導覽");

    var root = getSiteRoot();

    NAV.forEach(function (item) {
      var a       = document.createElement("a");
      a.href      = root + item.path;
      a.className = "ccm-ni" + (isActive(root, item.path) ? " ccm-na" : "");
      a.innerHTML =
        '<span class="ccm-ii">' + item.icon + "</span>" +
        '<span class="ccm-il">' + item.label + "</span>";
      nav.appendChild(a);
    });

    document.body.appendChild(nav);
  }

  /* 四重初始化保險 */
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", build);
  } else {
    build();
  }
  if (typeof document$ !== "undefined") { document$.subscribe(build); }
  window.addEventListener("load", build);
  document.addEventListener("DOMContentSwitch", build);

  var t;
  window.addEventListener("resize", function () {
    clearTimeout(t); t = setTimeout(build, 150);
  });
})();
