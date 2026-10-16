#!/usr/bin/env python3
"""
check_js_runtime.py — UI JS 執行期煙霧測試（規則 6 第五道）

【為什麼有這支】V4.20.0 的 extra.js 有 `root is not defined` ReferenceError，
整支 JS 停掉（版號徽章、SELA、bottom nav 全滅）——但 mkdocs build --strict
不執行 browser JS、node --check 只驗語法 → 四道全綠（坑 #77）。

【做什麼】node + 最小 window/document stub 實際執行 extra.js：
  1. 頂層執行不得 throw（path 缺失會在 injectMobileNav 的 item.path.charAt
     直接炸，被此步抓到——NAV_ITEMS 在 IIFE 內、外部看不到，不做直接屬性檢查）
  2. bottom nav 須注入且恰為 5 鈕
  3. active-state 斷言：多條路徑各執行一次，斷言亮起的鈕正確（見 CASES）。
     歸屬來自 extra.js 的 PAGE_CAT 單一對照表，不再用 URL regex。
  4. 涵蓋率：docs/*.md 每頁都要在 PAGE_CAT 有合法分類（新增頁面忘了登記 → FAIL）

【限制】stub 抓「執行期會炸/邏輯錯」，抓不到視覺問題。上線後人工點五鈕仍不可省。
"""
import json
import subprocess
import sys
from pathlib import Path

JS = Path(__file__).resolve().parent.parent / "docs" / "javascripts" / "extra.js"

HARNESS = r"""
var appended = [];
function El(tag){
  var el = {
    tag: tag, children: [], className: "", innerHTML: "", id: "", _classes: {},
    addEventListener: function(){},
    appendChild: function(c){ this.children.push(c); },
    setAttribute: function(){}, getAttribute: function(){ return null; },
    querySelectorAll: function(){ return this.children; },
  };
  el.classList = {
    add: function(c){ el._classes[c] = true; },
    remove: function(c){ delete el._classes[c]; },
  };
  return el;
}
global.window = { location: { pathname: PATHNAME } };
var navEl = null;
global.document = {
  getElementById: function(id){ return id === "ccm-mobile-nav" ? navEl : null; },
  querySelector: function(){ return null; },
  querySelectorAll: function(){ return []; },
  createElement: function(t){ return El(t); },
  body: { appendChild: function(n){ appended.push(n); if (n.id === "ccm-mobile-nav") navEl = n; } },
  addEventListener: function(ev, fn){ if (ev === "DOMContentLoaded") fn(); },
};
global.document.readyState = "loading";

try {
  require(JS_PATH);
} catch (e) {
  console.log("FAIL_TOPLEVEL: " + e.message);
  process.exit(1);
}

if (!navEl) { console.log("FAIL_NAV: bottom nav not injected"); process.exit(1); }
if (navEl.children.length !== 5) {
  console.log("FAIL_NAV: " + navEl.children.length + " buttons (expect 5)"); process.exit(1);
}
var active = [];
for (var i = 0; i < navEl.children.length; i++) {
  var a = navEl.children[i];
  var m = a.innerHTML.match(/<span>([^<]+)<\/span>/);
  var label = m ? m[1] : ("#" + i);
  if (a._classes["active"] || a.className === "active") active.push(label);
}
console.log("ACTIVE: " + JSON.stringify(active));
console.log("OK");
"""

# 路徑用 project-pages 形態（/repo/…）——getSiteRoot() 以「第一層=repo」推 root，
# 這是本站的實際部署形態（GitHub Pages project site）。根部署（/）非支援情境：
# 根層下 getSiteRoot 會把內容頁第一層誤判為 root（V4.20.2 補 active 測試時發現，
# 屬 stub 假陽性；若未來改根部署，getSiteRoot 與本測試都要改）。
# 期待值 None ＝不亮任何鈕（臨床速查、系統與管理沒有專屬鈕）
CASES = [
    ("/CCM-Manual/", "首頁"),
    ("/CCM-Manual/C6_prostate-cancer/", "癌別"),
    ("/CCM-Manual/hub_learning/", "學習"),
    ("/CCM-Manual/D3_phone-scripts/", "工作"),
    ("/CCM-Manual/H3_cancer-drugs/", None),       # 臨床速查（側欄歸屬），不再誤亮「工作」
    ("/CCM-Manual/H1_ccm-tracker-guide/", None),  # 系統與管理
]

VALID_CATS = {"learn", "daily", "cancer", "lookup", "admin"}


def check_coverage() -> int:
    """docs/ 下每個 md（首頁除外）都要在 PAGE_CAT 登記，且分類合法。"""
    import re
    src = JS.read_text(encoding="utf-8")
    block = src[src.index("var PAGE_CAT = {"):]
    block = block[:block.index("};")]
    mapping = dict(re.findall(r'"([^"]+)":\s*"([^"]+)"', block))
    docs = JS.parent.parent
    slugs = {f.stem for f in docs.glob("*.md") if f.stem != "index"}
    missing = sorted(slugs - mapping.keys())
    stale = sorted(mapping.keys() - slugs)
    bad = sorted(k for k, v in mapping.items() if v not in VALID_CATS)
    if missing or stale or bad:
        if missing: print(f"   🔴 PAGE_CAT 缺分類：{missing}")
        if stale:   print(f"   🔴 PAGE_CAT 有已不存在的頁：{stale}")
        if bad:     print(f"   🔴 分類代碼不合法：{bad}")
        return 1
    print(f"   ✓ PAGE_CAT 涵蓋全部 {len(slugs)} 個 md 頁")
    return 0


def run_case(pathname: str):
    pre = (
        "var JS_PATH = " + json.dumps(str(JS)) + ";\n"
        "var PATHNAME = " + json.dumps(pathname) + ";\n"
    )
    r = subprocess.run(["node", "-e", pre + HARNESS], capture_output=True, text=True)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def main() -> int:
    print(f"📱 UI JS 執行期檢查（stub DOM × {len(CASES)} 路徑 + 分類對照表涵蓋率）")
    if check_coverage():
        print("🔴 導航分類對照表與 docs/ 不一致——新增或改名頁面時要同步 extra.js 的 PAGE_CAT")
        return 1
    for pathname, expect in CASES:
        code, out = run_case(pathname)
        if code != 0 or "OK" not in out:
            print(f"   🔴 {pathname}")
            for line in out.strip().splitlines():
                print("      " + line)
            print("🔴 extra.js 執行期失敗——strict 與 node --check 都抓不到的層（坑 #77）")
            return 1
        m = [l for l in out.splitlines() if l.startswith("ACTIVE: ")]
        active = json.loads(m[0][8:]) if m else []
        want = [expect] if expect else []
        if active != want:
            print(f"   🔴 {pathname} → active {active}（應為 {want}）")
            print("🔴 active-state 錯誤——match regex 與路徑對不上（H[1-4] 類回歸）")
            return 1
        print(f"   ✓ {pathname:34} → {expect or '（不亮）'}")
    print("✓ extra.js 頂層執行、bottom nav 5 鈕、active-state、分類涵蓋率全部正常")
    return 0


if __name__ == "__main__":
    sys.exit(main())
