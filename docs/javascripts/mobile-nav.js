/* ============================================================
   彰濱秀傳 個管師指導書
   ① 版本徽章注入 header
   ② 手機底部導覽列
   V1.7.0
   ============================================================ */

var CCM_VERSION = "V1.8.6";

/* ── 版本徽章 ─────────────────────────────────────────── */
function injectVersionBadge() {
  var old = document.getElementById("ccm-ver");
  if (old) old.remove();

  var header = document.querySelector(".md-header__inner");
  if (!header) return;

  var badge = document.createElement("span");
  badge.id          = "ccm-ver";
  badge.textContent = CCM_VERSION;
  header.appendChild(badge);
}

/* ── 手機底部導覽列 ────────────────────────────────────── */
var NAV = [
  { icon: "🏠", label: "首頁",    path: "" },
  { icon: "📋", label: "新人通則", path: "A_work-guide/" },
  { icon: "🏥", label: "癌別指引", path: "C1_lung-cancer/" },
  { icon: "💻", label: "軟體操作", path: "H1_ccm-tracker-guide/" },
  { icon: "📊", label: "品質指標", path: "G_quality-index/" },
];

function getSiteRoot() {
  var el = document.querySelector("base[href]");
  return el ? el.href : window.location.origin + "/";
}

function buildBottomNav() {
  var old = document.getElementById("ccm-bnav");
  if (old) old.remove();

  var nav  = document.createElement("nav");
  nav.id   = "ccm-bnav";
  nav.setAttribute("aria-label", "快速導覽");

  var root = getSiteRoot();
  var cur  = window.location.pathname;

  NAV.forEach(function (item) {
    var href   = root + item.path;
    var target = new URL(href, window.location.origin).pathname;
    var active = item.path === ""
      ? (cur === target || cur === target + "index.html")
      : cur.indexOf(item.path.replace(/\/$/, "")) !== -1;

    var a       = document.createElement("a");
    a.href      = href;
    a.className = "ccm-ni" + (active ? " ccm-na" : "");
    a.innerHTML =
      '<span class="ccm-ii">' + item.icon + "</span>" +
      '<span class="ccm-il">' + item.label + "</span>";
    nav.appendChild(a);
  });

  document.body.appendChild(nav);
}

/* ── 統一初始化 ────────────────────────────────────────── */
function init() {
  injectVersionBadge();
  buildBottomNav();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init);
} else {
  init();
}

/* MkDocs Material instant navigation */
if (typeof document$ !== "undefined") { document$.subscribe(init); }
window.addEventListener("load", init);
document.addEventListener("DOMContentSwitch", init);

var resizeT;
window.addEventListener("resize", function () {
  clearTimeout(resizeT); resizeT = setTimeout(buildBottomNav, 150);
});
