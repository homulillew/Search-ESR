# Clean Recoverable Loop — implementation design audit

## Material Passport / branch boundary

Offline engineering and historical-fixture replay; no model-quality experiment.
2026-09-28: `git fetch origin --prune` completed. Remote Stage 4
`origin/experiment/ephemeral-obligation-decomposition` remains
`7fdb048e856545facd4acfb590e8cf28c46f1013`; no added commits to assess.
New branch `experiment/recoverable-loop-clean` starts exactly there. No merge or
cherry-pick of either later diagnostic branch. Later results are read using pinned
`git show` only, preserved on their original branches. AGENTS.md is an operational
preference document copied separately; this task's explicit offline-only boundary
takes precedence over standing paid-call authorization.

This audit is the first committed deliverable, before implementation.

## 1–4. Tool contract and previous error

1. Stage 4 implementation: `llm_chat/search_find_agent.py` supplies
   `SEARCH_FIND_TOOLS`, `HandleRegistry`, `SearchFindTools.execute`;
   `llm_chat/raw_windows.py` implements local window selection/continuation.
   `llm_chat/search_find_v3b_agent.py` supplies the existing Orthogonal Search
   subclass. No retriever, localizer or tool semantics will be modified.
2. Handles are episode-local. D maps to `(docid, full_document_sha256)`; changed
   document bytes create a different D identity. W maps to a canonical raw-window
   key derived from document identity and exact offsets. Identical spans reuse W;
   expanding a span creates a new W without changing the old one. Never restore a
   D/W alias without its exact document/window provenance.
