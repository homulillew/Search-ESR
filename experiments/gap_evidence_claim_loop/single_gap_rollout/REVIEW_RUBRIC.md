# Prefix-only and outcome review rubric

Before any F3 model calls, inspect only Question, historical prefix,
already-visible W and committed seed Claims. Reject action-style or already
resolved Gaps. A seed Claim must be supported by its referenced W, with no
unsupported identity, temporal or causal step. Record ambiguity.

After execution, review each new W independently: `useful_evidence` requires
new support, contradiction or valid exclusion material to the frozen Gap;
mere entity mention does not count. A `compatible_source` has the source type
and content to check the Gap even if the returned window misses. A new Claim
is valid only if its exact referenced W supports every substantive clause.
Assess true Gap resolution from verified Claims and observed W, independently
of the Gap Reviewer. Premature close means `resolved` without sufficient
Claims; missed close means `open` with sufficient Claims. Mark repeated same
query/source/window and redundant retrieval of facts already in seed/new
Claims. Assess scope using currently visible handles, not future sources.
Classify failures GE1–GE16 from the parent protocol. The single reviewer
records reasons and keeps uncertain judgments separate from clear errors.
