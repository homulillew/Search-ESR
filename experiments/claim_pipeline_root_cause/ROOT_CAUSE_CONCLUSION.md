# Claim Pipeline Root-Cause Ablation — stopped at the E1 contract gate

## Material Passport

- Task: Claim Pipeline Root-Cause Ablation; current user explicitly authorized the
  frozen E1/E2 and conditional E3 plan after preparation.
- Preparation HEAD: `cd288012`; execution HEAD: `af4b1496`.
- Execution date: 2026-09-28 Asia/Shanghai (2026-09-27 UTC).
- Scope: frozen archived evidence, diagnostic Claim pipeline only; no retrieval.
- Status: **E1_STOPPED_CONTRACT_FAILURE; H1/H2 inconclusive; H3 not tested.**
- Evidence: unchanged requests, raw response/reasoning, transport accounting,
  `e1/CONTRACT_FAILURE_AUDIT.json`, and preserved blind review packets.
- Review status: technical contract audit complete; semantic support/relevance
  labels and comparative semantic rates deliberately not assigned after gate stop.

## Outcome

E1 issued 85 paid requests at peak concurrency72 and completed in28.06 seconds.
All85 returned HTTP200; no timeout or HTTP error occurred. Eight responses failed
the frozen output-reference contract. One already constructed dependent request
was not sent after the first failure halted new sends. Already in-flight calls
completed and were retained. No retry, replacement, prompt edit or rerun occurred.

The halt occurred about7.4 seconds after transport initialization. Consequently,
later completions can also fail the same contract; this is not evidence of sending
new requests after the halt. The append-only attempt/request/result records make
the timeline auditable. All86 constructed request hashes match the preregistered
hashes, and every preparation file still matches the original freeze.

| Construction arm | Successful packet chains | Failed packet chains | Candidates in successful chains |
|---|---:|---:|---:|
| A0 |24/24 |0 |15 |
| A1 |22/24 |2 |17 |
| A2 |17/24 |7 (6 attempted failures +1 unsent dependency) |21 |

These are execution counts, **not** semantic precision, recall or Claim-bloat
comparisons. A2 has selective missingness, including on held-out cases. The53
candidate source/relevance review packets remain available, but they have not
received semantic labels. Failed responses retain their original findings too.
Neither valid JSON nor HTTP200 implies supported content or a valid evidence ref.

## Observed failure

Every attempted failure has the same technical form:

```text
Input contains window_ref = W#
and source_window_ref = w_<underlying identifier>.

Output evidence_refs contains the underlying identifier,
alone or together with W#.

Frozen validator permits only the current window_ref values.
```

All offending identifiers actually occur in the supplied source metadata. None of
these eight failures is an unknown identifier invented outside the input, and none
has a blank factual statement. This is **confusion between two visible reference
namespaces**. It is not, by itself, unsupported semantic strengthening.

Failures span q177,q186,q435,q633,q637,q673,q922 (seven qids). Two are A1 Reader
responses and six are A2 Formulator responses. The technical audit records exact
allowed refs, visible aliases, returned refs and untouched outputs. No aliases
have been rewritten into W# and no response has been retrospectively admitted.

Preparation tests proved that the harness rejects invalid refs; they did not prove
that the real model would consistently choose the correct namespace when both are
visible. This run exposes that unverified interface assumption. It does not show
that hard separation improves or worsens factual entailment.

## Gate decisions

- E1: stopped under TASK section37 and the frozen PROTOCOL failure policy.
- E2: not run; E1 is incomplete, so no valid reviewed candidate bank was frozen.
- E3: not run; no complete mechanism gate is eligible.
- Production Reader/Grounding, state, retrieval and other runtime components:
  unchanged. No additional persistent field was introduced.

The user authorization covered these stages. The stop is caused by the
**preregistered failure rule**, not by missing permission, account throughput or
provider connectivity. The previous preparation status files are historical
snapshots and remain unchanged; new execution/gate files record this outcome.

## Token and cache accounting

| Item | Observed |
|---|---:|
| Attempted calls |85 |
| HTTP200 responses |85 |
| Output-contract failures |8/85 (9.41%) |
| Unsent request records |1 |
| Consistent usage records among attempts |85/85 |
| Input tokens |92,761 |
| Output tokens |133,581 |
| Total tokens |226,342 |
| Cache-hit input tokens |21,503 |
| Cache-miss input tokens |71,258 |
| Cache hit rate |23.1811% |
| Median latency |4.40 s |
| P95 latency |21.29 s |
| Maximum latency |27.23 s |

Cache rate is21,503/92,761 over all85 complete, consistent usage records, including
the contract-failed paid responses. The transport summary's one missing usage
record belongs to the unsent request; no paid response lacks usage. Thinking was
enabled with high reasoning effort in every request, and all85 responses contain
nonempty reasoning content. E2/E3 calls=0; retrieval calls=0; retries=0.

## Answers to the17 research questions

| # | Question | Answer supported by this run |
|---|---|---|
|1 |Does false Claim strengthening recur across relation types? |Not established. Cross-qid reference-contract failures are not semantic strengthening labels. |
|2 |Is strengthening concentrated in Gap-relevant relation completion? |Not estimated; semantic review/comparison stopped. |
|3 |Does C in generation increase strengthening? |H1 inconclusive; A1 has contract failures. |
|4 |Does moving C to post-generation dedup improve it? |Not estimated; no valid complete paired semantic comparison. |
|5 |Does Gap-conditioned selection retain relevance? |Not established by selector completion counts. |
|6 |Does removing Gap from formulation reduce strengthening? |H2 inconclusive; A2 is incomplete. |
|7 |Does A2 recreate observation-only Claim bloat? |Cannot compare21 surviving A2 candidates with complete A0; missingness is differential. |
|8 |Does Correct Silence improve? |Not scored. Empty output requires frozen source/Gap/C review to count as correct silence. |
|9 |Does candidate anchoring increase false admission? |H3 not tested; E2 did not run. |
|10 |Does evidence-first Grounding cause recall collapse? |Not tested. |
|11 |Which mechanism has the same held-out direction? |None established by a complete valid gate. |
|12 |Is there an interaction? |Not tested; the planned two-arm E3 alone would not identify a factorial interaction. |
|13 |Should the formal Reader change? |No factual-prompt or runtime change is justified by this run. Reference-contract design needs separate investigation. |
|14 |Should the formal Grounding change? |No; Grounding was not tested here. |
|15 |Is there evidence for new persistent semantic state? |No evidence from this run. |
|16 |Should a complete Recovery rollout proceed? |No; first obtain a valid complete Claim-pipeline diagnostic under an unambiguous reference contract. |
|17 |Accept, partially accept, or reject the root-cause hypotheses? |Inconclusive, not accepted or rejected. This is a contract-level stop, not a negative causal finding. |

## Bounded next direction

A future, separately frozen contract investigation could define one public reference
namespace for generated citations or explicitly specify which field supplies legal
refs. Its scope should be mechanical reference identity, with unchanged source text
and no case-specific factual examples. The existing output schema is generic enough
to accept these strings structurally; the stricter reference-set check rejects them.
Potential repairs must therefore be evaluated as a new contract, not silently added
to this run or called a successful semantic intervention.

No fix or follow-up calls were made here. The original H1/H2/H3 explanation remains
open until a complete cross-case, held-out ablation can be measured.
