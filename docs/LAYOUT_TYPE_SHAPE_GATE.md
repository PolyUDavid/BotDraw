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

入口：`internaldraw` → 会拉起 `paper-figure-layout-distribution`。
