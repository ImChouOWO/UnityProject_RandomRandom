# BeyTail 全域拖尾寬度／長度設定

本補丁新增：

```text
beyblade/BeyTail/Effects/TrailRenderProfile.swift
```

所有特效的主要拖尾寬度與長度集中於：

```swift
static let values: [EffectType: TrailRenderProfile]
```

目前設定：

- 所有特效 `widthMultiplier = 1.25`，即寬度增加 25%。
- `lengthMs` 保留各特效原本的可見時間。
- Wave 原本局部的 1.25 倍設定會被移除，避免重複放大成 1.5625 倍。

## 安裝

```bash
cd /path/to/BeyTail_TrailRenderProfile_v1

python3 install_trail_render_profile.py \
  /Users/zhouchenghan/Desktop/iosAPP/beyblade
```

驗證：

```bash
python3 validate_trail_render_profile.py \
  /Users/zhouchenghan/Desktop/iosAPP/beyblade
```

最後在 Xcode 執行：

```text
Product → Clean Build Folder
Command + B
```

## 後續微調

只需修改：

```text
beyblade/BeyTail/Effects/TrailRenderProfile.swift
```

例如將 Wave 加寬到 1.40、長度改成 1000 ms：

```swift
.wave: TrailRenderProfile(
  widthMultiplier: 1.40,
  lengthMs: 1000
),
```

`lengthMs` 是軌跡點的保留時間。移動速度相同時，時間越長，視覺上的拖尾越長。
