#!/usr/bin/env python3
from __future__ import annotations
import sys
from pathlib import Path


def fail(message: str) -> None:
    print(f"[ERROR] {message}")
    raise SystemExit(1)


def main() -> None:
    if len(sys.argv) != 2:
        fail("使用方式：python3 validate_trail_render_profile.py <project-root>")

    root = Path(sys.argv[1]).expanduser().resolve()
    profile = root / "beyblade/BeyTail/Effects/TrailRenderProfile.swift"
    effect_type = root / "beyblade/BeyTail/Models/EffectType.swift"
    effects = root / "beyblade/BeyTail/UI/MetalEffects/Effects"

    if not profile.is_file():
        fail(f"找不到 {profile}")

    profile_text = profile.read_text(encoding="utf-8")
    if profile_text.count("widthMultiplier: 1.25") != 13:
        # 12 profiles + fallback
        fail("TrailRenderProfile 中的 1.25 設定數量不符合預期")

    if "return trailRenderProfile.lengthMs" not in effect_type.read_text(encoding="utf-8"):
        fail("EffectType.fadeDurationMs 尚未連接全域 lengthMs")

    checks = {
        "GenericMetalEffect.swift": "effectType.trailWidthMultiplier",
        "WaveMetalEffect.swift": "Self.baseTrailHalfWidth * widthScale",
        "MoneyMetalEffect.swift": "0.022 * widthScale",
        "BladeMetalEffect.swift": "0.012 * widthScale",
        "IceShatterMetalEffect.swift": "Self.trailHalfWidth * widthScale",
        "CrimsonLotusMetalEffect.swift": "Self.tongueHalfWidth * widthScale",
        "DeathRayMetalEffect.swift": "Self.beamHalfWidth * widthScale",
        "EmeraldMetalEffect.swift": "Self.vineHalfWidth * widthScale",
        "InkWashMetalEffect.swift": ") * widthScale",
        "SprayPaintMetalEffect.swift": "Self.trailHalfWidth * widthScale",
    }

    for filename, token in checks.items():
        path = effects / filename
        if not path.is_file():
            fail(f"找不到 {path}")
        if token not in path.read_text(encoding="utf-8"):
            fail(f"{filename} 尚未套用全域寬度：缺少 {token}")

    print("[OK] 全域拖尾參數檔存在")
    print("[OK] 12 種特效寬度倍率皆為 1.25")
    print("[OK] 拖尾長度由 lengthMs 統一提供")
    print("[OK] 10 個 MetalEffect 已使用全域寬度倍率")


if __name__ == "__main__":
    main()
