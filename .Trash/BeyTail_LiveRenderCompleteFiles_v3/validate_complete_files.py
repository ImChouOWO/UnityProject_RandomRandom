#!/usr/bin/env python3
from pathlib import Path
import re
import sys

if len(sys.argv) != 2:
    print(
        "使用方式：python3 validate_complete_files.py "
        "/Users/zhouchenghan/Desktop/iosAPP/beyblade"
    )
    raise SystemExit(1)

root = Path(sys.argv[1]).expanduser().resolve()

main_path = root / "beyblade/BeyTail/UI/MainViewModel.swift"
recording_path = (
    root / "beyblade/BeyTail/Recording/RecordingManager.swift"
)

if not main_path.is_file():
    print(f"[ERROR] 找不到：{main_path}")
    raise SystemExit(1)

if not recording_path.is_file():
    print(f"[ERROR] 找不到：{recording_path}")
    raise SystemExit(1)

main = main_path.read_text(encoding="utf-8")
recording = recording_path.read_text(encoding="utf-8")

has_live_trail_update = re.search(
    r"(?:self\s*\.\s*)?trailEffectEngine\s*\.\s*addPoint\s*\(",
    main,
) is not None

has_recording_trail_update = re.search(
    r"(?:self\s*\.\s*)?recordingTrailEffectEngine\s*\.\s*addPoint\s*\(",
    main,
) is not None

checks = {
    "相機 relay 限制為 30 FPS":
        "minimumDeliveryInterval: TimeInterval = 1.0 / 30.0" in main,

    "舊 relay while 已移除":
        "while let frame = self.takeLatestFrame()" not in main,

    "錄影開始保留即時相機":
        "let wasLiveCamera =" in main,

    "只清空錄影專用拖尾":
        re.search(
            r"(?:self\s*\.\s*)?"
            r"recordingTrailEffectEngine\s*\.\s*clear\s*\(",
            main,
        ) is not None,

    "主畫面拖尾持續更新":
        has_live_trail_update,

    "錄影專用拖尾持續更新":
        has_recording_trail_update,

    "錄影預期 FPS 為 30":
        "AVVideoExpectedSourceFrameRateKey: 30" in recording,

    "錄影 keyframe 為 30":
        "AVVideoMaxKeyFrameIntervalKey: 30" in recording,

    "bitrate 使用 30 FPS":
        "Double(width * height) * 30.0 * 0.14" in recording,
}

failed = False

for label, passed in checks.items():
    print(f"[{'OK' if passed else 'FAIL'}] {label}")
    failed = failed or not passed

if failed:
    print()
    print("[ERROR] 驗證未通過，請檢查上方 FAIL 項目")
    raise SystemExit(1)

print()
print("[OK] Live render complete files validation passed")
