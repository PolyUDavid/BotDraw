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

## Quality sync — geometry, then material, then light
Split vehicles by the projection you can see: short roof, long roof, hatch, notchback, side view. Measure aspect, shoulder and tail, wheelbase and track, roof and window boundaries, window arc, wheels, lamps, and bumper before assigning a material. Do not guess a brand or a blueprint. Do not recolor one silver car and rotate it into a different class.
Build a continuous shell, separate window glass, pillars, four wheels, lamp housings, mirrors, and a layered bumper. A source highlight that is continuous is not two fake dots. White paint, glass hardness, and shoulder radius are separate edits. Icons start at the source proportion.
Icon-only SBS uses the source slot, the same camera projection, the same ROI, and the same display scale (`ORIG|before|after`). Do not scale each crop to fill the frame, and do not stretch the PNG afterward. Keep a full-page SBS as well.
Name the axis frame. Scaling a rotated object on its local axis is not a world-track fix. Do not close an open curve. Do not use a radial fan topology on glass. Raising samples or mesh density is not a shape improvement.
A passed template may be reused only after that slot’s angle, proportion, and light are checked. A class that has not passed is not copied under the template’s name.
After saving, reopen the blend that was written. Record its SHA, engine, samples, transparency, camera, materials, lights, the actual Freestyle value, and external dependencies. A template title is not the value in the file. If Freestyle is off, do not say the Confirmation contract is fully met. User acceptance of the current look does not erase that gap.

```bash
python3 tools/quality_sync.py review-vehicle --record qa/<fig>_vehicle.json
```

This validator does not launch Blender.

## Ship
renders/*.png, blend/*.blend, scripts, keys_needed.txt; B h_med ≈ A; media_slots source=`Blender_Cycles`; reopened-blend record; fixed-scale icon SBS; docs triad updated.
