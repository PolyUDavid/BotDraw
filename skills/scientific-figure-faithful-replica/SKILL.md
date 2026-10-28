---
name: scientific-figure-faithful-replica
description: >-
  Use when faithfully reconstructing or repairing a scientific figure as
  editable PPT from a reference raster (left=orig, right=replica):
  geometry/panel IoU, chart semantics lock, OMML, Morandi/Times, round-trip
  overlay QA — not visual redesign.
---
# SCIENTIFIC FIGURE FAITHFUL REPLICA

## 0. Contract (highest priority)
**Faithful reconstruction / 临摹, NOT visual redesign.** The reference (left) defines palette, hierarchy, type scale, composition, axes, annotations, captions. Scientific records/user numbers are truth for quantitative values; if reference rendering disagrees with the record, FLAG — do not silently change numbers. The old PPT (right) is the correction target, not a layout template.

The replica must **read as a traced copy of the original**: same proportions for fonts, icons/images, panels, gutters, and element sizes (1:1 normalized geometry). If SBS overlay does not roughly register, it is a fail — redraw from ORIG, do not style-polish a wrong layout.

**Flat 2D by default.** No heavy 3D / emboss / thick drop-shadow / glassmorphism on cards, axes, or nodes. Only individual UI callouts the user/orig clearly need (e.g. steering wheel, car glyph) may be refined/volumetric.

Label simulated/trust results as synthetic. Do not pass symbolic cars as real CARLA screenshots. Do not invent bars, CIs, curves, points, n, or icons that imply unsupported experiments.

Also load local toolkit `/home/box/grokbot_tools` (FIG_LIB) and existing `a-ppt` constraints: no potrace; no dashed presets; OMML via `FIG_OMML=1`; slide size = reference ROI; overlap safety hard gate.

## 0a. Math = LaTeX → OMML (hard)
**Anything mathematical must be real editable OMML** (`m:oMath` / `a14:m` + AlternateContent), sourced from LaTeX:
- Subscripts/superscripts, Greek, Δ/ε/β/ρ/λ/σ, fractions, operators, `n_null`, `r_t`, `ε_h`, `N_path`, `p_err`, `p_TP`, `F_{ORIGIN}`, etc.
- Forbidden as sole solution: screenshot math, plain Unicode fake subscripts, doubled text+OMML ghosting.
- Before delivery: count `oMath` in PPTX XML ≥ number of math tokens on the reference; PowerPoint QA preferred (LO/web fallback alone is not a rebuild trigger).

## 0b. Progressive fidelity bar (clear vector > infinite overlay)
**Deliver clear, editable vector PPT that is overall close to the original — as 临摹.** Improve step by step — do not burn cycles on infinite pixel overlay of trivial glitches.

Chase / must fix:
- Wrong structure, panel layout, chart type, missing/wrong numbers or equations
- Wrong font/image/element **scale vs orig** (not 1:1)
- Overlaps, clipped text, illegible digits, wrong hierarchy
- Fake/missing math when OMML is required
- Non-vector finish (potrace, whole-slide raster) unless an allowed inset
- Heavy 3D decoration that makes it look unlike the flat orig

Do **not** obsess over (stop when overall vector 临摹 match is clear):
- LibreOffice / web-preview OMML fallback quirks (stacked fractions looking nested, AA halos)
- Sub-pixel anti-alias, 1–2 px edge ghosts, tiny badge AA
- Micro MAE floors caused only by renderer differences when PowerPoint shows correct OMML

Gates A/B/D and editability still hard-stop delivery; Gate E overlay is a **diagnostic**, not an infinite chase for trivial residuals once structure + readable vector OMML + 1:1 proportions are right.

## 1. Input parsing
1. Read per-figure checklist (e.g. `FIGURE_FIXES_28.md`) verbatim.
2. Open same-numbered reference + replica PNGs (or left/right halves of side-by-side PDF).
3. Crop only comparison headers/margins; keep aspect. Extract panels, titles, legends, values, equations, captions.
4. Build immutable `FigureSpec` before editing shapes: `{figure_id, reference_crop, W, H, panels, text_items, shapes, axes, chart_data, math_objects, image_insets, caption, checks}`.
5. Never reconstruct charts from guessed values. If data insufficient, keep source as embedded image or mark `requires verified data`.

