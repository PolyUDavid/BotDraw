---
name: internaldraw
description: >-
  Use when redrawing paper/SI/extended-data figures as 1:1 editable vector A-PPT
  (optional Blender B): measure-then-place, full OMML, refined layered UI, arrow
  tails, OCR font+overlap, same-type+叠图 layout gates. Load this first.
---
# internaldraw

## Load order
1. This skill
2. quality-merge
3. fig01-gold-bar
4. full-omml
5. arrow-proportion
6. scene-ui（精致分层 UI — 每图强制）
7. type-calibration + text-layout-clearance（t48u OCR 字号+叠字）
8. **layout-distribution（t49u 同类型字号齐 + 叠图 + 布局分布）**
9. layout-gates / a-ppt / faithful-replica / vector-ui
10. Optional B

## Non-negotiables
Faithful 1:1; region loop; hard FAIL on 叠字、**叠图**、同区同 role 字号不齐、plain math、bare/giant arrows、coarse UI、missing gate JSONs.

## Gates (Kevin t48u + t49u)
```bash
FIG_ROOT=<figroot> python tools/ocr_font_overlap_gate.py A FigXX
FIG_ROOT=<figroot> python tools/layout_type_shape_gate.py A FigXX
```
Both must pass before freeze / Drive.
