---
name: paper-figure-hierarchical-measure
description: >-
  Use when redrawing paper figures: measure big panels then small modules, group
  text into whole-block text boxes (not one-line-per-shape), map ORIG px 1:1 to
  PPT, plan full layout before draw, real OMML for all math.
---
# Hierarchical measure-then-place (paper figures)

Companion: [paper-figure-quality-merge](sand-workflow:paper-figure-quality-merge), [paper-figure-type-calibration](sand-workflow:paper-figure-type-calibration), [paper-figure-dense-region-pipeline](sand-workflow:paper-figure-dense-region-pipeline), [paper-figure-a-ppt](sand-workflow:paper-figure-a-ppt).

## Order (like painting)
1. **Big blocks** — panel frames (P1…Pn, KEY) from ORIG bbox; slide size = ORIG px (1:1).
2. **Small blocks** — subcards, icon wells, loop boxes, badge slots inside each panel.
3. **Text blocks** — group related copy into **one text box per content block** (multi-line wrap OK). **Ban** one independent shape per OCR line when lines belong to the same block.
4. **Icons / arrows / vehicles** — measured slots + Confirmation-grade vector or Cycles (B only).
5. **Math** — every formula = **real OMML** (`m:oMath`); no screenshot math, no long-term ASCII stand-ins.

## Coordinate contract
- ORIG `(x,y,w,h)` maps **symmetrically** to PPT EMUs/px on a slide whose size equals ORIG.
- UI sizes follow ORIG proportions; place from the measure table only — no eyeballing.
- Write `diag/<fig>_measure_coords.json` with hierarchy: `panels[] → modules[] → text_blocks[] + omml_slots[] + icons[]`, each with `font_px_orig` / bbox / z-order.

## Typography
- Measure ink height per **block** (and hero metrics separately); target h_med 1.05–1.16.
- Prefer enlarging the text box / wrap over `shrinkText` or global `FIG_TYPE_SCALE` after layout.

## Gate before draw / freeze
- Full hierarchical plan + z-order written **before** Drawer for that region.
- One region PASS (indistinguishable SBS + overlap + text_in_box + OMML) before next.
- No Drive “完成” until `qa/<fig>_indistinguishable.json` pass=true.
