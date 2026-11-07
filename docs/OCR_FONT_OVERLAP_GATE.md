# OCR 字号 + 叠字硬门禁（Kevin t48u）

English: hard gate that compares A-preview OCR ink height to ORIG (`h_med`) and rejects text–text bbox collisions before any PASS, freeze, or upload.

`tools/ocr_font_overlap_gate.py` is already in this repo. The skills that require it are already updated:

- `botdraw`
- `internaldraw`
- `internaldraw-2`
- `paper-figure-quality-merge`
- `paper-figure-type-calibration`
- `paper-figure-text-layout-clearance`
- `paper-figure-indistinguishable-gate`

`skills/` 按 [INSTALL.md](../INSTALL.md) 拷进 bot 的 workflows 根。`tools/ocr_font_overlap_gate.py` 留在克隆目录的 `tools/`（或拷到项目 `tools/` / `workflows/tools`），不必和技能文件夹混放。

画完每张图、声称 PASS / 冻结 / 上传 Drive 前：

```bash
FIG_ROOT=<figroot> python tools/ocr_font_overlap_gate.py A FigXX
```

要求 `qa/<fig>_ocr_font_overlap.json` 中：

- `font_pass: true`（对 ORIG 的 OCR 字高 h_med）
- `overlap_pass: true`（A 预览 OCR 墨迹框叠字 = 0）

仅 office check-overlap 不够。入口是 `botdraw`。`internaldraw` / `internaldraw-2` 是历史别名。

t48u 的 `version` 仍是 `2026-10-28-t48u`。`norm` 仍只保留字母数字，`pass` 仍只等于 `font_pass` 且 `overlap_pass`。不要为了让某个样本变绿去改 `IOU_FAIL` 或 `h_med` 带宽。

同一轮会另写 `qa/<fig>_spatial_ocr_pairing.json`（`spatial-ocr-pairing-v1`）。那份报告保留比较符，做全局一对一，并单列未配行。`spatial_pairing_changes_historical_pass` 为 false。历史 JSON 里的 `pass` 不会因为它改写。只看配对报告时，退出码 0 只表示文件写出来了。

也可以不跑 OCR，直接：

```bash
python3 tools/spatial_ocr_pairing.py --source qa/src_boxes.json --redraw qa/redraw_boxes.json --out qa/Fig_spatial_ocr_pairing.json
```

方向缺失时不会被当成水平。详见 [QUALITY_SYNC.md](QUALITY_SYNC.md)。

`FIG_ROOT` 是操作者自己的图目录（`orig/`、`prev/<A|B>/`、写出的 `qa/`）。本仓库不含论文图。不要把生成的 `qa/*.json` 或 `.ocr_cache/` 提交进来。脚本需要本机 Python 3、`Pillow`、`rapidocr_onnxruntime`。任一图未过硬门禁时进程退出码为 1。
