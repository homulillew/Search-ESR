# A1 result: gate fails on premature Claim admission

The prespecified 24 paired packets from 8 qids produced 48 first-stage calls. There were no provider failures and no retries. Six O outputs failed schema validation because two proposed Claims in each omitted `question_anchor_ids`; their raw JSON remains in `events.jsonl` and no Claim was admitted from those cells. G had no invalid outputs. The arm-blind single-reviewer annotations are in `REVIEWS.json`, with exact reviewer packets and the private reveal mapping saved separately.

| Measure | Observation-driven O | Gap-driven G |
| --- | ---: | ---: |
| Valid admitted Claims | 37 | 37 |
| Progress-appropriate Claims | 2/37 (5.4%) | 13/37 (35.1%) |
| Mean case-level coverage | 8.3% | 35.4% |
| Premature Claim rate | 1/37 (2.7%) | 18/37 (48.6%) |
| Redundant Claim rate | 6/37 (16.2%) | 1/37 (2.7%) |
| Schema-invalid cells | 6/24 | 0/24 |

The paired precision comparison is 8 improved, 1 worsened, 15 tied in favor of G. G passes paired precision, coverage, and redundancy gates. It **fails** the prespecified premature Claim gate (48.6% versus ≤15%). This failure alone prohibits C1 and R1.

The dominant G error is writing an exact but unseen opponent, episode title, year, league table row, or historical count into an open Claim. `status=open` prevents false evidence closure, but the unsupported specificity still directs future retrieval and can prematurely lock the research candidate. Examples include invented later Ding match opponents/dates from an opener report, a named season-one episode from a season-four page, an exact 2015 table row from a 2022/23 signing article, and exact Forbes/debut counts absent from the visible obituary. The issue is `SV2-3 bad claim admission`, with potential `SV2-1` hypothesis contamination. O's main issue is observed-fact expansion outside the active Gap; several raw proposals describe true local facts while missing the pending verification condition.

G did **not** reduce Claim count among schema-valid admissions (37 versus 37). It improved focus but remained vulnerable to unsupported candidate-specific details. The 6 invalid O outputs, containing 15 raw proposed Claims before validation, make the apparent O/G semantic precision difference partly confounded by schema compliance. A posthoc best-case treatment of all 15 as valid could change comparative precision and coverage, but cannot change G's frozen 18/37 premature failure. The gate decision is therefore robust to this compliance confound.

Coverage uses the frozen rule: valid proposed Claims plus adequate existing Claims, with broad conjunctions insufficient when they cannot diagnose separate conditions. These 24 cases are correlated siblings (3 per qid), and the reviewer is single-person; results are a bounded mechanism diagnostic, not a population estimate. All `semantically_plausible` labels mean only “could be true”; they are not evidence of truth. DeepSeek reported weighted prompt-cache hit rates of 16.6% (O) and 15.6% (G).
