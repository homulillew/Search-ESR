# Append-only semantic scoring correction

During G5 review, a missed independently useful relation was found in an already observed G3 window. Evidence `d16b2ded9977489d` describes the 2012/13 PTC Finals. Its 4–3 and 4–0 results do **not** verify the required 2023 sequence. However, its explicit **fifth career 147** establishes the separate more-than-three maximum-break condition before 2023. The initial whole-window NoProgress annotation overlooked this relation.

No model request, response, tool execution, frozen selection or historical artifact changed. The original G3 labels, metrics and RESULTS remain intact. The corrected labels and calculations are saved separately as `one_step_acquisition_v2/evidence_labels_review_correction.json`, `review_corrected_progress_reviews.json`, and `review_corrected_progress_metrics.json`; `analysis_v2/scoring_correction.py` reproduces them. This is an annotation correction to previously available evidence, not a new-source sensitivity or a change to the Progress rubric.

| G3 primary metric | Originally reported A0/A1/A2 | Corrected A0/A1/A2 |
|---|---|---|
| Any Progress /40 | 18 / 19 / 21 | **18 / 19 / 22** |
| Direct Progress | 15 / 16 / 18 | 15 / 16 / 19 |
| Acting NoProgress | 5 / 10 / 6 | 5 / 10 / 5 |
| Search actions with Progress | 21 / 21 / 23 | 21 / 21 / 24 |
| Calls / Progress | 2.50 / 3.05 / 2.57 | 2.50 / 3.05 / 2.45 |

All other aggregate metrics, including second-action marginal yield and alternative-source sensitivity, are unchanged. G4 does not contain this window. G5 uses the corrected relation. The final synthesis cites corrected G3 primary numbers and identifies this erratum explicitly; it does not silently rewrite the earlier report.

## Search rediscovery accounting correction

The earlier G3/G4 `path_metrics.json` reader checked only the optional `previously_discovered` boolean. Orthogonal Search reports old documents with `status: already_discovered` and omits that boolean. Treating the missing flag as false incorrectly produced zero rediscovery counts. The raw results and backend are unchanged. Corrected derivations are appended as `review_corrected_path_metrics.json`; the original files remain intact. G5 final path metrics use both actual registry forms.

- G3 already-known result items: A0 78/295, A1 58/325, A2 101/315; all-known Search calls: 3/0/3.
- G4 already-known result items: R0 17/75, R1 21/85, R2 36/130, R3 36/110; all-known Search calls: 0/0/0/3.
- G5 already-known result items: L0 93/246, L1 39/120, L2 80/196; all-known Search calls: 2/1/4.

These measure returned-document rediscovery, not repeated identical queries or proof of goal drift. Evidence Progress and closure counts are unaffected.
