---
name: paper-figure-semantic-overlap-exceptions
description: >-
  Use when a source time window, trajectory, nested layer, or source foreground
  occlusion trips a generic overlap gate. Keep the measured FAIL. Record an
  object-level semantic exception beside it. Do not move data to pass the gate.
---
# Semantic overlap exceptions

Load from [botdraw](sand-workflow:botdraw) beside [paper-figure-layout-distribution](sand-workflow:paper-figure-layout-distribution).

## When
The source itself overlaps events, paths, or a foreground label, and a generic overlap gate reports FAIL.

## Steps
1. Confirm the overlap on the source crop. One finding, one object list. No page-wide waiver.
2. Keep the data, time mapping, and z-order. Do not slide a window or edit a series to satisfy IoU.
3. Record `finding_id`, `source_evidence`, `shape_ids` / `object_ids`, `overlap_semantics`, `geometry_unchanged: true`, `effect_on_legibility`, `review_status: reviewed_semantic_exception`.

```bash
python3 tools/quality_sync.py review-semantic --report qa/<fig>_overlap_raw.json --exceptions qa/<fig>_semantic_exceptions.json
```

4. The tool copies the original `pass` value. `overrides_gate_pass` stays false. Status text is `REVIEWED_SEMANTIC_EXCEPTION`, not a measured PASS.
5. New collisions that are not in the source, clipped math, and cut-off edges are still repaired.
6. Missing evidence, missing object ids, or changed geometry is rejected. Leave that finding in `unexcepted_finding_ids`.

## Stop
The historical measurement file is not overwritten. A later visual acceptance does not flip it. See the status axes in [paper-figure-quality-merge](sand-workflow:paper-figure-quality-merge).
