# 驗證報告

## 已執行

1. 新增 Swift 檔案均通過：

```bash
swiftc -frontend -parse
```

2. 四個新 Effect／Support 檔案以專案介面 stub 執行跨檔案 typecheck，
未出現 Swift 型別錯誤。

3. 安裝器已在模擬的目前 Factory 結構執行：

- 成功備份原檔。
- 成功複製四個新 Swift 檔案。
- 成功將三個免費特效由 `GenericMetalEffect` 分離。
- 重複驗證時不會重新插入重複映射。

4. 驗證器確認：

- 三個新 Effect 使用 `TrailPoint.color`。
- 不使用 `EffectType.colorOverride`。
- 三個 Effect 都接入 `trailWidthMultiplier`。
- 粒子型子效果接入 `particleSizeMultiplier` 與
  `particleFrequencyMultiplier`。
- 即時預覽與錄影核心仍透過同一個 `MetalEffectFactory` 取得 renderer。

5. Buffer 容量檢查：

- Lightning 主線與分岔容量高於最大節點需求。
- Fire Ribbon 使用既有 65,536-float 共用 buffer。
- Fire wisp buffer 可容納全部 36 個三角形粒子。
- Stardust strand buffer 可容納 128 個節點。
- Stardust glint buffer 可容納 24 個八方向星芒 segment。

## 未能在目前環境執行

- Apple iOS SDK 完整 typecheck。
- Xcode target build。
- Metal GPU 實機渲染。
- 相機與錄影管線的幀級視覺比對。

本版沒有修改 `.metal` 檔案，因此不新增 Metal shader 編譯風險。最終視覺
仍應在實體 iPhone 依參考影片微調全域 profile 與各 Effect 內的 base
constant。
