# Protocol amendment after the Tool Competition Probe

Date: 2026-09-23. This is an additive amendment to the frozen v3b record. The
original `HYPOTHESES.md`, `EXPERIMENT_PLAN.md`, `RESULTS.md`, and
`FROZEN_STATE.md` remain historical records and are not revised.

## Frozen result retained

The preregistered rule puts Arm C exploratory Find = **4/50** in the **weak**
band (and 3/10 checkpoints). Arm A was 0/50. This classification is retained;
the amendment does not relabel the observations or discard failed calls.

## Treatment manipulation audit

Inspection of the original `competition_probe/20260922T174605.704525Z/events.jsonl`
and the probe's SDK response extraction confirms that Arm B's first action was
`search` in **41/50** cells and Arm C's in **36/50**. Those are provider-returned
function calls with `finish_reason=tool_calls`, although the B/C tool schemas
declare only `find` and `open`. Removing a name from the schema therefore did
not remove it from the model's generated action space. The one-step probe did
not execute tools, so it also did not test whether a harness rejection would
cause a later switch to Find.

Arm C replaced the dedicated Search paragraph but left the opening sentence
`You can research the local BrowseComp-Plus corpus with search, find, and open.`
intact. Its system message thus gave conflicting availability cues. Every
checkpoint prefix also contained successful assistant `search` calls and tool
previews. This history reinforced the action prior. The probe cannot isolate
the effect of removing Search's *capability*.

Experiment 1 informs **declared tool-menu competition**: the model often
generated an undeclared name. It does **not** adequately test whether Search's
ability to relocate inside an already discovered document suppresses Find.
That central H1 mechanism remains untested. The weak band alone must not be
used to reject it. The provider behavior also requires harness-side validation
of every returned tool name against the current schema before execution.

## Revised prospective order

Before any new paid call, freeze and run a true **Orthogonal Search** experiment:
global retrieval still returns its original top-k hits, but an already
discovered canonical `(docid, document_sha256)` yields only its D# identity,
title, URL and original preview reference. It must not run local BM25, create
a new W#, or inject new raw text. New documents keep the v3a preview path.
Compare short P0/P1 continuations from identical prefixes in both broad
relocation and prefix-identified local verification cohorts. Retain every
failure and enforce declared tool names in the harness.

Only if that intervention fails to yield a clear useful Find mechanism, test
minimal Verification State with S0 (none), S1 (unresolved need), and S2
(unresolved need plus prefix-supported focus D#). Keep any gold-derived focus
in a separate `diagnostic_oracle` arm. Test tool/API prior with scoped Search
only after the first two mechanisms have been tested. This order supersedes
the *prospective stage order* in the old plan; it does not rewrite the plan's
preregistered outcome or claim the old probe was invalid.

The causal target is now explicit: **Can global Search re-localize a document
already in the workspace?** A previously retrieved document is not by itself
a Find opportunity. A natural local verification opportunity additionally
requires a promising document in the model's prefix belief and a specific
unresolved need plausibly inside it. This distinction prevents retrospective
gold documents from being treated as natural focus documents.
