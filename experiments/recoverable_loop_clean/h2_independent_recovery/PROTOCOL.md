# H2: recovery on archived prefixes held out from H repair

## Authorization, gate and independence

Standing user authorization covers live API calls and dependency-safe concurrency.
H1/GATE_H2.json passes the executable-interface/no-authoritative-corruption gate.
The retained Closure schema failure is not repaired or retried. Runtime, role
prompts/schemas, tool semantics and transport stay exactly as H1; this cohort does
not tune them. No extra probes. No paid reviewer. No H3 or larger accuracy cohort.

SELECTION_PRECOMMIT.json mechanically selected twelve prefixes before seed semantic
review. It excludes all nine H repair fixture question IDs, including all six H1
questions. Acquisition S01 and frontier G5 L0_START pools are ordered by numeric
qid; R1 gets first four acquisition, R2 first four frontier, R3 next two of each.
No gold/future results are selection inputs. Source documents are inspected only
for exact integrity checks, not to select targets. These are historical research
cases held out from this repair, not a globally unseen/random benchmark.

R2_Q311 has no H, hence fails eligibility. It remains in the selection/exclusion
log and is not replaced or given invented H. Actual sample: **11 trajectories,
R1=4, R2=3, R3=4; one replicate; three decisions each**. All twenty seed C claims
are source-supported in SEED_REVIEW.json. The reviewer reads only the chosen
prefix, without gold, later results, full unobserved source, or final answer.
Initial R3 states are incomplete; expected outcome is CONTINUE, frozen before calls.
R2 has weak/unbound candidates, not confirmed wrong answers. Without a real
contradiction, wrong-H recovery has no evaluable opportunity and must be reported
as inconclusive. No outcome-driven relabeling as initially wrong.

## Prefix conversion and interventions

prepare.py preserves literal archived Q/C/H, observed D/W and source metadata.
Legacy E aliases map explicitly to their already observed W during pre-call seed
conversion. Existing H has empty basis rather than invented provenance. Full local
documents verify unique contiguous spans and hashes; only old observed spans enter
the role-visible registry. A single stable R1 repeats the original Q verbatim for
every new prefix. This deliberately avoids paid/bootstrap decomposition; it is a
cohort construction difference from H1, so H1-versus-H2 is not a causal contrast.
Mechanical archived trace is retained with unknown feedback unassessed. New trace
records the conversion. An initial offline keyword-argument error is preserved in
PREPARATION_FAILURE_001.txt; it occurred before model/retrieval calls or prefix saves.

- R1 forces the last actually observed Search query/k once; subsequent Actor free.
  The exact query and prefix request hashes are frozen. Unlike empty-H H1 fixtures,
  initial H can change despite no new raw observation. Record realized feedback;
  do not relabel Gain as NoGain to enlarge the recovery denominator.
- R2 starts with free Actor and the literal weak H. All tools remain available.
- R3 forces request_closure once, then free Actor after actual missing feedback.

Forced decisions consume a slot and zero paid calls. OneGap stays ephemeral;
long-term state is only Q/R/C/H/T. No hard masks, semantic-state additions,
automatic output translation, source reranking or tool modifications.

## Budget and execution

Ceiling: **174 requests = 4*17 + 3*18 + 4*13**, **29 acquisitions = 4*3 + 3*3 + 4*2**.
Unused H1 budget is not transferred. max_retries=0; no replacements or prompt edits.
DeepSeek Flash same temperature/thinking/token/JSON settings as H1. Initial/max
concurrency11 equals the number of independent trajectories; no independent queue
exists to justify higher concurrency. Async HTTP connection pool11; account budget
2400 with100 reserved; no other known Search-ESR API batch. Unknown external
account load cannot be measured directly. GPU0 uses unchanged BCPlus model/search;
retrieval serialized1, overlapped with model work, GPU1 left for its existing job.

HTTP connect30/read900/write60/pool30/total1200 seconds, stream=false. Timeout,
429 or503 halves concurrency for unsent requests down to1, without retry; retain
partial bytes. 400/401/402/403/404/422 or model mismatch halts unsent work. Preserve
in-flight outcomes. H model/provider/contract failure is auxiliary and atomic;
higher-authority role or integrity failure terminates that trajectory. Any
confirmed false C/READY blocks further stages. No post-result silent repair.

Freeze commit HEAD, config, eligibility/seed labels, initial requests, rubric,
prefix/source hashes, historical dependencies, prompts/schemas, Python sources,
versions, external BC+ snapshot and binary metadata before paid calls. Every
request archives its actual run HEAD, hash, raw response and status. No API keys.

## Review and metrics (frozen)

Codex single-reviewer, unblinded, source-relative; semantic judgments are not an
independent paid/model panel. Every new C is judged against its exact observed
support, including qualifiers and relation scope. Every H operation is judged
for namespace validity, direct contradiction versus candidate-local mismatch,
overbinding, premise hardening and churn. Every accepted Closure is checked
against Q/R/C and its supplied evidence; high-authority malformed output remains
a failed trajectory, not a corrected CONTINUE. No READY may rely on H alone.

Every acquisition: usable current OneGap, premise hardening, compatible source,
new raw evidence useful to that gap, supported/gap-useful C, H change. Raw evidence
yield excludes an already observed window even if newly converted into C. Record
that useful C-from-old-evidence separately. Inspection denominator=actual Find/Open
attempts; report all and valid-output denominators for failures. Runtime Gain is
reported separately from semantic progress. H-only churn is not verified recovery.

R1: realized initial NoGain count; whether next Actor/acquisition occurs; substantive
route change (same query paraphrase is insufficient); new gap-useful C by horizon.
Report forced-repeat trajectories producing Gain separately. R2: tested H, actual
contradictory/mismatch evidence, update appropriateness and subsequent route; if no
contradiction, do not claim recovery from a proven wrong H. R3: correct veto, next
acquisition addressing a named missing relation, useful C by horizon, repeated
Closure, false READY. Aggregate follow-up uses only within-horizon opportunities.

H errors/skips, C/Gain preservation and next Actor after H failure are separate
metrics. Zero H errors means no live isolation estimate. Replay all final states;
compare all historical micro_recovery and h_fix bytes against parent.

Accounting: attempted/not-sent/errors by role, tokens input/output/hit/miss,
sum(hit)/sum(input) over complete consistent usage, missing/inconsistent count,
latency percentiles, wall time, peak/changes in concurrency. Report every failure.
Small unequal families and three-slot horizon support descriptive mechanisms,
not causal effects, statistical success, or final answer accuracy. No arbitrary
post hoc pass threshold. Finish by identifying remaining failure layer and a
bounded recommendation; do not launch an additional stage in this task.
