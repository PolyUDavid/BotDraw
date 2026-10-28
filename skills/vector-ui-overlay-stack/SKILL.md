---
name: vector-ui-overlay-stack
description: >-
  Use when faithfully redrawing a scientific/paper figure as editable vector PPT
  with OCR overlay, multi-layer vector UI matching orig contours (no symbol
  substitutes), and a fast Designer→Drawer→Reviewer→Corrector region gate —
  aligned with icebird1998/scientific-illustrator plus a-ppt.
---
# Vector UI + OCR overlay stack (临摹叠齐)

Rebuild paper figures as editable vector PPT. Combine [a-ppt](sand-workflow:a-ppt), [scientific-figure-faithful-replica](sand-workflow:scientific-figure-faithful-replica), and [Scientific Illustrator](https://github.com/icebird1998/scientific-illustrator): Designer → Drawer → Reviewer → Corrector, **one region at a time**.

Toolkit: `/home/box/grokbot_tools` (`FIG_LIB`). Dense UI refs: `kevin_quality` when present.

## Measure-then-place (Kevin t195 — stop layout drift)
1. **Coordinates before drawing.** For every text box, UI icon, panel, connector endpoint: measure absolute pixel bbox/center from ORIG (OCR JSON + contour measure). Write `diag/<fig>_coords.json` / `reconstruction_spec` fields (`x0,y0,x1,y1` or cx,cy,w,h).
2. **Drawer only places at measured coords** — no eyeballing, no “nudge until looks ok” as first step. Corrector adjusts only when overlay proves a measured slot is wrong.
3. **Arrows required.** Every directed connector must use slim arrowheads matching orig stroke/head proportion (`slim_arrow` / equivalent). **Lines without heads = FAIL.** Never fat PPT triangles / DOWN_ARROW presets.
4. One region per loop; pass local gate (incl. **overlap=1.00**, **text_in_box_pass**, **panel_side_match**) before next region.
5. Pass SI scorecard (sem/edit/overlap 1.00; align≥0.95; ref≥0.90). Stop glyph_face / texture_gap thrash.

## Hard rules
1. No MDI/emoji substitute for drawn UI — multi-part vector, orig outer bbox + silhouette ≤5%.
2. No ORIG image strips for reconstructable text/icons.
3. OCR overlay after each region and whole figure; `h_med` alone ≠ pass.
4. Overlap PASS hard gate; real OMML; no potrace / whole-slide raster / dash presets.
5. One figure at a time when user asked slow 临摹.

## Stack procedure
**A. Prep** orig + OCR + palette.  
**B. Designer** reconstruction_spec with **full coordinate table** (text + UI + arrows).  
**C. Measure** UI contours → `diag/*_measure.json`.  
**D. Drawer** place by coords; z-order back→front; slim arrows on every directed edge.  
**E. Reviewer** crop overlay + `office pptx check-overlap`.  
**F. Corrector** object-level to measured targets.  
**G. Whole-figure gate** then deliver pptx + overlay + SBS.

## Anti-patterns
Blind layout / post-hoc MAE farming; missing arrowheads; F.img titles; MDI for cars/battery/RSU; claiming PASS while text overlaps or connectors are headless.

## Credit
Region-gate contract from Scientific Illustrator (MIT). A-PPT rules remain Kevin’s a-ppt + faithful-replica.

## Layout hard gates (t201)
Also load [paper-figure-layout-gates](sand-workflow:paper-figure-layout-gates).
Require **`text_in_box_pass`**, **`panel_side_match`** (no L/R mirror vs ORIG), **`key_grid_iou`≥0.90** when a Key/Results strip exists. Coords must include `parent_panel`+`side`. Overflow / wrong-side UI / Key cell drift = hard FAIL equal to overlap.
