---
name: paper-figure-type-calibration
description: >-
  Use when paper-figure text looks too big/small or Confirmation h_med is off:
  OCR paired height QA (qa_ocr2 + ocr_font_overlap_gate), zone
  title/body/caption ratios, measure-then-place px from ORIG — never whole-slide
  FIG_TYPE_SCALE as the only fix.
---
# Paper figure type calibration — measure ORIG then place

Companion to [paper-figure-quality-merge](sand-workflow:paper-figure-quality-merge), [paper-figure-hierarchical-measure](sand-workflow:paper-figure-hierarchical-measure), [paper-figure-text-layout-clearance](sand-workflow:paper-figure-text-layout-clearance), [paper-figure-fig01-gold-bar](sand-workflow:paper-figure-fig01-gold-bar).

## Goal
Fonts follow **ORIG proportions** (title : body : caption : hero), then optional small zone bump Kevin asks for — never eyeballing or late global `FIG_TYPE_SCALE`.

## Hard gate (Kevin t48u) — OCR required before PASS
Do **not** claim PASS / freeze / Drive without a fresh OCR run:

```bash
FIG_ROOT=<figroot> python tools/ocr_font_overlap_gate.py A FigXX
```

Must write `qa/<fig>_ocr_font_overlap.json` with:
- `font_pass: true` — paired RapidOCR heights vs ORIG
- `h_med` in **0.92–1.22** hard (preferred **1.00–1.16** Confirmation gold)
- **zero** per-pair outliers outside **0.75–1.40** (giant chip / tiny label)
- companion `qa_ocr2` / `qa/<fig>_type_calib.json` still required

Missing JSON or stub (`n_paired=0` with no error explanation) = **FAIL**, not soft warning.

## Technique

### A. OCR paired heights
1. Normalize ORIG and A PNG to same pixel width.
2. RapidOCR via `qa_ocr2.py` **and** `tools/ocr_font_overlap_gate.py`; match strings (sim ≥0.85).
3. `h_ratio = redraw_box_h / orig_box_h`; report **h_med** + zone medians + outlier list.
4. Gold band: h_med **1.05–1.16** (floor ≥1.00) unless Kevin asks larger — then re-measure and keep text_in_box.
5. Fix outliers **per block** (measure ORIG ink → set `font_px_orig`), never slide-wide scale.

### B. Manual crop rulers (Greek / OMML)
Measure ink bbox height in px → `font_px_orig` per **text_block** in `diag/<fig>_measure_coords.json`. Zone ratios from ORIG alone; place with one multiplier per zone.

### C. Kevin「整体再大一点」
Zone bump ×1.08–1.12 from measured ORIG px; enlarge frames or wrap **before** shrinking type. Ban slide-wide scale after dense freeze.

## Shrink-only local fit (Fig01 t33 lesson)
- After measure+place, fitting a string into its slot may **only shrink** (or wrap / widen frame).
- **Ban** `_LOCAL_MULT` and any short-string boost that enlarges chips (`edge`, `Hybrid`, `inference`, protocol tags) into giant overlays — that caused t33u P1/KEY disasters.
- Never re-enable bak OCR overlays that leak superseded glyphs.

## Placement contract
- `font_px_orig` + zone role before Drawer.
- Real **OMML** for all math; measure γ / subscripts from ORIG ink.
- Dense figs: calibrate **per region** ([dense-region-pipeline](sand-workflow:paper-figure-dense-region-pipeline)).

## Deliver
`qa/<fig>_type_calib.json` + `qa/<fig>_ocr_font_overlap.json`: orig zone px, ratios, h_med before/after, bumps, outliers, note shrink-only.
