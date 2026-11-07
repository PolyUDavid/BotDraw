---
name: paper-figure-source-symbol-audit
description: >-
  Use when a paper figure contains formulas or math text, or before claiming
  the redraw is complete: walk the source figure itself, not only candidate
  OMML boxes. Coverage is not correctness. < versus ≤, caption, axis labels,
  and outside-box conditions are in scope. Choice and Fallback are separate.
---
# Source symbol audit

Load from [botdraw](sand-workflow:botdraw) after [paper-figure-full-omml](sand-workflow:paper-figure-full-omml). This does not replace real OMML, arrow tails, or gold-bar UI.

## When
A figure has math, or someone is about to say the content is complete.

## Steps
1. Freeze the source version and the candidate PPTX SHA before reading symbols.
2. Walk the source figure in order: panel, axis, legend, caption, conditions outside boxes. Candidate OMML indexes are proposals, not ground truth. Digits and signs that never entered that index are still in scope.
3. For each row record `stable_source_id`, `source_roi`, `candidate_shape_ids`, `source_transcription`, `Choice_structure`, `Fallback_content`, `before_evidence`, `after_evidence`, `reviewer_result`, `uncertainty`, `input_hashes`. Split or merged boxes keep the old ids.
4. Check `< ≤ > ≥ ≠ ≈ =`, open and closed endpoints, sign, l/1/O, Greek case, bars, hats, subscripts and superscripts, fraction parts, operator glyph plus limits, matrix brackets, units, caption line endings, and axis labels.
5. Real math is editable OMML. Prose and filenames are not forced into formulas. An isolated inequality is still math.
6. Compare the whole math tree (namespace, order, attributes, text), not only `m:t`. Operators may live in `m:chr/@m:val`. Use:

```bash
python3 tools/quality_sync.py math-signature --xml qa/<fig>_choice_math.xml --compare qa/<fig>_other_math.xml
python3 tools/quality_sync.py audit-coverage --ledger qa/<fig>_symbol_ledger.json
```

7. `reviewed/N` is coverage. A full count can still hide a wrong relation. Count `extra_math`, `extra_literal`, unknown, and later errata separately. Unknown is not correct. An erratum changes the row result and does not grow the original denominator.
8. Choice and Fallback are both reviewed. A pretty Fallback does not certify Choice. Do not delete Choice to make a LibreOffice preview look finished.
9. Low-resolution source text is checked against the supplied DOCX or Markdown. If it is not there, write UNKNOWN. Do not invent a formula. Do not silently "correct" the source into a different physical claim.
10. A real fix becomes OMML, then A/B are re-rendered. The old FAIL file stays. New reports go to a new content-addressed file. Stop when [quality-merge](sand-workflow:paper-figure-quality-merge) says `STOP_SAME_CLASS`.

## Ledger
`source_index` is the fixed id list. `reviewed` maps those ids to `correct`, `defect`, `unknown`, or `reviewed`. Anything else belongs in `extra_math` or `extra_literal`.

## Not a PASS
A green `audit-coverage` JSON only shows the ledger arithmetic. It is not a user-figure PASS and not a native PowerPoint review.
