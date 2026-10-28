# BotDraw

论文插图 1:1 临摹 → 可编辑纯矢量 A-PPTX（可选 Blender B）技能包，供下一台 Grok Bot 下载安装。

English: a standalone skill pack that traces paper figures 1:1 into editable pure-vector A-PPTX, with an optional Blender B pass. Clone it onto the next Grok Bot or Cursor Agent and copy `skills/` into that bot’s workflows root.

**Clone:** `https://github.com/PolyUDavid/BotDraw.git`

本仓库自包含。技能正文里的 `sand-workflow:` 链接是技能 id，不是外部仓库依赖。更早的草稿仓库是 [PolyUDavid/internaldraw](https://github.com/PolyUDavid/internaldraw)；BotDraw 不读取、不依赖它。

## 入口

先加载 **`botdraw`**。它会拉起 `paper-figure-quality-merge`、`paper-figure-gold-bar-calibration` 与 `paper-figure-media-slot-harmony`（t58u），再带上 Fig01 金线、全真 OMML、箭头小尾巴、对照 `gold_bars/` 的精致分层 UI、轴箭头朝外、t48u OCR 字号与叠字硬门禁、t49u 同类型字号与叠图布局硬门禁，以及版式、测量、密图分区和不可区分门禁。不要跳过 quality-merge、gold-bar 校准或 media-slot-harmony 直接画图或宣称 PASS。

`internaldraw` 与 `internaldraw-2` 是历史别名，职责与 **botdraw** 相同；新对话请用 **botdraw**。二者同样应拉起 `paper-figure-media-slot-harmony`（或直接加载 botdraw，由其加载顺序带上该技能）。

- **t58u：** `@botdraw` 加载顺序包含 `paper-figure-media-slot-harmony`（边画边自检、禁截图裁半、可选局部 AI 补槽）。见 [docs/README_T58U.md](docs/README_T58U.md) 与 [docs/T58U_MEDIA_SLOT.md](docs/T58U_MEDIA_SLOT.md)。

安装步骤见 [INSTALL.md](INSTALL.md)。技能关系见 [docs/OVERVIEW.md](docs/OVERVIEW.md)。本地 Cursor 粘贴提示词见 [docs/MASTER_PROMPT_zh.md](docs/MASTER_PROMPT_zh.md)（对话里 `@botdraw`）。

## 技能一览

| 文件夹 | 一句话职责 |
| --- | --- |
| `botdraw` | 主入口。先加载本技能，再拉 quality-merge、gold-bar 校准、media-slot-harmony（t58u）、t48u OCR 门禁、t49u 同类型/叠图门禁与其余门禁。 |
| `internaldraw` | 历史别名，指向 `botdraw`（含 gold-bar 与 media-slot-harmony）。新对话请用 botdraw。 |
| `internaldraw-2` | 历史别名，指向 `botdraw`（与 `internaldraw` 同一套门禁，含 gold-bar 与 media-slot-harmony）。 |
| `getting-started` | 新 bot 首次对话：问清语言、Drive、期刊与风格参考。 |
| `paper-figure-quality-merge` | 总闸。锁定金线栈（含 gold_bars、t58u media-slot-harmony、t48u OCR 字号+叠字，以及 t49u 同类型字号+叠图）；画前或宣称 PASS 前必载。散文「精致」不可单独 PASS。 |
| `paper-figure-gold-bar-calibration` | 跨 bot 精致度主标准：`gold_bars/` 裁切 + checklist。禁散文单独 PASS。 |
| `paper-figure-fig01-gold-bar` | ConsensusRetNet Fig01 外观金线；Fig02–10 同一标准；UI 对照 gold_bars。 |
| `paper-figure-full-omml` | 全真可编辑 OMML，且 Fallback 预览要像 ORIG 的 LaTeX。 |
| `paper-figure-arrow-proportion` | 有向边必须是杆 + 可见小尾巴；禁裸三角与巨头。 |
| `paper-figure-media-slot-harmony` | t58u：边画边自检叠字与裁半；媒体槽必须完整；优先完整 ORIG 裁切，必要时 AI 局部补槽。 |
| `paper-figure-scene-ui` | 每图强制精致分层 UI。大脑强制层；icon SBS vs gold_bar；`scene_ui.json` 必含 gold_bar 字段；媒体槽完整（t58u）。 |
| `paper-figure-layout-gates` | 坐标刻度、Abl 引导线、图表层级、Fig08 机制阶梯线、`axis_arrows_outward_pass`。 |
| `paper-figure-layout-gates-2` | 文字入框、左右不镜像、Key 网格 IoU。YAML `name` 与上一文件夹冲突，按路径加载。 |
| `paper-figure-text-layout-clearance` | 整块文本框、边距，以及文字与线/箭头/图标的间隙；t48u OCR 叠字与 t49u 叠图硬门禁；t58u 边画边自检。 |
| `paper-figure-type-calibration` | 按 ORIG 测高再落字；禁止整页统一放大当唯一修复；t48u OCR 字号与 t49u 同类型字号锁定。 |
| `paper-figure-hierarchical-measure` | 大面板 → 小模块 → 整块文本；同一 `(panel, role)` 共用字号；ORIG 像素 1:1 映到 PPT。 |
| `paper-figure-dense-region-pipeline` | 密图分区冻结：切片、zoom-trace、逐区画完再冻结。 |
| `paper-figure-layout-distribution` | 同类型字号锁定、叠图与 ORIG 间距；t49u `layout_type_shape_gate`。 |
| `paper-figure-indistinguishable-gate` | 交付前对照 ORIG 自检（OCR 与 t49u 布局门禁，外加 gold_bar 字段、轴朝外与 t58u 媒体槽 complete）；缺 artifact 或任一硬缺陷即 FAIL。 |
| `paper-figure-feedback-to-skill` | 失败裁剪归档、映到门禁、必要时新增 gold_bar archetype、改技能，再重画。 |
| `paper-figure-a-ppt` | A 版合同：每张图一个纯矢量可编辑 PPTX。 |
| `a-ppt` | A 版执行：真 OMML、箭头小尾巴、分层 UI、重叠门禁、只缩不放。 |
| `paper-figure-b-blender` | A 通过之后的 B 版：Cycles 载具/三维插图，标注仍可编辑。 |
| `ppt-blender` | 论文全套 A+B 重绘流程（一图一 PPTX、OMML、重叠硬门禁）。 |
| `scientific-figure-faithful-replica` | 保真临摹，不是改设计：几何、图种、公式跟 ORIG。 |
| `vector-ui-overlay-stack` | OCR 叠齐 + 多层矢量 UI；Designer→Drawer→Reviewer→Corrector 逐区过闸。 |
| `advsci-endnote-polish` | Advanced Science 文献核实、排版、润色与 EndNote（稿件技能，不是插图绘制）。 |

共 27 个技能文件夹，每个里面一份 `SKILL.md`。

## t53u/t54u 金标（gold bar）

- 新增仓库根 `gold_bars/` 与技能 `paper-figure-gold-bar-calibration`。
- 散文「精致/ORIG级」不可单独 PASS。
- scene-ui：大脑强制层；icon SBS vs gold_bar；`scene_ui.json` 必含 gold_bar 字段。
- layout-gates：`axis_arrows_outward_pass`。
- 跨 bot 最小包：`botdraw` + `tools/` + `gold_bars/` + [docs/MASTER_PROMPT_zh.md](docs/MASTER_PROMPT_zh.md)。

`gold_bars/` 与 `skills/` 并列。每个 archetype 有 `orig.png`、`pass_example.png`、`checklist.md`。当前四类：`brain_layered`、`gear_layered`、`axis_arrows_outward`、`type_title_body_caption`。说明见 [docs/GOLD_BAR_CALIBRATION.md](docs/GOLD_BAR_CALIBRATION.md)。

## 硬门禁（ConsensusRetNet 金线）

画图与交付按这条金线，缺一项即未过：

1. **Clearance（留白与不重叠）。** 整块文本入框；ink 与边、邻字、箭头、图标留间隙；只允许局部缩小，禁止短字符串放大。
2. **全真可编辑 OMML + 像 LaTeX 的 Fallback。** Choice 用完整 `m:oMath`。LibreOffice 画的是 Fallback，所以保留 `mc:AlternateContent`，Fallback 用 DrawingML 富文本（`a:rPr baseline` 真下标/上标、横分式或堆叠分子分母）。禁止 unwrap Choice、禁止 Unicode 括号下标 `₍` `₎`、禁止 `V_sys` 这类下划线假公式。
3. **箭头杆 + 小尾巴。** 每条有向边是 shaft 加清晰箭头；杆在导出图上肉眼可见。裸三角、巨头、发丝线都是 FAIL。
4. **精致分层 UI。** 图标从底到顶一层层贴（底色、形体、齿/沟、内形、轮廓、高光）。扁平剪贴画、单形状脑/齿轮不算过。
5. **坐标刻度。** ORIG 有刻度短线就必须画（`axis_ticks_pass`）。
6. **Abl 引导线。** Abl 标签与点之间要有 leader（`abl_leader_pass`）。
7. **Fig08 机制阶梯线。** Predicted Mechanism 区要有五段彩色阶梯粗水平线（Hybrid 绿 / PoS 蓝 / PBFT 紫 / PoW 红 / DPoS 橙），竖虚线分隔；只有图标加文字、没有粗线 = FAIL（`mech_step_line_pass`）。
8. **不可区分门禁。** 交卷前写 SBS 与 `qa/<fig>_indistinguishable.json`。读者看得见的重叠、错内容、假公式、劣箭头、粗糙 UI，任一即 FAIL。
9. **密图分区冻结。** 高密度图先切片和 zoom-trace，一个区域做完分层 UI、OMML、箭头并 SBS 通过后再冻结；兄弟面板对齐最好的那一块，不得逐图降级。
10. **OCR 字号 + 叠字（t48u）。** 宣称 PASS / 冻结前跑 `tools/ocr_font_overlap_gate.py`。`qa/<fig>_ocr_font_overlap.json` 必须 `font_pass` 且 `overlap_pass`。只靠 office check-overlap 不算过。
11. **同类型字号 + 叠图（t49u）。** 同一轮再跑 `tools/layout_type_shape_gate.py`。`qa/<fig>_layout_type_shape.json` 必须 `type_uniform_pass`、`shape_overlap_pass`、`text_shape_clear_pass`。只过 t48u OCR、同一 role 字号不齐、或卡片/图标仍叠，都不算过。
12. **Gold-bar 精致度（t53u/t54u）。** 散文「精致/ORIG级」不可单独 PASS。对照 `gold_bars/<archetype>/` 裁切与 checklist；icon SBS vs gold_bar。`qa/<fig>_scene_ui.json` 必含 `gold_bar_ref`、`layer_count`、`sulci_strokes`、`icon_sbs`、`pass`。
13. **轴箭头朝外。** 有坐标轴则 `axis_arrows_outward_pass`：Y 顶朝上、X 右朝右；优先 poly tip；禁止 flip 把箭头画朝里。
14. **媒体槽完整（t58u）。** 边画边自检叠字与裁半。禁止截图裁半。优先完整 ORIG 裁切；槽不完整或不和谐时允许局部 AI 补图插入（禁整页 AI）。`qa/<fig>_media_slots.json` 每槽 `complete:true`。技能 `paper-figure-media-slot-harmony`，由 `@botdraw` 加载。

## 工具

`tools/fig_gate_audit.py` 与 `tools/audit_omml_arrows.py` 是本地 PPTX 审计脚本（OMML、Fallback 泄漏、箭头杆）。宣称 PASS 前必须同时跑过两道硬门禁：

- `tools/ocr_font_overlap_gate.py`（Kevin t48u）：对 ORIG 比字高（`font_pass` / `h_med`），并检查 A 预览墨迹框叠字（`overlap_pass`）。用法见 [docs/OCR_FONT_OVERLAP_GATE.md](docs/OCR_FONT_OVERLAP_GATE.md)。
- `tools/layout_type_shape_gate.py`（Kevin t49u）：同一 `(panel, role)` 字号锁定（`type_uniform_pass`），卡片/图标兄弟形状不叠图（`shape_overlap_pass`），文字不骑非父级图形（`text_shape_clear_pass`）。用法见 [docs/LAYOUT_TYPE_SHAPE_GATE.md](docs/LAYOUT_TYPE_SHAPE_GATE.md)。

它们不携带论文数据。默认路径指向操作者自己的工作区，运行前改成你的目录，或把 PPTX 路径传给 `audit_omml_arrows.py`。不要把生成的 `*.pptx`、`qa/*.json` 或 `.ocr_cache/` 提交进本仓库。

## 仓库里没有的东西

不含论文原稿、插图、Drive 文件 ID、令牌或密钥。那些留在操作者自己的工作区。
