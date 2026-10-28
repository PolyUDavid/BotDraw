# BotDraw 技能关系

BotDraw 是给 Grok Bot / Cursor Agent 用的论文插图技能包：1:1 临摹成可编辑纯矢量 A-PPTX，需要三维载具时再加 Blender B。仓库放技能、审计脚本，以及 t53u/t54u 的 `gold_bars/` 裁切库。

本地 Cursor 把 [MASTER_PROMPT_zh.md](MASTER_PROMPT_zh.md) 整段粘进对话，并先加载 `botdraw`（`@botdraw`）。

## 加载顺序

1. `botdraw`（主入口，先加载）。`internaldraw` 与 `internaldraw-2` 是历史别名，加载后按 botdraw 全套执行。
2. `paper-figure-quality-merge`（总闸，入口会拉它）。
3. 总闸锁定的栈，每张图都要：
   - `paper-figure-gold-bar-calibration` — `gold_bars/` 裁切 + checklist（t53u/t54u；散文不可单独 PASS）
   - `paper-figure-media-slot-harmony` — t58u：边画边自检；完整媒体槽（禁裁半）；可选 AI 局部补槽。`@botdraw` 加载顺序包含本技能
   - `paper-figure-fig01-gold-bar` — 留白与流程金线
   - `paper-figure-full-omml` — 真 OMML + DrawingML Fallback
   - `paper-figure-arrow-proportion` — 杆与小尾巴
   - `paper-figure-scene-ui` — 分层精致 UI；大脑强制层；icon SBS vs gold_bar
   - `paper-figure-layout-gates` — 刻度、Abl 引导线、Fig08 阶梯线、`axis_arrows_outward_pass`
4. 测量与版式：`paper-figure-hierarchical-measure`、`paper-figure-type-calibration`、`paper-figure-text-layout-clearance`、`paper-figure-layout-distribution`、`paper-figure-layout-gates-2`。
5. 密图走 `paper-figure-dense-region-pipeline`：逐区画、SBS、冻结，再下一区。
6. 交卷前 `paper-figure-indistinguishable-gate`。两道硬门禁都要过：`qa/<fig>_ocr_font_overlap.json` 里 `font_pass` 与 `overlap_pass` 都为真（t48u），且 `qa/<fig>_layout_type_shape.json` 里 `type_uniform_pass`、`shape_overlap_pass`、`text_shape_clear_pass` 都为真（t49u）。另需 scene_ui 的 gold_bar 字段，有轴则 `axis_arrows_outward_pass`，以及 `qa/<fig>_media_slots.json` 每槽 `complete:true`（t58u）。失败裁剪交给 `paper-figure-feedback-to-skill`（新视觉类可新增 `gold_bars/<archetype>/`）。
7. 绘制合同：`paper-figure-a-ppt` / `a-ppt`，叠齐用 `scientific-figure-faithful-replica` 与 `vector-ui-overlay-stack`。全套流程说明在 `ppt-blender`。
8. A 通过后才做 `paper-figure-b-blender`。没有载具时 B 等于 A，在 QA 里注明。

`advsci-endnote-polish` 管 Advanced Science 稿件的文献、排版、润色和 EndNote，不参与插图绘制循环。

## 审计脚本

- `tools/fig_gate_audit.py` — 扫一张 PPTX 的 OMML / Fallback（下划线假公式、`₍paren₎`、拆开 AlternateContent 的空白风险），并写出 scene / arrow / indistinguishable 候选 JSON。
- `tools/audit_omml_arrows.py` — 统计 `m:oMath`、箭头端点与命名 shaft，以及 OMML 之外的纯文本公式残留。
- `tools/ocr_font_overlap_gate.py` — Kevin t48u：对 ORIG 的 OCR 字高（`font_pass` / `h_med`）和 A 预览墨迹框叠字（`overlap_pass`）。宣称 PASS 前必跑。用法见 [OCR_FONT_OVERLAP_GATE.md](OCR_FONT_OVERLAP_GATE.md)。
- `tools/layout_type_shape_gate.py` — Kevin t49u：同一 `(panel, role)` 字号锁定（`type_uniform_pass`）、兄弟形状叠图（`shape_overlap_pass`）、文字不骑非父级图形（`text_shape_clear_pass`）。与 t48u 同一轮必跑。用法见 [LAYOUT_TYPE_SHAPE_GATE.md](LAYOUT_TYPE_SHAPE_GATE.md)。

脚本默认指向操作者本机的图目录。仓库不包含那些图，也不包含 Drive ID。
