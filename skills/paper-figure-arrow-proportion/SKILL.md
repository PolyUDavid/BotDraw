---
name: paper-figure-arrow-proportion
description: >-
  Use when redrawing paper-figure A-PPT connectors: ban triangle-only arrows,
  enforce balanced head/tail (Confirmation sarrow + Kevin 小尾巴), and gate headEnd
  size vs shaft weight before claiming PASS.
---
# Paper figure arrow proportion (Confirmation + Kevin 小尾巴)

Companion to [paper-figure-quality-merge](sand-workflow:paper-figure-quality-merge), [paper-figure-fig01-gold-bar](sand-workflow:paper-figure-fig01-gold-bar).

**Kevin t35u (Fig02–10 hard):** 三角形箭头要画清楚；**不要**以前那种过大三角；比例协调；**每一条有向边都要有可见小尾巴（shaft）**；头尾一体、方向对齐 ORIG。写进技能后全套 Fig02–10 一律执行。

## Gold pattern
- Confirmation `sarrow` / `carrow`: **filled head + shaft that stops at head base** (`_back` ≈ `hs*0.8`).
- Default visible unit: `lw≈1.6–2.0`, `hs≈6–8`（`head_len / lw ∈ [3, 5]`，目标 ≈4–5）。
- **小尾巴**：shaft 在导出 PNG 上肉眼可见（非 hairline）；短竖缝也要有短杆+小头，禁止只剩三角尖。
- Native OOXML `a:headEnd`：仅作备用；**LibreOffice 会翻转 headEnd** → 有向边优先 **poly shaft + poly head**（与 Confirmation 一致）。`w`/`len` 只用 `sm`/`med`，禁 `lg` 配细线。

## Direction (hard)
Match ORIG. 竖向流水 = 向下；水平 = ORIG 指向。方向反 = FAIL。

## Hard bans
1. **裸三角**（无 shaft，或 shaft 长 &lt; 2× head 长）—— Kevin「都要有小尾巴」。
2. **巨三角**（head 像独立 glyph；`head_len/lw` &gt; 6；或旧版 oversized heads）。
3. **看不见**：hairline `lw&lt;1.25` 配小头，或导出后箭头「不明显」。
4. Poly `*_head` 无匹配 `*_shaft`。
5. 只靠 `headEnd` 计数宣称 PASS。

## Drawer rules（Fig02–10）
1. 每条有向边 = shaft + head 一体；shaft 停在 head 底。
2. 用 `sarrow` / `slim_arrow` / `F.line(..., head=…)` 时保证 PNG 上 **头清晰 + 尾巴可见**。
3. 短缝（箱间 5–14px）：`lw≥1.55`，`hl≈max(2.4, 0.35–0.45×L)`，仍保留可见短杆。
4. 长边：不要把 head 放大成装饰三角；加粗 shaft 优先于加长 head。
5. RetNet ×N 侧面虚线括号等 ORIG 有的结构必须有。

## Reviewer gates (`qa/<fig>_arrow_gate.json`)
- `direction_match_orig`
- `no_bare_triangle`（每条有 `*_shaft`）
- `no_giant_head`
- `tail_visible`（小尾巴）
- `head_tail_ratio_ok` / `directed_clarity`
- 交付前 crop 有向边 SBS；Kevin 圈「不明显」= FAIL 重画该边

## Anti-patterns
- 为避巨头把全部箭头拧成看不见的针尖
- 箱间只用三角 tip、无杆
- Fig02 修好但 Fig03–10 仍用旧巨三角或裸三角
