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
    if count == 0:
        fail(f"找不到修改位置：{label}")
    if count > 1:
        fail(f"修改位置不唯一：{label}，找到 {count} 處")
    return text.replace(old, new, 1)


def replace_regex_once(text: str, pattern: str, replacement: str, label: str) -> str:
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.S)
    if count == 0:
        fail(f"找不到修改位置：{label}")
    return updated


def backup(path: Path, backup_root: Path, project_root: Path) -> None:
    relative = path.relative_to(project_root)
    target = backup_root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, target)


def patch_effect_type(path: Path) -> None:
    text = path.read_text(encoding="utf-8")

    if "enum EffectType: String, CaseIterable, Identifiable, Sendable" not in text:
        text = text.replace(
            "enum EffectType: String, CaseIterable, Identifiable {",
            "enum EffectType: String, CaseIterable, Identifiable, Sendable {",
            1,
        )

    if "return trailRenderProfile.lengthMs" not in text:
        pattern = r"    var fadeDurationMs: Int64 \{\n.*?\n    \}\n"
        replacement = """    var fadeDurationMs: Int64 {
        return trailRenderProfile.lengthMs
    }
"""
        text = replace_regex_once(
            text,
            pattern,
            replacement,
            "EffectType.fadeDurationMs 改由全域設定提供",
        )

    path.write_text(text, encoding="utf-8")


def patch_generic(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        "halfWidth: 0.070 * effectType.glowWidthMult,",
        "halfWidth: 0.070 * effectType.glowWidthMult * effectType.trailWidthMultiplier,",
    )
    text = text.replace(
        "halfWidth: 0.022 * effectType.coreWidthMult,",
        "halfWidth: 0.022 * effectType.coreWidthMult * effectType.trailWidthMultiplier,",
    )
    path.write_text(text, encoding="utf-8")


def patch_wave(path: Path) -> None:
    text = path.read_text(encoding="utf-8")

    if "widthScale: effectType.trailWidthMultiplier" not in text:
        text = replace_once(
            text,
            "drawRibbons(trackData: trackData, context: context)",
            "drawRibbons(\n      trackData: trackData,\n      context: context,\n      widthScale: effectType.trailWidthMultiplier\n    )",
            "Wave drawRibbons 呼叫",
        )

        text = replace_once(
            text,
            "private func drawRibbons(trackData: MetalTrackData, context: MetalRenderContext) {",
            "private func drawRibbons(\n    trackData: MetalTrackData,\n    context: MetalRenderContext,\n    widthScale: Float\n  ) {",
            "Wave drawRibbons 簽名",
        )

        text = replace_once(
            text,
            "drawFluidRibbon(points, context: context)",
            "drawFluidRibbon(points, context: context, widthScale: widthScale)",
            "Wave drawFluidRibbon 呼叫",
        )

        text = replace_once(
            text,
            "private func drawFluidRibbon(_ points: [MetalTrailSample], context: MetalRenderContext) {",
            "private func drawFluidRibbon(\n    _ points: [MetalTrailSample],\n    context: MetalRenderContext,\n    widthScale: Float\n  ) {",
            "Wave drawFluidRibbon 簽名",
        )

    # Tuned Wave version.
    tuned_pattern = (
        r"let halfWidth\s*=\s*\n?\s*Self\.baseTrailHalfWidth\s*\*\s*"
        r"Self\.trailWidthMultiplier\s*\n?\s*\*\s*\(0\.35 \+ 0\.65 \* alpha\)"
    )
    if re.search(tuned_pattern, text, flags=re.S):
        text = re.sub(
            tuned_pattern,
            "let halfWidth =\n        Self.baseTrailHalfWidth * widthScale\n        * (0.35 + 0.65 * alpha)",
            text,
            count=1,
            flags=re.S,
        )
    elif "let halfWidth: Float = 0.031 * (0.35 + 0.65 * alpha)" in text:
        text = text.replace(
            "let halfWidth: Float = 0.031 * (0.35 + 0.65 * alpha)",
            "let halfWidth: Float = Self.baseTrailHalfWidth * widthScale * (0.35 + 0.65 * alpha)",
            1,
        )
        if "private static let baseTrailHalfWidth" not in text:
            marker = "  private static let timeWrap: Float = 120\n"
            text = replace_once(
                text,
                marker,
                marker + "  private static let baseTrailHalfWidth: Float = 0.031\n",
                "Wave baseTrailHalfWidth",
            )
    elif "Self.baseTrailHalfWidth * widthScale" not in text:
        fail("找不到 Wave 拖尾寬度公式")

    # Remove obsolete local 1.25 multiplier to avoid accidental double scaling.
    text = re.sub(
        r"\n\s*private static let trailWidthMultiplier: Float = 1\.25\s*\n",
        "\n",
        text,
        count=1,
    )

    path.write_text(text, encoding="utf-8")


