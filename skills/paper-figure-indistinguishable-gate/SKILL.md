---
name: paper-figure-indistinguishable-gate
description: >-
  Use before claiming any paper-figure PASS or Drive deliver: hard self-check vs
  ORIG — OCR font/overlap, same-type uniformity, 叠图 shape clearance, full OMML,
  arrows, refined layered UI. Any defect = FAIL.
---
# Indistinguishable gate (+ refined UI)

Layout/text/structure must not show wrong panels, overflow, uneven type, or coarse defects.
Decorative UI: **layered ORIG-grade fineness** ([paper-figure-scene-ui](sand-workflow:paper-figure-scene-ui)).

## Absolute FAIL
1. Reader-visible 叠字 — OCR `overlap_pass` false
2. Reader-visible **叠图** — `shape_overlap_pass` / `text_shape_clear_pass` false
3. Wrong or uneven font scale — OCR `font_pass` false **or** `type_uniform_pass` false (same role, different sizes)
4. Arbitrary layout vs ORIG gutters / grid
5. Wrong/missing content
6. Bare/giant/hairline arrows (no 小尾巴)
7. Coarse UI on any fig
8. Plain-only math where ORIG has formulas
9. Key cell bleed
10. Missing `qa/<fig>_ocr_font_overlap.json` or `qa/<fig>_layout_type_shape.json`
11. PASS while Kevin crops still match hard defects

## Self-check
```bash
FIG_ROOT=<figroot> python tools/ocr_font_overlap_gate.py A FigXX
FIG_ROOT=<figroot> python tools/layout_type_shape_gate.py A FigXX
```
SBS + omml + arrows + scene_ui + both gate JSONs + indistinguishable.json.
