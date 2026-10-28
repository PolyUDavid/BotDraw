---
name: paper-figure-text-layout-clearance
description: >-
  Use when paper-figure text overlaps, graphics overlap, overflows boxes, or
  crowds arrows/icons: OCR text–text gate, shape clearance, whole-block boxes,
  padding, wrap before shrink, z-order; self-check each region while drawing
  (t58u).
---
# Paper figure text + graphic layout clearance

## Principle
Measured slots first. **叠字 and 叠图 are hard FAIL.** OCR gate PASS 仍须目视（t58u：门禁可假阴性）。

## Self-check while drawing（t58u）
每区落笔后立刻查叠字/骑边/出框；发现即改，禁止整页攒着修。

## Hard gates
```bash
FIG_ROOT=<figroot> python tools/ocr_font_overlap_gate.py A FigXX
FIG_ROOT=<figroot> python tools/layout_type_shape_gate.py A FigXX
```
Require overlap_pass、shape_overlap_pass、text_shape_clear_pass、text_in_box_pass。
Office check-overlap alone **not enough**.

## Whole-block text
One box per content block；禁一行一 shape；math = 真 OMML。

## Clearance
1. Box padding ≥2–4 px ink inside border
2. text–text gap ≥0.3× smaller font
3. shape–shape IoU &lt; 0.05
4. text–arrow ≥1.5× shaft
5. Panel letters / titles **不得压** 截图标题条或媒体（ED）
6. Z-order: fill → chrome → pics → arrows → text/OMML

## If still overlaps
Widen frame → wrap → role-group shrink → re-gate + 目视 SBS。
