---
name: ppt-blender
description: >-
  用户要把论文（正文、SI、扩展数据）里的所有插图重绘成每图一个可编辑 PPT 时使用；风格为浅马卡龙配色，配 Blender 3D 渲染和 OMML
  可编辑公式
---
# 论文插图 PPT 重绘流程（A 版矢量 + B 版 Blender）

A 版细则与纯矢量临摹见 [a-ppt](sand-workflow:a-ppt)。保真一比一另遵 [scientific-figure-faithful-replica](sand-workflow:scientific-figure-faithful-replica) 与 [vector-ui-overlay-stack](sand-workflow:vector-ui-overlay-stack)。

## 输入
- 论文正文和 SI 的 docx（提取原图、图注、数据、公式）
- 风格参考 PPT 或 zip（配色、字体、版式）
- GenAI 图片素材（pptx 或图片）：**原样复制**，不重新生成

## 总体要求
1. 每张图（Fig / Extended Data Fig / SFig，含子图 a/b/c）单独一个 PPTX，按论文编号命名（`Fig01.pptx`、`ExtFig02.pptx`、`SFig20a.pptx`）。
2. 幻灯片尺寸 = 原图宽高比与尺寸，禁止默认 16:9。
3. 数据来自论文：优先正文/SI 数值与表；无原始数值则从原图描点，清单标注「描点」。
4. 全部可编辑：原生图表或矢量形状；文字用文本框；禁止整图截图当成品。
5. 公式一律可编辑 OMML（`a14:m` + `mc:AlternateContent` + 回退图）；禁止图片公式；回退形状 ID 必须唯一。
6. 配色：参考 PPT 浅马卡龙（粉/薄荷/淡蓝/淡紫/奶黄等低饱和），全套统一；文字与坐标轴深灰。
7. 字体：Arial/Helvetica（无衬线），字号符合期刊、各图一致。（若用户另行要求临摹原图衬线/Times，走 a-ppt 保真规则。）
8. 轴线、刻度、单位、图例、子图标号 a/b/c 齐全；线宽/圆角/阴影风格统一；图注与原文一致。
9. **重叠硬门禁**：每张图交付前必须 `office pptx check-overlap`（或等价）**通过（overlap/clip = 1.00）**；未过不得交、不得进下一张。 Gate JSON 须写 `overlap_pass: true|false`。

## A 版（标准可编辑矢量）
按 [a-ppt](sand-workflow:a-ppt)：OCR 后矢量从头临摹；禁止原图抠图/截图贴图/potrace；图标、小图、波形、网络块、车辆行人等用 PPT 形状或矢量路径；数据图用原生图表或描点矢量；真 OMML；每张预览；合成 `preview_all.pdf`；列出描点与偏差；**重叠必须过**。

## B 版（Blender）
1. 必须真实安装并使用 Blender（如 4.2 LTS，Cycles），不得用其他工具冒充。
2. 适合 3D 的示意图（场景、网络、系统、流程）建模渲染 → 高分辨率透明 PNG 插入 PPT；标注与公式仍可编辑。
3. 保留 `.blend` 与建模脚本，单独打包。
4. B 版在 A 版基础上加渲染；两版图齐全，分文件夹。

## 版本与进度
- A 版 / B 版分开保留（例如各 55 张或论文全部插图）。
- 每完成一张就存进度，可断点续做。
- LibreOffice（或等价）渲染预览；最后 `preview_all.pdf`。
- 数据不一致或描点清单交给作者核对。

## 交付
1. `zip -X`，文件在 zip 根目录（不嵌套），`unzip -t` 验证。
2. 单包尽量 ~10 MB；过大拆开（PPT 包 / 模型包）。
3. 上传用户 Google Drive 并给链接；约 <5 MB 也可聊天附件。
4. 旧包移入 `_superseded`。
