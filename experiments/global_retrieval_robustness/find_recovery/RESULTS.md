# F1 oracle-document Find

All 40 canonical documents were verified against frozen text SHA-256 and anchor before calls. One unchanged `SearchFindTools.find` call per case used the frozen U1 find query, the original tokenizer, and the 400-token window budget. The raw returned windows and localizer audits are in `oracle_find_events.jsonl`; single-reviewer per-window judgments are in `oracle_reviews.json`.

| Type | Useful W | Fully sufficient W | Exact anchor hit |
|---|---:|---:|---:|
| A | 12/12 | 12/12 | 12/12 |
| B | 5/8 | 5/8 | 5/8 |
| C | 10/12 | 10/12 | 9/12 |
| D | 6/8 | 6/8 | 6/8 |
| Overall | **33/40 (82.5%)** | **33/40 (82.5%)** | 32/40 |

At 82.5%, F1 is in the preregistered 80–90% mechanism-audit band. q387 A01 **does** recover “5TB of Storage.” q517 B01 fails to recover “Policeman 1”: the window stops exactly at the filmography table header, although C10's different frozen find query reaches the role row in the same document. This is a query/localizer sensitivity within a correct D. q546 C11 and D08 both recover the requested professional-year facts; these cells do not test the original hard multi-match q546 sequence.

Seven cases fail the strict useful-W rubric: B01, B02, B07, C04, C08, D03, D04. In D03/D04, the frozen anchor string appears in a *different table* (days as table leaders) while the requested league-position/goal-difference row is absent. Conversely, C11/D05/D08 are fully sufficient even though their exact frozen anchor strings do not appear. Exact anchor hit is therefore a useful audit aid, not the outcome label. The seven reasons are recorded per case in `oracle_reviews.json`.
