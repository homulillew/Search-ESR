# Pre-execution audit

## Remote and source identity

Completed `git fetch origin --prune`, status/branch inspection and source log
inspection before creating the branch. The expected source remote did not move:

- `origin/experiment/ephemeral-obligation-decomposition`:
  `7fdb048e856545facd4acfb590e8cf28c46f1013`
- `origin/main`: `8021aca19a1ee5201730e40b338012c65ecd51cf`
- New branch: `experiment/skeleton-state-alignment`.
- Prior latest result: Q-only D2 absolute viability positive; comparative fresh
  gate failed because D0/D2 both had zero corruption. No alignment experiment
  already present at this source anchor.

Historical experiment files are read-only. Hashes of all tracked prior
experiment files are in analysis/HISTORICAL_HASHES.json. Existing unrelated
untracked auto_research/research_loop/research-notes files are excluded and
preserved. No search/retrieval backend or orthogonal semantics changed.

## Auditable construction order

- `81caa52`: Q-only Oracle and unchanged prior D1/D2 replicate1 committed.
- `4b8e9d8`: 27 whitelisted current states and54 Gold Masks committed before
  opening historical GoldO for addressability. Source evidence stays local to
  each state. Single reviewer has prior repository familiarity; no erased-memory
  or independent-reviewer claim.
- E0 and selection references then prepared offline. No new model outputs exist.
- Exact TASK §28/§52 prompts extracted, schemas/gates/108+108 mixed schedules
  frozen before any calls. E2 model-mask requests are necessarily conditional
  on E1; their builder/source replicate is frozen now and actual bytes will be
  committed before E2. This is not a claim that unknown predictions were frozen.

## Findings and limitations

D2 direct+coherent16/27 (59.3%) is below80%, with11/27 subnode-only. Preserve D2
primary and continue to E1 per TASK §12. D1 diagnostic is23/27 (85.2%). Gold Mask
reference has161 Oracle and132 D2 nodes over27 states; two replicates yield322
and264 scored node slots. State exactness and qid/empty-Claims strata protect
against overstating micro accuracy on many easy unsupported nodes.

Selection locality yields no admissible single D2 ID for G04/G05; planned
denominators remain unchanged, ideal selection ceiling25/27. No positive STOP
state exists. Primary and sensitivity locality interpretations are specified
before calls, with no after-result reference repair.

## Offline checks and paid boundary

Meaningful tests cover input exclusion, immutable replica selection, citation
alternatives, cross-candidate proof rejection, schema contracts, denominator
retention, NA gates, selector stability, timeout/no retry, first-call halt,
bounded concurrency, exclusive writes and token/cache accounting. Exact source,
span, prompt and schedule reconstruction is in analysis/OFFLINE_AUDIT.json;
test output is in analysis/OFFLINE_TESTS.json.

Credential presence is checked without logging the value. No live access or
billing check is claimed. Authentication preflight will be the first formal
request after authorization, with no extra canary.

TASK §70 explicitly prohibits extending old paid budgets to this task. Current
status is PREPARED_FOR_EXECUTION. Proposed authorization:108 E1 calls, plus108
E2 calls only if both frozen E1 gates pass; maximum216, concurrency8, retries0.
Token scenarios and omission of a hard output-token cap are in CALL_ESTIMATE.
No prices were verified, so no currency amount is reported. Preparation itself
does not authorize execution.
