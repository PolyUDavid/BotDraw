# fixtures/onboard — OnboardDemo（t69u）

新 bot 的固定夹具，不是用户论文图。金标仍在仓库 `gold_bars/`。

## 指向 gold_bars

媒体槽必须贴**完整**的 [`gold_bars/brain_layered/orig.png`](../../gold_bars/brain_layered/orig.png)（contain，禁止裁半）。大脑精致度仍按 [`gold_bars/brain_layered/checklist.md`](../../gold_bars/brain_layered/checklist.md)（层数、沟回、icon SBS）。本夹具只证明门禁能跑、并且能调到过。

`orig.png` 由 `spec.json` 画出：标题、两条同 role 正文、一条 caption，右侧一个媒体槽。

## 如何产出 OnboardDemo

在 BotDraw 仓库根：

```bash
python3 tools/onboard_selftest.py
```

脚本把 `fixtures/onboard/orig.png` 放进临时 FIG_ROOT 的 `orig/OnboardDemo.png`，从偏小字号和骑槽文字框开始，按 `h_med` 与 clearance 自调，然后执行技能里的两道门禁：

```bash
FIG_ROOT=<onboard_root> python tools/ocr_font_overlap_gate.py A OnboardDemo
FIG_ROOT=<onboard_root> python tools/layout_type_shape_gate.py A OnboardDemo
```

通过后写 `qa/onboard_selftest.json`，其中 `"ready": true`，并带：

- `ocr`: `qa/OnboardDemo_ocr_font_overlap.json`
- `layout`: `qa/OnboardDemo_layout_type_shape.json`
- `sbs`: `qa/OnboardDemo_whole_sbs.png`

`ready` 不为 true 时不要开用户 FIG_ROOT。t68u 粗糙 B 禁令在此之后仍然有效。
