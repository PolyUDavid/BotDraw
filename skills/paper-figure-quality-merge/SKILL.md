---
name: paper-figure-quality-merge
description: >-
  Use when redrawing paper/SI figures as editable A-PPT and B+Blender with
  Confirmation-gold QA, full OMML, layered refined UI, OCR font+overlap (t48u),
  same-type+叠图 layout (t49u), and indistinguishable hard gate. Load before
  drawing or claiming PASS.
---
# Paper figure quality merge

**Final bar:** [paper-figure-indistinguishable-gate](sand-workflow:paper-figure-indistinguishable-gate).

**Locked stack (every fig, no exceptions):**
1. [paper-figure-fig01-gold-bar](sand-workflow:paper-figure-fig01-gold-bar) — clearance / process
2. [paper-figure-full-omml](sand-workflow:paper-figure-full-omml) — all ORIG math → real OMML
3. [paper-figure-arrow-proportion](sand-workflow:paper-figure-arrow-proportion) — clear head + 小尾巴
4. [paper-figure-scene-ui](sand-workflow:paper-figure-scene-ui) — layered refined UI
5. [paper-figure-layout-gates](sand-workflow:paper-figure-layout-gates) — axis ticks、Abl leaders、chart z-order、虚线、markers
6. [paper-figure-type-calibration](sand-workflow:paper-figure-type-calibration) + [paper-figure-text-layout-clearance](sand-workflow:paper-figure-text-layout-clearance) — **t48u OCR** font+叠字
7. **[paper-figure-layout-distribution](sand-workflow:paper-figure-layout-distribution)** — **t49u** same-role type lock + 叠图 + ORIG gutters

Also: dense-region, hierarchical-measure, layout-gates-2, feedback-to-skill, b-blender.

## Contract
One PPTX/fig; slide=ORIG; A pic=0; B=A+Cycles or B=A.
Before PASS run **both**:
```bash
python tools/ocr_font_overlap_gate.py A FigXX
python tools/layout_type_shape_gate.py A FigXX
```
Require `font_pass`∧`overlap_pass`∧`type_uniform_pass`∧`shape_overlap_pass`∧`text_shape_clear_pass`.

## Hard bans
Whole-slide paste; potrace; plain/fake math; coarse UI; bare/giant arrows; Drive before Kevin freeze; PASS on OCR alone while same-type fonts uneven or graphics overlap; per-string font tweaks that break role uniformity.

## Per-fig deliverables
`qa/<fig>_omml_audit.json`, `qa/<fig>_arrow_gate.json`, `qa/<fig>_scene_ui.json`, `qa/<fig>_layout_gates.json`, `qa/<fig>_ocr_font_overlap.json`, **`qa/<fig>_layout_type_shape.json`**, `qa/<fig>_type_calib.json`, `qa/<fig>_indistinguishable.json`, ORIG|A SBS.

## Loop
Designer → Drawer → Reviewer → Corrector; one region; screenshot-as-you-draw.
Reviewer runs **both** gate scripts before freeze.
