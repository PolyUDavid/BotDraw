---
name: paper-figure-font-renderer-proof
description: >-
  Use when substituting fonts, when glyph size or baseline does not match the
  source, or before claiming a face was actually used. fc-match is a prediction.
  Proof is the exported PDF's own font and span evidence.
---
# Font renderer proof

Load from [botdraw](sand-workflow:botdraw) next to [paper-figure-type-calibration](sand-workflow:paper-figure-type-calibration).

## When
A fallback face is suspected, ink does not match the source role, or a report names a specific font.

## Steps
1. Record `requested_font`, `fc_match_prediction`, installed file, license, and file hash separately. `fc-match` success does not mean this PDF used that face. Do not blame a font cache without evidence. Use only fonts already licensed on this machine.
2. Keep the exported PDF. Read its bytes:

```bash
python3 tools/quality_sync.py font-evidence --pdf prev/<variant>/<fig>.pdf --requested-font "Requested Family" --fc-match-prediction "Predicted Family"
```

`pdffonts` is optional (`poppler-utils`). If it is missing, the command still reads `/BaseFont` and sets span attribution to UNKNOWN. A page font list is not proof that one Greek glyph used that face.
3. A span face needs its own evidence object. Passing `fc-match` as that evidence is rejected.
4. Family-only trial: freeze geometry, size, weight, and paragraph, then change only the family. After that, adjust size, baseline, weight, and numeric sidebearing one variable at a time. Do not credit a role-size fix to a font install.
5. Same role stays consistent, including roles that are actually different (value, interval, condition). No global bold and no one-token boost. Calibrate to source ink, baseline, fraction bar, and column gap.
6. Rotated axis labels take height along the line normal, not the long side of the AABB. Unknown direction stays unknown.
7. If native PowerPoint was not opened, `native_application_review` is `NOT_PERFORMED`. A good LibreOffice Fallback is not a Choice layout certificate.

## Not a PASS
This command does not render the figure and does not certify a user plate. OCR `h_med` remains the separate t48u measurement.
