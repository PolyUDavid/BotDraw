# BotDraw 技能关系

BotDraw 是给 Grok Bot / Cursor Agent 用的论文插图技能包：1:1 临摹成可编辑纯矢量 A-PPTX，需要三维载具时再加 Blender B。仓库放技能、审计脚本，以及 t53u/t54u 的 `gold_bars/` 裁切库。

本地 Cursor 把 [MASTER_PROMPT_zh.md](MASTER_PROMPT_zh.md) 整段粘进对话，并先加载 `botdraw`（`@botdraw`）。

## 加载顺序

<!-- botdraw-load-order -->
0. `paper-figure-onboard-selftest`（t69u，新 bot：自检预调试）。`qa/onboard_selftest.json` 的 `ready:true` 之后才接受用户图。先跑 `python3 tools/quality_sync.py selftest`（合成逻辑，不是用户图 PASS）。夹具门禁：`python tools/ocr_font_overlap_gate.py A OnboardDemo` 与 `python tools/layout_type_shape_gate.py A OnboardDemo`。禁止无 artifact 宣称 ready。
1. `botdraw`（主入口）。`internaldraw` 与 `internaldraw-2` 只是别名，不另开流程。
2. `paper-figure-quality-merge`（总闸：六条状态轴与停止/继续）。
3. `paper-figure-data-provenance`
4. `paper-figure-gold-bar-calibration`
5. `paper-figure-media-slot-harmony`
6. `paper-figure-fig01-gold-bar`
7. `paper-figure-full-omml`
8. `paper-figure-source-symbol-audit`
9. `paper-figure-arrow-proportion`
10. `paper-figure-scene-ui`
11. `paper-figure-illustrator-layer-trace`
12. `paper-figure-type-calibration`
13. `paper-figure-text-layout-clearance`
14. `paper-figure-font-renderer-proof`
15. `paper-figure-layout-distribution`
16. `paper-figure-semantic-overlap-exceptions`
17. `paper-figure-spatial-ocr-pairing`
18. `paper-figure-layout-gates`
19. `paper-figure-layout-gates-2`（按文件夹路径；YAML name 仍与上一份冲突）
20. `paper-figure-hierarchical-measure`
21. `paper-figure-dense-region-pipeline`
22. `paper-figure-indistinguishable-gate`
23. `paper-figure-a-ppt`
24. `paper-figure-b-blender`
25. `paper-figure-unified-delivery`

上面的编号是唯一加载顺序。`internaldraw` 与 `internaldraw-2` 加载后按 botdraw 执行，不另开流程。`ppt-blender` 是全套说明，入口仍是 botdraw。

仍要同时满足的旧硬标准：gold_bars 裁切与 checklist；媒体槽完整（t58u，另加文件 SHA 与 uniform contain）；真 OMML 与 DrawingML Fallback；箭头杆与小尾巴；分层 UI 与 illustrator 图层临摹；刻度、Abl 引导线、Fig08 阶梯线、轴朝外；同 role 字号与叠图门禁；密图分区冻结。交卷前两道硬门禁都要过：`qa/<fig>_ocr_font_overlap.json` 里 `font_pass` 与 `overlap_pass`（t48u，历史结论不因新配对报告改写），且 `qa/<fig>_layout_type_shape.json` 里 `type_uniform_pass`、`shape_overlap_pass`、`text_shape_clear_pass`（t49u，只读 `out_A` 或 `out_B`）。另需 scene_ui 的 gold_bar 字段、有轴则 `axis_arrows_outward_pass`、`qa/<fig>_media_slots.json` 每槽 `complete:true`。失败裁剪交给 `paper-figure-feedback-to-skill`。B 在 A 之后：糊截图或过简灰块 Cycles 仍禁止；按投影类量几何再上材质和光。没有三维槽时 B 等于 A，在 QA 里注明 SHA。用户接受当前外观不改这些测量。详见 [QUALITY_SYNC.md](QUALITY_SYNC.md)。

`advsci-endnote-polish` 管 Advanced Science 稿件的文献、排版、润色和 EndNote，不参与插图绘制循环。

## 审计脚本

- `tools/fig_gate_audit.py` — 扫一张 PPTX 的 OMML / Fallback（下划线假公式、`₍paren₎`、拆开 AlternateContent 的空白风险），并写出 scene / arrow / indistinguishable 候选 JSON。
- `tools/audit_omml_arrows.py` — 统计 `m:oMath`、箭头端点与命名 shaft，以及 OMML 之外的纯文本公式残留。
- `tools/ocr_font_overlap_gate.py` — Kevin t48u：对 ORIG 的 OCR 字高（`font_pass` / `h_med`）和 A 预览墨迹框叠字（`overlap_pass`）。宣称 PASS 前必跑。用法见 [OCR_FONT_OVERLAP_GATE.md](OCR_FONT_OVERLAP_GATE.md)。
- `tools/layout_type_shape_gate.py` — Kevin t49u：同一 `(panel, role)` 字号锁定（`type_uniform_pass`）、兄弟形状叠图（`shape_overlap_pass`）、文字不骑非父级图形（`text_shape_clear_pass`）。与 t48u 同一轮必跑。只解析 `out_A` 或 `out_B`。用法见 [LAYOUT_TYPE_SHAPE_GATE.md](LAYOUT_TYPE_SHAPE_GATE.md)。
- `tools/quality_sync.py` — 标准库命令：`selftest`、`wiring`、显式 A/B、符号覆盖、数学树、空间配对、语义例外、字体 PDF 字节、媒体/车型/数据记录、快照与 ZIP。`selftest` 全绿不是用户图 PASS。`pdffonts` 可选。
- `tools/spatial_ocr_pairing.py` — 位置与方向的一对一配对。不修改 t48u 的 `pass`。
- `tools/quality_primitives.py` — 被上述命令调用的合成原语。
- `tools/export_skill_sync.py` — 导出相对 `main` 有改动的 `SKILL.md` 与 hash manifest。

脚本默认指向操作者本机的图目录。仓库不包含那些图，也不包含 Drive ID。操作说明见 [QUALITY_SYNC.md](QUALITY_SYNC.md)，与当前 main 的对照见 [QUALITY_SYNC_GAP_MATRIX.md](QUALITY_SYNC_GAP_MATRIX.md)。
