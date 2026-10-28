---
name: paper-figure-hierarchical-measure
description: >-
  Use when redrawing paper figures: measure big panels then small modules, group
  text into whole-block boxes with shared role font sizes, map ORIG px 1:1 to
  PPT, plan full layout before draw, real OMML for all math.
---
# Hierarchical measure-then-place (paper figures)

Companion: [paper-figure-quality-merge](sand-workflow:paper-figure-quality-merge), [paper-figure-type-calibration](sand-workflow:paper-figure-type-calibration), [paper-figure-layout-distribution](sand-workflow:paper-figure-layout-distribution), [paper-figure-dense-region-pipeline](sand-workflow:paper-figure-dense-region-pipeline).

## Order (like painting)
1. **Big blocks** — panel frames from ORIG bbox; slide size = ORIG px (1:1).
2. **Small blocks** — subcards, icon wells, badge slots; gutters from ORIG (t49u layout).
3. **Text blocks** — one box per content block; each row has **`role` + `font_px_orig`**; same `(panel, role)` → identical px.
4. **Icons / arrows / vehicles** — measured slots; **no 叠图** with siblings.
5. **Math** — real OMML only.

## Coordinate contract
- ORIG `(x,y,w,h)` → PPT 1:1.
- Write `diag/<fig>_measure_coords.json`: `panels[] → modules[] → text_blocks[]` with `role`, `font_px_orig`, bbox, z-order.
- Sibling modules: non-overlapping geometry; parent may contain children.

## Typography
- Measure ink per **role**; one px per `(panel, role)`.
- Prefer enlarge box / wrap; role-group shrink together; ban per-string scatter.

## Gate before draw / freeze
Full hierarchical plan before Drawer.
PASS needs t48u OCR + t49u `layout_type_shape_gate` + indistinguishable SBS.
