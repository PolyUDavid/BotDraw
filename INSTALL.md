# 安装 BotDraw

把本仓库的 `skills/` 拷进下一台 Grok Bot / Cursor Agent 的 **workflows 根目录**（该目录下每个子文件夹一份 `SKILL.md`，由 bot 按文件夹发现）。

```bash
git clone https://github.com/PolyUDavid/BotDraw.git
cd BotDraw

# 将 $BOT_WORKFLOWS_ROOT 换成这台 bot 实际的 workflows 根
mkdir -p "$BOT_WORKFLOWS_ROOT"
cp -a skills/. "$BOT_WORKFLOWS_ROOT/"

# 新 bot 首次：环境自检 + 固定金标证明。PASS 之前不要画用户图。
python3 tools/onboard_selftest.py
# 期望 qa/onboard_selftest.json 里 "pass": true
```

装完后，新对话先加载文件夹 **`botdraw`**。加载顺序第 0 步是 `paper-figure-onboard-selftest`（t69u）：新 bot 首次跑 onboard selftest，PASS 后再画。`internaldraw` 与 `internaldraw-2` 是历史别名，仅兼容旧提示词；二者应同样拉起 `paper-figure-media-slot-harmony`（或直接加载 botdraw）。主入口会拉起 `paper-figure-quality-merge`、`paper-figure-gold-bar-calibration`、`paper-figure-media-slot-harmony` 以及 OMML、箭头、分层 UI、t48u OCR 字号+叠字门禁、t49u 同类型字号+叠图门禁和其余门禁。

- **t58u：** `@botdraw` 加载顺序包含 `paper-figure-media-slot-harmony`（边画边自检、禁截图裁半、可选局部 AI 补槽）。见 [docs/README_T58U.md](docs/README_T58U.md)。
- **t68u B：** 需要 B 时加载顺序含 `paper-figure-b-blender`。糊截图或过简灰块 Cycles = FAIL；按 ORIG 用 Confirmation Cycles 重建（`film_transparent`、Freestyle `#34363A`、双 SUN、`SAMPLES≥96`）。范例：Fig08 (a) HIL / FiSens / PV。自测之后仍然有效。
- **t69u：** 新 bot 首次跑 `python3 tools/onboard_selftest.py`。`qa/onboard_selftest.json` 必须 `pass:true`（字号 `h_med`、叠字 0、布局门禁、一个媒体槽 SBS）。无此文件不得宣称 ready，不得开始用户 `FIG_ROOT`。

本地 Cursor 的粘贴提示词在 [docs/MASTER_PROMPT_zh.md](docs/MASTER_PROMPT_zh.md)：对话里 `@botdraw`。

`tools/` 留在克隆目录里按需运行，不必拷进 workflows 根。`fig_gate_audit.py` 需要本机已安装的 Python 3、`lxml`、`Pillow`，并且它写死了操作者工作区路径，跑之前改 `ROOT`。`audit_omml_arrows.py` 接受 PPTX 路径参数：

```bash
python3 tools/audit_omml_arrows.py /path/to/Fig01.pptx
```

`ocr_font_overlap_gate.py` 是宣称 PASS / 冻结前的 OCR 字号 + 叠字硬门禁（Kevin t48u）。需要 Python 3、`Pillow`、`rapidocr_onnxruntime`。`FIG_ROOT` 指向操作者自己的图目录：

```bash
FIG_ROOT=<figroot> python tools/ocr_font_overlap_gate.py A FigXX
```

通过条件与 JSON 字段见 [docs/OCR_FONT_OVERLAP_GATE.md](docs/OCR_FONT_OVERLAP_GATE.md)。仅 office check-overlap 不够。

`layout_type_shape_gate.py` 是同一轮宣称 PASS / 冻结前的同类型字号 + 叠图硬门禁（Kevin t49u）。需要 Python 3（标准库；读 PPTX 与 `diag/<fig>_measure_coords.json`）。`FIG_ROOT` 同样指向操作者自己的图目录：

```bash
FIG_ROOT=<figroot> python tools/layout_type_shape_gate.py A FigXX
```

通过条件：`qa/<fig>_layout_type_shape.json` 里 `type_uniform_pass`、`shape_overlap_pass`、`text_shape_clear_pass` 都为真。字段见 [docs/LAYOUT_TYPE_SHAPE_GATE.md](docs/LAYOUT_TYPE_SHAPE_GATE.md)。两道门禁都要过；只跑其中一道不算 PASS。

## 要拷贝的技能文件夹（28）

- `a-ppt`
- `advsci-endnote-polish`
- `botdraw`
- `getting-started`
- `internaldraw`
- `internaldraw-2`
- `paper-figure-a-ppt`
- `paper-figure-arrow-proportion`
- `paper-figure-b-blender`
- `paper-figure-dense-region-pipeline`
- `paper-figure-feedback-to-skill`
- `paper-figure-fig01-gold-bar`
- `paper-figure-full-omml`
- `paper-figure-gold-bar-calibration`
- `paper-figure-hierarchical-measure`
- `paper-figure-indistinguishable-gate`
- `paper-figure-layout-distribution`
- `paper-figure-layout-gates`
- `paper-figure-layout-gates-2`
- `paper-figure-media-slot-harmony`
- `paper-figure-onboard-selftest`
- `paper-figure-quality-merge`
- `paper-figure-scene-ui`
- `paper-figure-text-layout-clearance`
- `paper-figure-type-calibration`
- `ppt-blender`
- `scientific-figure-faithful-replica`
- `vector-ui-overlay-stack`

每个文件夹只含 `SKILL.md`。不要改名，入口技能按文件夹名加载。

## 名称冲突：`layout-gates` 与 `layout-gates-2`

这两个文件夹的 YAML 都写成了 `name: paper-figure-layout-gates`：

| 文件夹 | 内容 |
| --- | --- |
| `paper-figure-layout-gates` | ConsensusRetNet 金线（t41u/t42u/t53u）：坐标刻度、Abl 引导线、图表 z-order / 标记、Fig08 机制阶梯线、`axis_arrows_outward_pass`。`paper-figure-quality-merge` 指的是这一份。 |
| `paper-figure-layout-gates-2` | 文字入框（`text_in_box_pass`）、左右不镜像（`panel_side_match`）、Key 网格 IoU（`key_grid_iou`）。 |

若加载器只认 YAML `name`，后拷贝的那一份会盖住前一份。需要指定某一份时，**按文件夹路径加载**，不要只凭 `name`。两份都要留在 workflows 根里。

## t53u/t54u 追加

1. 仓库根保留 `gold_bars/`。
2. `ln -s /path/to/BotDraw/gold_bars FIG_ROOT/gold_bars`
3. 新技能 `paper-figure-gold-bar-calibration` 由 botdraw 加载顺序拉起。
