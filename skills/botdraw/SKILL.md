---
name: botdraw
description: >-
  PRIMARY entry for BotDraw paper-figure redraw: 1:1 editable A-PPT (optional
  Blender B). Load this first from PolyUDavid/BotDraw — pulls quality-merge,
  gold_bars calibration (t53u/t54u cross-bot), full OMML, arrows, scene UI,
  OCR+layout gates. Use when user says botdraw / 论文插图 / redraw figures.
---
# botdraw — BotDraw 入口（主入口）

仓库：[PolyUDavid/BotDraw](https://github.com/PolyUDavid/BotDraw)

这是 **BotDraw 技能包的唯一推荐入口**。本地 Cursor / 下一台 Bot：先加载本技能，再画图。
（历史别名：`internaldraw` / `internaldraw-2`，职责相同，新对话请用 **botdraw**。）

## 跨 bot 可复现（Kevin t54u）
换任何一台 bot，只要装了本仓 **skills + tools + gold_bars + MASTER_PROMPT**，给图应一次画到同精致度。
- 不可靠：纯散文「精致/ORIG级」
- 可靠：gold_bar 裁切+checklist；OCR/几何数字门禁；禁止无 artifact 宣称 PASS
- 流程：量测 → 对照 gold_bar 分层画 → 双门禁 → icon SBS vs gold → 整页 SBS
详见 [paper-figure-gold-bar-calibration](sand-workflow:paper-figure-gold-bar-calibration)。

## 加载顺序（强制）
1. **本技能 botdraw**
2. paper-figure-quality-merge
3. paper-figure-gold-bar-calibration（t53u/t54u 可视金标）
4. paper-figure-fig01-gold-bar
5. paper-figure-full-omml
6. paper-figure-arrow-proportion
7. paper-figure-scene-ui
8. paper-figure-type-calibration + paper-figure-text-layout-clearance（t48u）
9. paper-figure-layout-distribution（t49u）
10. paper-figure-layout-gates + paper-figure-layout-gates-2
11. paper-figure-hierarchical-measure + paper-figure-dense-region-pipeline
12. paper-figure-indistinguishable-gate
13. paper-figure-a-ppt / a-ppt / scientific-figure-faithful-replica / vector-ui-overlay-stack
14. 需要 B 时：paper-figure-b-blender

不要跳过 quality-merge / gold-bar-calibration 直接画或宣称 PASS。

## 非协商硬标准
- 忠实 1:1 量测落笔；禁止整页截图/potrace 当矢量
- 全真可编辑 OMML + LaTeX 级 Fallback 预览
- 箭头杆 + 可见小尾巴；轴箭头朝外（poly tip）
- 精致分层 UI **对照 gold_bars/**（禁扁平 clip-art；禁散文单独 PASS）
- 同 panel 同 role 字号一致
- 零叠字、零叠图
- 布局 gutter / Key 网格按 ORIG
- 密图分区冻结；边画边 SBS

## PASS 前必跑
```bash
FIG_ROOT=<figroot> python tools/ocr_font_overlap_gate.py A FigXX
FIG_ROOT=<figroot> python tools/layout_type_shape_gate.py A FigXX
```
要求：`font_pass` ∧ `overlap_pass` ∧ `type_uniform_pass` ∧ `shape_overlap_pass` ∧ `text_shape_clear_pass`。
另：`qa/<fig>_scene_ui.json` gold_bar 字段；有轴则 `axis_arrows_outward_pass`。
缺 JSON 或任一为假 = FAIL。

## 每图交付
`out_A/<Fig>.pptx`、`prev/A/<Fig>.png`、双门禁 JSON、type_calib、omml/arrow/scene/layout 审计、`indistinguishable.json`、ORIG|A SBS、icon SBS vs gold_bar。

## 新 bot 最小安装
Clone 本仓 → 拷 `skills/` 进 workflows → 拷 `tools/` → 保留仓库根 `gold_bars/` → `@botdraw` + `docs/MASTER_PROMPT_zh.md`。
