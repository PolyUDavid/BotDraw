---
name: paper-figure-media-slot-harmony
description: >-
  Use when paper-figure photo/UI/3D slots are cut off, incomplete,
  disharmonious, or Kevin asks for AI-filled media inserts; also when
  self-checking crop completeness while redrawing A-PPT (t58u).
---
# Media-slot harmony + crop completeness (Kevin t58u)

## Problem
OCR/layout gates can PASS while Kevin still sees **文字重叠**、**截图裁半**、照片/3D 槽不和谐。必须 **边画边自检** + 完整媒体槽。

## Self-check while drawing（强制）
每完成一区或插入一张媒体后立刻：
1. **文字**：目视清叠；跑 `ocr_font_overlap_gate`；叠字/骑边/出框立刻改（整块框、padding、缩字、挪箭头），禁止攒到整页。
2. **媒体完整**：对照 ORIG 同区，插入图须整块可见（车/电池包/机柜/仪表盘不得裁半、缺角）。
3. **槽框**：picture 框 ≥ 内容；禁止框大半图半截。
4. **标签 vs 媒体**：panel 字母/标题不得压截图标题条（ED 尤其）。
5. 写 `qa/<fig>_media_slots.json`：每槽 `{id, source, complete, method: orig_crop|ai_fill|vector, notes}`；任一 `complete:false` → 不得 scene_ui/indistinguishable PASS。

## 媒体槽优先级
1. **完整 ORIG 裁切**（首选）：按面板 bbox 裁满。
2. **AI 补图插入**（t58u 允许）：裁切仍不完整或矢量扁图标不和谐时，用 GenerateImage（对照 ORIG）生成和谐 3D/设备/UI，**插入图片槽**；外框/标题/公式/箭头仍矢量+真 OMML。
3. **纯矢量**：仅简单图标且能对齐 gold_bar。

## AI 生图硬边界
- 允许：局部 media slot。
- 禁止：整页 AI 冒充可编辑 A-PPT；禁止生图代替公式/坐标轴/可编辑标签。
- 产物进 `assets/<fig>/`，`method=ai_fill` 记入 media_slots.json；插入后仍双门禁 + SBS。

## Hooks
清叠：[paper-figure-text-layout-clearance](sand-workflow:paper-figure-text-layout-clearance)
总闸：[paper-figure-quality-merge](sand-workflow:paper-figure-quality-merge) / [botdraw](sand-workflow:botdraw)
PASS：[paper-figure-indistinguishable-gate](sand-workflow:paper-figure-indistinguishable-gate) — 缺 media_slots.json = FAIL
