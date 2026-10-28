# gold_bars — BotDraw visual calibration (Kevin t53u)

Prose like "精致 / ORIG-grade" is **not** a stable gate. Use this crop library.

Each archetype:
- `orig.png` — ORIG pixel crop (source of truth)
- `pass_example.png` — last passing replica crop (ORIG placeholder until freeze)
- `checklist.md` — min layers / strokes / bans

## Archetypes
| id | purpose |
|----|---------|
| `brain_layered` | Fig01/Fig03 brain fineness |
| `gear_layered` | Fig03 gear mass |
| `axis_arrows_outward` | Fig09 axis tips outward |
| `type_title_body_caption` | type ladder (with PPT ruler) |

See skill `paper-figure-gold-bar-calibration`.

## 跨 bot（t54u）
本目录是「精致度」的可执行标准。新 bot 最小包必须包含 `gold_bars/`；缺目录则 scene-ui / 大脑精致度不可宣称 PASS。
