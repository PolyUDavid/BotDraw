---
name: paper-figure-scene-ui
description: >-
  Use for every paper-figure redraw: ORIG-grade layered refined UI gated by
  gold_bars; complete media slots (no cut-off; optional AI fill t58u); mandatory
  icon/media SBS. Ban flat clip-art.
---
# Scene UI + media slots

对照 gold_bars checklist 分层画；禁扁平 clip-art。

## t58u
- 照片/3D/仪表盘槽必须 **完整**（禁裁半）。
- 完整 ORIG 裁切优先；不和谐或不完整 → AI 局部补图插入（见 [paper-figure-media-slot-harmony](sand-workflow:paper-figure-media-slot-harmony)）。
- `qa/<fig>_scene_ui.json` + `qa/<fig>_media_slots.json`；icon/media SBS。
- Panel 字母不得压截图标题。

## PASS
缺 gold_bar 字段或 media complete:false → FAIL。

## Quality sync — layers are not a certificate
Start icons at the source proportion. Do not draw a small thick placeholder and scale it up later. Windows, wheels, lamps, and bumpers are separate checks when the source shows them. `layer_count` and mesh or sample counts do not certify refinement. Pair with [paper-figure-b-blender](sand-workflow:paper-figure-b-blender) for vehicle geometry and with [paper-figure-illustrator-layer-trace](sand-workflow:paper-figure-illustrator-layer-trace) for vector layer order.
