---
name: paper-figure-gold-bar-calibration
description: >-
  Use when raising unreadable "精致/ORIG-grade" prose into a cross-bot
  reproducible bar: gold_bar crops+checklists, PPT type ruler (geometry only),
  and Kevin crop feedback loop. Load with quality-merge / botdraw (t53u/t54u).
---
# Gold-bar calibration — 跨 bot 可复现精致度（t53u/t54u）

**Kevin t54u 核心：** 不是只改这一次，而是标准化。换任何一台 bot、只要装了这套 skills + `gold_bars/` + tools，下一次给图就能一次画到同精致度。不同 AI 对散文理解不同 → **禁止把散文当唯一门禁**。

## 不可靠 vs 可靠

| 不可靠（禁单独作为 PASS） | 可靠（跨 bot 可复现） |
| --- | --- |
| 「精致」「ORIG 级」「一点一点贴」等散文 | `gold_bars/<archetype>/orig.png` + `checklist.md` 层数/笔触 |
| 口头说大脑好看 | icon-only SBS vs gold_bar 同裁切框 |
| 只写 `"pass": true` 无字段 | `qa/<fig>_scene_ui.json` 必含 `gold_bar_ref`/`layer_count`/`sulci_strokes`/`icon_sbs`/`pass` |
| PPT 标定页当精致唯一标准 | PPT `qa/<fig>_type_ruler.json` **只**管字号/轴几何 |

## 三件套

### A. Gold-bar 裁切库（主标准，可视）
路径（工作区）：`<FIG_ROOT>/gold_bars/<archetype>/`
同步进 BotDraw：`gold_bars/`（仓库根，与 `skills/` 并列）。

每个 archetype：
- `orig.png` — ORIG 像素裁切（或轴箭头 schematic+ORIG 角区）
- `pass_example.png` — 曾通过的复刻裁切（可先 ORIG 占位并在 checklist 注明）
- `checklist.md` — 最少层数 / 笔触 / 禁止项

当前 archetype：
- `brain_layered` — Fig01/Fig03 大脑
- `gear_layered` — Fig03 齿轮
- `axis_arrows_outward` — 轴端朝外（Fig09）
- `type_title_body_caption` — 字号阶梯示意

新失败类型：Kevin 贴裁切 → [paper-figure-feedback-to-skill](sand-workflow:paper-figure-feedback-to-skill) → 必要时 **新增 archetype**。

### B. PPT type ruler（辅，几何/字号）
可选 `qa/<fig>_type_ruler.json`：从 ORIG OCR 量 title/body/caption/hero 中位墨高 → pt；轴/箭头用模板几何。
**禁止**把 PPT 标定页当成大脑/图标精致度的唯一门禁。

### C. Kevin 标注裁切反馈环
归档 `user_feedback_YYYYMMDD/` → 映射 gate id → 升 gold_bar 或改 checklist → 再画。

## 一次画成流程（新 bot 必遵）
1. **量测** → `diag/<fig>_measure_coords.json`（bbox、role、font_px_orig、z-order）
2. **按 archetype 对照 gold_bar** 分层画 UI（脑/齿轮等打开对应 checklist）
3. **双门禁** `ocr_font_overlap_gate` + `layout_type_shape_gate`
4. **icon-only SBS** vs `gold_bars/<archetype>/orig.png`
5. **整页 ORIG\|A SBS** + 全套 qa JSON（缺 artifact = FAIL）

## 新 bot 最小包
`botdraw` 入口 + `tools/*.py` + `gold_bars/` + `docs/MASTER_PROMPT_zh.md`（整仓 clone 亦可）。

## Hard bans
- 散文标准单独 PASS
- 无 gold_bar SBS 宣称大脑/齿轮精致
- PPT ruler 替代 scene-ui / gold_bar
- 跨 bot 时省略 `gold_bars/` 目录
