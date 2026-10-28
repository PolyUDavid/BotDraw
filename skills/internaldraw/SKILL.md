---
name: internaldraw
description: >-
  Use when redrawing paper/SI/extended-data figures as 1:1 editable vector A-PPT
  (optional Blender B): measure-then-place, full OMML, refined layered UI, arrow
  tails, OCR font+overlap gate, SI gates. Load this first.
---
# internaldraw

## Load order
1. This skill
2. quality-merge
3. fig01-gold-bar
4. full-omml
5. arrow-proportion
6. **scene-ui（精致分层 UI — 每图强制）**
7. **type-calibration + text-layout-clearance（t48u OCR 字号+叠字硬门禁）**
8. layout-gates / a-ppt / faithful-replica / vector-ui
9. Optional B

## Non-negotiables
Faithful 1:1; region loop; hard FAIL on overlap, plain math, bare/giant arrows, **coarse UI on any fig**, h_med&lt;1.00, **OCR `font_pass`/`overlap_pass` false or missing `qa/<fig>_ocr_font_overlap.json`**.
后续所有图同一精致 UI 标准，不少项。

## OCR gate (Kevin t48u)
```bash
FIG_ROOT=<figroot> python tools/ocr_font_overlap_gate.py A FigXX
```
Must pass before freeze / Drive.
