#!/usr/bin/env python3
from __future__ import annotations

import re
import shutil
import sys
from datetime import datetime
from pathlib import Path


EFFECT_FILES = [
    "FreeEffectRenderSupport.swift",
    "LightningMetalEffect.swift",
    "FireMetalEffect.swift",
    "StardustMetalEffect.swift",
]


def fail(message: str) -> None:
    print(f"[ERROR] {message}")
    raise SystemExit(1)


def backup(
    path: Path,
    backup_root: Path,
    project_root: Path,
) -> None:
    if not path.exists():
        return

    relative = path.relative_to(project_root)
    target = backup_root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, target)


def patch_factory(path: Path) -> None:
    text = path.read_text(encoding="utf-8")

    expected = [
        "renderer = LightningMetalEffect()",
        "renderer = FireMetalEffect()",
        "renderer = StardustMetalEffect()",
    ]

    if all(token in text for token in expected):
        return

    pattern = re.compile(
        r"""
        (?P<indent>[ \t]*)case[ \t]+\.lightning,[ \t]*\n
        [ \t]*\.fire,[ \t]*\n
        [ \t]*\.stardust:[ \t]*\n
        (?:
            [ \t]*//[^\n]*\n
        )*
        [ \t]*renderer[ \t]*=[ \t]*GenericMetalEffect\(\)
        """,
        re.VERBOSE,
    )

    replacement = """\\g<indent>case .lightning:
\\g<indent>    renderer = LightningMetalEffect()

\\g<indent>case .fire:
\\g<indent>    renderer = FireMetalEffect()

\\g<indent>case .stardust:
\\g<indent>    renderer = StardustMetalEffect()"""

    updated, count = pattern.subn(
        replacement,
        text,
        count=1,
    )

    if count != 1:
        fail(
            "無法定位 MetalEffectFactory 中的免費特效 GenericMetalEffect 映射。"
            "請確認專案與 GitHub main 一致。"
        )

    path.write_text(
        updated,
        encoding="utf-8",
    )


def main() -> None:
    if len(sys.argv) != 2:
        fail(
            "使用方式：python3 install_free_effects.py "
            "/Users/zhouchenghan/Desktop/iosAPP/beyblade"
        )

    package_root = Path(__file__).resolve().parent
    project_root = Path(sys.argv[1]).expanduser().resolve()

    xcode_project = project_root / "beyblade.xcodeproj"
    effect_dir = (
        project_root
        / "beyblade/BeyTail/UI/MetalEffects/Effects"
    )
    factory_path = (
        project_root
        / "beyblade/BeyTail/UI/MetalEffects/Core/MetalEffectFactory.swift"
    )
    profile_path = (
        project_root
        / "beyblade/BeyTail/Effects/TrailRenderProfile.swift"
    )

    if not xcode_project.exists():
        fail(f"找不到 Xcode 專案：{xcode_project}")

    if not effect_dir.is_dir():
        fail(f"找不到 Metal Effects 目錄：{effect_dir}")

    if not factory_path.is_file():
        fail(f"找不到 MetalEffectFactory.swift：{factory_path}")

    if not profile_path.is_file():
        fail(f"找不到 TrailRenderProfile.swift：{profile_path}")

    profile_text = profile_path.read_text(encoding="utf-8")
    required_profile_tokens = [
        "widthMultiplier",
        "lengthMs",
        "particleSizeMultiplier",
        "particleFrequencyMultiplier",
    ]

    for token in required_profile_tokens:
        if token not in profile_text:
            fail(
                "目前 TrailRenderProfile 缺少必要欄位："
                f"{token}"
            )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )
    backup_root = (
        project_root
        / "tmp"
        / f"free_effect_backup_{timestamp}"
    )
    backup_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    backup(
        factory_path,
        backup_root,
        project_root,
    )

    for filename in EFFECT_FILES:
        destination = effect_dir / filename
        backup(
            destination,
            backup_root,
            project_root,
        )

    source_dir = (
        package_root
        / "beyblade/BeyTail/UI/MetalEffects/Effects"
    )

    for filename in EFFECT_FILES:
        source = source_dir / filename

        if not source.is_file():
            fail(f"安裝包缺少：{source}")

        shutil.copy2(
            source,
            effect_dir / filename,
        )

    patch_factory(factory_path)

    print("[OK] 新免費特效已安裝")
    print("[OK] 閃電 -> LightningMetalEffect")
    print("[OK] 火炎 -> FireMetalEffect")
    print("[OK] 星塵 -> StardustMetalEffect")
    print("[OK] 動態顏色使用 TrailPoint.color")
    print("[OK] 未修改 BeyTailEffects.metal")
    print(f"[OK] 備份：{backup_root}")
    print()
    print("Next:")
    print(
        f'  python3 "{package_root / "validate_free_effects.py"}" '
        f'"{project_root}"'
    )
    print(
        f'  open "{project_root / "beyblade.xcodeproj"}"'
    )
    print("  Product > Clean Build Folder")
    print("  Build and test on a physical iPhone")


if __name__ == "__main__":
    main()
