---
name: paper-figure-quality-merge
description: >-
  Use when redrawing paper/SI figures as editable A-PPT and B+Blender with
  Confirmation-gold QA, full OMML, gold_bar UI, OCR+layout gates, media-slot
  harmony (t58u: no cut-off crops, optional AI fill), and indistinguishable hard
  gate. Load before drawing or claiming PASS.
---
# Paper figure quality merge

**Final bar:** [paper-figure-indistinguishable-gate](sand-workflow:paper-figure-indistinguishable-gate).

## 跨 bot（t54u）
可靠标准 = gold_bars + 数字门禁 + artifact；禁散文单独 PASS。

## Locked stack
1. fig01-gold-bar
2. full-omml
3. arrow-proportion
4. scene-ui + gold-bar-calibration
5. **media-slot-harmony（t58u）** — 边画边自检；完整 ORIG 裁切；必要时 AI 局部补槽
6. layout-gates（含 axis_arrows_outward）
7. type-calibration + text-layout-clearance
8. layout-distribution
Also: dense-region, hierarchical-measure, layout-gates-2, feedback-to-skill, b-blender.

## Contract
One PPTX/fig; slide=ORIG.
Before PASS:
```bash
python tools/ocr_font_overlap_gate.py A FigXX
python tools/layout_type_shape_gate.py A FigXX
```
+ **目视**清叠字/裁半（门禁假阴性仍 FAIL）
+ `qa/<fig>_media_slots.json` 每槽 `complete:true`
+ scene_ui / indistinguishable artifacts

## Hard bans
Whole-slide paste as sole deliverable; potrace; fake math; coarse UI; bare arrows; **截图裁半**；OCR PASS 但肉眼叠字；散文精致无 artifact。
**允许**：局部 media slot 用 AI 生图插入以和谐（禁整页 AI）。

## Loop
Designer → Drawer → Reviewer → Corrector；**一区一检**（叠字+媒体完整+SBS crop）。
