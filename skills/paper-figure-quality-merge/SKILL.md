---
name: paper-figure-quality-merge
description: >-
  Use when redrawing paper/SI figures as editable A-PPT and B+Blender with
  Confirmation-gold QA, full OMML, layered refined UI, OCR font+overlap hard
  gate, and indistinguishable hard gate. Load before drawing or claiming PASS.
---
# Paper figure quality merge

**Final bar:** [paper-figure-indistinguishable-gate](sand-workflow:paper-figure-indistinguishable-gate).

**Locked stack (every fig, no exceptions):**
1. [paper-figure-fig01-gold-bar](sand-workflow:paper-figure-fig01-gold-bar) — clearance / process
2. [paper-figure-full-omml](sand-workflow:paper-figure-full-omml) — all ORIG math → real OMML; **complete token discovery**; t40u Fallback/preview gates; t41u 禁错拆（`f_byz`/`P_attack`/`T` 分式）
3. [paper-figure-arrow-proportion](sand-workflow:paper-figure-arrow-proportion) — clear head + 小尾巴
4. [paper-figure-scene-ui](sand-workflow:paper-figure-scene-ui) — layered refined UI
5. [paper-figure-layout-gates](sand-workflow:paper-figure-layout-gates) — **t41u:** axis ticks、Abl leader/progress lines、chart z-order（带在线下）、虚线参考线、series markers
6. **[paper-figure-type-calibration](sand-workflow:paper-figure-type-calibration) + [paper-figure-text-layout-clearance](sand-workflow:paper-figure-text-layout-clearance)** — **t48u OCR hard gate:** `tools/ocr_font_overlap_gate.py` → `font_pass` + `overlap_pass` before any PASS

Also: dense-region, hierarchical-measure, layout-gates-2, feedback-to-skill, b-blender.

## Contract
One PPTX/fig; slide=ORIG; A pic=0; B=A+Cycles or B=A.
h_med preferred 1.05–1.16 (≥1.00 hard preferred; OCR gate hard band 0.92–1.22) **and** zero OCR text–text collisions, without overflow.

## Hard bans
Whole-slide paste; potrace; plain/fake math; incomplete math discovery; `fb_γz`/`PattacK` style breaks; missing axis ticks when ORIG has them; Abl.7 missing leaders; threshold band above series; solid refs when ORIG dashed; missing series markers; coarse UI; bare/giant arrows; unwrap AC for LO; Drive before Kevin freeze; **PASS without `qa/<fig>_ocr_font_overlap.json` or with `font_pass`/`overlap_pass` false**.

## Per-fig deliverables
`qa/<fig>_omml_audit.json`, `qa/<fig>_arrow_gate.json`, `qa/<fig>_scene_ui.json`, `qa/<fig>_layout_gates.json`, **`qa/<fig>_ocr_font_overlap.json`**, `qa/<fig>_type_calib.json`, `qa/<fig>_indistinguishable.json`, ORIG|A SBS.

## Loop
Designer → Drawer → Reviewer → Corrector; one region; screenshot-as-you-draw.
Reviewer **must** run OCR font+overlap gate on the region/full A preview before freeze.
