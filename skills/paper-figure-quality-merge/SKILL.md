---
name: paper-figure-quality-merge
description: >-
  Use when redrawing paper/SI figures as editable A-PPT and B+Blender with
  Confirmation-gold QA, full OMML, gold_bar layered UI (t53u/t54u cross-bot),
  OCR font+overlap (t48u), same-type+叠图 layout (t49u), and indistinguishable
  hard gate. Load before drawing or claiming PASS.
---
# Paper figure quality merge

**Final bar:** [paper-figure-indistinguishable-gate](sand-workflow:paper-figure-indistinguishable-gate).

## 跨 bot 可复现（Kevin t54u）— 写进总闸
- **不可靠：** 纯散文「精致 / ORIG 级」——不同 AI 理解不同，禁止单独当 PASS。
- **可靠：** `gold_bars/` 裁切 + checklist 层数；OCR/几何数字门禁；**禁止宣称 PASS 无 artifact**。
- **一次画成：** 量测坐标表 → 按 archetype 对照 gold_bar 分层画 → 双门禁 → icon SBS vs gold → 整页 SBS。
- **新 bot 最小包：** `botdraw` + `tools/` + `gold_bars/` + `docs/MASTER_PROMPT_zh.md`。
详见 [paper-figure-gold-bar-calibration](sand-workflow:paper-figure-gold-bar-calibration)。

**Locked stack (every fig, no exceptions):**
1. [paper-figure-fig01-gold-bar](sand-workflow:paper-figure-fig01-gold-bar) — clearance / process
2. [paper-figure-full-omml](sand-workflow:paper-figure-full-omml) — all ORIG math → real OMML
3. [paper-figure-arrow-proportion](sand-workflow:paper-figure-arrow-proportion) — clear head + 小尾巴
4. [paper-figure-scene-ui](sand-workflow:paper-figure-scene-ui) — layered UI **+ gold_bar SBS**
5. [paper-figure-gold-bar-calibration](sand-workflow:paper-figure-gold-bar-calibration) — 可视金标裁切库
6. [paper-figure-layout-gates](sand-workflow:paper-figure-layout-gates) — ticks、Abl、**axis_arrows_outward**、Fig08 阶梯
7. [paper-figure-type-calibration](sand-workflow:paper-figure-type-calibration) + [paper-figure-text-layout-clearance](sand-workflow:paper-figure-text-layout-clearance) — t48u
8. [paper-figure-layout-distribution](sand-workflow:paper-figure-layout-distribution) — t49u

Also: dense-region, hierarchical-measure, layout-gates-2, feedback-to-skill, b-blender.

## Contract
One PPTX/fig; slide=ORIG; A pic=0; B=A+Cycles or B=A.
Before PASS run **both**:
```bash
python tools/ocr_font_overlap_gate.py A FigXX
python tools/layout_type_shape_gate.py A FigXX
```
Require `font_pass`∧`overlap_pass`∧`type_uniform_pass`∧`shape_overlap_pass`∧`text_shape_clear_pass`.

Also require scene_ui gold_bar fields + layout `axis_arrows_outward_pass` when axes present.

## Hard bans
Whole-slide paste; potrace; plain/fake math; coarse UI / 无 gold_bar SBS; bare/giant arrows; Drive before Kevin freeze; PASS on OCR alone while same-type fonts uneven or graphics overlap; **散文精致无 artifact**; PPT ruler as sole UI fineness gate.

## Per-fig deliverables
`qa/<fig>_omml_audit.json`, `qa/<fig>_arrow_gate.json`, `qa/<fig>_scene_ui.json`（含 gold_bar 字段）, `qa/<fig>_layout_gates.json`（含 axis_arrows_outward_pass）, `qa/<fig>_ocr_font_overlap.json`, `qa/<fig>_layout_type_shape.json`, `qa/<fig>_type_calib.json`, optional `qa/<fig>_type_ruler.json`, `qa/<fig>_indistinguishable.json`, ORIG|A SBS, icon SBS vs gold_bar.

## Loop
Designer → Drawer → Reviewer → Corrector; one region; screenshot-as-you-draw.
Reviewer runs **both** gate scripts + gold_bar icon SBS before freeze.
