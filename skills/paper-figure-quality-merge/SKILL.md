---
name: paper-figure-quality-merge
description: >-
  Use when redrawing paper/SI figures as editable A-PPT and B+Blender with
  Confirmation-gold QA, full OMML, layered refined UI, and indistinguishable
  hard gate. Load before drawing or claiming PASS.
---
# Paper figure quality merge

**Final bar:** [paper-figure-indistinguishable-gate](sand-workflow:paper-figure-indistinguishable-gate).

**Locked stack (every fig, no exceptions):**
1. [paper-figure-fig01-gold-bar](sand-workflow:paper-figure-fig01-gold-bar) — clearance / process
2. [paper-figure-full-omml](sand-workflow:paper-figure-full-omml) — all ORIG math → real OMML; **complete token discovery**; t40u Fallback/preview gates; t41u 禁错拆（`f_byz`/`P_attack`/`T` 分式）
3. [paper-figure-arrow-proportion](sand-workflow:paper-figure-arrow-proportion) — clear head + 小尾巴
4. [paper-figure-scene-ui](sand-workflow:paper-figure-scene-ui) — layered refined UI
5. [paper-figure-layout-gates](sand-workflow:paper-figure-layout-gates) — **t41u:** axis ticks、Abl leader/progress lines、chart z-order（带在线下）、虚线参考线、series markers

Also: type-calibration, text-layout-clearance, dense-region, hierarchical-measure, feedback-to-skill, b-blender.

## Contract
One PPTX/fig; slide=ORIG; A pic=0; B=A+Cycles or B=A.
h_med 1.05–1.16 preferred (≥1.00 hard) without overflow.

## Hard bans
Whole-slide paste; potrace; plain/fake math; incomplete math discovery; `fb_γz`/`PattacK` style breaks; missing axis ticks when ORIG has them; Abl.7 missing leaders; threshold band above series; solid refs when ORIG dashed; missing series markers; coarse UI; bare/giant arrows; unwrap AC for LO; Drive before Kevin freeze.

## Per-fig deliverables
`qa/<fig>_omml_audit.json`, `qa/<fig>_arrow_gate.json`, `qa/<fig>_scene_ui.json`, `qa/<fig>_layout_gates.json`, `qa/<fig>_indistinguishable.json`, ORIG|A SBS.

## Loop
Designer → Drawer → Reviewer → Corrector; one region; screenshot-as-you-draw.
