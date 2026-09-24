# Frozen single-reviewer F1 rubric

Review only the original question, one semantic Gap, exact current W,
pre-call required/optional/duplicate/forbidden labels and arm output. Do not
inspect later trajectories, full documents, gold answers or other arm outputs
while judging a cell. A different wording can satisfy a required finding if
it entails the same observed fact. One combined statement may cover multiple
required atoms, provided each relation is supported; one required atom counts
at most once. A generic or broader statement does not cover a specific atom.

For each output statement record `evidence_grounded`, `gap_relevant`,
`world_fact`, `overreach`, `duplicate_existing`, `matched_required` (list of
zero-based required indices), `reason`. Evidence grounding requires the
current W to establish the *stated relation*, not just mention the entities.
Overreach is true when the statement imports a missing identity, causal link,
sequence step or full conjunction. A true world fact can be Gap-irrelevant.
Duplicate is evaluated for C against displayed committed Claims, and for B
only as a separate comparator diagnostic using frozen duplicate labels. A/B
precision never penalizes duplication. A Finding can be useful partial
evidence without closing the Gap. Meta-statements such as “still unknown” are
not world facts. The four E5 seed Claims are independently supported by prior
historical W but their new W is a repeated copy: this is a controlled
duplicate challenge, not a historical claim that the agent revisited it.

Cell error or invalid schema remains in denominator with zero findings and
zero required coverage. NoGain silence is evaluated only on E6. Per-finding
precision uses all produced findings as denominator; empty outputs provide no
precision credit. Unsupported inference is any ungrounded or overreaching
statement. State expansion is mean produced count per case. All labels and
case selection are frozen before requests; semantic decisions are recorded
with short reasons after responses.
