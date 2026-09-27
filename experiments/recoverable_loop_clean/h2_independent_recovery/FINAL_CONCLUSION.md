# H2 — recovery works locally; authoritative support gate fails

## Decision

**Do not expand the experiment.** Repaired H contracts execute correctly and the
loop continues after real NoGain and Closure veto. But one unsupported temporal
relation crossed Reader and Grounding into C. The factual boundary required for
clean recovery is not yet established. H2 does not pass the no-authoritative-error
criterion, despite positive control-continuation signals.

This cohort has eleven archived prefixes held out from the H repair questions,
one replica each, at most three decisions. Twelve were mechanically preselected;
R2_Q311 lacked an initial H and was excluded without replacement. Whole-Q R and
the archived cohort differ from H1; H1/H2 comparisons are descriptive, not causal.

## Outcomes

| Measure | H2 |
|---|---:|
| Trajectories | 11 (R1=4, R2=3, R3=4) |
| Horizon / READY-finalized / failed | 9 / 1 / 1 |
| H proposals / contract failures / skips | 22 / 0 / 2 |
| New C / source-supported C | 12 / 11 |
| New C useful to current gap | 8 / 12 |
| CONTINUE / READY / unsupported READY | 4 / 1 / 0 |
| Mechanical integrity/replay failures | 0 |
| Unsupported temporal C promotion | 1 |
| Compatible inspections | 12 / 12 |
| Inspections with new raw support for current Need | 1 / 12 |
| Premise hardening in free acquisitions | 2 / 20 |

Source compatibility here means a reasonable document to inspect. It does not
certify that the selected window resolves the gap. For example, the paper and
biography were appropriate sources but localization returned detector simulations
or disputed poem attribution. An expanded W with a new ID can repeat already seen
information: q261's title/authors were already in W10, so its new C is useful but
does not count as new raw evidence. No statistical precision improvement claim.

### R1: NoGain recovery

Three of four forced repeats actually produced NoGain. All three then reached a
free Actor acquisition and changed from Search to Find. By horizon, q261 obtained
a useful title/author C and q601 discovered a footballer/business-partnership C:
**2/3 realized NoGain trajectories**, or **2/4 all forced-repeat trajectories**.
q264 stayed in the wrong part of the right paper and obtained no C. q169's empty-
basis H ADD produced Gain without a new observation, so it is excluded from the
NoGain denominator. More control activity alone is not recovery.

### R2: weak H validation; wrong-H recovery remains untested

- q177 retained Rangers, repeatedly inspected a complete old article, then found
  real founding/history facts. The target season/capital/trophy conjunction remains
  unbound. Its seven/eight league-title totals do not establish fifteen trophies.
- q186 searched the missing company-name history, grounded it, received a
  source-supported READY, and finalized the game name. The Closure input contains
  the release/credits metadata, developed-by relation and former-company name.
  This is candidate confirmation from local evidence, not recovery from wrong H
  and not a gold-scored accuracy result. A1993 alternative source was retained in
  low-authority H; it did not replace the supported November1992 C.
- q387's first Actor echoed the JSON-schema `oneOf` wrapper and was rejected.
  Its raw output and failure remain; no unwrapping, retry or replacement occurred.

No R2 seed was pre-labeled as provably wrong and no evaluable direct contradiction
was produced. The wrong-H recovery denominator is **zero**, not a failure rate or
a successful recovery estimate.

### R3: veto recovery with one factual failure

All four incomplete seeds correctly received CONTINUE. All four subsequent Actors
acquired evidence for a named missing condition. Three eventually obtained a
gap-useful supported C (q435, q517, q633); q673 extracted a true but already visible
poem-attribution fact unrelated to the remaining biographical requirements.

q435 also admitted unsupported C5: retrospective67albums was promoted into
67albums-by-the2016-interview. Earlier Closure explicitly left that relation open;
the following Open added no disambiguating temporal support. Reader proposed the
stronger relation and Grounding accepted textual adjacency as evidence. Later H
shifted to a2017 lead without removing C5. See `FAILURE_CASE_Q435.md`.

This is a source-relative unsupported assertion, not an independently proved false
count. If a reviewer reads the source's adjacency more permissively, the numerical
false-C count is sensitive to that interpretation. The strict epistemic gate
still cannot be declared robustly passed without resolving this support boundary.

## H after the repair

No namespace/nomination failure in22 calls; all H transactions retained the
intended authority boundary. Zero live H failures means live failure-isolation
rate is undefined. Offline replay of the original twelve bad outputs remains the
evidence for continuation after failure; we did not inject new paid failures.

H semantics remain fallible: q601 treats professional-club history as academy
support; q633 asserts only-one-in-era beyond the observed publisher blurb and
earlier nominates an obviously mismatched2009/200page book; q517 changes from Peter
King to Peter Nzioki even though seed C equates them. No global REJECT occurred.
Six of sixteen Gain steps had no new C; nine had no supported gap-useful C.
These counts cannot serve as a recovery metric.

## Accounting and integrity

81 attempted requests,0 not-sent,1 model schema failure (1/81),0 HTTP/provider
failures. Actor22, Reader19, Grounding12, H22, Closure5, Final1. Peak concurrency11,
unchanged throughout; no retries/replacements. Wall time133.61s including local
model loading; p50 latency7.88s, p95 29.52s, maximum42.14s.

Input185,076; output179,815; total364,891 tokens. Hit42,112/miss142,964;
cache hit rate **22.7539%**. All81 usage records complete and consistent. Twenty-
four tool acquisitions remain below29; calls remain below174. Same user isolation
and backend; serialized GPU0 retrieval overlapped with independent API requests.

All eleven traces replay exactly. Historical micro_recovery/run001, h_fix and
runtime/tool code remain unchanged. The semantic C failure is retained even
though its mechanical trace is valid. All calls ran at frozen commit1c8d189f.
146 offline tests passed. Post-run annotation code initially assumed READY had the
same event shape as CONTINUE; it was corrected to read its nested result before
any review file was emitted. No live output was changed.

## Next priority

Preserve the H repair. Prioritize source-relative temporal/relation support in
Reader/Grounding, followed by bounded diagnosis of local-window navigation and
schema-wrapper output failures. Do not add state fields or hard gating and do not
expand recovery samples now. A correct source route helps only when the resulting
claim preserves the scope and time relation actually supported by observation.
