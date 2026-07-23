#!/usr/bin/env python3
from __future__ import annotations

import re
import shutil
import sys
from datetime import datetime
from pathlib import Path


def fail(message: str) -> None:
    print(f"[ERROR] {message}")
    raise SystemExit(1)


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        fail(f"{label}：預期 1 處，實際找到 {count} 處")
    return text.replace(old, new, 1)


def patch_effect_type(text: str) -> str:
    if "temporarilyHiddenEffects" in text:
        print("[SKIP] EffectType 已包含暫時隱藏設定")
        return text

    marker = "    var id: String { rawValue }\n"
    if marker not in text:
        fail("EffectType.swift 找不到 var id")

    availability = '''    /// 下個版本才會開放的特效。
    ///
    /// 保留 enum case、Product ID 與 Metal renderer，避免未來重新加入時
    /// 破壞既有購買紀錄；目前所有 UI 與快捷選單都必須排除。
    static let temporarilyHiddenEffects: Set<EffectType> = [
        .crimson,
        .deathRay,
        .emerald,
        .inkWash,
        .spray
    ]

    var isAvailableInCurrentRelease: Bool {
        !Self.temporarilyHiddenEffects.contains(self)
    }

    /// 手動提供 CaseIterable 清單，讓所有使用 EffectType.allCases 的畫面
    /// 自動排除尚未開放的特效。
    static let allCases: [EffectType] = [
        .lightning,
        .fire,
        .stardust,
        .wave,
        .thunder,
        .vortex,
        .dark
    ]

'''

    text = text.replace(marker, marker + "\n" + availability, 1)

    old_shop = '''    static var shopEffects: [EffectType] {
        [
            .wave,
            .thunder,
            .vortex,
            .dark,
            .crimson,
            .deathRay,
            .emerald,
            .inkWash,
            .spray
        ]
    }'''

    new_shop = '''    static var shopEffects: [EffectType] {
        [
            .wave,
            .thunder,
            .vortex,
            .dark
        ]
    }'''

    text = replace_once(
        text,
        old_shop,
        new_shop,
        "更新 shopEffects"
    )

    print("[OK] EffectType.allCases 已排除 5 款下次更新特效")
    print("[OK] shopEffects 與 individualProductIDs 不再包含隱藏特效")
    return text


def patch_quick_store(text: str) -> str:
    if "effect.isAvailableInCurrentRelease else" not in text:
        pattern = re.compile(
            r"(guard\s+!id\.isEmpty,.*?"
            r"let\s+effect\s*=\s*EffectType\("
            r"\s*rawValue:\s*id\s*\))"
            r"\s*else\s*\{",
            re.DOTALL,
        )
        match = pattern.search(text)
        if not match:
            fail(
                "EffectQuickMenuStore.swift 找不到 "
                "decodeSlots 的 EffectType 解析區塊"
            )

        replacement = (
            match.group(1)
            + ",\n                  "
            + "effect.isAvailableInCurrentRelease else {"
        )
        text = (
            text[:match.start()]
            + replacement
            + text[match.end():]
        )

    old_add_guard = '''        guard !contains(effect), !isFull else {
            return false
        }'''

    new_add_guard = '''        guard effect.isAvailableInCurrentRelease,
              !contains(effect),
              !isFull else {
            return false
        }'''

    if new_add_guard not in text:
        text = replace_once(
            text,
            old_add_guard,
            new_add_guard,
            "限制快捷選單新增"
        )

    old_loop = '''        for effect in effects {
            guard seen.insert(
                effect.rawValue
            ).inserted else {'''

    new_loop = '''        for effect in effects {
            guard effect.isAvailableInCurrentRelease,
                  seen.insert(
                    effect.rawValue
                  ).inserted else {'''

    if new_loop not in text:
        text = replace_once(
            text,
            old_loop,
            new_loop,
            "過濾快捷選單既有資料"
        )

    print("[OK] 快捷選單會自動移除舊 UserDefaults 中的隱藏特效")
    return text


