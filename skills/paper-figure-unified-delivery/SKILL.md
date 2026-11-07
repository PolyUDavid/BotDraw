---
name: paper-figure-unified-delivery
description: >-
  Use for multi-figure A/B delivery, resume after a crash, snapshots, ZIPs, or
  a cloud folder handoff. Resolve out_A and out_B explicitly, bind SHA and CRC,
  and keep owner acceptance off the measurement record.
---
# Unified delivery

Load last from [botdraw](sand-workflow:botdraw), after the current SHA is rechecked.

## When
More than one figure, an interrupted job, a snapshot, a ZIP, or a remote folder.

## Resume
1. Check file SHA, PPTX CRC, the command exit code, and the preview on disk. Do not inherit an unfinished PASS.
2. Do not replay a cumulative color, scale, or nudge script. Resume from the saved file or refuse when the precondition hash differs.
3. Variant resolution is explicit. `B` missing is an error even if `out_A` or a backup exists.

```bash
python3 tools/quality_sync.py resolve-variant --root "$FIG_ROOT" --tag FigXX --variant B
FIG_ROOT=<figroot> python tools/layout_type_shape_gate.py B FigXX
```

The layout gate reads only `out_<variant>/<tag>.pptx` (or `out_<variant>/SI/` when `FIG_SUPPLEMENTARY=1`). It does not search the other variant and it does not recurse into backups.

## Snapshot and ZIP
Whitelist primary PPTX files into `ALL_FIGURES/out_A/` and `ALL_FIGURES/out_B/`. Leave verified alternatives, old copies, patches, QA, and blend files out of that whitelist. Counts come from the manifest, not a hardcoded total.

```bash
python3 tools/quality_sync.py freeze --source "$FIG_ROOT" --dest "$SNAP" --files files.txt --manifest "$SNAP/manifest.json"
python3 tools/quality_sync.py make-zip --snapshot "$SNAP" --manifest "$SNAP/manifest.json" --output part.zip
python3 tools/quality_sync.py verify-zip --archive part.zip --manifest "$SNAP/manifest.json"
```

`files.txt` is one relative path per line, such as `out_A/Fig01.pptx`. The tools refuse path escape, symlink members, a dirty destination, a changed byte, a missing member, an extra member, and a duplicate ZIP name. Each part is an ordinary ZIP with the same root. The byte limit is real. The ZIP's own SHA is recorded outside the ZIP. A remote listing that has no hash field stays `remote_hash_verified: UNKNOWN`.

Write the PPTX to a new temp file, close the ZIP, check CRC and parts, then replace. Do not read and write the same file. Do not let a backup overwrite the frozen file.

## README of a delivery
List, separately: owner acceptance and its scope, historical technical FAIL, any B=A case, native application review, and data conflicts. Acceptance does not rewrite a historical FAIL. A later fix does not backfill an old PASS.

## Not a PASS
Freeze and verify prove bytes. They do not prove the plates.
