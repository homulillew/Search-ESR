# q435: an unverified time relation crosses Reader and Grounding

## Adjudication boundary

This is a source-relative **unsupported temporal promotion**, not an independently
proved wrong album count. No gold answer, later source, or complete unobserved
article is required for the judgment. The source's juxtaposition admits a tempting
reading; it does not unambiguously establish the temporal relation asserted by C5.
Under the frozen strict support rubric, that ambiguity cannot become a fact.
This is a single-reviewer judgment, not a consensus annotation.

## Within-prefix sequence

1. Seed C3 carefully preserves the retrospective's “67 albums later” attribution.
   Seed C4 separately records its reference to a Forbes Africa interview in2016.
   W2 contains both statements. SEED_REVIEW does not time-bind the album count.
2. Forced Closure correctly returns CONTINUE. Among its missing conditions:
   the67-album count is not explicitly tied to the feature date; May is absent.
3. Actor slot2 asks for the exact feature month/date and count, then Open around W2.
   W3 adds surrounding biography but repeats the same key sentence:
   “67 albums later, Mtukudzi still spoke as if he was in search of what to call a
   career, telling Forbes Africa in2016...” (spacing normalized here only).
4. Reader proposes, and Grounding accepts:
   `Oliver Mtukudzi had 67 albums by the time of his Forbes Africa interview in 2016.`
   Grounding's reason explicitly relies on the count immediately preceding the
  2016 quotation. Runtime commits C5, producing Gain.
5. Slot3 Search obtains a distinct June2017 article separately mentioning a May2017
   Forbes listing and65albums. C6 retains these as attributed source statements.
   H lowers the2016 hypothesis and adds a tentative2017 alternative. C5 remains
   in the final C list. No later Actor/Closure decision fits in this horizon.

Step5 is not used retroactively to judge step4. It also does not establish a gold
answer or logically prove C5 false. It shows why a provisional interpretation
should not have been stored as an authoritative temporal relation.

## Failure layer

Reader creates the stronger relation; Grounding approves adjacency as entailment.
H's updates are contract-valid and nonfatal. This is not an H formatting failure,
not a namespace bug, and not a mechanical trace/provenance corruption. All hashes
and replay checks pass. A correct Closure veto earlier cannot prevent a later
Reader/Grounding promotion of the very condition it identified as missing.

C5 is preserved unchanged in the run. We do not edit it, relabel the trajectory
as a clean recovery, or infer a false final answer that was never generated.

## Exact audit trail

- `prefixes/R3_Q435.json` and `SEED_REVIEW.json`
- `run001/trajectories/R3_Q435__rep1/calls/001_closure.*`
- `run001/trajectories/R3_Q435__rep1/calls/003_reader.*`
- `run001/trajectories/R3_Q435__rep1/calls/004_grounding.*`
- `run001/trajectories/R3_Q435__rep1/trace.jsonl`
- `run001/trajectories/R3_Q435__rep1/FINAL_STATE.json`
- `analysis/SEMANTIC_REVIEW.json` and `analysis/INTEGRITY.json`

## Bounded next work (not executed)

Audit whether current Grounding input gives enough scope to distinguish a source
statement, its quotation date and the requested count-at-date relation. Build an
offline contrast set with explicit time binding, loose retrospective adjacency,
and two incompatible time scopes. Preserve the current strict C contract and
classify failures before proposing prompt changes. Do not add persistent fields,
hard masks, another semantic agent, or a larger recovery cohort to hide this case.
