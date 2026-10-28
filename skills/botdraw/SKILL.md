---
name: botdraw
description: >-
  PRIMARY entry for BotDraw paper-figure redraw: 1:1 editable A-PPT (optional
  Blender B). Load first from PolyUDavid/BotDraw — quality-merge, gold_bars,
  OMML, arrows, scene UI, OCR+layout, media-slot harmony (t58u self-check + full
  crops/AI fill). Use when user says botdraw / 论文插图 / redraw figures.
---
# botdraw — BotDraw 入口（主入口）

仓库：[PolyUDavid/BotDraw](https://github.com/PolyUDavid/BotDraw)

这是 **BotDraw 技能包的唯一推荐入口**。本地 Cursor / 下一台 Bot：先加载本技能，再画图。
（历史别名：`internaldraw` / `internaldraw-2`，新对话请用 **botdraw**。）

## 跨 bot 可复现（Kevin t54u）
- 不可靠：纯散文「精致/ORIG级」
- 可靠：gold_bar 裁切+checklist；OCR/几何数字门禁；禁止无 artifact 宣称 PASS
- 流程：量测 → 对照 gold_bar 分层画 → **边画边自检叠字/裁半** → 双门禁 → icon SBS vs gold → 整页 SBS
详见 [paper-figure-gold-bar-calibration](sand-workflow:paper-figure-gold-bar-calibration)、[paper-figure-media-slot-harmony](sand-workflow:paper-figure-media-slot-harmony)。

## 加载顺序（强制）
1. **本技能 botdraw**
2. paper-figure-quality-merge
3. paper-figure-gold-bar-calibration
4. paper-figure-media-slot-harmony（t58u：完整裁切 / AI 补槽 / 边画边查）
5. paper-figure-fig01-gold-bar
6. paper-figure-full-omml
7. paper-figure-arrow-proportion
8. paper-figure-scene-ui
9. paper-figure-type-calibration + paper-figure-text-layout-clearance
10. paper-figure-layout-distribution
11. paper-figure-layout-gates + paper-figure-layout-gates-2
12. paper-figure-hierarchical-measure + paper-figure-dense-region-pipeline
13. paper-figure-indistinguishable-gate
14. paper-figure-a-ppt / a-ppt / scientific-figure-faithful-replica / vector-ui-overlay-stack
15. 需要 B 时：paper-figure-b-blender

## 非协商硬标准
- 1:1 量测；禁整页截图/potrace 当可编辑交付
- 真 OMML；箭头小尾巴；轴朝外
- gold_bars 分层 UI
- 同 role 字号一致；**零叠字、零叠图**（门禁 PASS 仍须目视；漏检不算过）
- **媒体槽完整**：禁截图裁半；优先完整 ORIG 裁切，不和谐时允许 AI 局部补图插入（见 media-slot-harmony）
- 密图分区；**边画边 SBS/自检**

## PASS 前必跑
```bash
FIG_ROOT=<figroot> python tools/ocr_font_overlap_gate.py A FigXX
FIG_ROOT=<figroot> python tools/layout_type_shape_gate.py A FigXX
```
另需：`qa/<fig>_media_slots.json`（每槽 complete）、scene_ui、indistinguishable；缺 = FAIL。

## 每图交付
out_A pptx、prev、双门禁、media_slots、omml/arrow/scene/layout、indistinguishable、ORIG|A SBS、icon/media SBS。
