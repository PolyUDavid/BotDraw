---
name: paper-figure-b-blender
description: >-
  Paper-figure B after A-PPT: Confirmation-grade Blender Cycles insets
  (vehicles/3D/hardware), editable OMML/labels, .blend pack; pair with scene-ui
  and quality-merge. t68u: never ship oversimplified grey-block or blurry
  screenshot B — rebuild Cycles to match ORIG composition.
---
# Paper-figure B (Confirmation Cycles)

Load after A PASS. Also load [paper-figure-scene-ui](sand-workflow:paper-figure-scene-ui) and [paper-figure-quality-merge](sand-workflow:paper-figure-quality-merge).

## Contract
B = A + Cycles vehicle/3D/**hardware** insets only. Labels/OMML/arrows stay editable. No vehicle/3D slot → B=A (note in QA).

## Stack
Reuse Confirmation: `bl_common.py`, `models.py`, `cars_b.py`, optional `render2.py`.
Keys: `car_{rear|front|side}[_r|_l|_flip]_<HEX>` plus figure-specific hardware keys (e.g. Fig08 `hil_pack` / `fisens` / `pv_wind_home`).
Cycles + film_transparent + Freestyle `#34363A` + Principled + dual SUN. Fit=contain. SAMPLES≥96.

## A scene first
Before B, A cars/roads/hardware frames must already use Confirmation vector (`lib_ck` car_* / road_persp) or complete media slots, not cartoon UI. B only upgrades 3D/hardware media to PNG.

## Hard ban — crude B (Kevin t68u)
- **Forbidden as B deliverable:** blurry ORIG paste, half-crop screenshots, or oversimplified grey-block Cycles that do not match ORIG composition (missing cabinets, screens, cables, packs, sensors).
- If a hardware/vehicle slot looks worse than ORIG or like a toy block, **rebuild the Blender scene** to ORIG composition (geometry + cables + panels), re-render, swap into B pptx, then SBS.
- Canonical example: **Fig08 panel (a)** triad — Leading-OEM HIL pack, FiSens box+fiber, Public PV/wind/home — must be Confirmation-grade Cycles insets in `out_B`, not crude blocks.

## Ship
renders/*.png, blend/*.blend, scripts, keys_needed.txt; B h_med ≈ A; media_slots source=`Blender_Cycles`; docs triad updated.
