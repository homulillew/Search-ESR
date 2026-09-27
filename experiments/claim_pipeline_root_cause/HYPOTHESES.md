# Preregistered hypotheses (all currently unmeasured)

H1: removing C from formulation reduces unsupported strengthening while preserving
useful recall. Compare A1 versus A0 with identical production Reader prompt/schema.
Support requires FSSR relative reduction >=30%, GRSR drop <=10 percentage points,
positive packet-paired and qid-clustered direction, and the same improvement
direction in H-diagnostic. If baseline FSSR is0 or there are too few eligible
events, report inconclusive, not an infinite improvement or proven absence.

H2: removing Gap from formulation after Gap+C-conditioned selection additionally
reduces strengthening. Compare A2 versus A1: FSSR reduction >=30%, GRSR drop<=10pp,
Gap-relevance precision drop<=10pp, paired/qid direction and H-diagnostic direction.
Report selected-window omissions and irrelevant fact bloat. The split involves
extra calls and generic role specialization; causal attribution is to the
information-flow intervention as a package.

H3: evidence-first inventory plus candidate coverage lowers false admission.
Compare G1 versus unchanged G0 on the same frozen actual candidate/evidence pairs.
Require false-admit reduction>=50%, true-positive admit recall>=85%, paired/qid
direction and matching H-diagnostic direction. Report ambiguous cases separately,
inventory coverage and inventory strengthening. Universal rejection fails.

No p-value gate; small correlated mechanism diagnostic. Denominators, absolute
differences, relative changes, packet-paired changes and unweighted qid direction
are mandatory. Failed requests remain failures/missing, not silence or refusal.
No result-driven retries, thresholds, exclusions, prompt edits or negative examples.

E3 is conditional on at least one hypothesis meeting its complete gate. Components
are chosen by the E1/E2 decision table, before opening any H-confirmation outputs.
Use only the frozen H-confirmation packets; do not replace inconvenient cases.
Goal:0 observed false authoritative claims, source-supported precision>=95%,
gap-useful supported recall>=80%, correct-silence>=80%. Zero output has undefined
precision and cannot pass. No inference of population reliability from zero errors.

Decision table: A1-only advantage supports C-visible novelty pressure; A2-only
advantage supports selection/formulation coupling; G1-only advantage supports
admission anchoring/commitment separation. Combined advantage is consistent with
joint mechanisms. A two-arm E3 alone does not establish statistical interaction
without a factorial contrast. No mechanism signal means reject support for these
interventions here (or inconclusive for inadequate opportunities), not patching
production. A future implementation is a separate task even if E3 passes.
