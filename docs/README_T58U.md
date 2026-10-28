# BotDraw t58u patch — media slot harmony + self-check

## What changed
- New skill: `paper-figure-media-slot-harmony`
- Updated: `botdraw`, `paper-figure-quality-merge`, `paper-figure-text-layout-clearance`, `paper-figure-indistinguishable-gate`, `paper-figure-scene-ui`
- MASTER_PROMPT_zh.md: t58u section

## Rules (Kevin t58u)
1. Self-check while drawing (叠字目视 + OCR; 门禁假阴性仍 FAIL)
2. Media slots must be complete — no half-cut screenshots
3. Prefer full ORIG crop; if incomplete/disharmonious, allow **local AI GenerateImage insert** into picture slot (NOT whole-slide AI)
4. Require `qa/<fig>_media_slots.json` before PASS

## Apply
Copy `skills/*` into BotDraw `skills/` (overwrite), merge docs into `docs/`.
