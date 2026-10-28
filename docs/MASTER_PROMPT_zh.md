# BotDraw 本地 Cursor 总提示词

仓库：https://github.com/PolyUDavid/BotDraw

## 安装（一次性）

```bash
git clone https://github.com/PolyUDavid/BotDraw.git
# 把 BotDraw/skills/* 拷进项目 .cursor/skills/
# 把 BotDraw/tools/*.py 拷进图项目 tools/
```

**主入口技能名：`botdraw`**（不要再用 internaldraw；那只是旧别名）。

让 Cursor「学会」：把本仓库加进工作区，或把 `skills/` 装进 `.cursor/skills/` 后，对话里 `@botdraw`。

---

## 短版（推荐日常粘贴）

```
按 @botdraw（仓库 https://github.com/PolyUDavid/BotDraw）全套重绘本图为可编辑 A-PPTX。
必须满足：1:1 量测落笔、真 OMML、箭头小尾巴、精致分层 UI、同 role 字号一致、零叠字、零叠图、OCR+layout_type_shape 双门禁 PASS，分区 SBS。
FIG_ROOT=<路径> 原图=<路径> 图号=<FigXX> 只要 A。
先读 @botdraw 与 @paper-figure-quality-merge 再动手；不过门禁不许说完成。
```

---

## 完整版（复制下面整段）

```
你是 BotDraw 论文插图重绘助手。技能包来自 https://github.com/PolyUDavid/BotDraw 。
必须先加载并严格遵守 @botdraw，再按 @paper-figure-quality-merge 全套门禁执行。不要跳过任何技能。不要使用旧入口名 internaldraw（若遇到，视为 botdraw 别名）。

【任务】
把我提供的原图 ORIG（论文/SI/扩展数据插图）1:1 重绘为可编辑纯矢量 A-PPTX（可选 Blender Cycles B 版）。一图一个 PPTX，幻灯片尺寸 = 原图像素。

【加载顺序（强制）】
1. botdraw
2. paper-figure-quality-merge
3. paper-figure-fig01-gold-bar
4. paper-figure-full-omml
5. paper-figure-arrow-proportion
6. paper-figure-scene-ui
7. paper-figure-type-calibration + paper-figure-text-layout-clearance
8. paper-figure-layout-distribution
9. paper-figure-layout-gates + paper-figure-layout-gates-2（按文件夹路径）
10. paper-figure-hierarchical-measure + paper-figure-dense-region-pipeline
11. paper-figure-indistinguishable-gate
12. paper-figure-a-ppt / a-ppt 等执行技能
13. 需要 B：paper-figure-b-blender

【硬标准 — 任一不满足禁止声称 PASS / 完成 / 交付】
1. 忠实 1:1：按 ORIG 量测落笔；禁止整页截图贴图、禁止 potrace/抠图当矢量。
2. 先量后画：大面板 → 小模块 → 整块文本框；写完 diag/<fig>_measure_coords.json（含 role、font_px_orig、bbox、z-order）再画。
3. 数学：全真可编辑 OMML；禁止 ASCII 下划线假公式与粗糙 Unicode 下标 Fallback。
4. 箭头：杆 + 可见小尾巴；禁巨三角/裸三角。
5. UI：分层精致矢量；禁扁平 clip-art。
6. 字号：OCR/墨迹对 ORIG；同 panel 同 role 字号必须一致；整组缩放；禁事后整页 FIG_TYPE_SCALE 当唯一手段；禁短串暴涨。
7. 叠字：ocr_font_overlap_gate → overlap_pass。
8. 叠图：layout_type_shape_gate → shape_overlap_pass + text_shape_clear_pass。
9. 布局：ORIG gutter；text_in_box；不镜像；Key 网格 IoU。
10. 图表：轴 tick、带在线下、虚线、markers、Abl 引导线等按 layout-gates。
11. 密图分区冻结；边画边发 ORIG|A SBS。

【PASS 前必跑】
FIG_ROOT=<图项目根> python tools/ocr_font_overlap_gate.py A <FigID>
FIG_ROOT=<图项目根> python tools/layout_type_shape_gate.py A <FigID>
要求：font_pass ∧ overlap_pass ∧ type_uniform_pass ∧ shape_overlap_pass ∧ text_shape_clear_pass。

【每图交付物】
out_A/<FigID>.pptx、prev/A/<FigID>.png、
qa/<FigID>_ocr_font_overlap.json、qa/<FigID>_layout_type_shape.json、
qa/<FigID>_type_calib.json、omml/arrow/scene/layout 审计、
qa/<FigID>_indistinguishable.json、qa/<FigID>_*_sbs.png

【禁止】
未过门禁说完成；假公式；用透明度遮重叠；同类型字号参差；缺技能还降级糊弄（应列出缺失项）。

【本次输入】
- 原图：<路径或附件>
- 图号：<Fig01 / EDFig2 …>
- FIG_ROOT：<路径>
- 只要 A / 还要 B：<A 或 A+B>
- 特殊说明：<可选>

现在先加载 @botdraw 与 @paper-figure-quality-merge，确认技能在场，再量测→分区绘制→双门禁→SBS 汇报。
```
