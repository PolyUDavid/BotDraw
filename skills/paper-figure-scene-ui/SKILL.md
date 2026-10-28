---
name: paper-figure-scene-ui
description: >-
  Use for every paper-figure redraw: ORIG-grade layered refined UI (brain,
  gears, icons, cars, hubs) — mandatory on each fig, same standard later. Ban
  flat clip-art.
---
# Paper figure scene UI — 精致分层（每图强制）

Kevin t38u/t39u: **所有 UI 高度精致还原原图那种一点一点一层一层贴上去**；写进 skills/工作流后 **每张图都不少**，后续同标。

Load with quality-merge before Drawer. Missing `qa/<fig>_scene_ui.json` = no PASS.

## Layer recipe
1. Measure ORIG crop (silhouette, strokes, inlays, highlights).
2. Stack bottom→top: base fill → mid forms → ridges/teeth/sulci → inner glyphs → outline → accents.
3. **Brain / gears** (Fig03+): multi-shape only; ban single oval / MDI gear.
4. Other icons, cars, hubs: same layered craft.
5. Icon-only SBS before freeze.

## Gates
`qa/<fig>_scene_ui.json`: `icon_fineness=layered_orig_grade`, layer counts, SBS paths.
FAIL if any panel’s UI is flatter/coarser than ORIG craft in SBS.

## Hard bans
Skipping UI polish on “simple” figs; cartoon/single-path icons; claiming PASS without scene_ui artifact.
