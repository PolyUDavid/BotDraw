---
name: paper-figure-type-calibration
description: >-
  Use when paper-figure text looks too big/small, uneven within the same type,
  or Confirmation h_med is off: OCR paired height QA, same-role font lock
  (t49u), zone ratios, measure-then-place — never whole-slide FIG_TYPE_SCALE as
  the only fix.
---
# Paper figure type calibration — measure ORIG then place

Companion to [paper-figure-quality-merge](sand-workflow:paper-figure-quality-merge), [paper-figure-hierarchical-measure](sand-workflow:paper-figure-hierarchical-measure), [paper-figure-text-layout-clearance](sand-workflow:paper-figure-text-layout-clearance), [paper-figure-layout-distribution](sand-workflow:paper-figure-layout-distribution), [paper-figure-fig01-gold-bar](sand-workflow:paper-figure-fig01-gold-bar).

## Goal
Fonts follow **ORIG proportions** (title : body : caption : hero), then optional small zone bump Kevin asks for — never eyeballing or late global `FIG_TYPE_SCALE`.

## Hard gates before PASS
**t48u OCR size vs ORIG** + **t49u same-type lock**:

```bash
FIG_ROOT=<figroot> python tools/ocr_font_overlap_gate.py A FigXX
FIG_ROOT=<figroot> python tools/layout_type_shape_gate.py A FigXX
```

- `qa/<fig>_ocr_font_overlap.json`: `font_pass`, h_med band, no size outliers
- `qa/<fig>_layout_type_shape.json`: `type_uniform_pass` — within each `(panel, role)`, font max/min ≤ 1.08

Missing JSON = FAIL.

## Same-type consistency (Kevin t49u)
1. Tag every text block with `role` (`title|section|body|caption|chip|badge|hero|axis|key_cell|footnote|…`).
2. One `font_px` per `(panel, role)` from ORIG median ink for that role.
3. Overflow: wrap / widen / shrink **entire role group** together — never one stray chip larger/smaller than siblings.
4. Record roles in `diag/<fig>_measure_coords.json` before Drawer.

## Technique

### A. OCR paired heights
1. Normalize ORIG and A PNG to same pixel width.
2. RapidOCR via `qa_ocr2.py` **and** `tools/ocr_font_overlap_gate.py`; match strings (sim ≥0.85).
3. `h_ratio = redraw_box_h / orig_box_h`; report **h_med** + zone medians + outlier list.
4. Gold band: h_med **1.05–1.16** (floor ≥1.00) unless Kevin asks larger — then re-measure and keep text_in_box.
5. Fix outliers **per role group**, never slide-wide scale.

### B. Manual crop rulers (Greek / OMML)
Measure ink bbox height in px → `font_px_orig` per **text_block** in `diag/<fig>_measure_coords.json`. Zone ratios from ORIG alone; place with one multiplier per zone/role.

### C. Kevin「整体再大一点」
Zone bump ×1.08–1.12 from measured ORIG px; enlarge frames or wrap **before** shrinking type. Ban slide-wide scale after dense freeze. Bumps apply **per role**, keeping siblings equal.

## Shrink-only local fit (Fig01 t33 lesson)
- After measure+place, fitting may **only shrink** (or wrap / widen frame).
- **Ban** `_LOCAL_MULT` short-string boosts (`edge`, `Hybrid`, `inference`) — causes uneven type + giant overlays.
- Never re-enable bak OCR overlays.

## Placement contract
- `font_px_orig` + `role` + zone before Drawer.
- Real **OMML** for all math.
- Dense figs: calibrate **per region** ([dense-region-pipeline](sand-workflow:paper-figure-dense-region-pipeline)).

## Deliver
`qa/<fig>_type_calib.json` + `qa/<fig>_ocr_font_overlap.json` + `qa/<fig>_layout_type_shape.json`.
