#!/usr/bin/env python3
"""
check_doc_meta.py — 文件元資料守門員（規則 6 第四道煙霧測試）

【為什麼有這支】
Sela V4.14.1 回饋：「你還是沒有更新 C0-C6 的文件更新時間，要想一個可以確保會更新的方式」。

盤點後發現不是「偶爾忘記」，是**全站級失控**：
  - C4 在 V4.11.0 對照 BCLC 2026 原文全文重寫，文件資訊還寫「0.3（V3.4.18 補臨床細節，依公開準則整理）」
  - C5 差 17 版、C3 差 15 版、C2 還停在「0.1 框架版」
  - 38 檔裡只有 7 檔有「更新日期」，格式四種

【根因】= Kit 坑 #78（本專案 C-1 貢獻的）
  「我最常做的那件事，build/lint 真的檢查得到嗎？」
  → 我最常做的是「改癌別檔」，而 mkdocs 只檢查連結與 anchor，
    **完全不檢查「內容改了，元資料有沒有跟上」**。這是死角。
  → 死角處自建掃描器，綁進升版必跑的煙霧測試。

【為什麼這樣就「確保」得了】
  手動提醒自己「記得改日期」= 靠記憶 = 會再忘（已證實）。
  這支會在內容雜湊變動、但「最後更新版本」沒跟上當前版本時 **直接 FAIL**，
  升版跑煙霧測試就過不了 → 交付不出去 → 只能改。

【納管方式：opt-in，但一旦納管就強制】
  檔案的「文件資訊」表有 `| 最後更新 | V4.x.y |` 這一列 → 自動納管。
  沒有這一列 → 不納管（掃描器只列出來提示，不 FAIL）。
  要納管新檔：加上那一列即可。

【雜湊排除文件資訊區塊】
  雜湊只算「**文件資訊**」之前的內容——否則改版本號會改雜湊，變成循環。

【用法】
  python3 tools/check_doc_meta.py              # 唯讀檢查（煙霧測試用）
  python3 tools/check_doc_meta.py --update     # 檢查通過後更新 manifest（升版時用）
  python3 tools/check_doc_meta.py --init       # 首次建立 manifest（只用一次）
"""

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
MANIFEST = ROOT / "tools" / "doc-manifest.json"
CLAUDE_MD = ROOT / "CLAUDE.md"

META_MARKER = "**文件資訊**"
# 納管欄位：| 最後更新 | V4.15.0 |（允許粗體與空白變化）
VER_ROW = re.compile(r"\|\s*\*{0,2}最後更新\*{0,2}\s*\|\s*\*{0,2}(V\d+\.\d+\.\d+)\*{0,2}")


def current_version() -> str:
    """從 CLAUDE.md 第一個『當前版本』撈（規則 1 的單一真相）。"""
    text = CLAUDE_MD.read_text(encoding="utf-8")
    m = re.search(r"當前版本\*{0,2}[：:]\s*\*{0,2}(V\d+\.\d+\.\d+)", text)
    assert m, "❌ CLAUDE.md 找不到『當前版本』——規則 1 壞了"
    return m.group(1)


def body_hash(text: str) -> str:
    """算內容雜湊，排除文件資訊區塊本身（否則改版號→改雜湊→循環）。"""
    body = text.split(META_MARKER)[0]
    return hashlib.sha256(body.encode("utf-8")).hexdigest()[:16]


def declared_version(text: str):
    """抽出『最後更新』欄；沒有 = 未納管。"""
    m = VER_ROW.search(text)
    return m.group(1) if m else None


def scan():
    cur = current_version()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}
    tracked, untracked, failures, updates = [], [], [], {}

    for path in sorted(DOCS.glob("*.md")):
        name = path.name
        text = path.read_text(encoding="utf-8")
        decl = declared_version(text)
        if decl is None:
            untracked.append(name)
            continue

        tracked.append(name)
        h = body_hash(text)
        recorded = manifest.get(name, {})
        old_hash = recorded.get("hash")
        old_ver = recorded.get("version")

        if old_hash is None:
            updates[name] = {"hash": h, "version": decl}
            continue

        # 判準只有一條：內容變了 → 『最後更新』就必須等於當前版本。
        # （V4.15.0 開發時踩過：原本多加一個 `decl == old_ver` 條件會誤報——
        #   當「這一版改了它、也標了這一版」時 old_ver 本來就等於 cur，是合法狀態。）
        changed = h != old_hash
        if changed and decl != cur:
            failures.append(
                f"🔴 {name}\n"
                f"     內容已變動，但『最後更新』寫的是 {decl}，當前版本是 {cur}\n"
                f"     → 這一版動了它，就要把『最後更新』改成 {cur}（版本與年月一起改）"
            )
        else:
            updates[name] = {"hash": h, "version": decl}

    return cur, tracked, untracked, failures, updates, manifest


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    cur, tracked, untracked, failures, updates, manifest = scan()

    print(f"📋 文件元資料檢查（當前版本 {cur}）")
    print(f"   納管 {len(tracked)} 檔／未納管 {len(untracked)} 檔")

    # 🔴 自我防護：納管 0 檔時「全部同步」是永遠為真的空命題（零檔案的全稱命題）
    #    V4.15.0 開發時真的踩到——regex 沒考慮欄位名粗體 → 納管 0 檔 → 報綠燈。
    #    這支工具的存在理由就是「防止假的完成訊號」，它自己絕不能製造一個。
    if len(tracked) == 0:
        print("\n🔴 納管 0 檔——這不是『通過』，是掃描器抓不到欄位。")
        print("   檢查：欄位格式是否為 `| 最後更新 | V4.x.y（年月）|`（欄位名可加粗體）")
        return 1
    MIN_TRACKED = 15  # C0-C13 + D2；低於此代表有檔案掉出納管
    if len(tracked) < MIN_TRACKED:
        print(f"\n🔴 納管檔案只有 {len(tracked)} 個，少於預期的 {MIN_TRACKED} 個。")
        print("   有檔案掉出納管（欄位被刪或格式跑掉）——這正是本工具要防的事。")
        return 1

    if mode == "--init":
        new = {n: {"hash": body_hash((DOCS / n).read_text(encoding="utf-8")),
                   "version": declared_version((DOCS / n).read_text(encoding="utf-8"))}
               for n in tracked}
        MANIFEST.write_text(json.dumps(new, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"✓ manifest 已初始化：{len(new)} 檔")
        return 0

    if failures:
        print(f"\n{'─' * 62}")
        print(f"🔴 {len(failures)} 個檔案改了內容、但元資料沒跟上：\n")
        for f in failures:
            print(f)
            print()
        print("─" * 62)
        print("這正是本掃描器存在的理由——mkdocs 不會抓這個（Kit 坑 #78：build 工具的死角）。")
        print("修完再跑一次；要更新 manifest 用 --update。")
        return 1

    if mode == "--update":
        manifest.update(updates)
        # 移除已不存在或已取消納管的檔
        for gone in set(manifest) - set(tracked):
            del manifest[gone]
        MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"✓ manifest 已更新（{len(manifest)} 檔）")
    else:
        print("✓ 納管檔案的元資料全部同步")

    if untracked:
        print(f"\n💡 未納管（無『最後更新』欄，不強制、不 FAIL）：")
        print(f"   {', '.join(n.replace('.md', '') for n in untracked)}")
        print("   要納管：在該檔『文件資訊』表加一列 `| 最後更新 | V<當前> |`")

    return 0


if __name__ == "__main__":
    sys.exit(main())