def patch_call_and_helper(
    path: Path,
    call_old: str,
    call_new: str,
    signature_old: str,
    signature_new: str,
    width_old: str,
    width_new: str,
    token: str,
) -> None:
    text = path.read_text(encoding="utf-8")
    if token not in text:
        text = replace_once(text, call_old, call_new, f"{path.name} helper 呼叫")
        text = replace_once(text, signature_old, signature_new, f"{path.name} helper 簽名")
        text = replace_once(text, width_old, width_new, f"{path.name} 寬度公式")
    path.write_text(text, encoding="utf-8")


def patch_money(path: Path) -> None:
    patch_call_and_helper(
        path,
        "drawRibbon(points, context: context)",
        "drawRibbon(points, context: context, widthScale: effectType.trailWidthMultiplier)",
        "private func drawRibbon(_ points: [MetalTrailSample], context: MetalRenderContext) {",
        "private func drawRibbon(\n    _ points: [MetalTrailSample],\n    context: MetalRenderContext,\n    widthScale: Float\n  ) {",
        "let width: Float = 0.022 * (0.3 + 0.7 * alpha)",
        "let width: Float = 0.022 * widthScale * (0.3 + 0.7 * alpha)",
        "0.022 * widthScale",
    )


def patch_blade(path: Path) -> None:
    patch_call_and_helper(
        path,
        "drawBlade(points, context: context)",
        "drawBlade(points, context: context, widthScale: effectType.trailWidthMultiplier)",
        "private func drawBlade(_ points: [MetalTrailSample], context: MetalRenderContext) {",
        "private func drawBlade(\n    _ points: [MetalTrailSample],\n    context: MetalRenderContext,\n    widthScale: Float\n  ) {",
        "let half: Float = 0.012 * envelope",
        "let half: Float = 0.012 * widthScale * envelope",
        "0.012 * widthScale",
    )


def patch_crimson(path: Path) -> None:
    patch_call_and_helper(
        path,
        "drawFireTongues(points, context: context)",
        "drawFireTongues(points, context: context, widthScale: effectType.trailWidthMultiplier)",
        "private func drawFireTongues(_ points: [MetalTrailSample], context: MetalRenderContext) {",
        "private func drawFireTongues(\n    _ points: [MetalTrailSample],\n    context: MetalRenderContext,\n    widthScale: Float\n  ) {",
        "let halfWidth = Self.tongueHalfWidth * widthMultiplier * (0.30 + 0.70 * life)",
        "let halfWidth =\n          Self.tongueHalfWidth * widthScale * widthMultiplier * (0.30 + 0.70 * life)",
        "Self.tongueHalfWidth * widthScale",
    )


def patch_death(path: Path) -> None:
    patch_call_and_helper(
        path,
        "drawBeam(points, context: context)",
        "drawBeam(points, context: context, widthScale: effectType.trailWidthMultiplier)",
        "private func drawBeam(_ points: [MetalTrailSample], context: MetalRenderContext) {",
        "private func drawBeam(\n    _ points: [MetalTrailSample],\n    context: MetalRenderContext,\n    widthScale: Float\n  ) {",
        "let halfWidth = Self.beamHalfWidth * (0.72 + 0.28 * life)",
        "let halfWidth = Self.beamHalfWidth * widthScale * (0.72 + 0.28 * life)",
        "Self.beamHalfWidth * widthScale",
    )


def patch_emerald(path: Path) -> None:
    patch_call_and_helper(
        path,
        "drawVine(points, context: context)",
        "drawVine(points, context: context, widthScale: effectType.trailWidthMultiplier)",
        "private func drawVine(_ points: [MetalTrailSample], context: MetalRenderContext) {",
        "private func drawVine(\n    _ points: [MetalTrailSample],\n    context: MetalRenderContext,\n    widthScale: Float\n  ) {",
        "let halfWidth = Self.vineHalfWidth * (0.35 + 0.65 * life)",
        "let halfWidth = Self.vineHalfWidth * widthScale * (0.35 + 0.65 * life)",
        "Self.vineHalfWidth * widthScale",
    )


def patch_ice(path: Path) -> None:
    patch_call_and_helper(
        path,
        "drawRibbon(points, context: context)",
        "drawRibbon(points, context: context, widthScale: effectType.trailWidthMultiplier)",
        "private func drawRibbon(_ points: [MetalTrailSample], context: MetalRenderContext) {",
        "private func drawRibbon(\n    _ points: [MetalTrailSample],\n    context: MetalRenderContext,\n    widthScale: Float\n  ) {",
        "let halfWidth = Self.trailHalfWidth * (0.22 + 0.78 * alpha)",
        "let halfWidth = Self.trailHalfWidth * widthScale * (0.22 + 0.78 * alpha)",
        "Self.trailHalfWidth * widthScale",
    )


