---
name: paper-figure-indistinguishable-gate
description: >-
  Use before claiming any paper-figure PASS or Drive deliver: hard self-check vs
  ORIG — OCR/overlap, type uniformity, 叠图, OMML, arrows, gold_bar UI, complete
  media slots (no cut-off; t58u). Any defect or missing artifact = FAIL.
---
# Indistinguishable gate

**t54u/t58u：** 无 artifact 禁 PASS。门禁数字 PASS ≠ 肉眼过关。

## Absolute FAIL
1. 叠字（OCR 或目视）
2. 叠图
3. 字号不齐 / 错尺度
4. 布局 gutter 乱
5. 内容错漏
6. 箭头无小尾巴 / 轴朝内
7. 粗糙 UI / 缺 gold_bar 字段
8. 假公式
9. Key 穿格
10. 缺 ocr / layout JSON
11. Kevin 裁切仍指出硬伤
12. **媒体截断/裁半** 或缺 `qa/<fig>_media_slots.json` / 任一槽 `complete:false`
13. 仅散文 / 空 pass:true

## Self-check
双门禁脚本 + 目视 SBS + media_slots + omml + arrows + scene_ui + layout_gates + indistinguishable.json。
媒体规则见 [paper-figure-media-slot-harmony](sand-workflow:paper-figure-media-slot-harmony)。
