---
name: paper-figure-feedback-to-skill
description: >-
  Use when Kevin attaches failure crops or zoomed ORIG panels: archive, map to
  gates, update skills, add gold_bar archetype when needed, enforce
  indistinguishable-from-ORIG self-check, then redraw (t53u/t54u).
---
# Paper figure feedback → skill / gold_bar

**t54u：** 反馈要沉淀成下一台 bot 可执行的标准，不只是本轮口头改图。

1. Archive crops under `user_feedback_YYYYMMDD/` (+ `orig_zoom/` when magnified).
2. Map to gate ids（ocr / layout_type_shape / scene_ui / axis_arrows_outward / omml / arrow…）.
3. If defect is a **new visual class** (新图标精致度、新轴样式) → 新增 `gold_bars/<archetype>/`（`orig.png` + `checklist.md` + `pass_example.png`）并更新 [paper-figure-gold-bar-calibration](sand-workflow:paper-figure-gold-bar-calibration).
4. Update merge / layout / arrow / scene / type skills as needed.
5. Redraw under [paper-figure-indistinguishable-gate](sand-workflow:paper-figure-indistinguishable-gate): **no PASS until SBS looks like ORIG** and gold_bar checklist fields exist.
6. Clear every attached crop region before deliver.
7. Mention skill pills in Chinese; push BotDraw so **下一台 bot** 装到同一套。
