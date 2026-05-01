/* ============================================================
   彰濱秀傳 個管師指導書
   ① 版本徽章注入 header
   ② 手機底部導覽列
   V1.9.8
   ============================================================ */

var CCM_VERSION = "V1.9.8";

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
  { icon: "💻", label: "專用軟體", path: "H1_ccm-tracker-guide/" },
  { icon: "📊", label: "品質指標", path: "G_quality-index/" },
];

/*
 * getSiteRoot()
 *
 * 從 window.location.pathname 推算網站根目錄。
 * 不依賴 <base href>，避免 Android Chrome + MkDocs instant navigation
 * 下 base.href 解析成目前頁面路徑導致路徑疊加（坑 #4、#13）。
 *
 * GitHub Pages 路徑結構：
 *   根頁面：/CCM-manual/
 *   子頁面：/CCM-manual/{pagename}/
 *   → 所有頁面最多兩層，root 永遠是第一層
 */
function getSiteRoot() {
  var loc      = window.location;
  var pathname = loc.pathname;

  // 拆 path，過濾空字串（去除首尾 "/"）
  var segs = pathname.split("/").filter(function (s) { return s !== ""; });
  // 若最後一段是 index.html，移除
  if (segs.length && segs[segs.length - 1] === "index.html") segs.pop();

  // 判斷深度
  // 根頁面：segs = ["CCM-manual"]
  // 子頁面：segs = ["CCM-manual", "G_quality-index"]
  if (segs.length <= 1) {
    // 已在根層
    return loc.origin + "/" + (segs[0] ? segs[0] + "/" : "");
  } else {
    // 取前 N-1 層（對我們的站來說就是第一層）
    return loc.origin + "/" + segs.slice(0, segs.length - 1).join("/") + "/";
  }
}

function buildBottomNav() {
  var old = document.getElementById("ccm-bnav");
  if (old) old.remove();

  var nav = document.createElement("nav");
  nav.id  = "ccm-bnav";
  nav.setAttribute("aria-label", "快速導覽");

  var root = getSiteRoot();
  var cur  = window.location.pathname;

  NAV.forEach(function (item) {
    var href   = root + item.path;
    var active = item.path === ""
      ? (cur === new URL(href).pathname || cur === new URL(href).pathname + "index.html")
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
