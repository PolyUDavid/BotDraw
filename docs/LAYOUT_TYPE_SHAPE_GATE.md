# t49u 布局 · 同类型字号 · 叠图

宣称 PASS / 冻结 / Drive 前必须同时：

```bash
FIG_ROOT=<figroot> python tools/ocr_font_overlap_gate.py A FigXX
FIG_ROOT=<figroot> python tools/layout_type_shape_gate.py A FigXX
```

`qa/<fig>_layout_type_shape.json` 要求：
- `type_uniform_pass`：同一 panel 内同一 role 字号一致（max/min ≤ 1.08）
- `shape_overlap_pass`：卡片/图标/徽章等非包含兄弟形状不叠（叠图）
- `text_shape_clear_pass`：文字不骑非父级图形

入口：`botdraw` → `paper-figure-layout-distribution`。`internaldraw` 只是别名。

解析器是 `explicit-out-variant-v1`。唯一输入是 `FIG_ROOT/out_A/<Fig>.pptx` 或 `FIG_ROOT/out_B/<Fig>.pptx`。`FIG_SUPPLEMENTARY=1` 时使用 `out_<variant>/SI/<Fig>.pptx`。缺 B 失败，错误文本包含 `refused fallback`。不读取另一变体，不递归搜索备份，拒绝符号链接。阈值常量仍是 `TYPE_RATIO_MAX=1.08`、`SHAPE_IOU_FAIL=0.05`、`TEXT_SHAPE_IOU_FAIL=0.06`，`version` 仍是 `2026-10-28-t49u`。成功报告额外有 `pptx_rel`、`pptx_sha256`、`resolver_fallback_used: false`、`thresholds_changed: false`。

科学叠放不要靠改这些阈值放过。用 `python3 tools/quality_sync.py review-semantic`，并保留原来的 `pass: false`。