## 2. Geometry (1:1 临摹)
- Normalize coords `(u=x/W, v=y/H)` on cropped reference; place PPT shapes with the same normalized bboxes.
- Match panel x/y/w/h, gutters, padding, row heights, axis heights, caption area, radii, arrow lengths, icon scale, plot-to-table ratios — **fonts and inset images included**.
- Group by semantic panel; keep paths/text separately editable.
- Slide aspect = **reference figure ROI** (not 16:9). No unequal x/y fit-to-page.
- Preserve whitespace; no shrink-to-top-half; no stretch into wrong density.
- No label overlap across panels; non-autofit boxes; wrap points matching reference.

## 3. Fonts, math, color
- Times New Roman (or matching serif) where reference uses it; match case/weight/leading **and size ratio to orig**.
- Sample colors from reference pixels; Morandi only if orig is already soft; no neon dashboard decor.
- Formulae: keep exact LaTeX; insert real editable **OMML** (`FIG_OMML=1`). If OMML unavailable, vector SVG + `math_sources.json` and mark non-native — still not screenshot math.
- Preserve `Π_F`, `ρ`, `λ_e`, `Δr`, `β`, `σ`, true minus signs, etc.
- Prefer PowerPoint for OMML visual QA; LO/web preview may distort fractions — that alone is not a rebuild trigger.

## 4. Chart semantic lock
- Exact axis type/direction/range/ticks/origin/grid/series/mark type/thresholds/units.
- Bar≠line≠dots≠stacked; discrete rates ≠ smoothed continuous categorical axis.
- Preserve signed axes, zero-lines, fixed thresholds (e.g. −0.05).
- Tables: every row/column/value/legend; no silent ellipses.
- Named categories (`M0–M5`, `TP/FA/MS/NULL`, `PASS/MISS/·`, etc.) must not be renamed or generalized (e.g. ■/· ≠ ✓/✗).
- Schematic bifurcation: compute from stated equations at stated grids — not fabricated empirics.
- Label non-screenshot insets as illustration/schematic.

## 5. HARD GATES (all must pass)
- **A Semantic 100%:** panels, values, units, tags, equations, notes.
- **B Structure ≥95%:** panel IoU ≥0.95; relative positions; ≤1% size/pos error target; **font/image scale 1:1 vs orig**.
- **C Fonts/graphics:** no unexpected family or chart-type change; palette match; h_med ∈ [0.95, 1.05]; **flat 2D unless orig UI needs volume**.
- **D Layout 100%:** no clip/overlap/wrong order/illegible digits/extra blank regions; **panel_side_match**; **text_in_box_pass**; Key strip **key_grid_iou≥0.90**.
- **E Round-trip:** PPTX→PNG same size; 50% overlay + abs-diff as diagnostic — structure must register as 临摹; stop only when residual is renderer 毛刺 (§0b).
- **F Editability + math:** native text/shapes/charts; verify OMML in XML before claiming it; **every math token is OMML**.

Never finalize with failed A/B/D/F. No “looks good” self-cert. Do not fail delivery solely on trivial Gate-E MAE floors from LO fallback.

## 6. Per-figure QA deliverable
`TITLE_MATCH`, `PANEL_COUNT_ORDER`, `GEOMETRY_IOU`, `TEXT_OVERLAPS`, `MATH_COUNT_MATCH` (+ native OMML count), `DATA_DIGIT_CHECK`, `AXIS_CHART_SEMANTICS`, `COLOR_FONT_STYLE`, `CAPTION_NOTES`, `FLAT_2D_OK`, overlay path, editable status, unresolved gaps (label residual 毛刺 as non-blocking when §0b applies).

## 7. Batch
- One editable slide/group per figure; process in order; QA each before next.
- Fix structural/semantic first, then font/math, axes, palette; strip unintended 3D.
- Improve incrementally across versions; do not embellish for aesthetics over fidelity.
- Persist these rules as skill; do NOT persist article-specific numbers as global defaults.

## 8. Local paths (REGAIN example)
- Pack: `/home/box/nature_data/trf_ppt/refs/regain_fidelity_pack/` (`FIGURE_FIXES_28.md`, tracker CSV)
- Orig: `/home/box/nature_data/trf_ppt/orig/`
- PPT: `/home/box/nature_data/trf_ppt/out_A/`
- Toolkit: `/home/box/grokbot_tools` with `FIG_V2=1 FIG_OMML=1 FIG_CLEAN=1`

## Layout hard gates (t201)
Also load [paper-figure-layout-gates](sand-workflow:paper-figure-layout-gates).
Require **`text_in_box_pass`**, **`panel_side_match`** (no L/R mirror vs ORIG), **`key_grid_iou`≥0.90** when a Key/Results strip exists. Coords must include `parent_panel`+`side`. Overflow / wrong-side UI / Key cell drift = hard FAIL equal to overlap.
