---
name: paper-figure-text-layout-clearance
description: >-
  Use when paper-figure text overlaps, overflows boxes, or crowds arrows/icons:
  whole-block text boxes, padding from edges, line–text clearance, wrap before
  shrink, z-order rules.
---
# Paper figure text layout clearance (no overlap)

Companion to [paper-figure-type-calibration](sand-workflow:paper-figure-type-calibration), [paper-figure-hierarchical-measure](sand-workflow:paper-figure-hierarchical-measure), [paper-figure-fig01-gold-bar](sand-workflow:paper-figure-fig01-gold-bar).

## Principle
Measured slots first, then type that fits. Never drop large type into a tight frame and hope shrinkText saves it.

## Whole-block text (Kevin)
1. One text box per content block (multi-line wrap OK).
2. Ban one shape per OCR line when lines belong together.
3. Contradiction / war captions: **2-line whole block** in reserved slot.
4. Math = **real OMML** with reserved `omml_slots`.

## Clearance rules (before freeze)
1. **Box padding**: ink ≥2–4 px (or ≥0.04×box_h) inside border.
2. **text–text**: gap ≥0.3× smaller font px (or merge blocks).
3. **text–line / arrow**: clearance ≥1.5× shaft; shafts never cross glyphs.
4. **text–icon / badge**: reserved wells; no riding stroke.
5. **Crowded dual labels** (e.g. mech name vs Confidence%): **separate slots**, do not stack in one band.
6. **Key/Results**: clamp each string to its cell; ban cross-cell float.
7. **Z-order**: fill → chrome → icons → arrows → text/OMML on top.

## If it still overlaps
1. Widen/tall frame from ORIG measure.
2. Wrap 2 lines / tighten tracking.
3. Shorten only if ORIG does.
4. Last: tiny local px cut (−4–8%) on that block — **shrink-only**, never short-string `_LOCAL_MULT` boost.

## Gates
- `text_in_box_pass`; text–text findings = 0 for reader-visible collisions.
- Crop every crowded corner; &lt;3s visible collide → FAIL.
- Write residuals into `qa/<fig>_indistinguishable.json`.

## Anti-patterns
- shrinkText / fit=False overflow
- Absolute Y from OCR without block merge
- Raising type after arrows through the text band
- Bak OCR ghost layers
- Mech/conf or Key hero sharing one overloaded slot
