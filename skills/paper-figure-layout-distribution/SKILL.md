---
name: paper-figure-layout-distribution
description: >-
  Use when paper-figure fonts look uneven within a type, graphics overlap (叠图),
  or layout spacing looks arbitrary: same-role type lock, shape/graphic
  clearance, ORIG gutters — Kevin t49u hard gate with
  tools/layout_type_shape_gate.py.
---
# Paper figure layout distribution (Kevin t49u)

Companion to [paper-figure-type-calibration](sand-workflow:paper-figure-type-calibration), [paper-figure-text-layout-clearance](sand-workflow:paper-figure-text-layout-clearance), [paper-figure-hierarchical-measure](sand-workflow:paper-figure-hierarchical-measure), [paper-figure-quality-merge](sand-workflow:paper-figure-quality-merge).

## Why
OCR cleared 叠字, but Kevin still saw **uneven same-type sizes**, **叠图** (cards/icons/badges riding each other), and **arbitrary spacing**. Those are hard FAIL before PASS / Drive.

## Hard gate before PASS

```bash
FIG_ROOT=<figroot> python tools/ocr_font_overlap_gate.py A FigXX
FIG_ROOT=<figroot> python tools/layout_type_shape_gate.py A FigXX
```

Require both JSONs:
- `qa/<fig>_ocr_font_overlap.json` — `font_pass` ∧ `overlap_pass` (t48u)
- `qa/<fig>_layout_type_shape.json` — `type_uniform_pass` ∧ `shape_overlap_pass` ∧ `text_shape_clear_pass` (t49u)

Missing either = FAIL.

## 1. Same-type font lock (`type_uniform_pass`)
Within one **panel/region**, every text block that shares a **role** must use the **same** `font_px`:

Roles (examples): `title`, `section`, `body`, `caption`, `chip`, `badge`, `hero`, `axis`, `key_cell`, `footnote`.

Rules:
1. Designer writes `role` + `font_px_orig` on every `text_blocks[]` row in `diag/<fig>_measure_coords.json`.
2. Drawer uses **one** px per `(panel, role)` — never per-string eyeballing.
3. Gate: within group, `max/min ≤ 1.08` and absolute Δ ≤ 1pt; else FAIL with samples.
4. Fitting overflow: wrap / widen slot / **shrink the whole role group together** — ban shrinking one chip while siblings stay large.
5. Hero / OMML subscripts are separate roles; do not mix into `body`.

## 2. Graphic / shape clearance (`shape_overlap_pass` · 叠图)
Non-contained sibling shapes (cards, pills, icon wells, pics, badges) must **not** overlap:

- IoU ≥ 0.05 between siblings = FAIL (unless true parent contains child ≥85% area — text-in-card OK).
- Text riding a non-parent graphic: IoU ≥ 0.06 = FAIL (`text_shape_clear_pass`).
- Z-order still: fill → chrome → icons → arrows → text/OMML on top — but **geometry must not collide** even with z-order.
- Arrows/connectors excluded from 叠图 area test when tiny; shafts still need text clearance (t48u).

Fix order: move to ORIG measured slots → enlarge gutters → shrink decorative only if ORIG does → never hide overlap under opacity.

## 3. Layout distribution (合理布局)
1. **Big panels first**, then modules, then text — hierarchical measure.
2. Gutters / padding / column alignment copy **ORIG** measure table (1:1), not “looks balanced”.
3. Same-row siblings: equal visual weight and shared baseline when ORIG does.
4. Key/Results = measured grid (`key_grid_iou`); ban free-float badges across cells.
5. Crowded dual labels get **separate reserved slots** (mech vs Confidence, etc.).
6. If distribution drifts: rebuild coords from ORIG, do not nudge one box forever.

## Deliver
`qa/<fig>_layout_type_shape.json` + updated `diag/<fig>_measure_coords.json` with `role` on every text block.
Region freeze only when t48u OCR **and** t49u layout gates pass on that region/full slide.

## Anti-patterns
- Per-string font tweaks that break role uniformity
- Office overlap=OK while cards/icons still collide in preview
- Stacking badges to “save space” against ORIG gutters
- Claiming PASS on OCR alone after t49u
