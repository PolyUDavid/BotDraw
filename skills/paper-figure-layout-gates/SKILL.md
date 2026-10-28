---
name: paper-figure-layout-gates
description: >-
  Hard layout gates for paper-figure A-PPT: axis ticks, abl leaders, chart
  z-order/markers, Fig08 predicted-mechanism step line. Load with quality-merge.
---
# Layout gates (t41u + t42u)

Load with [paper-figure-quality-merge](sand-workflow:paper-figure-quality-merge).

## Gates
1. `axis_ticks_pass` — ORIG 有刻度短线则必须画
2. `abl_leader_pass` — Abl 标签↔点引导线
3. `band_under_series` / `vrefs_dashed` / `series_markers_pass` — Fig10
4. **`mech_step_line_pass` (Fig08 t42u):** Predicted Mechanism 区须有 **五段彩色阶梯粗水平线**（Hybrid绿/PoS蓝/PBFT紫/PoW红/DPoS橙），竖虚线分隔，高度/位置对齐 ORIG；仅图标+文字无粗线 = FAIL。Kevin 截图 `t42u/fig08_orig_axis_line.png`。

Write `qa/<fig>_layout_gates.json`.
