# BeyTail 暫時隱藏下次更新特效

隱藏以下五款，但保留 enum case、Product ID 與 Metal renderer：

- 紅蓮破滅（crimson）
- 破壞死光（deathRay）
- 水墨橫空（inkWash）
- 翡翠破壞（emerald）
- 噴漆塗鴉（spray）

## 隱藏範圍

- 主畫面快捷特效選單
- 完整特效商店
- 已擁有特效區
- 單件購買區
- 影片後製中的所有 `EffectType.allCases` 選單
- 快捷選單編輯器
- 舊版 UserDefaults 已儲存的快捷項目
- StoreKit 單件商品載入清單

## 安裝

```bash
python3 install_hide_upcoming_effects.py \
  /Users/zhouchenghan/Desktop/iosAPP/beyblade
```

## 驗證

```bash
python3 validate_hide_upcoming_effects.py \
  /Users/zhouchenghan/Desktop/iosAPP/beyblade
```

## 下次重新開啟

將 `EffectType.swift` 的 `allCases` 與 `shopEffects`
加回五個 case，並將 `temporarilyHiddenEffects` 清空即可。
Product ID 與 renderer 不需要重建。
