# Final integrity

**PASS for mechanical integrity.** This is separate from the insufficient-bank
efficacy gate and single-reviewer semantic judgments.

Reproduce with `python experiments/deferred_recovery/analysis/integrity.py`.
The exact results are in [analysis/FINAL_INTEGRITY.json](analysis/FINAL_INTEGRITY.json).

|Check|Result|
|---|---|
|All files tracked at base `2544fbf` unchanged|10,318 / 10,318|
|Frozen code, bank, prompt, schema, request and backend files unchanged|36 / 36|
|Full corpus/index/embedding/config hash verification|17 / 17; 20,121,459,507 bytes|
|Source document identities checked against frozen SQLite|77 distinct documents|
|Actor requests|28 starts, 28 completions|
|Writer requests|72 starts, 72 completions|
|Tools|13 Search, 8 Find, 0 Open|
|Actor Stops|7, all in second decision|
|New source observations|72; all corpus substrings; every one followed by U1|
|Provider model identity|`deepseek-flash`, 100 / 100 responses|
|Reported input usage equals cache hit + miss|100 / 100|
|Structural / Harness / incomplete / provider / tool errors|0 / 0 / 0 / 0 / 0|

The audit reconstructs every Actor and Writer request from the recorded prior
state and frozen builders. It checks one start/completion per stage/tag/cell,
exact decoded output, one Actor action at most, k=5, handle validity, max two
claims per U1 update, and mechanical application of every proposal. R1 requests
were committed at `21afbd8`; R2 requests and the actual R1 post-state hash were
committed at `fd281ce`. All live events name the corresponding committed HEAD.
R1 decisions/updates are identical prefixes of R2; no first step was resampled.

Initial G/H public projections are identical except available action/response
schemas. The old catalog contains only D/title/url; old W text and private
truth are absent. New raw observations become visible through actual tools.
Claims remain append-only. Registry restoration does not introduce a semantic
router. The frozen v3a/v3b, retriever, localizer and Find/Open files are unchanged.

The code records some final cells as `active` because they did not output Stop;
all such cells have exhausted the two-decision horizon. Derived metrics label
them `horizon_exhausted`. No live call or background research process remains.

Semantic failures are retained despite zero operational failures: one strict
temporal admission miss, one unresolved local-window retrieval case, and an
unsupported season upper-bound Hypothesis. The latter did not mislead the next
Actor into Stop. Single-reviewer labels and their scope sensitivities are
archived; they are not machine-verified truth.

Only this experiment directory is included in this branch's changes.
Preexisting untracked user work outside it was left untouched. Credentials and
authorization headers are not present in the request journals.
