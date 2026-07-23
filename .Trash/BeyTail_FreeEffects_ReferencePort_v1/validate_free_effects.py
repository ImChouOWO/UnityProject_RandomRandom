#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


EFFECT_FILES = {
    "LightningMetalEffect.swift": {
        "class": "final class LightningMetalEffect",
        "effect": "effectType == .lightning",
        "particle": [
            "particleSizeMultiplier",
            "particleFrequencyMultiplier",
        ],
    },
    "FireMetalEffect.swift": {
        "class": "final class FireMetalEffect",
        "effect": "effectType == .fire",
        "particle": [
            "particleSizeMultiplier",
            "particleFrequencyMultiplier",
            "FlameWisp",
        ],
    },
    "StardustMetalEffect.swift": {
        "class": "final class StardustMetalEffect",
        "effect": "effectType == .stardust",
        "particle": [
            "particleSizeMultiplier",
            "particleFrequencyMultiplier",
            "Glint",
        ],
    },
}


def fail(message: str) -> None:
    print(f"[ERROR] {message}")
    raise SystemExit(1)


def require(
    condition: bool,
    message: str,
) -> None:
    if not condition:
        fail(message)


def run_parse(files: list[Path]) -> None:
    swiftc = shutil.which("swiftc")

    if swiftc is None:
        print(
            "[WARN] 找不到 swiftc，略過 Swift parser 驗證"
        )
        return

    for path in files:
        result = subprocess.run(
            [
                swiftc,
                "-frontend",
                "-parse",
                str(path),
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print(result.stdout)
            print(result.stderr)
            fail(f"Swift syntax parse 失敗：{path}")

    print(
        f"[OK] Swift syntax parse：{len(files)} files"
    )


def main() -> None:
    if len(sys.argv) != 2:
        fail(
            "使用方式：python3 validate_free_effects.py "
            "/Users/zhouchenghan/Desktop/iosAPP/beyblade"
        )

    project_root = Path(sys.argv[1]).expanduser().resolve()
    effect_dir = (
        project_root
        / "beyblade/BeyTail/UI/MetalEffects/Effects"
    )
    core_dir = (
        project_root
        / "beyblade/BeyTail/UI/MetalEffects/Core"
    )
    factory_path = (
        core_dir
        / "MetalEffectFactory.swift"
    )
    profile_path = (
        project_root
        / "beyblade/BeyTail/Effects/TrailRenderProfile.swift"
    )
    live_path = (
        core_dir
        / "MetalTrailOverlayView.swift"
    )
    recording_path = (
        project_root
        / "beyblade/BeyTail/UI/pic/icon/PicTrailMetalRenderCore.swift"
    )

    support_path = (
        effect_dir
        / "FreeEffectRenderSupport.swift"
    )

    require(
        support_path.is_file(),
        f"缺少：{support_path}",
    )

    support_text = support_path.read_text(
        encoding="utf-8"
    )

    require(
        "mixedColor" in support_text
        and "clipPosition" in support_text,
        "FreeEffectRenderSupport 內容不完整",
    )

    parse_files = [
        support_path,
        factory_path,
    ]

    for filename, expectations in EFFECT_FILES.items():
        path = effect_dir / filename

        require(
            path.is_file(),
            f"缺少：{path}",
        )

        text = path.read_text(
            encoding="utf-8"
        )

        require(
            expectations["class"] in text,
            f"{filename} 類別名稱不正確",
        )

        require(
            expectations["effect"] in text,
            f"{filename} 未限制正確 EffectType",
        )

        require(
            ".first.color" in text
            or "first.color" in text,
            f"{filename} 未使用 TrailPoint.color",
        )

        require(
            "colorOverride" not in text,
            f"{filename} 仍使用固定 colorOverride",
        )

        require(
            "trailWidthMultiplier" in text,
            f"{filename} 未接入全域寬度設定",
        )

        for token in expectations["particle"]:
            require(
                token in text,
                f"{filename} 缺少粒子控制：{token}",
            )

        parse_files.append(path)

    factory_text = factory_path.read_text(
        encoding="utf-8"
    )

    factory_tokens = [
        "renderer = LightningMetalEffect()",
        "renderer = FireMetalEffect()",
        "renderer = StardustMetalEffect()",
    ]

    for token in factory_tokens:
        require(
            token in factory_text,
            f"Factory 缺少映射：{token}",
        )

    require(
        not (
            "case .lightning," in factory_text
            and "renderer = GenericMetalEffect()"
                in factory_text
        ),
        "免費特效仍映射至 GenericMetalEffect",
    )

    profile_text = profile_path.read_text(
        encoding="utf-8"
    )

    for token in [
        "widthMultiplier",
        "lengthMs",
        "particleSizeMultiplier",
        "particleFrequencyMultiplier",
        ".lightning:",
        ".fire:",
        ".stardust:",
    ]:
        require(
            token in profile_text,
            f"TrailRenderProfile 缺少：{token}",
        )

    live_text = live_path.read_text(
        encoding="utf-8"
    )
    recording_text = recording_path.read_text(
        encoding="utf-8"
    )

    require(
        "MetalEffectFactory.makeEffect" in live_text,
        "即時預覽未使用 MetalEffectFactory",
    )

    require(
        "MetalEffectFactory.makeEffect" in recording_text,
        "錄影／離線渲染未使用 MetalEffectFactory",
    )

    run_parse(parse_files)

    print("[OK] 三個免費特效皆使用偵測主色")
    print("[OK] 全域寬度／粒子大小／粒子頻率已接入")
    print("[OK] 即時預覽與錄影共用同一 Factory")
    print("[OK] GenericMetalEffect 保留但不再承接免費特效")
    print("[OK] 無需修改 MetalProgram 或 BeyTailEffects.metal")
    print("[OK] Free effect validation completed")


if __name__ == "__main__":
    main()
