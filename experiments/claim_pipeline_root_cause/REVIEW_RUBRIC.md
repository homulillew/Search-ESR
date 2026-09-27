# Frozen source-relative review and blinding

Single reviewer: Codex, authorized by this task. Support decisions use only the
exact supplied Observation and its visible metadata. No gold, final answer,
future tool output, whole-document lookup, model familiarity or another arm's
output. Archived Gap/C contexts are flagged; their truth is not assumed.

## Candidate labels

Every factual candidate gets `source_supported`, `semantic_strengthening`,
`strengthening_type` (zero or more of the eight preregistered families),
`gap_relevant`, `duplicate_with_C`, `gap_useful_if_supported`, and a reason.
Also record `ambiguous_relation`, `covered_atom_ids`, and `duplicate_group`.
Unsupported strengthening adds an unobserved subject, object, relation, time,
quantity, modality, condition or identity commitment. Plausibility is insufficient.
If any conjunct is unsupported, the whole candidate is unsupported; do not award
atom recall to its otherwise correct clauses. Attribution, uncertainty and local
scope are part of the proposition. An explicit quotation can support an attributed
claim without proving the underlying reported event. Numeric/cross-entity/time
facts cannot be transferred merely because they are adjacent.

Source disagreement or unreadable/truncated binding is `source_supported=false`
with a reason and ambiguity flag. Unsupported is not necessarily false in the world.
Historical C is novelty context only, never extra evidence for a new commitment.
Actual historical candidates remain verbatim, even if wrong. No constructed negative
is sent to a model. Synthetic tests exercise contracts only and never enter the bank.

## Atoms and silence

E0 freezes local, new, Gap-useful atoms before any new output. The anchor offsets in
annotations locate relevant source text; the full unchanged window and visible
title/table header, not a clipped quote, remain the support unit. A broad Gap can
have a useful partial fact without the entire target being established. Each atom
is one recall unit even when a minimal natural relation needs multiple arguments.
No missing relation is supplied by an expected atom. Frozen denominators never
expand because an arm produced an attractive statement. Extra valid statements
may receive candidate-level supported/useful labels, but are reported separately
from frozen-atom recall. Report atom denominators by split and qid.

Primary Correct Silence includes `duplicate_no_new` (relevant facts already in C)
and `relevant_no_new` (the current candidate/document is inspected but its visible
text supplies no fact about the requested missing relation). Report these strata
separately too. Other zero-atom windows form a separate off-gap silence diagnostic;
do not pool those to inflate primary Correct Silence. Report raw/post-dedup empties;
A1's intended dedup benefit is measured after generation, with raw duplicates retained.
No primary silence cases in a split => undefined, never zero/100% or automatic pass.

Dedup: normalized exact statements first, then blinded semantic `duplicate_with_C`
and within-output `duplicate_group`. For a group keep the earliest original index.
Identical treatment across arms; no arm-specific leniency. A false stronger relation
is not a duplicate just because C contains its separate premises. Raw strengthening
is always counted before this filter.

## Review packets

Two separate files per opaque candidate ID: source-support packet with Candidate
and Observation only; relevance/dedup packet additionally with OneGap and C.
The private mapping contains arm/packet/origin and is excluded from review input.
Never bundle alternatives from other arms. Generate mapping before labels. Review
support first, freeze those labels, then relevance. A separate source-only inventory
review marks omissions, strengthening and reference validity. A separate packet-level
review checks whether frozen atoms were covered; empty output is not missing output.
Author/reviewer is the same agent and familiar historical text may reveal provenance:
blinding reduces displayed cues, it does not establish independent review.

## E2 labels

Freeze the candidate/evidence bank after E1 review and before G0/G1 calls. Supported
positives, unsupported strengthened negatives and ambiguous relations are separate
flags (ambiguous is a subset flag, not a third verdict). Require supported and
strengthened-negative pairs in each D/H-diagnostic split or stop H3 inference.
G1 coverage is evaluated against the source-relative candidate label, not declared
correct merely because an erroneous inventory agrees. Inventory omission can lower
TPR; inventory strengthening can raise FAR. Record both independently.

## Denominators and gates

Report numerators/denominators, paired packet deltas and equal-weight qid mean deltas,
by D and H-diagnostic plus pooled; context-kind and family sensitivity tables.
No treating candidates from one qid as independent replicated cases. No p-value gate.
Undefined denominator, missing review or any schema/transport failure makes the
affected stage gate indeterminate. Preserve all outputs/failures, no replacements.
Zero baseline errors => relative error reduction undefined, not mechanism support.
Mechanism support requires pooled threshold and the same error-reduction direction
on H-diagnostic, with recall/precision guardrails there too. Opposite qid-weighted
direction blocks a mechanism claim. See PROTOCOL.md for numeric thresholds.
