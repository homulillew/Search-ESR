# Round 1 — one mechanism, locality

Observed mechanism: B5 broad frontier. P1 returned 13/24 developer outputs;
7 were strict valid, 5 bundled independent facts, 1 asserted an unprovided
zodiac mapping. Eleven outputs exhausted the 4096-token budget. Five B5 failures
span q177, q546 and q1034; q546 contributes three and dependence is disclosed.
The attached bad-case packet includes all 17 P1 failures, actual QCH, frozen
gap labels and original provenance. Output-unavailable cells are not assigned
invented semantic defects. Raw responses confirm reasoning consumed the cap.

Why existing prompt failed: it says one question, but the model can express
whole-candidate verification or a multi-match sequence as one grammatical
question. P3 also often encodes candidate identity as its missing issue, so its
second call expands that into all conditions. P3 8/24 versus P1 7/24 is only
4.17pp, below frozen 8pp cost rule; P1 remains the production-development baseline.
P4 22/24 shows that a narrowed supplied issue is often expressible, although it
has premise errors and its lower truncation rate is part of the observed gap.

Minimal intervention: append one generic locality rule to P1: choose exactly
one independently answerable fact/relation, including one identifying clue for
discovery; leave the rest for later. No task examples, ontology, source tools,
new fields, H removal, separate verifier or token-budget change.

What should improve: fewer broad/global-candidate Needs across qids; more local
first steps on no-H states. Output completion could also improve if narrowing
reduces generation effort, but this is secondary, not assumed causality.

What could regress: selecting a trivial/covered relation, dropping a necessary
join, unsafe concrete assumptions, or losing the sole remaining gap. Include
five valid baseline controls, one premise failure and five length failures.

## Frozen selection and analysis

16 already-exposed development states / 5 qids. B5 targets N004,N015,N016,N018,
N020; premise control N013; length cases N001,N006,N009,N019,N023; previously
valid controls N003,N007,N014,N021,N024. Baseline P1 reused exactly. New arm P5
= P1+locality, one sample each, 16 calls maximum, same model/temperature/token
cap/timeouts/retries0/8 workers, no tools. This is exploration, not confirmation.

Primary mechanism signal: number of five B5 cases becoming strict valid;
count W regressions among other 11. Report overall strict and premise, valid
control preservation, no-H and one-gap. Do not claim success solely from fewer
truncated responses. Clear mechanism evidence requires at least 3/5 B5 repairs
across at least two qids, with at most one regression among five valid controls
and no increase in premise count over the same 16 baseline cells. This is an
exploratory decision rule, not the task's confirmation gate.

Fresh confirmation is unavailable before this call: reserve only spans 5 qids,
minimum8 not met. Stop further tuning after this bounded exploration; report
whether the mechanism signal is present and what remains unvalidated. Do not
consume reserve as a pretend confirmation and do not run closure/simulation.
