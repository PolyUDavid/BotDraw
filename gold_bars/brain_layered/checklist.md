# brain_layered gold bar (t53u)

Source: ConsensusRetNet ORIG `Fig03.png` oracle node brain (primary);
secondary: `Fig01.png` brain_card icon (`orig_fig01_small.png`).

## Required layers (bottom → top)
1. **base fill** — white/cream cortex body (closed poly, not a single oval)
2. **hemisphere splits** — longitudinal fissure (≥1 center stroke)
3. **sulci** — ≥8 distinct curved sulcus strokes matching ORIG density (count on `orig.png`)
4. **ridge highlights** — ≥2 light edge/glint strokes on crown
5. **outline** — thick cortex stroke (ORIG weight)
6. **accents** — net/nodes/glints if ORIG has them

## Minimums
- `layer_count` ≥ 6 (named layers above)
- `sulci_strokes` ≥ 8 (count freehand curves on ORIG crop)
- Icon-only SBS vs this `orig.png` before PASS
- `qa/<fig>_scene_ui.json` must include: `gold_bar_ref`, `layer_count`, `sulci_strokes`, `icon_sbs`, `pass`

## Hard bans
- Single ellipse / stadium / MDI brain
- Flat clip-art fill with no sulci
- Claiming PASS with only prose "layered_orig_grade"
- Using PPT type-ruler page as the fineness gate

## pass_example.png
Placeholder = ORIG crop until a replica SBS passes; replace when Fig03 brain redraw freezes.
