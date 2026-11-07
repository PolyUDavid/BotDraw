# 当前 main 差异矩阵

对照基线是 GitHub `main` 的 `bb3153edd5b0c80ec45f59ed2fb21633a0713e6e`（调查时与 `origin/main` 相同）。附件里的本地技能 diff 只说明旧本地副本，不作为“远程缺失”的结论。下表是直接阅读该提交后的结果。

| 主题 | `bb3153e` 上实际有的 | 缺口 | 本分支 |
| --- | --- | --- | --- |
| 入口 | `botdraw` 加载 onboard、quality-merge、gold bar、media、OMML、箭头、scene-ui、**illustrator-layer-trace**、双门禁、t68u | 没有源符号、字体 PDF、空间配对、语义例外、数据出处、统一交付 | 六项技能进入 botdraw、quality-merge、onboard、README、INSTALL、总提示词、OVERVIEW。别名仍只指向 botdraw |
| 硬标准 | 真 OMML、箭头小尾巴、gold_bars、禁整页截图、数据侧有“忠实临摹”散文 | 散文没有机器可查的双版本与“覆盖≠正确” | 硬标准保留。新增账本/签名/系列校验 |
| 逐源符号 | `paper-figure-full-omml` 要求 Choice + Fallback，并点名若干式子 | 没有源图全扫、框外条件、完整树（含 `m:chr`）、覆盖与正确分账 | 新技能 + `math-signature` / `audit-coverage` |
| 字体 | t48u 用 OCR `h_med` | 没有把 `fc-match` 和本次 PDF 分开，也没有 span 证据字段 | `font-evidence` 读 PDF 字节里的 `/BaseFont`。span 在没有专用证据时保持 UNKNOWN |
| OCR 配对 | `ocr_font_overlap_gate.py` 的 `norm` 只留字母数字（约 79–80 行），`pair_heights` 每个源各自取最佳候选（约 116–151 行），`pass` 只看 `font_pass` 与 `overlap_pass`（约 175–181 行） | 比较符被剥掉，候选可被重复使用，未配源不阻止 PASS | **不改** t48u 版本号和阈值。另写 `spatial-ocr-pairing-v1`。历史函数行为由反例锁住 |
| 布局 A/B | `find_pptx` 先找 `out_A`，再 `rglob`（约 45–57 行） | 请求 B 时会命中 A 或旧备份 | 只读 `out_<variant>/<tag>.pptx`。缺文件失败。阈值常量未改。报告增加 SHA |
| 科学叠放 | t49u 把兄弟形状重叠当 FAIL | 没有对象级例外，也没有“禁止改写成测得 PASS” | `review_semantic` 复制原 `pass`，`overrides_gate_pass` 为 false |
| 媒体 | `complete: true`、禁裁半、AI 只填槽 | 没有 SHA、别名≠实验 run、错配必须换文件、srcRect / contain | `review-media` 与 media 技能补这些字段 |
| B 车型 | Confirmation 模板名：透明胶片、Freestyle 色、双 SUN、`SAMPLES≥96`；禁灰块 | 模板名不等于重开文件后的实值；加 samples 被当成进度；没有按投影类的固定尺度 SBS | `review-vehicle` 拒绝 samples-only、未重开、以及用局部轴冒充世界轮距。不启动 Blender |
| 数据 | 技能要求跟 ORIG，不改设计 | 没有系列级 raw / 像素几何 / verified 旁路隔离 | `review-series` 拒绝把像素几何说成实验序列，并拒绝旁路落在 `out_A`/`out_B` |
| 交付 | 技能提到 `out_A` 与 `out_B` | 没有白名单快照、CRC、缺 B 失败 | `freeze` / `make-zip` / `verify-zip`。远端 hash 未验证时写 UNKNOWN |
| 接受 vs 测量 | 单一 `pass` / `ready` | 用户接受会和测量混成一件事 | 六轴。`STOP_SAME_CLASS` 与 `STOP_ACCEPTED_STYLE_KEEP_FAIL` |
| 自检 | OnboardDemo + 两道门禁 | 新环境可以不加载上述证据链 | onboard 调用 `selftest` 与 `wiring`。缺技能文件则不能 ready |
| 私有材料 | 仓库已有 gold_bars 与合成 onboard 图 | 不能把未授权稿件裁切当成新金标 | 本分支只加合成 JSON/XML/PDF 字节。不新增论文图、账号、字体二进制 |

## 有意保留、没有当成缺口去“修掉”

- t48u 仍会剥掉比较符，并且一个候选框仍可服务多个源。新报告负责完整性。两边同时读。
- `paper-figure-layout-gates-2` 的 YAML `name` 仍是 `paper-figure-layout-gates`。按文件夹加载。
- illustrator-layer-trace 仍在 scene-ui 之后。质量合并栈没有拿掉它。
- 已有 gold_bars 图片保持原样。本分支不重新授权，也不替换成用户稿件裁切。

## 本分支仍做不到

- 不从 PDF 内容流证明某一个希腊字母用了哪个 face。
- 不自动重开 Blender，也不做原生 PowerPoint 回验。
- 不把云端文件大小当成 SHA。
- 合成夹具通过不等于任何一张用户图通过。
