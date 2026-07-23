# 修改範圍

| 檔案 | 動作 | 用途 |
|---|---|---|
| `FreeEffectRenderSupport.swift` | 新增 | 共用座標、顏色與線段工具 |
| `LightningMetalEffect.swift` | 新增 | 閃電折線、光暈與分岔 |
| `FireMetalEffect.swift` | 新增 | 火焰 Ribbon、熱核心與火舌 |
| `StardustMetalEffect.swift` | 新增 | 五重平行線與星芒 |
| `MetalEffectFactory.swift` | 修改 | 三個免費特效改用獨立 renderer |

未刪除 `GenericMetalEffect.swift`，避免影響既有版本回退與其他尚未確認的
參照。新架構穩定後再考慮移除。
