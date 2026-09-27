# Stage 5-R: OneGap Recoverability

## Material Passport

Experiment: controlled, historical, paired one-step Actor diagnostic. Source:
the user's TASK.md and read-only repository artifacts. No human participant data.
Mode: run plus descriptive validation; single Codex semantic reviewer. No external
literature/gold/source-web lookup is used to construct or score this bank.

## Question and authority

Can Q/R/C/H/T produce useful, revisable OneGap control and respond to NoGain or
source feedback without persistent Residual? OneGap has action authority only.
This experiment performs only Actor API calls. Proposed SEARCH/FIND/OPEN are
recorded JSON, never executed. No Writer, Admission, Closure, state mutation or
retrieval calls. The independent Minimal Recoverable Loop E1 failure is historical,
not this experiment's gate. Its Writer/Admission code is not imported.

## E0 bank and selection

16 natural snapshots, 10 qids. Seven requested semantic families use the historical
Stage 4 D2 replicate-1 source-anchored skeleton and natural snapshots. q261 is an
additional relation/affiliation state. Two q546/q1094 checkpoints use historical
F2-verified seed Claims and the already frozen Q-only sentence skeletons as a
mechanical supplement. This R-origin difference is disclosed and fixed before calls.

Selection enumerates 14 snapshots in prepare.py plus the prior q546 checkpoint33
and q1094 checkpoint69. It covers early/late candidate-local states, already-known
facts and still-unestablished qualifiers. Selection uses historical bad-case
coverage, not fresh output performance or gold answers. The reviewer has seen
historical studies; no fresh-cohort or erased-memory claim is made.

C is copied verbatim from historical snapshots with exact prior supported-review
matches, observation hashes and source refs. A missing/disputed review excludes
the claim, without repair. F3 seed Claims use their historical F2-verification
provenance. H remains low-authority even where a historical H sentence says 'is'.

Recent trace includes at most three authentic actions. For newer snapshots, Gain
means accepted C additions visible at that snapshot; for old v3a prefixes, Gain
only denotes new observed W handles, explicitly labeled. These feedback proxies
are not claims that retrieved evidence was useful. Source entries are observed
titles/handles; no source score or post hoc answer labels enter Actor input.

## Conditions / fixed request count

| Condition | Count | Intervention |
|---|---:|---|
| P0 | 16 | Normal projected historical state |
| P1 | 8 | Append a historically seen weak candidate to H only |
| P2 | 16 | Replay last historical action twice with marked hypothetical NoGain |
| P3 | 2 | Resurface historical discovery preview and uninspected source opportunity |

P1 weak candidates are not universally known false: target-role membership is
unestablished. Report this as Wrong/Weak-H, not a gold-verified false-candidate
accuracy test. Two snapshots can share qid/C; all analyses disclose this dependence.
P2 tests response to explicit intervention, not a naturally measured two-step
failure trajectory. P3 tests source-feedback packaging/salience; its full preview
was historically visible but omitted from the compact P0 trace. No claim of a
pure binary-marker effect. All variants preserve Q/R/C exactly.

## Prompt, transport and freeze

System prompt is verbatim from TASK.md section10, newline-normalized. A shared
user-level contract lists the eight allowed strategy labels, known-handle action
argument shapes and JSON formatting; no residual, gold gap, support mask or tool
directive. Each condition has exactly one response, temperature0, max_retries0.
No max_tokens cap; raw response plus usage and exceptions archived by request ID.

42 independent requests use an async queue and 42 HTTP connections, matching the
new user concurrency preference min(N,256,available budget). No separate model
smoke test or paid concurrency benchmark. Freeze hashes input/variants, rubric,
prompt, request set, runner/scorer, historical heads and exact CALL_ESTIMATE before
HTTP. Standing API authorization is recorded with the request-set hash.

## Assessment and downstream boundary

REVIEW_RUBRIC.md defines all output judgments and denominators. Review every
content output before aggregate gate computation; preserve invalids and failures.
No new semantic fields or prompt iteration based on this batch. Stage 5-C is the
next separate experiment if gates pass. This one-step test cannot establish actual
evidence gain, P(recover) in a live loop, closure safety or final accuracy.
