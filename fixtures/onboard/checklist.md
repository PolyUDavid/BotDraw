# Onboard fixture (Kevin t69u)

Mini panel used by `tools/onboard_selftest.py` before any user figure. This is not a paper figure.

## What is bundled
- `orig.png` — Fig01-scale mini ORIG rendered from `spec.json` (title / two body lines / caption + one media slot).
- `spec.json` — roles, font_px, slot box. Same `(panel, role)` shares one size (body ×2).
- Media slot pastes the **full** `gold_bars/brain_layered/orig.png` (contain, no half-crop).

## What this does not certify
Brain fineness still follows `gold_bars/brain_layered/checklist.md` (layers, sulci, icon SBS). Passing onboard only proves the new bot can run the gates and tune type/clearance.

## Proof (not prose)
`qa/onboard_selftest.json` must exist with `ready: true` before user `FIG_ROOT` work. The figure id is `OnboardDemo`. Gates must show `overlap_pass`, `h_med` inside the t48u band, and layout PASS. SBS path is `qa/OnboardDemo_whole_sbs.png`.

## After onboard
t68u still applies: Fig08 (a) HIL / FiSens / PV must be Confirmation Cycles, not grey blocks or blurry screenshots.
