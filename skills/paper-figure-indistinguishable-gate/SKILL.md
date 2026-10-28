---
name: paper-figure-indistinguishable-gate
description: >-
  Use before claiming any paper-figure PASS or Drive deliver: hard self-check vs
  ORIG — OCR font/overlap, same-type uniformity, 叠图 shape clearance, full OMML,
  arrows, gold_bar layered UI. Any defect or missing artifact = FAIL (t53u/t54u).
---
# Indistinguishable gate (+ gold_bar UI)

Layout/text/structure must not show wrong panels, overflow, uneven type, or coarse defects.
Decorative UI: **gold_bar checklist + icon SBS** ([paper-figure-scene-ui](sand-workflow:paper-figure-scene-ui), [paper-figure-gold-bar-calibration](sand-workflow:paper-figure-gold-bar-calibration)).

**t54u：** 无 artifact 禁止宣称 PASS。散文「看起来精致」不够。

## Absolute FAIL
1. Reader-visible 叠字 — OCR `overlap_pass` false
2. Reader-visible **叠图** — `shape_overlap_pass` / `text_shape_clear_pass` false
3. Wrong or uneven font scale — OCR `font_pass` false **or** `type_uniform_pass` false
4. Arbitrary layout vs ORIG gutters / grid
5. Wrong/missing content
6. Bare/giant/hairline arrows (no 小尾巴)
7. Coarse UI **or** missing `gold_bar_ref` / `icon_sbs` / checklist fields on UI figs
8. Plain-only math where ORIG has formulas
9. Key cell bleed
10. Missing `qa/<fig>_ocr_font_overlap.json` or `qa/<fig>_layout_type_shape.json`
11. PASS while Kevin crops still match hard defects
12. Axes with inward tips — `axis_arrows_outward_pass` false/missing
13. Claiming PASS with only prose / `"pass":true` and no gold_bar evidence

## Self-check
```bash
FIG_ROOT=<figroot> python tools/ocr_font_overlap_gate.py A FigXX
FIG_ROOT=<figroot> python tools/layout_type_shape_gate.py A FigXX
```
SBS + omml + arrows + scene_ui(gold_bar) + layout_gates(axis outward) + both gate JSONs + indistinguishable.json.
