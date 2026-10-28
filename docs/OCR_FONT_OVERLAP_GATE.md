# OCR 字号 + 叠字硬门禁（Kevin t48u）

English: hard gate that compares A-preview OCR ink height to ORIG (`h_med`) and rejects text–text bbox collisions before any PASS, freeze, or upload.

`tools/ocr_font_overlap_gate.py` is already in this repo. The six skills that require it are already updated:

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

仅 office check-overlap 不够。入口仍是 `internaldraw`。

`FIG_ROOT` 是操作者自己的图目录（`orig/`、`prev/<A|B>/`、写出的 `qa/`）。本仓库不含论文图。不要把生成的 `qa/*.json` 或 `.ocr_cache/` 提交进来。脚本需要本机 Python 3、`Pillow`、`rapidocr_onnxruntime`。任一图未过硬门禁时进程退出码为 1。
