#!/usr/bin/env python3
"""跨檔 anchor 掃描器 — 規則 6 煙霧測試第 2 道

為什麼需要：`mkdocs build --strict` 只檢查「同一檔內」的 anchor，
**跨檔連結 [X](other.md#anchor) 的 anchor 不存在時它完全不報**。
使用者點了會跳到頁面頂端（看起來沒壞，其實壞了）。

用法（每次升版前跑，接在 mkdocs build 之後）：
    mkdocs build --strict && python3 tools/check_anchors.py

離開碼：0 = 全部有效；1 = 有斷鏈
"""
import re
import sys
from pathlib import Path

SITE = Path("site")


def main() -> int:
    if not SITE.exists():
        print("✗ 找不到 site/，請先跑 mkdocs build")
        return 1

    # 收集每個頁面的 anchor id
    ids: dict[str, set[str]] = {}
    for f in SITE.rglob("index.html"):
        key = f.parent.name if f.parent != SITE else ""
        ids[key] = set(re.findall(r'id="([^"]+)"', f.read_text(encoding="utf-8")))

    bad: list[str] = []
    for f in SITE.rglob("index.html"):
        src = f.parent.name if f.parent != SITE else "(root)"
        html = f.read_text(encoding="utf-8")
        for page, anchor in re.findall(r'href="\.\./([^"/]+)/#([^"]+)"', html):
            if page in ids and anchor not in ids[page]:
                bad.append(f"  {src} → {page}#{anchor}")

    if bad:
        print(f"✗ 跨檔 anchor 斷鏈 {len(set(bad))} 個：")
        for line in sorted(set(bad)):
            print(line)
        print("\n修法：grep -oE 'id=\"目標關鍵字[^\"]*\"' site/<目標頁>/index.html 拿實際 anchor")
        return 1

    print("✓ 跨檔 anchor 全部有效（0 斷鏈）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
