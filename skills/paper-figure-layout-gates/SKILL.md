---
name: paper-figure-layout-gates
description: >-
  Hard layout gates for paper-figure A-PPT: axis ticks, abl leaders, chart
  z-order/markers, Fig08 predicted-mechanism step line, and
  axis_arrows_outward_pass (t53u). Load with quality-merge.
---
# Layout gates (t41u + t42u + t53u axis outward)

Load with [paper-figure-quality-merge](sand-workflow:paper-figure-quality-merge).
Axis tip visual bar: `gold_bars/axis_arrows_outward/` + [paper-figure-gold-bar-calibration](sand-workflow:paper-figure-gold-bar-calibration).

## Gates
1. `axis_ticks_pass` — ORIG 有刻度短线则必须画
2. `abl_leader_pass` — Abl 标签↔点引导线
3. `band_under_series` / `vrefs_dashed` / `series_markers_pass` — Fig10
4. **`mech_step_line_pass` (Fig08 t42u):** Predicted Mechanism 五段彩色阶梯粗水平线；仅图标+文字无粗线 = FAIL
5. **`axis_arrows_outward_pass` (t53u/t54u):**
   - Y 顶箭头 **朝上**；X 右箭头 **朝右**（朝外、离开绘图区）
   - **禁** connector `flipV`/`flipH` 导致 `a:headEnd` 画朝里
   - **优先** filled **poly tip**（`ax_y_head` / `ax_x_head`）；上行轴不要挂 OOXML headEnd
   - 对照 `gold_bars/axis_arrows_outward/orig.png`（PASS vs FAIL schematic）
   - JSON: `"axis_arrows_outward_pass": true`, `"axis_tip_method": "poly_outward"`

Write `qa/<fig>_layout_gates.json`. Missing `axis_arrows_outward_pass` on figs with axes = FAIL.
