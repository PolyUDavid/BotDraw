---
name: paper-figure-data-provenance
description: >-
  Use when tracing a curve from pixels, when the printed source disagrees with
  a verified table, or when a side file might be mixed into the primary figure.
  Do not invent an experimental series. Keep the source trace and any verified
  alternative in separate places.
---
# Data provenance

Load from [botdraw](sand-workflow:botdraw) before drawing charts. This keeps the ban on fabricated data.

## When
A series comes from a raster, a verified table disagrees with the printed figure, or two printed versions disagree.

## Steps
1. Tag every series as `raw`, `printed`, `image_geometry`, `synthetic`, or `verified`.
2. Without raw values, say pixel geometry only. Do not call it a recovered run, sample, or confidence interval. An editable chart is not an experiment.
3. Follow source axis mapping, nonuniform ticks, corners, rebounds, and marker positions. Do not interpolate a "more reasonable" curve without saying so.
4. On conflict, the primary trace is labeled `NON_VERIFIED_SOURCE_TRACE`. A verified alternative is a separate file labeled `VERIFIED_ALTERNATIVE` and is not stored under `out_A/` or `out_B/`. Do not mix the two and do not silently repair the source.

```bash
python3 tools/quality_sync.py review-series --series qa/<fig>_series.json
```

5. After a chart edit, recheck the chart cache, embedded workbook, and geometry whitelist. A real math fix is listed field by field. `m:t` being unchanged does not hide an operator change.
6. The delivery README names the version boundary. Acceptance of the current look does not delete the conflict.

## Not a PASS
A valid series record is not proof that a user plate matches a laboratory run.
