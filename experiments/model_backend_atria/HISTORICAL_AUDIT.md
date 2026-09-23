# Historical Qwen audit before model intervention

Remote fetch on 2026-09-23 found
`origin/experiment/search-find-v3b-orthogonal = a63ca25`. This branch was
created from that commit; v3a/v3b history remains untouched.

I re-read the v3a and v3b result records and recounted original event rows,
rather than adopting the prose alone:

| Source | Independent raw-event check | Historical report |
|---|---:|---:|
| v3a qid 546 / 1094 | 12 + 76 `search`; 0 `find` | Find 0/88 |
| Orthogonal partial | 26 `cell_end`; P1 four Find calls in two cells | 26/26; Find 2/13 cells |
| Orthogonal P1 Search results | 38 no-gain results (>half old hits and zero new preview) | 38 |
| Orthogonal P1 temporal trace | 0/38 Find within two later decisions; 11 cells with later Search after no-gain | 0/38; 11/13 |
| Verification State | 8 new completed S1/S2 cells | 8/8 |
| Scoped Search | 4 completed cells, 29 `search` starts | 4; 29 returned Search calls |
| Alias | 4 completed cells; interrupted partial excluded | 4; 28 completed-cell Search calls |

The zero useful local-evidence judgment remains the bounded published
interpretation based on review of raw windows, not merely counts. The v3a
Section 7(a) narrative count
corrections in `../search_find_v3a/AUDIT_SECTION7A.md` are carried forward:
D17 Ding was returned once in the v3a 546 Search–Find run, while the baseline
returned that doc four times. The key preview-location gap remains valid.

No conflicting core count was found that would require stopping for a new
audit before M0. These are two selected historical bad questions, not a
representative sample.
