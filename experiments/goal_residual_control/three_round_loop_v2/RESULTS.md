# G5v2 — completed three-decision loop

Ten frozen question seeds × three arms; at most three Actor decisions and two independent actions per decision. Every cell reached STOP, its horizon, or a retained failure. This is a diagnostic cohort, not a final-answer accuracy benchmark.

## Primary outcomes

Closure is judged from actual committed Claims against the original question. Working Hypothesis and uncommitted source text cannot close the primary goal.

| Metric | L0 Persistent Gap | L1 State-only | L2 Derived Residual |
|---|---:|---:|---:|
| Original Goal Resolution / 10 planned | 1 | 1 | 1 |
| Correct STOP | 1 | 1 | 1 |
| Premature STOP / 10 planned | 3 | 4 | 2 |
| Late research decisions | 0 | 0 | 0 |
| Unrelated goal drift | 0 | 0 | 0 |
| Failed cells | 0 | 3 | 2 |
| Open at horizon | 6 | 2 | 5 |
| Actor calls / valid | 25 / 25 | 20 / 17 | 25 / 24 |
| Acting decisions | 21 | 12 | 23 |
| Primary Progress decisions | 7 | 5 | 8 |
| NoProgress / acting | 14/21 | 7/12 | 15/23 |
| Alternative-source Progress, lower bound | 14 | 8 | 12 |
| Tool calls | 41 | 24 | 45 |
| Search / Find / Open | 33 / 6 / 2 | 20 / 4 / 0 | 34 / 6 / 5 |

L0/L1 resolve q186 after two tools and correctly stop at their next decision. L2 resolves q435 after six tools and stops at the final Goal Review. These are different questions; equal totals do not imply paired equivalence. L0 q435's last Search returns no new window and its Open moves beyond the relevant musician entry. It does not receive L2's new exact May-2017 count relation.

Across the six qids without failures in either L1 or L2, both resolve 0/6; premature stops are 4 versus 2, tools 18 versus 29, Progress decisions 3 versus 6. Failure exclusion is a selected sensitivity, not a repaired primary estimate. L2 has no demonstrated original-goal resolution advantage over L1 in this small run.

## Failure and scheduling accounting

All 472 API calls returned: 70 Actor, 372 Updater, 30 Reviewer. Actor validity is 66/70. Three invalid Actors include forbidden Find `k`; one has a JSON trailing comma. The q311 L2 round-1 Updater reaches `finish_reason=length`, spending 65,536 completion tokens on reasoning without usable output. That cell terminates, with no repair or retry. Updater validity is 371/372 and Reviewer validity 30/30. All 110 tools return without tool errors. There are no authentication failures.

**Scheduling deviation:** the frozen implementation coalesces Goal Review at the completed tool-batch boundary after sequential per-window Updates. It does not invoke Review after every individual window mutation. A resolved review stops before another Actor; a final review after decision three is allowed without a fourth Actor. Thus the cost/result comparison applies to this batched L2 variant, not literally to a per-window-review controller. Serialized changes, including incidental writes, trigger review. See [EXECUTION_NOTES.md](EXECUTION_NOTES.md). No post-result rerun was used to hide this limitation.

## Closure sensitivity and concrete cases

- **Strict all-clue closure:** L0/L1/L2 = 1/1/0. L2 q435 establishes the requested date-specific count but lacks every background-clue sentence. Its primary success is consistent with the predeclared discriminative-identity rubric; the strict result is reported separately.
- **Source-visible reconstruction:** 3/2/2 cells have enough support in observed source content. Correct/premature stops become 2/2, 2/3, 2/1. In q580, five seasons was already visible in initial Workspace W3, but was never committed into Claims. Calling these stops primary-premature is a state-closure finding, not evidence that the answer was unavailable to the Actor. q435 L0/L2 also have reconstructable count support at round 0 before the exact relation is retained.
- **q517:** role/director evidence accumulates, but the required Goat zodiac is unresolved against the 1978 birthday. L2 Reviewer declares closure anyway; Actor-only arms also stop early. Reviewer closure agreement is 29/30; this one false positive is consequential.
- **q311 L0:** acquires the Argentine title Cocomiel, TF1 and the director/two writers. It does not establish the character conjunction; runtime and season scopes remain unresolved. The four-minute runtime is present in Observation but omitted by the Updater. A title match is not counted as full closure.
- **q1094:** 95th-minute events and club-origin fragments produce useful candidate paths but no complete fixture identification. Provisional candidates are repeatedly replaced on weak partial clues.

## State quality and growth

503/504 admitted Claim sentences are literally source-supported (99.80%); 373/504 are atomic. However, **369/504 (73.21%) are incidental to the current goal**. Five sentences omit material qualifiers; one unsupported sentence generalizes a FUT game-clock fact to football. These categories can overlap. Source support measures observed-text entailment, not independent world truth, useful admission, or preserved temporal scope.

No unsupported full candidate-identification Claim is found. Hypothesis control still has errors: contradicted Hijitus is reintroduced; PSG timing contradictions are sometimes retained without rejection; two candidates are cleared using an unrelated match; four discriminating admissions are missed. Detailed reasons and overlapping flags are in `hypothesis_control_reviews.json` and `claim_reviews.json`. Candidate uncertainty is not automatically managed well just because it resides outside Claims.

Each arm starts with 22 total Claim sentences across ten seeds. Final totals: L0 249, L1 146, L2 175. Serialized semantic-state characters (Question + Claims + Hypothesis, excluding Workspace) are 32,263 / 22,099 / 24,302. Exact duplicate Claim strings are zero; this does not exclude paraphrased redundancy. Many source-supported unrelated facts accumulate.

Normalized identical action repeats are zero. Search nonetheless returns already-known documents in 93/246, 39/120 and 80/196 result items; all-known Search calls are 2/1/4. Different query wording does not guarantee a new path. These rediscovery counts alone do not establish irrational Search or stale-goal pursuit.

## Cost and cache

| Metric | L0 | L1 | L2 |
|---|---:|---:|---:|
| Model calls, all nodes | 186 | 105 | 181 |
| Input tokens, all nodes | 451,355 | 244,537 | 363,544 |
| Actor input tokens | 175,014 | 106,221 | 145,664 |
| Completion tokens, including reasoning | 944,684 | 710,240 | 1,034,160 |
| Total tokens | 1,396,039 | 954,777 | 1,397,704 |
| Cache hit tokens / input tokens | 219,520/451,355 | 125,824/244,537 | 177,664/363,544 |
| Weighted cache hit rate | 48.64% | 51.45% | 48.87% |

L2 Reviewer contributes 30 calls, 21,624 input and 99,112 total tokens. Trajectories diverge, so the whole-arm cost difference is not just Reviewer overhead. L1's lowest total cost is partly termination by failure and premature STOP. Tools per successful cell are 2/2/6, but compare different tasks and omit unsuccessful spend. Complete cost is retained in the table. No monetary price is inferred.

## Conclusion

The loop is executable after contract repair. L2 modestly improves stopping/progress counts in this diagnostic, without improving the planned-denominator resolution rate; strict closure and failure sensitivity weaken a claim of architectural superiority. There is no observed late research or unrelated goal drift to support declaring persistent Gap harmful. The strongest recurring semantic problem is selecting and retaining task-relevant, correctly scoped evidence, followed by reliable closure and candidate rejection. Neither extra Residual calls nor more Find/Open alone solves it.

All raw requests/responses, intermediate states, tool audits, failures, reviewer packets and costs are archived. `LOOP_ADJUDICATION.json` is the final cell review; its `_DRAFT` predecessor only records the interim review and is superseded.
