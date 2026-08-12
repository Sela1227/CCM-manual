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
  3. active-state 斷言（V4.20.2 補，審稿指出 H[1-4] 修正沒被驗到）：
     4 條路徑各執行一次，斷言亮起的鈕正確——
       /                    → 首頁
       /H3_cancer-drugs/    → 工作（H[124]→H[1-4] 回歸測試）
       /C6_prostate-cancer/ → 癌別
       /hub_learning/       → 學習

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
CASES = [
    ("/CCM-Manual/", "首頁"),
    ("/CCM-Manual/H3_cancer-drugs/", "工作"),      # H[124] → H[1-4] 回歸測試
    ("/CCM-Manual/C6_prostate-cancer/", "癌別"),
    ("/CCM-Manual/hub_learning/", "學習"),
]


def run_case(pathname: str):
    pre = (
        "var JS_PATH = " + json.dumps(str(JS)) + ";\n"
        "var PATHNAME = " + json.dumps(pathname) + ";\n"
    )
    r = subprocess.run(["node", "-e", pre + HARNESS], capture_output=True, text=True)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def main() -> int:
    print("📱 UI JS 執行期檢查（stub DOM × 4 路徑）")
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
        if active != [expect]:
            print(f"   🔴 {pathname} → active {active}（應為 ['{expect}']）")
            print("🔴 active-state 錯誤——match regex 與路徑對不上（H[1-4] 類回歸）")
            return 1
        print(f"   ✓ {pathname:26} → {expect}")
    print("✓ extra.js 頂層執行、bottom nav 5 鈕、4 路徑 active-state 全部正常")
    return 0


if __name__ == "__main__":
    sys.exit(main())
