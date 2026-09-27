# H1: repaired contract continuation

## Verdict

**Interface gate passed with one retained non-H model-output failure.** Eleven of
twelve trajectories reached the three-slot horizon. All 22 H proposals passed the
repaired contracts; five H calls were mechanically skipped. No new C corruption,
false READY, or replay/integrity failure was found. H2 is allowed by the frozen
gate; this is not a claim that H semantics or end-to-end recovery are reliable.

The single failure was R3_Q538__rep2, slot 1: Closure echoed a `oneOf` schema
wrapper around CONTINUE. It was rejected without mutation, repair or retry. The
high-authority failure boundary remains conservative. All failures are retained.

## Results

| Measure | H1 |
|---|---:|
| Trajectories / completed three slots | 12 / 11 |
| Paid requests / H requests / H skips | 93 / 22 / 5 |
| Namespace or source-nomination violations | 0 / 22 |
| New supported C / all new C | 14 / 14 |
| C useful to the current gap | 12 / 14 |
| Accepted CONTINUE / READY | 6 / 0 |
| Forced R1 NoGain followed by next Actor | 4 / 4 |
| R1 trajectories obtaining new supported C | 1 / 4 |
| Forced R3 valid CONTINUE followed by acquisition | 3 / 3 (4 forced) |
| R3 trajectories obtaining new gap-useful C | 1 / 4 |
| Compatible inspections / all inspections | 15 / 16 |
| Inspections yielding new raw evidence for current Need | 4 / 16 |
| Free acquisitions with premise hardening | 3 / 23 |

Both q637 trajectories DEPRIORITIZE SPS rather than REJECT it from local FOP
evidence. No REJECT operation occurred anywhere. Both q228 trajectories committed
the supported Ding childlessness claim and continued. R1 paths changed after
NoGain, but changes mostly did not produce grounded progress. q922 obtained the
North Transylvania statement in one replica while the other continued seeking
the unbound delivering-officer relation.

## What this does and does not establish

H1 has **zero live H failures**, so the live failure-isolation denominator is
zero, not a 100% success rate. The separate offline replay remains the evidence
that the original twelve invalid H outputs preserve C/Gain and allow the next
Actor. Old 12/14 invalid H versus new 0/22 is descriptive: these reused questions
informed the repair and the trajectories differ after the first decision.

H remains semantically weak. Examples include unsupported Pirlo/minute guesses,
promotion of partial match/team evidence into a global fixture hypothesis, an
irrelevant snooker candidate after a darts/scope mismatch, source-year conflict
not acknowledged for a gift candidate, and substituting a coup for accession.
These stayed outside C; they still distorted control. Eleven of nineteen runtime
Gain steps had no new C. H churn/source nomination must not be scored as semantic
recovery. Inspecting a plausible document is also insufficient: 4/16 inspections
yielded new raw evidence for their current Need.

Single-reviewer, unblinded, source-relative labels are in
`analysis/SEMANTIC_REVIEW.json`; all new claims, H updates, accepted Closure outputs
and acquisition steps are covered. Three decisions per trajectory do not measure
final accuracy. H2 will use archived questions excluded from H repair/H1, without
claiming the historical bank is a globally untouched benchmark.

## Cost and integrity

93 requests, all HTTP 200 and finish=stop; one schema failure (1/93), zero retries,
zero replacements. Peak concurrency 12, no reduction, wall time 300.03 seconds.
Input 221,093; output 355,504; total 576,597 tokens. Hit 66,046, miss 155,047;
cache hit rate **29.8725%**. All 93 usage records are complete and consistent.
Latency p50 11.31 s, p95 55.82 s, maximum 85.26 s. All twelve traces replay to
their stored final state. Historical micro_recovery/run001 and h_fix are unchanged.

The repair removed an interface obstacle. Reliable recovery from weak control
hypotheses remains an empirical question; unchanged H2 is the next bounded test.
