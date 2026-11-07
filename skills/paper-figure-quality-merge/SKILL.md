---
name: paper-figure-quality-merge
description: >-
  Use when redrawing paper/SI figures as editable A-PPT and B+Blender with
  Confirmation-gold QA, full OMML, gold_bar UI, OCR+layout gates, media-slot
  harmony (t58u), indistinguishable gate, and t68u crude-B ban. Load before
  drawing or claiming PASS. Keeps measurement, source review, visual review,
  owner acceptance, native application review, and delivery integrity separate.
---
# Paper figure quality merge

**Final bar:** [paper-figure-indistinguishable-gate](sand-workflow:paper-figure-indistinguishable-gate).

## 跨 bot（t54u）
可靠标准 = gold_bars + 数字门禁 + artifact；禁散文单独 PASS。

<!-- botdraw-load-order -->
## Locked stack
0. paper-figure-onboard-selftest
1. botdraw
2. paper-figure-quality-merge
3. paper-figure-data-provenance
4. paper-figure-gold-bar-calibration
5. paper-figure-media-slot-harmony（t58u）
6. paper-figure-fig01-gold-bar
7. paper-figure-full-omml
8. paper-figure-source-symbol-audit
9. paper-figure-arrow-proportion
10. paper-figure-scene-ui + paper-figure-illustrator-layer-trace（t126）
11. paper-figure-type-calibration + paper-figure-text-layout-clearance
12. paper-figure-font-renderer-proof
13. paper-figure-layout-distribution
14. paper-figure-semantic-overlap-exceptions
15. paper-figure-spatial-ocr-pairing
16. paper-figure-layout-gates（含 axis_arrows_outward）+ paper-figure-layout-gates-2（按文件夹）
17. paper-figure-hierarchical-measure + paper-figure-dense-region-pipeline
18. paper-figure-indistinguishable-gate
19. paper-figure-a-ppt
20. paper-figure-b-blender（t68u 禁粗糙 B）
21. paper-figure-unified-delivery
Also: feedback-to-skill. 旧别名 internaldraw / internaldraw-2 只指向 botdraw。

## 六条状态轴
`measurement`（原门禁原报告）、`source_review`、`visual_review`、`owner_acceptance`（范围写明）、`native_application_review`、`delivery_integrity`。
报告绑定当前 PPTX SHA、源图 SHA、预览 SHA、脚本版本和命令退出码。旧截图不能冒充当前。

```bash
python3 tools/quality_sync.py status-policy --state qa/<fig>_status.json
```

## 检查层级与停止/继续
- L0 合成工具：全绿只证明工具逻辑，不能声明用户图 PASS。
- L1 测量：历史 FAIL 文件不改写成 PASS。新测量用新文件。
- L2 源内容：符号、数据出处、媒体身份。
- L3 目视：逐区样式。AABB 相交但有墨迹间隙时分开写。
- L4 用户接受：可以和 L1 的 FAIL 并存。接受不翻转测量。
- L5 原生应用：没打开 PowerPoint 就是 `NOT_PERFORMED`，不能写成原生 PASS。
- L6 交付：SHA/CRC/`out_A`/`out_B`。失败则 `STOP_DELIVERY`。

动作：
- 同一缺陷类、同一门禁版本，连续达到上限（默认 3）→ `STOP_SAME_CLASS`。不要无限重试同类 FAIL。
- 门禁版本变了 → `CONTINUE_RETEST_NEW_VERSION`，旧报告保留。
- 用户已接受当前外观且没有新的技术修复请求 → `STOP_ACCEPTED_STYLE_KEEP_FAIL`。
- 新缺陷类 → `CONTINUE_NEW_CLASS`。
- 把合成绿或未做的原生回验说成用户图 PASS → 拒绝。
- 测量、源、目视、交付都过，且原生也过 → `CONTINUE_DELIVER`。原生未做则交付可以继续，但原生结论保持 UNKNOWN。

## Contract
One PPTX/fig; slide=ORIG.
Before PASS:
```bash
python3 tools/quality_sync.py selftest
python tools/ocr_font_overlap_gate.py A FigXX
python tools/layout_type_shape_gate.py A FigXX
```
+ **目视**清叠字/裁半（门禁假阴性仍 FAIL）
+ `qa/<fig>_media_slots.json` 每槽 `complete:true`
+ scene_ui / indistinguishable artifacts
+ 有数学时的符号账本；宣称字体时的 PDF 证据
+ **有 B 时**：硬件/车辆槽须按投影类几何重建后的 Cycles，禁糊截图与过简灰块（Kevin t68u；见 [paper-figure-b-blender](sand-workflow:paper-figure-b-blender)）。缺 `out_B` 不得改读 `out_A`。

t48u 历史 PASS 与空间配对覆盖率是两份报告。配对工具不许改历史结论。科学叠放例外也不把 `measured_pass` 改成 true。

## Hard bans
Whole-slide paste as sole deliverable; potrace; fake math; coarse UI; bare arrows; **截图裁半**；OCR PASS 但肉眼叠字；散文精致无 artifact；**B 槽用糊截图/玩具灰块充数**；编造实验序列；用 fc-match 冒充 PDF 字体；把用户接受写进旧 FAIL。
**允许**：局部 media slot 用 AI 生图插入以和谐（禁整页 AI）；B 硬件用 Blender 按 ORIG 构图重建；源图自身的科学叠放记为例外。

## Loop
Designer → Drawer → Reviewer → Corrector；**一区一检**（叠字+媒体完整+SBS crop）。同一类 FAIL 到停止规则就停，把缺的证据写成 UNKNOWN。
