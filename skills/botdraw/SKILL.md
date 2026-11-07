---
name: botdraw
description: >-
  PRIMARY entry for BotDraw paper-figure redraw: 1:1 editable A-PPT (optional
  Blender B). New bots run paper-figure-onboard-selftest until proof PASS, then
  the quality-sync evidence skills. Includes the t68u crude-B ban. Historical
  measurement FAIL is not rewritten by owner acceptance.
---
# botdraw — BotDraw 入口（主入口）

仓库：[PolyUDavid/BotDraw](https://github.com/PolyUDavid/BotDraw)

这是 **BotDraw 技能包的唯一推荐入口**。本地 Cursor / 下一台 Bot：先加载本技能，再画图。
（历史别名：`internaldraw` / `internaldraw-2`，新对话请用 **botdraw**。别名不另开一套流程。）

## 新 bot 强制预调试（Kevin t69u）
下载/安装本仓库后，**先**加载并跑完 [paper-figure-onboard-selftest](sand-workflow:paper-figure-onboard-selftest)：
环境探测 → `python3 tools/quality_sync.py selftest`（合成逻辑，不是用户图 PASS）→ 固定夹具试画 → OCR+layout 数字证明 → 同一失败类连续 3 轮未变则 `STOP_SAME_CLASS` → `qa/onboard_selftest.json` 里 `ready:true` **之后**，才允许开用户 FIG_ROOT。
禁止用「环境应该没问题」跳过。`ready` 也不代替该项目的逐源符号审计。

## 状态轴（与目视接受分开）
每张图、每个 A/B 版本分开记：`measurement`、`source_review`、`visual_review`、`owner_acceptance`、`native_application_review`、`delivery_integrity`。
用户可以接受当前外观，同时测量仍是 FAIL。禁止改旧报告求 PASS，也禁止把合成测试全绿写成用户图 PASS。动作由 [paper-figure-quality-merge](sand-workflow:paper-figure-quality-merge) 的停止/继续规则决定。

## 跨 bot 可复现（Kevin t54u）
- 不可靠：纯散文「精致/ORIG级」
- 可靠：gold_bar 裁切+checklist；OCR/几何数字门禁；禁止无 artifact 宣称 PASS
- 高级 UI 以图层临摹 skill + gold_bar icon SBS 为准。
- 证据顺序：固定源与数据出处 → 量测 → 矢量 OMML → 逐源符号 → 字体/预览证据 → 空间 OCR 与语义例外 → 逐区 SBS → B 车型/模型实值 → 当前 SHA 复测 → 干净 `out_A`/`out_B` 交付。
详见 [paper-figure-gold-bar-calibration](sand-workflow:paper-figure-gold-bar-calibration)、[paper-figure-media-slot-harmony](sand-workflow:paper-figure-media-slot-harmony)。

<!-- botdraw-load-order -->
## 加载顺序（强制）
0. paper-figure-onboard-selftest（新 bot / 换机首次；`ready:true` 可跳过绘制夹具，不可跳过技能文件）
1. botdraw
2. paper-figure-quality-merge
3. paper-figure-data-provenance（源/数据版本先固定；禁止编造实验序列）
4. paper-figure-gold-bar-calibration
5. paper-figure-media-slot-harmony（t58u：完整裁切 / AI 补槽 / 边画边查；另加文件身份与 contain）
6. paper-figure-fig01-gold-bar
7. paper-figure-full-omml
8. paper-figure-source-symbol-audit（覆盖计数不是正确；Choice 与 Fallback 分开）
9. paper-figure-arrow-proportion
10. paper-figure-scene-ui
11. paper-figure-illustrator-layer-trace（t126：Illustrator MCP + scientific-illustrator 图层临摹/z-order/多 path 图标 → 纯矢量 A-PPT；先 reconstruction_spec）
12. paper-figure-type-calibration + paper-figure-text-layout-clearance
13. paper-figure-font-renderer-proof（fc-match 不是本次 PDF 证明）
14. paper-figure-layout-distribution
15. paper-figure-semantic-overlap-exceptions（科学叠放另账，不改测量 FAIL）
16. paper-figure-spatial-ocr-pairing（一对一；不改 t48u 历史 PASS）
17. paper-figure-layout-gates + paper-figure-layout-gates-2（按文件夹路径加载）
18. paper-figure-hierarchical-measure + paper-figure-dense-region-pipeline
19. paper-figure-indistinguishable-gate
20. paper-figure-a-ppt / a-ppt / scientific-figure-faithful-replica / vector-ui-overlay-stack
21. 需要 B 时：paper-figure-b-blender（**含 t68u：禁粗糙灰块/糊截图当 B**；按车型几何→材质→光，固定尺度 SBS）
22. paper-figure-unified-delivery（显式 A/B、SHA/CRC、`out_A`/`out_B`；缺 B 不回退 A）

## 非协商硬标准
- 1:1 量测；禁整页截图/potrace 当可编辑交付
- 真 OMML；箭头小尾巴；轴朝外
- gold_bars 分层 UI
- 同 role 字号一致；**零叠字、零叠图**（门禁 PASS 仍须目视；漏检不算过；源图科学叠放走语义例外，不手改成测得 PASS）
- **媒体槽完整**：禁截图裁半；优先完整 ORIG 裁切；等比 contain；错配必须换上真实文件。不和谐时允许 AI 局部补图插入（见 media-slot-harmony）。标签/轴/公式仍可编辑。
- **B 硬件/车辆槽（t68u）**：糊截图或过简灰块 Cycles = FAIL；须按该投影类的轮廓/轮距/窗/灯重建，不用加 samples 代替造型。
- 数据不可编造。无 raw 只称像素几何。冲突时主临摹与 verified 旁路分开，旁路不进主 `out_A`/`out_B`。
- 密图分区；**边画边 SBS/自检**

## PASS 前必跑
```bash
python3 tools/quality_sync.py selftest
python3 tools/quality_sync.py wiring
FIG_ROOT=<figroot> python tools/ocr_font_overlap_gate.py A FigXX
FIG_ROOT=<figroot> python tools/layout_type_shape_gate.py A FigXX
```
`ocr_font_overlap_gate.py` 需要本机已装的 Python 3、Pillow、`rapidocr_onnxruntime`（可选依赖；未安装则不能宣称 t48u PASS）。`selftest`、`wiring`、空间配对和 `layout_type_shape_gate.py` 只用标准库。
有 B 时把 variant 换成 `B`。解析不到 `out_B/<Fig>.pptx` 即失败，禁止改用 A 或旧备份。
另需：`qa/<fig>_media_slots.json`（每槽 complete，且含身份 SHA 与 contain）、scene_ui、indistinguishable、符号账本（有数学时）、字体证据（宣称某字体时）。缺 = FAIL。历史测量 JSON 不覆盖。

## 每图交付
`out_A/<Fig>.pptx`、prev、双门禁、空间配对报告、media_slots、omml/arrow/scene/layout、indistinguishable、ORIG|A SBS、icon/media SBS。有 B 时另交 `out_B` + 重开后的 Cycles 实值与 `.blend` SHA。统一打包用 paper-figure-unified-delivery。
