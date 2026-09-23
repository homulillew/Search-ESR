# Orthogonal Search: frozen prospective design

This plan supersedes the *ordering* of the old v3b plan following
`../AMENDMENT_AFTER_COMPETITION_PROBE.md`. Freeze the exact code, checkpoints,
inputs and gate in `freeze.json` / `gate.txt` before any new model call.

## Causal question and arms

From an identical recorded v3a `api_request` prefix, continue for at most **four
API decision rounds** without forcing a final answer. P0 uses v3a
`SearchFindTools`; P1 uses `OrthogonalSearchFindTools`. Model, full messages,
prompt, tool schema/name, query, retriever, top-k, new-document localizer,
Find, Open, context, and stop policy are unchanged. The only treatment is
whether a later global Search can localize a *new* raw window in a canonical
document that is already discovered. Search queries remain model chosen.

P1 calls the original global retriever for exactly top-k hits. For each new
`(docid, sha256)` it registers a D# and uses the v3a preview builder. For each
old hit it skips the builder entirely and returns D#, source title/URL,
`already_discovered`, and the first discovery preview W# with a fixed local
Find instruction. Rank and score live only in private events. It does not
fill removed preview slots from deeper ranks. A Search returning mainly old
hits and no new raw window is `NoGainSearch`.

Both arms receive the same original prefix, including historical Search
results. Existing D#/W# and full documents are restored from the prefix audit
and pinned corpus; restoration verifies canonical SHA and exact raw window
slices. No retriever or localizer runs during restoration. Prefixes contain no
new gold or invented source text. The continuation harness validates every
returned function name against `SEARCH_FIND_TOOLS` **before any call in that
batch is executed**. An undeclared name is recorded, given an error tool
message, and never executed. No fuzzy repair.

## Frozen cohorts

**A: Broad Relocation**, all ten pre-existing mechanical checkpoints:
qid 546 seq 9/17/25/33/41; qid 1094 seq 23/34/45/53/61. These are
`RediscoveryOpportunity`, not automatically local Find opportunities.

**B: Local Verification Opportunity**, identified by reading only the prefix
question, reasoning, available D# titles/previews, and specific missing need.
These are additional checkpoints (not in A). The model's own next historical
action is checked for Search/Answer eligibility only after prefix selection;
no future outcomes or gold are used to choose a focus.

| qid / seq | Prefix supported focus and current unresolved need | Why the need could be inside |
|---|---|---|
| 1094 / 69 | Inter is considered plausible; D38 `Inter Milan` exists. Need: which early-century Inter match involved the late free kick/player? | A club page might have notable match history. Weakest B entry; do not assume it contains the answer. |
| 1094 / 93 | Reasoning considers a 95th-minute free kick alternative to the Messi clip; D14 `Last-minute goal` exists. Need: another player/event at 95 minutes. | A list of last-minute goals can reasonably contain other late free-kick events. |
| 1094 / 77 | Reasoning still treats Inter as plausible and considers several 95th-minute takers; D14 and D38 already exist. Need: a matching late-match event/player. | D14 may list it; D38 may recount an Inter match. This is correlated with the earlier 1094 entry. |

The B cohort is only one question and later prefixes are highly correlated;
results must be interpreted as mechanism cases, not independent frequency
estimates. qid 546's D17 Ding document is excluded from natural B: the
contemporaneous reasoning did not make it a promising focus. It is a separate
`DocumentTriageFailure` candidate. An optional D17 injection, if ever run,
must be separately labeled `diagnostic_oracle` and excluded from natural
effect estimates. No such oracle is in this batch.

## Batch, metrics, decision

13 distinct checkpoints × 2 arms × 1 continuation = **26 partial rollouts**.
Run all cells in fixed order, interleaved by checkpoint P0 then P1. Four
decisions max. If direction is mixed, add one replicate to **every** cell,
never just interesting cells. Preserve API, invalid call, OOM, timeout, and
harness failures in events; no best-of.

Report by arm and cohort: `find_before_next_search`, Find within decision
1/2/3, Find within two decisions of `NoGainSearch`, another Search after
`NoGainSearch`, new documents, old-document new windows from Search (must be
zero in P1), raw characters and repeated old-preview savings, prompt/total
tokens, latency, premature answer, and useful Find windows. A returned new W#
alone is not useful evidence: review the need, new fact, support/refutation,
and subsequent belief update separately. Do not force final answers or score
accuracy on partial continuations.

Strong H1 support requires a clear Find increase, switches after no-gain
Search, useful new Find windows at **at least two distinct checkpoints**, no
old-document Search relocation in P1, and no explanation by premature stop.
If this is not met, test S0/S1/S2 minimal Verification State next. Stop after
a strong mechanism signal; no prompt patch or full benchmark in this batch.
