---
name: paper-figure-illustrator-layer-trace
description: >-
  Use when Kevin wants higher-end paper-figure UI via Illustrator-style layer
  tracing/structure (scientific-illustrator + illustrator-mcp patterns) mapped
  to pure-vector A-PPT: named layers, z-order back→front, multi-path icons,
  reconstruction_spec before draw.
---
# Illustrator-style layer trace → pure-vector A-PPT

Sources (study, then apply in PPT — box may lack Adobe Illustrator):
- Skills: [icebird1998/scientific-illustrator](https://github.com/icebird1998/scientific-illustrator) (Designer→Drawer→Reviewer→Corrector)
- MCP: [ie3jp/illustrator-mcp-server](https://github.com/ie3jp/illustrator-mcp-server) (`manage_layers`, `set_z_order`, `group_objects`, `create_path`/`ellipse`/`rectangle`/`gradient`, `get_layers`/`get_path_items`)

Load with [botdraw](sand-workflow:botdraw) + [paper-figure-quality-merge](sand-workflow:paper-figure-quality-merge) + [vector-ui-overlay-stack](sand-workflow:vector-ui-overlay-stack). **Kevin t125/t126: prefer pure vector; no ORIG screenshot embeds** unless he explicitly re-allows media slots.

## Layer grammar (map AI layers → PPT)
| Illustrator concept | A-PPT practice |
|---|---|
| Named layers (`manage_layers`) | Semantic shape names + `diag/<fig>_layers.json` listing back→front groups |
| `set_z_order` / `move_to_layer` | Draw order = z-order: background fill → panel chrome → icons (multi-path) → connectors → text/OMML |
| `group_objects` | One icon = many shapes treated as a motif (car body+window+battery badge); duplicate motif across cards |
| `create_path` + gradients | Freeform silhouettes + soft fills (pastel card fills, soft shadow rect under card) — ban single flat emoji/MDI |
| `get_document_structure` | After each region: inventory object count vs reconstruction_spec |

## Construction order (non-negotiable)
1. **Designer**: write `items/<Fig>_reconstruction_spec.json` — region ids, object ids, px bbox from ORIG, palette, typography (serif labels when ORIG uses serif), connector lanes, **z-order list**, grouping, acceptance notes. No draw before spec.
2. **Drawer**: one region at a time, **back → front**. Icons ≥3–6 layered paths (fill + mid + highlight/stroke). Soft rounded cards with inset highlight edge.
3. **Reviewer**: OCR+layout gates + icon-only SBS vs gold_bar / ORIG crop; scorecard target sem/edit/overlap 1.00, align≥0.95, ref≥0.90 (honest if short).
4. **Corrector**: object-level only; never flatten/screenshot to hide defects.

## Premium UI checklist (asset cards example)
- Pastel card fills matching ORIG (blue/green/lilac/peach), equal size, equal radius, soft drop shadow shape behind.
- Icons: car+battery, PV grid+sun, twin turbines (thin blades), house+battery — silhouette fidelity, not generic blobs.
- Labels: ORIG font family feel (Times/serif if ORIG serif); two-line wrap; centered under icon.
- Branching collector line under four cards → single down arrow; equal spacing.

## Hard bans
Flat clip-art / emoji / single-shape icons; whole-panel raster; drawing without reconstruction_spec; skipping z-order; Physics-box covering twin streams; inventing chart numbers.

## Deliverables per fig
`out_A/<Fig>.pptx` (no `ppt/media` unless Kevin re-allows), `diag/<Fig>_reconstruction_spec.json`, `diag/<Fig>_layers.json`, gates, `qa/<Fig>_orig_A_sbs.png`, icon SBS for gold_bar motifs.
