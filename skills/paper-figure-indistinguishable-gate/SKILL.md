---
name: paper-figure-indistinguishable-gate
description: >-
  Use before claiming any paper-figure PASS or Drive deliver: hard self-check vs
  ORIG — OCR font size + text–text overlap, full OMML, arrows, and refined
  layered UI. Any defect = FAIL.
---
# Indistinguishable gate (+ refined UI)

Layout/text/structure must not show wrong panels, overflow, or coarse defects.
Decorative UI: **layered ORIG-grade fineness** ([paper-figure-scene-ui](sand-workflow:paper-figure-scene-ui)) — Kevin t38u/t39u: 精致 UI 每张图都不少，后续同标。

## Absolute FAIL
1. Reader-visible overlap/overflow — includes **OCR ink text–text** (`overlap_pass` false)
2. Wrong font scale vs ORIG — **OCR `font_pass` false** / h_med out of band / outliers
3. Wrong/missing content
4. Bare/giant/hairline arrows (no 小尾巴)
5. **Coarse UI**: flat brain/gear/icons, cartoon cars, single-shape fakes — any fig
6. Plain-only math where ORIG has formulas
7. Key cell bleed
8. PASS while Kevin crops still match hard defects
9. Missing `qa/<fig>_ocr_font_overlap.json` (Kevin t48u)

## Do NOT block only on
Pixel-identical decorative density when layered craft already matches; LO Times on true PPTX OMML.

## Self-check
SBS + omml_audit + arrow_gate + **scene_ui.json** + **ocr_font_overlap.json** (`font_pass` ∧ `overlap_pass`) + indistinguishable.json.
Region freeze only if local pass including UI craft **and** OCR gates.

```bash
FIG_ROOT=<figroot> python tools/ocr_font_overlap_gate.py A FigXX
```
