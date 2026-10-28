---
name: paper-figure-onboard-selftest
description: >-
  t69u first-run gate for a new BotDraw install. Self-detect Python, LibreOffice,
  Blender, OCR/layout tools, and gold_bars; run fixtures/onboard until
  qa/onboard_selftest.json passes. Do not start user FIG_ROOT work before pass.
  t68u crude-B ban still applies after this proof.
---
# Onboard self-test (Kevin t69u)

新 bot 克隆/安装 BotDraw 之后、**任何用户插图之前**跑本技能。入口仍是 [botdraw](sand-workflow:botdraw) 的加载顺序第 0 步。无 `qa/onboard_selftest.json` 或 `pass` 不为 true，禁止宣称 ready，禁止打开用户 `FIG_ROOT`。

## 命令
在仓库根：

```bash
python3 tools/onboard_selftest.py
```

退出码 0 且 `qa/onboard_selftest.json` 里 `"pass": true` 才算过。旁证 SBS：`qa/onboard_sbs.png`（字段 `sbs_path`）。

## 自检什么
1. **环境：** Python、Pillow、`rapidocr_onnxruntime`、`tools/ocr_font_overlap_gate.py`、`tools/layout_type_shape_gate.py`、`gold_bars/` 四类（orig + checklist + pass_example）。缺一则 `env_pass: false`。
2. **探测记录：** LibreOffice、Blender。缺 LibreOffice 只记 warning（用户图导出 PNG 前仍须安装）。缺 Blender 不挡住这次 A 证明；之后要 B 必须另装，且 **t68u 粗糙 B 禁令仍然有效**。
3. **固定证明（禁止散文）：** 对照 `fixtures/onboard/orig.png`（`spec.json` 迷你面板；媒体槽贴完整 `gold_bars/brain_layered/orig.png`，不裁半）。跑真门禁，不是口头「环境正常」。

## 调到 PASS 再停
脚本故意从偏小字号 + 文字框骑进媒体槽开始。FAIL 则自动：
- 按 `h_med` 调整 type scale，重渲预览
- 拉开文字框（clearance），避开槽
- 重跑两道门禁

最多 6 轮。仍 FAIL → 不要开始用户的图。

通过条件（与 `fixtures/onboard/expected.json` 一致）：
- `font_pass` 且 `h_med` 在 t48u 带内，`overlap_pass` 且叠字数 = 0
- `type_uniform_pass`、`shape_overlap_pass`、`text_shape_clear_pass`
- `media_slot_complete: true`

## 证明文件
`qa/onboard_selftest.json` 必含：`pass`、`ready_for_user_figures`、`env_pass`、`proof_pass`、`font_pass`、`overlap_pass`、`h_med`、`type_uniform_pass`、`shape_overlap_pass`、`text_shape_clear_pass`、`media_slot_complete`、`sbs_path`、`rounds`。生成物不要提交。

## 自测之后
t68u 仍在：Fig08 (a) HIL / FiSens / PV 必须是 Confirmation Cycles（`film_transparent`、Freestyle `#34363A`、双 SUN、`SAMPLES≥96`），禁止灰块或糊截图当 B。本证明不代替 B。
