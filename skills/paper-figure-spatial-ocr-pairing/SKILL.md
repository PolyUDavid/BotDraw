---
name: paper-figure-spatial-ocr-pairing
description: >-
  Use when the same label is horizontal and vertical, when conditions are split,
  when OCR lines stay unmatched, or when font size is blamed on a bad pair.
  Global one-to-one matching keeps relation signs and digits. It does not rewrite
  the historical t48u PASS.
---
# Spatial OCR pairing

Load from [botdraw](sand-workflow:botdraw) with the t48u OCR gate. The historical gate is unchanged on purpose.

## What stays historical
`tools/ocr_font_overlap_gate.py` version `2026-10-28-t48u` still strips non-alphanumeric characters, can reuse one redraw box for several sources, and can pass while source lines remain unmatched. Do not retune `IOU_FAIL` or the `h_med` band to clear a sample. Those reports stay as measurement history.

## What this skill adds
```bash
python3 tools/spatial_ocr_pairing.py --source qa/<fig>_src_boxes.json --redraw qa/<fig>_redraw_boxes.json --out qa/<fig>_spatial_ocr_pairing.json
```
Boxes use the same normalized source frame (`id`, `text`, `x`, `y`, `orientation` `h|v`, `zone`). Exit 0 means the report was written, not that the figure passed.

When the OCR gate runs, it also writes `qa/<fig>_spatial_ocr_pairing.json` from the raw OCR polygons. `spatial_pairing_changes_historical_pass` is false.

## Rules
1. Keep every raw OCR token, confidence, polygon, and direction. Do not drop relation signs or digits while normalizing. Do not drop single characters silently.
2. One redraw box serves one source box. Horizontal and vertical copies of the same word do not pair with each other. A subscript fragment is not the full label. A numeric bound does not jump to another condition.
3. Unknown orientation is not horizontal. AABB-only height is marked approximate. Vertical text uses the normal, not the long side.
4. Report source total, excluded, paired, unmatched source, unmatched redraw, and reject reasons. Coverage and the font median are separate. Matched rows being fine does not excuse unmatched rows.
5. Re-recognize fragments on the same ROI on both sides. A merge keeps the original box ids and the rule. Low confidence does not vanish.
6. Classify each FAIL as: real missing or wrong glyph, real crop or occlusion, source semantic overlap, or pairing error. Give the same ROI crop and the ink gap. A pure recognition error keeps the original FAIL. A tool fix is a new version and a retest, not an edited old JSON.

## Stop
Do not loop the same pairing class. Follow `STOP_SAME_CLASS` in [paper-figure-quality-merge](sand-workflow:paper-figure-quality-merge).
