---
name: internaldraw
description: >-
  Legacy alias for botdraw. Prefer loading botdraw (PolyUDavid/BotDraw primary
  entry). Same stack: 1:1 A-PPT, full OMML, OCR+layout gates.
---
# internaldraw（历史别名）

**请改用主入口 [botdraw](sand-workflow:botdraw)。**
本文件夹仅兼容旧提示词；加载后立即按 **botdraw** 全套执行（quality-merge + t48u OCR + t49u 布局/叠图 + 其余门禁）。

```bash
FIG_ROOT=<figroot> python tools/ocr_font_overlap_gate.py A FigXX
FIG_ROOT=<figroot> python tools/layout_type_shape_gate.py A FigXX
```
