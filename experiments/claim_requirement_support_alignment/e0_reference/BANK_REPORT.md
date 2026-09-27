# E0 bank and single-reviewer reference

Status: complete before any new model call. Reviewer: Codex, one task-familiar semantic reviewer; no claim of independent validation. Evidence reviewed: Original Q, source-anchored D2 Parent, whole current Claim list. Historical human masks were available as reference. No historical model prediction, provider reasoning, future observation or source full text was used to decide these labels.

## Coverage

24 parent-state cells, 16 distinct natural snapshots, 9 qids; 82 cell×Claim annotations. Claims are nonempty in every cell. Frozen selection: 12 hard negatives, 12 positive controls (7 partial / 5 full). The three source studies share their underlying bank; only 9 qids have an eligible nonempty-Claims snapshot. This falls short of the >=10-qid target and is disclosed rather than filled with fabricated states. This is an enriched mechanism bank, not prevalence estimation or fresh generalization.

| Primary role | Claims |
|---|---:|
| SUBSTANTIVE_SUPPORT | 18 |
| BINDING_CONTEXT | 28 |
| BACKGROUND | 33 |
| IRRELEVANT | 3 |

All 24 support sets and full/partial/zero strata agree with historical human contributing-Claim references. New role and exact-scope annotation was rereviewed, not inferred from model outputs. Historical files remain untouched.

## Reference conventions

- Candidate-conditional support is allowed on an explicitly identified branch; it does not verify that candidate as the final answer. Kwon and Ding may not exchange properties.
- A bare entity's attributes do not satisfy a relation to an unidentified book, charity, building, patient or teammate. Euler's birth is binding context for L.E., not target-book reference support.
- Binding may identify a currently considered candidate even when no substantive support exists yet. A secondary biographical detail without referent-disambiguation value is background, not automatically binding.
- Joint support is allowed only for explicitly observed operands bound to the same entity/event. C1+C3 in A14 supplies book/article years and topics; C3+C5 in A19 supplies the two release dates. A fragment that names a comparison is conditional on that declared joint group. Neither operand alone is a full relation.
- Thus A13 book-only is binding, whereas A14 book plus observed article contributes to a grounded comparison. This context-dependent role boundary is explicitly ambiguous. It is not evidence for a universal claim-level label independent of current Claims.
- A17 patient nationality does not establish report country. Only the clinical-history sentence is supported. A20 supports religion/technology and mechanics changes, leaving the playable-European-nation qualifier unresolved; no outside geography is admitted.
- Exact fragments are evaluation annotations, not new task nodes. They must not be sent to E2 or stored as persistent state.

## Ambiguity and sensitivity

Frozen AMBIGUOUS_REFERENCE cells: A06, A08, A13, A14, A19, A20. Primary labels remain fixed. Report primary metrics on all cells; additionally report nonambiguous-only metrics and each flagged cell's contribution without replacing the primary gate. Two ambiguities are secondary role boundaries; four involve joint support or mechanics scope. Do not post-hoc remove a newly difficult model output to claim PASS. New review disagreement must be disclosed separately with original labels preserved.

## Mandatory cases

Euler A15; SPS A16/A17; memorandum/letter date A23; nationality/report-country A17; alma mater/building A06/A08; coder and teammates A22; artist/charity A09/A11; Kwon/Ding A05/A07/A08. Natural transitions for E2: A05→A07 (G05R2→G06R2), A16→A17 (G17R3→G18R3). Both add true support and require a changed residual. Stable negative pairs A06→A08 and A09→A11 are secondary invariance diagnostics.
