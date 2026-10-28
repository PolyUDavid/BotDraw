---
name: paper-figure-scene-ui
description: >-
  Use for every paper-figure redraw: ORIG-grade layered refined UI (brain,
  gears, icons, cars, hubs) gated by gold_bars crops + checklist — mandatory
  icon-only SBS vs gold_bar. Ban flat clip-art. Cross-bot reproducible (t53u/t54u).
---
# Paper figure scene UI — gold_bar 分层（每图强制，跨 bot）

Load with [paper-figure-quality-merge](sand-workflow:paper-figure-quality-merge) and
[paper-figure-gold-bar-calibration](sand-workflow:paper-figure-gold-bar-calibration).

**t54u：** 散文「精致」不可靠。PASS 前必须对照 `gold_bars/<archetype>/` 裁切 + checklist，并写出可机读 JSON。

## Brain 强制层清单（`brain_layered`）
对照 `gold_bars/brain_layered/checklist.md` 与 `orig.png`：
1. base fill（封闭皮层体，禁单椭圆）
2. hemisphere splits（纵裂 ≥1）
3. sulci ≥ N 条（N = 对照 ORIG 裁切计数；最低 **8**）
4. ridge highlights
5. outline（ORIG 线重）
6. accents（net / nodes / glints 若 ORIG 有）

**禁：** 单椭圆、扁平 clip-art、MDI brain、无 sulci 的实心团。

## Gear（`gear_layered`）
base fill → teeth → rim → bore → highlight（+ 第二啮合轮若 ORIG 有）。禁 MDI gear。

## PASS 前
1. **icon-only SBS** vs `gold_bars/brain_layered/orig.png`（或对应 archetype；同裁切框）
2. 写 `qa/<fig>_scene_ui.json`，**缺一不可**：
```json
{
  "fig": "Fig03",
  "gold_bar_ref": "gold_bars/brain_layered/orig.png",
  "layer_count": 6,
  "sulci_strokes": 10,
  "icon_sbs": "qa/Fig03_brain_icon_sbs.png",
  "pass": false,
  "gaps": ["sulci fewer than ORIG", "missing ridge highlights"]
}
```
- `pass:true` 仅当 checklist 全满足且 icon SBS 目视对齐 ORIG 精致度
- 大脑明显扁 / 层数不够 → **`pass:false`** 并列出 `gaps`（不得散文糊弄）

## 其他 UI
Cars / hubs / icons：同样分层；有 archetype 则对照 gold_bar。

## Hard bans
跳过 UI；卡通单路径；无 `gold_bar_ref`/`icon_sbs` 宣称 PASS；用 PPT type ruler 当精致门禁。
