# READY FOR NEW AUTHORIZATION — Claim Pipeline Root-Cause Ablation

Preparation complete. **E1/E2/E3 have not run. New API calls=0; retrieval calls=0.**
This is an experimental design/harness readiness decision, not support for H1/H2/H3.

## Prepared

- Verified remote base `dadf69f1c5fb96491f4fd3a34e0ece3418878de3`; isolated branch
  `experiment/claim-pipeline-root-cause`. Original working directory left intact.
- Audit/hypotheses commit `74145c2f`; bank/review commit `ac484eaa`; final harness
  commit is the commit containing this file and FREEZE.json.
- 36 natural observed-window packets,20 qids,at most2/qid,8 reviewed relation families.
- D12/8 qids,H-diagnostic12/6 qids,H-confirmation12/6 qids; disjoint qids.
- 16 positive,6 duplicate/no-new,8 relevant/no-new,6 other ambiguous/off-gap packets;
  27 frozen useful atoms. Exact source hashes, row pointers and metadata lineage saved.
- A0/A1 Reader and G0 Grounding unchanged; new generic prompts implement A2 and G1
  with explicit information isolation. No production file/state field changed.
- Independent async requests, bounded pools, max_retries0, append-only archives,
  raw reasoning/output and cache usage accounting, stopped gates on failures.
- Offline contract tests cover visibility, refs, role dependencies, blinding,
  concurrency, timeout/failure isolation, no retries, budgets, metrics and provenance.
  Exact test results/version information is saved in OFFLINE_TEST_RESULTS.json.

## Budgets requiring a new grant

| Stage | Cases | Calls |
|---|---|---:|
| E1 |24 packets × A0/A1/A2 |72–96 |
| E2 |<=60 actual reviewed candidate/evidence pairs;<=23 unique inventories |<=143 |
| E3 |12 reserved packets; only after a complete mechanism gate |conditional<=120 |

E1+E2 ceiling239 calls. Including conditional E3 ceiling359. Actual count follows
selection empties, real candidate count and chosen components; never fill the budget.
Same frozen DeepSeek Flash,temperature0,thinking enabled/high,max_tokens32768.
See CALL_ESTIMATE.json for formulas and token caps. No provider-price assumption.

## Limits that matter before authorization

- 14 packets have legacy review-authored Gap/C;22 come from actual Reader requests.
  Historical date metadata enrichment is explicitly traced. This is a natural
  **evidence** bank, not36 fresh online trajectories. Report both context strata.
- Historical E2 candidates currently include9 supported and1 strengthened candidate;
  that single negative is q435 in D. H-diagnostic negatives must arise naturally in
  E1. If absent, stop that gate; no invented negatives or sample replacement.
- E3 has only7 useful atoms and4 primary silence packets. Gates are small-sample
  expansion criteria, not population reliability estimates.
- G0's pre-existing case examples are retained solely to keep the baseline exact.
  No new role prompt contains those examples.
- A2/G1 also alter role specialization/call count; G1 adds an inventory bottleneck.
  Outcomes diagnose the structural interventions, not a uniquely identified mental
  process. Two-arm E3 does not establish a factorial interaction.
- Single-reviewer blinding removes displayed arm/hypothesis/other-arm outputs but
  does not erase familiarity with historical cases.

## Why execution stops here

The current user task **section50 explicitly requires a new authorization for this
experiment even if standing API authorization exists**. Section49 requests stopping
after the three preparation commits. No AUTHORIZATION.json has been created.
After a new grant, bind it to FREEZE.json, run E1, freeze source-only/relevance
reviews, then form E2 and evaluate gates. E3 remains conditional. Runtime changes
and a full Recovery rollout require a separate implementation task.

All17 causal questions in TASK section53 remain unmeasured here. The preparation
does not justify accepting hypotheses, declaring q435 solved, changing Reader or
Grounding, or adding persistent semantic state.
