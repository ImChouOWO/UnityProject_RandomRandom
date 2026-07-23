#!/usr/bin/env python3
from pathlib import Path
import re
import sys

if len(sys.argv) != 2:
    print(
        "使用方式：python3 validate_hide_upcoming_effects.py "
        "/Users/zhouchenghan/Desktop/iosAPP/beyblade"
    )
    raise SystemExit(1)

root = Path(sys.argv[1]).expanduser().resolve()

files = {
    "EffectType":
        root / "beyblade/BeyTail/Models/EffectType.swift",

    "QuickStore":
        root
        / "beyblade/BeyTail/Models/"
        / "EffectQuickMenuStore.swift",

    "QuickMenu":
        root / "beyblade/BeyTail/UI/EffectMenuView.swift",

    "MainVM":
        root / "beyblade/BeyTail/UI/MainViewModel.swift",
}

texts = {
    name: path.read_text(encoding="utf-8")
    for name, path in files.items()
}

effect = texts["EffectType"]

all_cases_match = re.search(
    r"static let allCases:\s*\[EffectType\]\s*=\s*\[(.*?)\]",
    effect,
    re.DOTALL,
)

shop_match = re.search(
    r"static var shopEffects:\s*\[EffectType\]\s*"
    r"\{\s*\[(.*?)\]\s*\}",
    effect,
    re.DOTALL,
)

hidden_tokens = [
    ".crimson",
    ".deathRay",
    ".emerald",
    ".inkWash",
    ".spray",
]

checks = {
    "保留暫時隱藏清單":
        "temporarilyHiddenEffects" in effect,

    "allCases 不包含隱藏特效":
        all_cases_match is not None
        and all(
            token not in all_cases_match.group(1)
            for token in hidden_tokens
        ),

    "shopEffects 不包含隱藏特效":
        shop_match is not None
        and all(
            token not in shop_match.group(1)
            for token in hidden_tokens
        ),

    "快捷選單解碼會排除隱藏特效":
        "effect.isAvailableInCurrentRelease else"
        in texts["QuickStore"],

    "快捷選單不可新增隱藏特效":
        "guard effect.isAvailableInCurrentRelease"
        in texts["QuickStore"],

    "主畫面快捷選單再次過濾":
        "$0.isAvailableInCurrentRelease"
        in texts["QuickMenu"],

    "MainViewModel 拒絕隱藏特效":
        "guard selectedEffect.isAvailableInCurrentRelease"
        in texts["MainVM"]
        and "guard effect.isAvailableInCurrentRelease"
        in texts["MainVM"],
}

failed = False

for label, passed in checks.items():
    print(f"[{'OK' if passed else 'FAIL'}] {label}")
    failed = failed or not passed

if failed:
    raise SystemExit(1)

print()
print(
    "[OK] 五款下次更新特效已從所有 "
    "EffectType.allCases 畫面、商店與快捷選單隱藏"
)
