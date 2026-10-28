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
1. **环境探测**：Python3、pptx/PIL、tesseract 或项目 OCR 依赖、LibreOffice（prev 导出）、可选 Blender（B）；`tools/ocr_font_overlap_gate.py`、`tools/layout_type_shape_gate.py` 可读；`gold_bars/` 存在。
2. **跑固定夹具**（`fixtures/onboard/` 或仓库附带 mini ORIG + 期望 checklist）：按 [botdraw](sand-workflow:botdraw) 最短路径画一页 A（或修一页已知金标 panel）。
3. **数字证明**：
```bash
FIG_ROOT=<onboard_root> python tools/ocr_font_overlap_gate.py A OnboardDemo
FIG_ROOT=<onboard_root> python tools/layout_type_shape_gate.py A OnboardDemo
```
要求：`overlap_pass`、合理 `h_med`（对照夹具 ORIG）、layout PASS；写出 ORIG|A SBS。
4. **FAIL → 自调**：字号/净空/叠字按 type-calibration + text-layout-clearance 修正，重跑门禁；最多明确迭代 N 轮并记录；仍 FAIL 则标 `ready:false` 并报告缺依赖/夹具，**不要硬画用户图**。
5. **PASS**：写 `qa/onboard_selftest.json`（ready、gate 路径、SBS、时间），再加载 quality-merge 开用户任务。

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