def patch_ink(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    token = "* widthScale"
    if "drawInkStrand(points, context: context, strand: strand, widthScale:" not in text:
        text = replace_once(
            text,
            "drawInkStrand(points, context: context, strand: strand)",
            "drawInkStrand(\n          points,\n          context: context,\n          strand: strand,\n          widthScale: effectType.trailWidthMultiplier\n        )",
            "InkWash drawInkStrand 呼叫",
        )
        text = replace_once(
            text,
            "private func drawInkStrand(_ points: [MetalTrailSample], context: MetalRenderContext, strand: Int) {",
            "private func drawInkStrand(\n    _ points: [MetalTrailSample],\n    context: MetalRenderContext,\n    strand: Int,\n    widthScale: Float\n  ) {",
            "InkWash drawInkStrand 簽名",
        )
        text = replace_once(
            text,
            "let baseHalfWidth = isMain ? Self.inkHalfWidth : Self.inkHalfWidth * 0.16",
            "let baseHalfWidth =\n      (isMain ? Self.inkHalfWidth : Self.inkHalfWidth * 0.16) * widthScale",
            "InkWash 寬度公式",
        )
    path.write_text(text, encoding="utf-8")


def patch_spray(path: Path) -> None:
    patch_call_and_helper(
        path,
        "drawPaintTrail(points, context: context)",
        "drawPaintTrail(points, context: context, widthScale: effectType.trailWidthMultiplier)",
        "private func drawPaintTrail(_ points: [MetalTrailSample], context: MetalRenderContext) {",
        "private func drawPaintTrail(\n    _ points: [MetalTrailSample],\n    context: MetalRenderContext,\n    widthScale: Float\n  ) {",
        "let halfWidth = Self.trailHalfWidth * (0.45 + 0.55 * alpha)",
        "let halfWidth = Self.trailHalfWidth * widthScale * (0.45 + 0.55 * alpha)",
        "Self.trailHalfWidth * widthScale",
    )


def main() -> None:
    if len(sys.argv) != 2:
        fail(
            "使用方式：python3 install_trail_render_profile.py "
            "/Users/zhouchenghan/Desktop/iosAPP/beyblade"
        )

    project_root = Path(sys.argv[1]).expanduser().resolve()
    source_root = Path(__file__).resolve().parent
    profile_source = source_root / "beyblade/BeyTail/Effects/TrailRenderProfile.swift"
    profile_destination = project_root / "beyblade/BeyTail/Effects/TrailRenderProfile.swift"
    effect_type = project_root / "beyblade/BeyTail/Models/EffectType.swift"
    effects_root = project_root / "beyblade/BeyTail/UI/MetalEffects/Effects"

    required = [
        effect_type,
        effects_root / "GenericMetalEffect.swift",
        effects_root / "WaveMetalEffect.swift",
        effects_root / "MoneyMetalEffect.swift",
        effects_root / "BladeMetalEffect.swift",
        effects_root / "IceShatterMetalEffect.swift",
        effects_root / "CrimsonLotusMetalEffect.swift",
        effects_root / "DeathRayMetalEffect.swift",
        effects_root / "EmeraldMetalEffect.swift",
        effects_root / "InkWashMetalEffect.swift",
        effects_root / "SprayPaintMetalEffect.swift",
    ]

    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        fail("缺少必要檔案：\n" + "\n".join(missing))

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_root = project_root / "tmp" / f"trail_render_profile_backup_{timestamp}"

    for path in required:
        backup(path, backup_root, project_root)
    if profile_destination.exists():
        backup(profile_destination, backup_root, project_root)

    profile_destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(profile_source, profile_destination)

    patch_effect_type(effect_type)
    patch_generic(effects_root / "GenericMetalEffect.swift")
    patch_wave(effects_root / "WaveMetalEffect.swift")
    patch_money(effects_root / "MoneyMetalEffect.swift")
    patch_blade(effects_root / "BladeMetalEffect.swift")
    patch_ice(effects_root / "IceShatterMetalEffect.swift")
    patch_crimson(effects_root / "CrimsonLotusMetalEffect.swift")
    patch_death(effects_root / "DeathRayMetalEffect.swift")
    patch_emerald(effects_root / "EmeraldMetalEffect.swift")
    patch_ink(effects_root / "InkWashMetalEffect.swift")
    patch_spray(effects_root / "SprayPaintMetalEffect.swift")

    print("[OK] 已建立全域 TrailRenderProfile")
    print("[OK] 12 種 EffectType 的寬度倍率目前皆為 1.25")
    print("[OK] 拖尾長度已集中為 lengthMs")
    print("[OK] 10 個 MetalEffect 已改用全域 widthMultiplier")
    print(f"[OK] Backup: {backup_root}")
    print("[NEXT] Xcode：Product > Clean Build Folder，然後 Command+B")


if __name__ == "__main__":
    main()
