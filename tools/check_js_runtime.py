#!/usr/bin/env python3
"""
check_js_runtime.py — UI JS 執行期煙霧測試（規則 6 第五道）

【為什麼有這支】V4.20.0 的 extra.js 有一個 `root is not defined` 的 ReferenceError，
整支 JS 停掉（版號徽章、SELA 印記、bottom nav 全部不會出現）——
但四道煙霧測試全綠：
  - mkdocs build --strict 不執行 browser JavaScript
  - node --check 只驗語法，ReferenceError 是執行期錯誤
坑 #77：「語法檢查 ≠ 執行檢查」。UI JS 至少要用 stub DOM 實際執行一次頂層。

【做什麼】用 node + 最小 window/document stub 執行 docs/javascripts/extra.js：
  1. 頂層執行不得 throw
  2. 執行後 NAV_ITEMS 每個 item 都要有 path 屬性（V4.20.0 的第二層 bug：
     首頁 item 用 href 沒有 path → item.path.charAt(0) 會炸）
  3. injectMobileNav() 實際呼叫一次，模擬 DOM 收到 5 個 <a>

【限制】stub 不是真瀏覽器——它抓「執行期會炸的錯」，抓不到視覺/佈局問題。
真上線前的人工點測（載入首頁點五鈕各一次）仍不可省。
"""
import subprocess
import sys
from pathlib import Path

JS = Path(__file__).resolve().parent.parent / "docs" / "javascripts" / "extra.js"

NODE_HARNESS = r"""
var appended = [];
function El(tag){ return {
  tag: tag, children: [], className: "", innerHTML: "", id: "",
  classList: { add: function(){}, remove: function(){} },
  addEventListener: function(){},
  appendChild: function(c){ this.children.push(c); },
  setAttribute: function(){}, getAttribute: function(){ return this._href || null; },
}; }
global.window = { location: { pathname: "/" } };
global.document = {
  getElementById: function(){ return null; },
  querySelector: function(){ return null; },
  querySelectorAll: function(){ return []; },
  createElement: function(t){ return El(t); },
  body: { appendChild: function(n){ appended.push(n); } },
  addEventListener: function(ev, fn){ if (ev === "DOMContentLoaded") fn(); },
};
global.document.readyState = "loading";

try {
  require(JS_PATH);
} catch (e) {
  console.log("FAIL_TOPLEVEL: " + e.message);
  process.exit(1);
}

// NAV_ITEMS 每項都要有 path（首頁曾用 href 漏 path → charAt 炸）
if (typeof NAV_ITEMS !== "undefined") {
  for (var i = 0; i < NAV_ITEMS.length; i++) {
    if (typeof NAV_ITEMS[i].path !== "string") {
      console.log("FAIL_ITEM: NAV_ITEMS[" + i + "] (" + NAV_ITEMS[i].label + ") 沒有 path 屬性");
      process.exit(1);
    }
  }
  console.log("NAV_ITEMS: " + NAV_ITEMS.length + " 項，path 全齊");
}

// bottom nav 應被注入且有 5 個子節點
var nav = null;
for (var j = 0; j < appended.length; j++) {
  if (appended[j].id === "ccm-mobile-nav") nav = appended[j];
}
if (!nav) { console.log("FAIL_NAV: bottom nav 未被注入"); process.exit(1); }
if (nav.children.length !== 5) {
  console.log("FAIL_NAV: bottom nav 有 " + nav.children.length + " 鈕（應為 5）"); process.exit(1);
}
console.log("bottom nav: 已注入、5 鈕");
console.log("OK");
"""


def main() -> int:
    harness = 'var JS_PATH = ' + repr(str(JS)).replace("'", '"') + ';\n' + NODE_HARNESS
    r = subprocess.run(["node", "-e", harness], capture_output=True, text=True)
    out = (r.stdout or "") + (r.stderr or "")
    print("📱 UI JS 執行期檢查（stub DOM）")
    for line in out.strip().splitlines():
        print("   " + line)
    if r.returncode != 0 or "OK" not in out:
        print("🔴 extra.js 執行期失敗——這是 strict build 與 node --check 都抓不到的（坑 #77）")
        return 1
    print("✓ extra.js 頂層執行、NAV_ITEMS、bottom nav 注入全部正常")
    return 0


if __name__ == "__main__":
    sys.exit(main())