3. Actual arguments: search `{query,k?}` (k1–10, default5); find `{doc_ref,query}`;
   open `{window_ref,direction}`, direction before/after/**around**. All query
   strings must be nonempty and <=16000 chars. Find/open reject extra arguments.
   Search execution currently ignores extra keys although its advertised schema
   forbids them; the new adapter will enforce the existing schema before dispatch.
4. Previous `onegap-recovery-control` introduced an independent uppercase action
   union with `source_ref` and `pattern`, and omitted around. Eleven outputs used
   OPEN with a keyword instead of direction. That was an avoidable harness/API
   mismatch; it is not evidence that the real Open backend failed. The old scores
   and artifacts will remain unchanged. The new action is exactly
   `{tool: name, arguments: original_function_arguments}`; no intent conversion.

## 5–7. Reuse and exclusion

- Reuse actual tool schemas/execute/registry/raw-window machinery unchanged.
- Reuse Stage 4 D2 skeleton outputs and exact original question spans as data.
- Reuse historical Gap-conditioned Reader's 0–3 selective-fact principle and
  source-relative verifier principle from `gap-evidence-claim-loop`. Its F1/F2
  signal was positive; F3 showed truth/closure failures, so its runner is not a
  validated general loop.
- Reader receives OneGap, existing C, and actual normalized Observation(s). One
  acquisition can return several windows: cap at three candidate facts across
  that acquisition, rather than three per window. No broad fact inventory.
- Reader outputs statements plus selected observed W references; selecting which
  evidence supports a statement is semantic work. Hashes, offsets, URLs, texts,
  Claim IDs and versions are assigned/copied by the harness, never rewritten by
  the model. Do not demand a model-authored excerpt.
- Grounding verdict receives the candidate and full cited observed windows with
  source metadata. Unlike the old historical verifier, it receives no Gap or
  unrelated committed C as substitute evidence. No single-excerpt-only admission.
- Do not import later Writer/Admission logic, E1 gates, custom action union,
  residual fields or previous premature-closure-is-unsafe scoring.

## 8–10. Roles, authority and mechanical information

| Component | Input | Output / authority |
|---|---|---|
| Actor | Q/R/C/H/TraceView/observed handles | acquire with ephemeral OneGap + real action, or request_closure |
| Tool adapter | validated tool arguments | unchanged execute call, normalized raw observations |
| Reader | OneGap/C/current observations | 0–3 temporary factual candidates; no state writes |
| Grounding verdict | candidate + full selected raw observations | supported/insufficient, bound to exact payload |
| Commit | valid supported verdict + observed refs | append new C with mechanical ID/version/provenance |
| H manager | Q/R/H/new observations/new C/trace outcome | bounded ADD/KEEP/DEPRIORITIZE/REJECT proposals; useful source nominations |
| Feedback | committed deltas, actual tools, source nominations | mechanical Gain/NoGain and Trace |
| Closure | Q/R/C/evidence supporting C | CONTINUE feedback or READY; no H/OneGap/Trace |
| Finalizer | Q/C/supporting evidence/READY verdict | answer only after a current READY permit |

Persistent semantic state has exactly Q/R/C/H/T. Raw Workspace/evidence is an
immutable source archive, not another semantic progress graph. OneGap can appear
in historical T but is not retained as an active authority or separate state slot.
Q/R are immutable. No generic model-authored state patches. Typed narrow
transitions and copied role inputs prevent incidental mutation. These are
engineering boundaries, not a sandbox against malicious host Python code.

## 11–13. Action, premise and Closure choices

Choose **B**, thin Actor Decision JSON. Action embeds `{tool,arguments}`; the
argument schema is copied programmatically from `SEARCH_FIND_TOOLS`, not authored
again. Validate JSON, source existence and the real executor's bounds, then call
`execute(action['tool'], action['arguments'])` unchanged. Invalid output is logged
as a failure, never converted, retried or replaced. Closure is a distinct decision
with no artificial OneGap/strategy/action arguments.

Prompt explicitly distinguishes candidate properties from known C, with the
Euler, memo/letter and Ding relative-clause examples. Offline fixtures contain
human-readable acceptable/unacceptable premise examples. A deterministic test
cannot prove general natural-language entailment; no keyword blacklist or new
semantic verifier will pretend to solve that. Fixture judgments test the intended
review contract and state isolation, not future model compliance. A structurally
valid but semantically hardened OneGap remains a measurable control error, unable
to directly mutate C.

Premature request_closure is allowed even after NoGain. A scripted/real Closure
CONTINUE supplies open requirement IDs and missing summaries into T only. Next
Actor sees the feedback. Only Closure READY permits finalization. READY is bound
to the exact Q/R/C/evidence snapshot; changing facts invalidates the permit.
False READY is a semantic model risk, not something mocks can certify away.

## 14. Gain/NoGain

Gain requires an accepted new Gap-relevant fact, a new nonduplicate hypothesis,
an active H becoming rejected/deprioritized, or a newly discovered uninspected
source that the H manager nominates as useful. A conflict resolved by new facts
or H correction counts through those deltas; no separate conflict graph is added.
Bare new handles, repeated H/claims, invalid outputs and closure requests are not
automatically Gain. Reader handles relevance/semantic novelty, while exact
duplicate checks and deltas are mechanical. Claim bloat/semantic duplicates remain
audited risks: log all proposed/rejected/committed facts and gain reasons.

Same-route feedback uses (requirement ID, small strategy label, tested H IDs),
ignoring query wording, as a **mechanical signal**, not a proof of semantic route
identity. TraceView is recent-three attempts, latest Closure feedback and pending
uninspected opportunities. These fields are T projections, not persistent Residual.

## 15. Offline invariants and scope

Test all three Open directions through the real execute method, unknown/wrong
handles, strict action shape, unchanged raw text/hash/offset, reference stability,
and both ordinary/Orthogonal observations. Mock only corpus retrieval and use a
deterministic local test tokenizer: no BC+ encoder load or network.

Test immutable Q/R, Actor cannot write C or finalize, H cannot promote itself,
bounded H/claims, unsupported verdict rejection, full-window verifier input,
failure retention, no retries, NoGain despite duplicate/irrelevant discoveries,
CONTINUE feedback round-trip, READY snapshot binding, and append-only log replay.

Replay historical Euler, book/article, memo, patient/report-country, teammate,
DLC, q637, Ding, q546 and q1094 fixtures. Scripted semantics explicitly identify
what is assumed by a mock; no offline metric will be labeled model accuracy,
Claim truth precision or False-READY performance. New paid/live experiments are
outside this task; deliver reports, an unexecuted 2–3-step plan and call bounds.
