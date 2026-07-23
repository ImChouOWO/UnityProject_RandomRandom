# BeyTail 免費特效參考影片移植包 v1

本修改包以目前 GitHub `main` 的 Metal 架構為基準，將原本共用
`GenericMetalEffect` 的三個免費特效拆分為獨立 renderer：

- 閃電：`LightningMetalEffect`
- 火炎：`FireMetalEffect`
- 星塵：`StardustMetalEffect`

三個特效皆直接使用每個 `TrailPoint.color`，因此拖尾會跟隨
`InferenceEngine` 與 `DominantColorExtractor` 產生的陀螺主色。

## 修改範圍

新增：

```text
beyblade/BeyTail/UI/MetalEffects/Effects/
├── FreeEffectRenderSupport.swift
├── LightningMetalEffect.swift
├── FireMetalEffect.swift
└── StardustMetalEffect.swift
```

修改：

```text
beyblade/BeyTail/UI/MetalEffects/Core/MetalEffectFactory.swift
```

保留但不再承接免費特效：

```text
beyblade/BeyTail/UI/MetalEffects/Effects/GenericMetalEffect.swift
```

未修改：

```text
BeyTailEffects.metal
MetalProgram.swift
MetalRenderContext.swift
TrailRenderProfile.swift
InferenceEngine.swift
DominantColorExtractor.swift
```

本次使用既有 `flatColor` Metal pipeline，以 CPU 產生線段、Ribbon
與幾何粒子，避免新增 shader branch，降低整合幅度與 Metal 編譯風險。

## 參考影片對應

### 閃電

- 單條細長、折線式電弧。
- 外層為陀螺主色光暈。
- 內層為接近白色的高亮電芯。
- 少量短分岔由粒子頻率控制。

### 火炎

- 以陀螺主色形成較粗、邊緣不規則的火焰 Ribbon。
- 中央加入較亮的熱核心。
- 少量脫離主軌跡的火舌粒子。

### 星塵

- 五條緊密排列的平行發光線。
- 軌跡節點維持明顯折線感。
- 整體顏色向白色提亮，但仍保留陀螺主色。
- 少量十字星芒由粒子設定控制。

## 全域設定

沿用既有：

```text
beyblade/BeyTail/Effects/TrailRenderProfile.swift
```

三個新特效均使用：

```swift
widthMultiplier
lengthMs
particleSizeMultiplier
particleFrequencyMultiplier
```

其中：

- `widthMultiplier`：主拖尾、光暈與線寬倍率。
- `lengthMs`：軌跡保留時間。
- `particleSizeMultiplier`：閃電分岔、火舌、星芒大小。
- `particleFrequencyMultiplier`：閃電分岔、火舌、星芒頻率。

## 自動安裝

```bash
cd /path/to/BeyTail_FreeEffects_ReferencePort_v1

python3 install_free_effects.py \
  /Users/zhouchenghan/Desktop/iosAPP/beyblade
```

安裝器會備份至：

```text
tmp/free_effect_backup_<時間>
```

驗證：

```bash
python3 validate_free_effects.py \
  /Users/zhouchenghan/Desktop/iosAPP/beyblade
```

接著：

```text
Product → Clean Build Folder
Command + B
```

最後使用實體 iPhone 測試即時預覽、錄影與離線影片輸出。

## 手動安裝

將四個 Effect 檔案複製到：

```text
beyblade/BeyTail/UI/MetalEffects/Effects/
```

再以修改包內的：

```text
beyblade/BeyTail/UI/MetalEffects/Core/MetalEffectFactory.swift
```

替換專案中的同名檔案。

專案使用 filesystem-synchronized group，通常不需要在 Xcode 手動加入檔案；
仍應確認四個新 Swift 檔案具有正確的 Target Membership。
