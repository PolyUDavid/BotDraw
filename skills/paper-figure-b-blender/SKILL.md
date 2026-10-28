---
name: paper-figure-b-blender
description: >-
  Paper-figure B after A-PPT: Confirmation-grade Blender Cycles insets
  (vehicles/3D), editable OMML/labels, .blend pack; pair with scene-ui and
  quality-merge.
---
# Paper-figure B (Confirmation Cycles)

Load after A PASS. Also load [paper-figure-scene-ui](sand-workflow:paper-figure-scene-ui) and [paper-figure-quality-merge](sand-workflow:paper-figure-quality-merge).

## Contract
B = A + Cycles vehicle/3D insets only. Labels/OMML/arrows stay editable. No vehicle → B=A (note in QA).

## Stack
Reuse Confirmation: `bl_common.py`, `models.py`, `cars_b.py`, optional `render2.py`.
Keys: `car_{rear|front|side}[_r|_l|_flip]_&lt;HEX&gt;`.
Cycles + film_transparent + Freestyle `#34363A` + Principled + dual SUN. Fit=contain.

## A scene first
Before B, A cars/roads must already use Confirmation vector (`lib_ck` car_* / road_persp), not cartoon UI. B only upgrades vehicles to PNG.

## Ship
renders/*.png, blend/*.blend, scripts, keys_needed.txt; B h_med ≈ A; docs triad updated.
