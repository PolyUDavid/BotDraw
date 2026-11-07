# 质量同步：命令、层级、停止规则

这份说明服务当前 BotDraw 仓库。合成测试全绿只证明工具逻辑，不是用户图 PASS，也不是原生 PowerPoint 或 Blender 验收。

## 安装后会真正跑到的入口

1. 把 `skills/` 拷进 workflows 根（见 [INSTALL.md](../INSTALL.md)）。
2. 新对话加载 `botdraw`。它的加载顺序包含六个技能：`paper-figure-source-symbol-audit`、`paper-figure-font-renderer-proof`、`paper-figure-spatial-ocr-pairing`、`paper-figure-semantic-overlap-exceptions`、`paper-figure-data-provenance`、`paper-figure-unified-delivery`。
3. `paper-figure-quality-merge` 与 `paper-figure-onboard-selftest` 使用同一组名字。`internaldraw` 与 `internaldraw-2` 只指向 botdraw。

```bash
python3 tools/quality_sync.py selftest
python3 tools/quality_sync.py wiring
python3 -m unittest discover -s tests -v
```

这三条只用 Python 3 标准库。`selftest` 只跑 `tests/test_quality_primitives.py`。完整回归用第三条，里面还有正反例集成测试。

## 可选依赖

| 命令 | 何时需要 | 缺失时 |
| --- | --- | --- |
| `tools/ocr_font_overlap_gate.py`、`tools/onboard_selftest.py` 的绘制夹具 | Pillow、`rapidocr_onnxruntime`、DejaVu 或 Liberation 字体 | 不能宣称 t48u 或 `ready:true` |
| `python3 tools/quality_sync.py font-evidence --pdf FILE` | 无。`pdffonts`（poppler-utils）可选 | 仍读取 PDF 里的 `/BaseFont`；span 归属 UNKNOWN |
| LibreOffice、Blender、原生 PowerPoint | 预览、B 渲染、原生回验 | 写成 `NOT_PERFORMED` 或 UNKNOWN，不要写成 PASS |

`fc-match` 只允许出现在 `fc_match_prediction`。它不是本次 PDF 的字体证明。

## 六条状态轴

`measurement`、`source_review`、`visual_review`、`owner_acceptance`、`native_application_review`、`delivery_integrity`。

```bash
python3 tools/quality_sync.py status-policy --state qa/<fig>_status.json
```

用户可以接受当前外观，同时测量保持 FAIL。旧报告不原地改成 PASS。

## 停止 / 继续

- `CONTINUE_REPAIR`：测量仍失败，同一类尝试次数还没到上限。
- `STOP_SAME_CLASS`：同一缺陷类、同一门禁版本，达到上限（默认 3）。停止这一类重试。
- `CONTINUE_RETEST_NEW_VERSION`：门禁版本变了，用同一输入重测。旧文件保留。
- `STOP_ACCEPTED_STYLE_KEEP_FAIL`：用户已接受当前外观，且没有新的技术修复请求。
- `CONTINUE_NEW_CLASS`：缺陷类变了。
- `REJECT_REWRITE`：试图把历史 FAIL 写成 PASS。
- `REJECT_FALSE_PASS`：用合成绿宣称用户图 PASS。
- `REJECT_NATIVE_CLAIM`：原生应用没做却宣称原生 PASS。
- `STOP_DELIVERY`：交付完整性失败。
- `CONTINUE_DELIVER`：测量、源、目视、交付、原生都过。
- `CONTINUE_DELIVER_NATIVE_UNKNOWN`：其余都过，原生仍未知。可以交付文件，不能写原生 PASS。
- `STOP_INCOMPLETE`：还有 UNKNOWN 或 FAIL。

## 常用命令

```bash
python3 tools/quality_sync.py resolve-variant --root "$FIG_ROOT" --tag Fig01 --variant B
python3 tools/quality_sync.py audit-coverage --ledger qa/Fig01_symbol_ledger.json
python3 tools/quality_sync.py math-signature --xml qa/choice.xml --compare qa/other.xml
python3 tools/spatial_ocr_pairing.py --source qa/src.json --redraw qa/redraw.json --out qa/Fig01_spatial_ocr_pairing.json
python3 tools/quality_sync.py review-semantic --report qa/raw.json --exceptions qa/exceptions.json
python3 tools/quality_sync.py review-series --series qa/series.json
python3 tools/quality_sync.py review-media --slot qa/slot.json
python3 tools/quality_sync.py review-vehicle --record qa/vehicle.json
python3 tools/quality_sync.py font-evidence --pdf prev/A/Fig01.pdf
python3 tools/quality_sync.py freeze --source "$FIG_ROOT" --dest "$SNAP" --files files.txt --manifest "$SNAP/manifest.json"
python3 tools/quality_sync.py make-zip --snapshot "$SNAP" --manifest "$SNAP/manifest.json" --output part.zip
python3 tools/quality_sync.py verify-zip --archive part.zip --manifest "$SNAP/manifest.json"
python3 tools/export_skill_sync.py /tmp/skills_sync_export.zip
```

`files.txt` 每行一个相对路径，例如 `out_A/Fig01.pptx`。布局门禁与 `resolve-variant` 都拒绝缺 B 时回退到 A。t48u 与 t49u 的阈值没有为了样本通过而改动。

## 仍要人工或可选工具的部分

- 源图逐符号阅读、同 ROI 裁切和科学语义是否成立。
- PDF 里某一个希腊字母的 span 归属（本仓库只读 `/BaseFont`；有 `pdffonts` 也只是整页字体列表）。
- 重新打开 `.blend` 并抄录 Freestyle 等实值。校验器只检查记录，不启动 Blender。
- 原生 PowerPoint 排版。
- 云端目录若没有 hash 字段，`remote_hash_verified` 保持 UNKNOWN。
