---
name: paper-figure-text-layout-clearance
description: >-
  Use when paper-figure text overlaps, graphics overlap (叠图), overflows boxes,
  or crowds arrows/icons: OCR text–text gate, shape/graphic clearance,
  whole-block boxes, padding, wrap before shrink, z-order.
---
# Paper figure text + graphic layout clearance

Companion to [paper-figure-type-calibration](sand-workflow:paper-figure-type-calibration), [paper-figure-layout-distribution](sand-workflow:paper-figure-layout-distribution), [paper-figure-hierarchical-measure](sand-workflow:paper-figure-hierarchical-measure).

## Principle
Measured slots first, then type that fits. Never drop large type into a tight frame and hope shrinkText saves it. **叠字 and 叠图 are both hard FAIL.**

## Hard gates before PASS (t48u + t49u)

```bash
FIG_ROOT=<figroot> python tools/ocr_font_overlap_gate.py A FigXX
FIG_ROOT=<figroot> python tools/layout_type_shape_gate.py A FigXX
```

Require:
- OCR `overlap_pass` — text–text ink IoU cleared
- `shape_overlap_pass` — cards/icons/badges/pics not colliding (IoU≥0.05 siblings)
- `text_shape_clear_pass` — text not riding non-parent graphics
- `text_in_box_pass` ([layout-gates-2](sand-workflow:paper-figure-layout-gates-2))

Office `check-overlap` alone is **not enough**.

## Whole-block text (Kevin)
1. One text box per content block (multi-line wrap OK).
2. Ban one shape per OCR line when lines belong together.
3. Contradiction / war captions: **2-line whole block** in reserved slot.
4. Math = **real OMML** with reserved `omml_slots`.

## Clearance rules (before freeze)
1. **Box padding**: ink ≥2–4 px (or ≥0.04×box_h) inside border.
2. **text–text**: gap ≥0.3× smaller font px; OCR gate 0 collisions.
3. **shape–shape (叠图)**: non-contained siblings IoU &lt; 0.05; place from ORIG slots.
4. **text–line / arrow**: clearance ≥1.5× shaft; shafts never cross glyphs.
5. **text–icon / badge**: reserved wells; no riding stroke.
6. **Crowded dual labels**: separate slots.
7. **Key/Results**: clamp to cells; ban cross-cell float.
8. **Z-order**: fill → chrome → icons → arrows → text/OMML — geometry still non-colliding.

## If it still overlaps
1. Widen/tall frame from ORIG measure.
2. Wrap 2 lines / tighten tracking.
3. Shorten only if ORIG does.
4. Role-group shrink (−4–8%) together — never one-off `_LOCAL_MULT`.
5. Re-run both gate scripts until pass.

## Anti-patterns
- Claiming PASS on OCR while cards/icons still overlap
- Hiding 叠图 with z-order / opacity
- Uneven chip sizes inside one role to dodge collision