def patch_quick_menu_view(text: str) -> str:
    old_filter = '''                .filter {
                    purchaseStore.isPurchased($0)
                }'''

    new_filter = '''                .filter {
                    $0.isAvailableInCurrentRelease
                    && purchaseStore.isPurchased($0)
                }'''

    if new_filter not in text:
        text = replace_once(
            text,
            old_filter,
            new_filter,
            "過濾主畫面快捷選單"
        )

    print("[OK] 主畫面快捷選單不會顯示隱藏特效")
    return text


def patch_main_view_model(text: str) -> str:
    old_didset = '''        didSet {
            guard EffectPurchaseStore.shared.isPurchased(selectedEffect) else {'''

    new_didset = '''        didSet {
            guard selectedEffect.isAvailableInCurrentRelease,
                  EffectPurchaseStore.shared.isPurchased(selectedEffect) else {'''

    if new_didset not in text:
        text = replace_once(
            text,
            old_didset,
            new_didset,
            "限制 selectedEffect"
        )

    old_select = '''        guard !effect.isLocked else {
            return
        }'''

    new_select = '''        guard effect.isAvailableInCurrentRelease,
              !effect.isLocked else {
            return
        }'''

    if new_select not in text:
        text = replace_once(
            text,
            old_select,
            new_select,
            "限制 onEffectSelected"
        )

    print("[OK] MainViewModel 不接受任何隱藏特效選擇")
    return text


def main() -> None:
    if len(sys.argv) != 2:
        fail(
            "使用方式：python3 install_hide_upcoming_effects.py "
            "/Users/zhouchenghan/Desktop/iosAPP/beyblade"
        )

    root = Path(sys.argv[1]).expanduser().resolve()

    paths = {
        "EffectType.swift":
            root / "beyblade/BeyTail/Models/EffectType.swift",

        "EffectQuickMenuStore.swift":
            root
            / "beyblade/BeyTail/Models/"
            / "EffectQuickMenuStore.swift",

        "EffectMenuView.swift":
            root / "beyblade/BeyTail/UI/EffectMenuView.swift",

        "MainViewModel.swift":
            root / "beyblade/BeyTail/UI/MainViewModel.swift",
    }

    for path in paths.values():
        if not path.is_file():
            fail(f"找不到：{path}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = (
        root
        / "tmp"
        / f"hide_upcoming_effects_backup_{timestamp}"
    )
    backup.mkdir(parents=True, exist_ok=True)

    for name, path in paths.items():
        shutil.copy2(path, backup / name)

    effect_type = patch_effect_type(
        paths["EffectType.swift"].read_text(
            encoding="utf-8"
        )
    )

    quick_store = patch_quick_store(
        paths["EffectQuickMenuStore.swift"].read_text(
            encoding="utf-8"
        )
    )

    quick_menu = patch_quick_menu_view(
        paths["EffectMenuView.swift"].read_text(
            encoding="utf-8"
        )
    )

    main_vm = patch_main_view_model(
        paths["MainViewModel.swift"].read_text(
            encoding="utf-8"
        )
    )

    paths["EffectType.swift"].write_text(
        effect_type,
        encoding="utf-8"
    )

    paths["EffectQuickMenuStore.swift"].write_text(
        quick_store,
        encoding="utf-8"
    )

    paths["EffectMenuView.swift"].write_text(
        quick_menu,
        encoding="utf-8"
    )

    paths["MainViewModel.swift"].write_text(
        main_vm,
        encoding="utf-8"
    )

    print(f"[OK] 備份位置：{backup}")
    print(
        "[OK] 已隱藏：紅蓮破滅、破壞死光、"
        "水墨橫空、翡翠破壞、噴漆塗鴉"
    )
    print("[NEXT] 執行 validate_hide_upcoming_effects.py")


if __name__ == "__main__":
    main()
