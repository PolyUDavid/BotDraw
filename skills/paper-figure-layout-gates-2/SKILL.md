---
name: paper-figure-layout-gates
description: >-
  Hard layout gates for 1:1 paper-figure A-PPT: text_in_box_pass (no overflow),
  panel_side_match (no L/R mirror vs ORIG), key_grid_iou (bottom Key/Results
  cell IoU + hero metric type scale). Load with paper-figure-quality-merge
  before Drawer or before claiming PASS. Use when text spills boxes, a panel's
  UI is on the wrong side, Key strip cells misalign, or metric font ratios (e.g.
  99.98%) drift.
---
# Paper figure layout gates（文字入框 · 左右不镜像 · Key 网格）

Companion to [paper-figure-quality-merge](sand-workflow:paper-figure-quality-merge).
Absorbs executable layout rules from Scientific Illustrator audit taxonomy,
Changhooo native-layout/typography, FigEdit `pptx_text_fit`, nature-paper2ppt
overflow=block, nature-figure panel-alignment, open-design Cursor rails
(adapted to ORIG canvas), and ts-pptx conservative measure ideas — **without**
adopting 16:9 decks, shrink-to-fit delivery, or hybrid crop defaults.

## Hard gates (any FAIL = no deliver / no next region)

### 1. `text_in_box_pass`
- Every editable text run's **ink bbox** must lie inside its parent shape or
  declared label slot. Margin ≥ `max(2px, 0.02 * min(box_w, box_h))`.
- `autofit = none`. Exported OOXML must not contain effective `a:normAutofit`,
  `a:spAutoFit`, or `fontScale` < 100%.
- Prefer shorter copy / larger measured box / split lines — **never** silent
  shrink as the layout strategy.
- Reviewer: structure (shape vs text extents) + renderer SBS crop. Treat glyph
  past border as hard fail (same severity as overlap).

### 1b. `wrap_2line_center_when_overflow` (Kevin t205)
- If a **single-line** title/metric strip is wider than its parent pill/box
  (e.g. `Average confidence across scenarios: 92.72%`, long entropy titles):
  **prefer 2 centered lines + modestly smaller measured pt** so ink fits with
  margin — not one stretched line past the border.
- Keep reading order; hero numbers may stay on line 2 alone when clearer.
- Still ban PPT autofit; set explicit font size from measure, then wrap.
- Scan whole figure for the same pattern before PASS.

### 2. `panel_side_match`
- For each panel / subregion, classify child objects (UI icons, charts, timeline
  chips, callouts) as Left / Right / Center (or Top / Bottom) relative to the
  **panel** mid-line using ORIG OCR/contour centers.
- Replica must match ORIG side for ≥ **95%** of paired children.
- **Mirror FAIL examples:** ORIG panel-5 timeline+UI stacked on the **left**,
  replica dumps the same UI to the far **right**; icon column and text column
  swapped inside a card.
- Designer must write `side` + `parent_panel` on every row of
  `diag/<fig>_coords.json`. Drawer places only those slots.

### 3. `key_grid_iou`
- Bottom Key / Results / legend strip: cell count and reading order = ORIG.
- Each Key cell bbox vs ORIG OCR/contour cell: **IoU ≥ 0.90**.
- Hero metrics inside cells (accuracy `%`, latency, speedup `240-538x`, etc.):
  ink height ratio `h_med ∈ [1.00, 1.05]` vs ORIG (e.g. Selection Accuracy
  `99.98%` must not look like body text).
- Write `qa/<fig>_key_grid.json` with per-cell IoU before whole-figure PASS.

## Measure-then-place additions
Each coords row should carry:
```json
{
  "id": "P5_step3_ui",
  "parent_panel": "P5",
  "side": "L",
  "slot_kind": "ui|text|chart|key_cell|badge",
  "bbox": [x0, y0, x1, y1],
  "font_px_orig": 22
}
```
Drawer refuses objects missing `parent_panel`+`side` when the parent region has
a side map.

## Reviewer checklist (layout)
1. Run existing overlap / hierarchy gates.
2. Compute `text_in_box_pass` (ink vs parent).
3. Flag single-line overflow candidates → apply `wrap_2line_center_when_overflow`.
4. Compute `panel_side_match` from ORIG vs replica centers.
5. If figure has a Key/Results strip: `key_grid_iou` + hero `h_med`.
6. Record in `qa/<fig>_gate.json`:
   `text_in_box_pass`, `panel_side_match`, `key_grid_iou`, `key_grid_pass`,
   `wrap_2line_applied`, `layout_gates_version` (`2026-10-27-t205`).

## Corrector order (layout-specific)
Wrong side → move whole child group to measured slot (do not flip locally).
Overflow → enlarge slot to measured ORIG box **or** 2-line center wrap; never
PPT shrinkText. Key grid → rebuild cell geometry from coords table, then type scale.

## Anti-patterns
- Eyeballing “looks balanced” after a mirror.
- Growing a text box past ORIG slot to hide overflow without updating coords.
- Treating Key as free-form badges instead of a measured grid.
- Claiming PASS while any of the three gates is false/missing.
- One long line that clips the pill instead of two centered lines.

## Sources
See `/workspace/kevin_figure_skills_pack/LAYOUT_SKILLS_SURVEY.md`.
