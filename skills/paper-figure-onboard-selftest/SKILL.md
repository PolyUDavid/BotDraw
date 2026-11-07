---
name: paper-figure-onboard-selftest
description: >-
  Use when a new bot installs BotDraw or before first paper-figure draw:
  environment smoke, gold fixture self-test, tune until OCR/layout proof PASS,
  only then start user figures (Kevin t69u).
---
# paper-figure-onboard-selftest（新 bot 预调试）

Kevin t69u：新 bot 下载 BotDraw 后，**必须先自检测试并调到能画出当前金标效果**，再给用户画图。效果不好就自己调到合适为止。

## When
- 首次安装 / 克隆 PolyUDavid/BotDraw
- 换机器、换 bot、技能包大更新后
- 用户说「先自检」「预调试」时

## Gate (non-negotiable)
`qa/onboard_selftest.json` 里 `ready:true` 之前，**禁止**开用户 FIG_ROOT 正式画图。

## Steps
1. **环境探测**：Python3；`python3 tools/quality_sync.py selftest` 与 `python3 tools/quality_sync.py wiring` 必须先过（标准库）。再查 pptx/PIL、`rapidocr_onnxruntime`、LibreOffice（prev 导出，可选）、Blender（B，可选）；`tools/ocr_font_overlap_gate.py`、`tools/layout_type_shape_gate.py`、`tools/spatial_ocr_pairing.py` 可读；`gold_bars/` 存在。下列技能目录必须在：`paper-figure-source-symbol-audit`、`paper-figure-font-renderer-proof`、`paper-figure-spatial-ocr-pairing`、`paper-figure-semantic-overlap-exceptions`、`paper-figure-data-provenance`、`paper-figure-unified-delivery`。
2. **跑固定夹具**（`fixtures/onboard/` 或仓库附带 mini ORIG + 期望 checklist）：按 [botdraw](sand-workflow:botdraw) 最短路径画一页 A（或修一页已知金标 panel）。
3. **数字证明**：
```bash
FIG_ROOT=<onboard_root> python tools/ocr_font_overlap_gate.py A OnboardDemo
FIG_ROOT=<onboard_root> python tools/layout_type_shape_gate.py A OnboardDemo
```
要求：`overlap_pass`、合理 `h_med`（对照夹具 ORIG）、layout PASS；写出 ORIG|A SBS。
4. **FAIL → 自调**：字号/净空/叠字按 type-calibration + text-layout-clearance 修正，重跑门禁。同一失败类、同一门禁版本连续 3 轮不变 → `STOP_SAME_CLASS`，停止这一类重试。仍 FAIL 则标 `ready:false` 并报告缺依赖/夹具，**不要硬画用户图**，也不要改历史 FAIL 文件。
5. **PASS**：写 `qa/onboard_selftest.json`（ready、gate 路径、SBS、时间、`quality_sync_primitives_pass`）。再加载 quality-merge 开用户任务。`ready:true` 只说明夹具门禁和技能接线，**不代替**该项目的逐源符号、字体 PDF、车型或原生 PowerPoint 审查。

合成回归（由 selftest / `python3 -m unittest discover -s tests -v` 覆盖，全绿 ≠ 用户图 PASS）：比较符与算子属性、框外数学不计入原索引、同名横竖不互配、缺 B 不回退 A、语义例外不翻转测量 FAIL、快照漏项被拒绝。

## Proof artifact shape
```json
{
  "ready": true,
  "ocr": "qa/OnboardDemo_ocr_font_overlap.json",
  "layout": "qa/OnboardDemo_layout_type_shape.json",
  "sbs": "qa/OnboardDemo_whole_sbs.png",
  "notes": "t69u"
}
```

## Ban
用散文「环境应该没问题」代替 artifact；跳过自检直接画用户 Fig；门禁假 PASS 不目视 SBS。
