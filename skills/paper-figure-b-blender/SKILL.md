---
name: paper-figure-b-blender
description: >-
  Paper-figure B after A-PPT: Confirmation-grade Blender Cycles insets
  (vehicles/3D and hardware media slots). t68u: rebuild low-quality
  screenshot/crop or grey-block slots in Cycles (film_transparent, Freestyle
  #34363A, dual SUN, SAMPLES≥96). Fig08 (a) hardware triad is the example.
  Editable OMML/labels, .blend pack; pair with scene-ui and quality-merge.
---
# Paper-figure B (Confirmation Cycles)

Load after A PASS. Also load [paper-figure-scene-ui](sand-workflow:paper-figure-scene-ui) and [paper-figure-quality-merge](sand-workflow:paper-figure-quality-merge).

## Contract
B = A + Cycles insets. Labels/OMML/arrows stay editable. No 3D media slot at all → B=A (note in QA).

## Stack
Reuse Confirmation: `bl_common.py`, `models.py`, `cars_b.py`, optional `render2.py`.
Keys: `car_{rear|front|side}[_r|_l|_flip]_&lt;HEX&gt;`.
Cycles + film_transparent + Freestyle `#34363A` + Principled + dual SUN. Fit=contain. `SAMPLES≥96`.

## t68u B media slots (hard)
When a B media slot would otherwise be a low-quality screenshot/crop or an oversimplified grey-block Cycles stand-in, rebuild that slot in Blender Cycles to match ORIG composition (hardware, cables, screens). Ban blurry ORIG paste and crude blocks as the B inset.
Confirmation stack (required): `film_transparent`, Freestyle `#34363A`, dual SUN, `SAMPLES≥96`.
Canonical example: Fig08 panel (a) hardware triad (HIL pack / FiSens / PV-wind-home) — B must use Cycles insets, not grey blocks or blurry ORIG paste.

## A scene first
Before B, A cars/roads must already use Confirmation vector (`lib_ck` car_* / road_persp), not cartoon UI. B upgrades vehicles and t68u hardware media slots to PNG.

## Ship
renders/*.png, blend/*.blend, scripts, keys_needed.txt; B h_med ≈ A; docs triad updated.
