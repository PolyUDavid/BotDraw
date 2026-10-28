# axis_arrows_outward gold bar (t53u/t54u)

**Primary visual:** `orig.png` — schematic PASS vs FAIL (Y tip up, X tip right).
**Secondary ORIG regions:** `orig_fig09_p1_y_region.png`, `orig_fig09_p1_x_region.png` (Fig09 P1 corners).

## Geometry (hard — cross-bot)
- **Y tip** points **up / outward** (away from plot interior)
- **X tip** points **right / outward**
- Prefer **filled poly triangle tips** (not OOXML `a:headEnd` on upward `cxnSp`)
- **Ban** connector `flipV`/`flipH` that paints headEnd toward plot interior
- Kevin: inward arrows = FAIL `axis_arrows_outward_pass`

## Gate artifact
`qa/<fig>_layout_gates.json` must include:
```json
"axis_arrows_outward_pass": true,
"axis_tip_method": "poly_outward"
```
Missing key or false = no PASS.
