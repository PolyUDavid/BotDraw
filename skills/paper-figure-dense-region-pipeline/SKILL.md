---
name: paper-figure-dense-region-pipeline
description: >-
  Use for high-density paper figures: region-freeze pipeline, zoom-trace,
  sibling bar matching best panel, refined layered UI on every region; full
  redraw when user says 全面重画.
---
# Dense figure region pipeline

Companion: quality-merge, fig01-gold-bar, scene-ui, full-omml, arrow-proportion.

## Pipeline
1. Slice regions + orig_zoom.
2. Zoom-trace measure.
3. One region → layered UI + OMML + arrows → SBS → freeze.
4. Sibling panels match best panel **and** Fig01/Fig03 UI craft bar — no “good enough separately”.
5. **每区 scene UI 不得降级**；脑/齿轮/复杂图标必须分层贴。
6. Screenshot-as-you-draw to Kevin.
7. Next fig only after current meets full checklist (or Kevin continue-all).
8. B last.

## Anti-patterns
Skipping UI polish on later figs; global type scale after freeze; approx_pass with coarse icons.
