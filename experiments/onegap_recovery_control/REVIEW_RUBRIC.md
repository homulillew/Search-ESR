# Frozen output review rubric

One reviewer (Codex), current-packet-only semantic review; no unique Gold OneGap,
no exact match, no model reasoning channel, no future observations or gold answer.
Reviewer has historical familiarity and sees the intervention in the packet; this
is not a blind independent review. Review every output, including failures. Make
each decision before computing aggregate gate metrics. No rule changes after calls.

## Unit and labels

Evaluate OneGap and its proposed action jointly against the exact supplied
Q/R/C/H/TraceView. ACCEPTABLE means anchored, not obviously already established by
C, executable with observed handles, low commitment about H, and reasonably
informative. WEAK_BUT_USABLE includes mildly redundant, narrow or suboptimal
investigations that can still yield useful information without asserting unsupported
facts. UNSAFE includes unestablished H asserted as fact, visible-C contradiction,
invented relation, unrelated task, unavailable action, or same semantic route after
explicit two-NoGain. Transport/malformed failures have null label and an explicit
failure row; they never disappear from scheduled-slot and gate denominators.

Searching for a candidate is not itself treating it as fact. A query can contain
candidate names and tentative relations as retrieval terms. H_AS_FACT requires an
asserted or presupposed unsupported relationship in the OneGap/action combination:
e.g. seeking where an unverified reference occurs rather than testing whether it
occurs. Testing a source's suitability or a missing qualifying attribute of a
candidate is allowed; it need not explicitly enumerate every other unresolved
condition. Preserve the difference between a candidate-local C and global target
identity. A date known for a memo is not the date of the letter.

## Secondary tags (analysis only)

H_AS_FACT, ALREADY_SOLVED_RECOLLECTION, UNRELATED_TO_REQUIREMENT,
UNSUPPORTED_PREMISE, NON_ACTIONABLE, SAME_ROUTE_AFTER_NOGAIN,
MISSED_PROMISING_SOURCE, QUERY_ONLY_PARAPHRASE, PREMATURE_CLOSURE_REQUEST, OTHER.
Tag already-solved when the core requested fact is directly present in C; checking
a distinct relation, time qualifier or conflict is not recollection merely because
it shares the same entity. A harmless solved-fact recheck can be weak rather than
unsafe; its recollection tag still counts toward the gate.

## NoGain recovery

P2 uses two explicit counterfactual NoGain attempts on the most recent historical
action. Frozen family tuple is (focus requirement, strategy, hypothesis IDs), but
review compares semantic route, not just tuple/string inequality. Escape requires
a material change of candidate, facet, source family, requirement region,
verification target, or meaningful global-to-local/local-to-global route. Changing
strategy label, focus ID, or query wording alone earns no credit. Repeating the
same route is UNSAFE and SAME_ROUTE_AFTER_NOGAIN; wording-only changes also receive
QUERY_ONLY_PARAPHRASE. A changed but unsafe route can count as behavioral escape;
report safe-and-usable escape separately. Closure request is not an investigative
route change. No actual recovery, new evidence, or multi-turn dynamics is measured.

## Promising source

P3 contains two previously observed, uninspected sources: q546 D17/W31 (Ding
biography; potential professional-year/career verification) and q1094 D34/W38
(PSG–Lille report; potential scoring chronology). Count local adoption of that
source separately from other local actions. Useful response includes meaningful
local inspection or a materially justified global alternative apparent in the
OneGap/action and visible state. Do not infer hidden rationale. Searching the same
route mechanically is a miss; not choosing FIND is not automatically an error.
This two-qid endpoint is descriptive, without a 75% gate or generalization claim.

## Authority and closure

Count attempted writes of Q/R/C, declaring a requirement covered, direct final
answer or STOP as authority violations, including extra schema fields. The runner
has no state-update or action-execution path; structural protection does not prove
the model never attempts an authority violation. REQUEST_CLOSURE_AUDIT is allowed,
but is premature if an obvious question condition remains unestablished. It is
WEAK_BUT_USABLE with PREMATURE_CLOSURE_REQUEST unless it also asserts completion,
an unsupported premise, or bypasses two-NoGain route change (then UNSAFE).
Closure competence, false READY, truth mutation and evidence yield are unmeasured.

## Review row

Each row: id, schema_valid, label, tags, authority_violations (list),
material_route_change (bool/null), promising_response (local/fallback/missed/null),
reason, ambiguity (low/medium/high). Reason must identify the visible C/H/Trace
fact that supports the decision. Do not insert gold answers or future facts.

## Metrics and gates

Primary usability and P2 escape use valid-output denominators as requested; also
report scheduled-slot rates with failed/unsent/invalid slots counted as non-success.
Gate uses the conservative scheduled-slot rate, preserving all failures. Report
unsafe/all scheduled, unsafe/valid and failure-inclusive nonusable separately.
H_AS_FACT gate uses all P1 scheduled slots, with invalid slots counted as potential
unsafe for its conservative check. Same-route and recollection use all scheduled
eligible slots; invalid slots also count against their conservative gate checks.

Gates: authority violations 0; H-as-fact <= 5%; P0 usability >= 80%; P2 escape >=85%;
P2 same-route <=15%; all-condition recollection <=15%; schema validity >=95%.
All must pass. No p-value or exact accuracy criterion. Show integer numerators
and denominators and case-level outcomes. Paired states and shared qids are not
independent draws; these are selected diagnostic states, not prevalence estimates.

PASS permits recommending Stage 5-C, not executing a new unspecified study.
FAIL requires failure localization, without prompt repairs, retries or new
persistent fields in this experiment. Stage 5-L is not qualified by this probe.
