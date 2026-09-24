# Ephemeral policy / persistent state boundary: final conclusion

**Decision.** A speculative Search term is an action hypothesis, not evidence.
S1 shows mixed retrieval effects. In the controlled S2 sample, an explicit
query-as-action-history instruction already kept L clean; I and X performed
identically, so the preregistered improvement gate failed. Stop before S3
and S4. The clean result is bounded to 40 easy-to-inspect historical W slot
challenges, not a proof of full runtime state safety.

## Required answers

| # | Question | Result |
|---:|---|---|
| 1 | Does query-level speculation help actual retrieval? | Mixed: one unique direct scene resolution, many ties, and some worse source retrieval. The 48 original queries yielded 3/16, 5/16, 4/16 useful-evidence results in Q0/Q1/Q2. |
| 2 | What does mechanical deletion change? | Across 23 pairs, suitable source favored S 1, D 2, with 20 ties; useful evidence S 1, D 3, with 19 ties. Direct unknown resolution S 1, D 0. |
| 3 | How often was the guessed value supported? | 5/23 speculative exact values were supported in the required relation by top-five previews (21.7%). Mere mention did not count. |
| 4 | Does L copy query guesses more? | No observed excess. L, I, X each proposed the guessed value in 9/40 cases; all nine were also supported by W. I/X never saw query history. |
| 5 | Does query-blind Binder reduce bad proposals? | Not in this bank: L/I/X each made zero false proposals. |
| 6 | Does extractive gating further reduce promotion? | No measurable difference: X rejected zero values mechanically, and all arms had zero false commits. |
| 7 | Is the semantic Verifier necessary? | Unresolved empirically here. It saw 72 correct proposals and rejected none; this bank cannot estimate its protection against an incorrect literal mention. |
| 8 | Were incidental mentions bound incorrectly? | No: the five P2 relation traps produced no commits in any arm. |
| 9 | Can query X, observation Y recover Y? | Yes in this controlled bank: all three arms committed the W-supported Y in 11/11 P5 cases. |
| 10 | Does NoGain leave state unknown? | Yes in the seven P4 cases, all arms made no commit (7/7). |
| 11 | Can conflict evidence replace an old binding? | Yes for the four seeded conflicts, all arms replaced X with W-supported Y (4/4). These old bindings were experimental seeds, not reconstructed verified history. |
| 12 | Does visible query history repeat a guess after NoGain? | Not measured. S3 was prohibited by the S2 gate. |
| 13 | Is an explicit ephemeral label enough? | Not measured; S3 did not run. |
| 14 | Is context projection needed? | Not established; S3 did not run. The I/X boundary audit shows query fields can be omitted from persistence input. |
| 15 | Does the harness improve useful evidence per retrieval? | Not measured causally; S4 did not run. S1 measured one-step Search previews only. |
| 16 | Does it lower unsupported persistent bindings? | No relative reduction observed in S2 because L was already at zero; S4 runtime unmeasured. |
| 17 | Does it improve NoGain recovery? | Persistent unknown preservation was 7/7 in S2; next-action recovery was not measured. |
| 18 | Is speculation useful, harmless, or a candidate lock in real Search? | All three patterns occurred descriptively: series-specific wording resolved a scene, most pairs tied, and candidate-specific wording sometimes displaced a useful Forbes source. |
| 19 | What is the best-supported bottleneck? | The observed shortfall is retrieval/source selection: original useful-evidence rates were 3–5/16 per arm, while these controlled binding packets were clean. The data do not isolate query policy from source routing or diagnose localizer, frontier, or context expiry. |
| 20 | Enter a longer ESR runtime? | Not on this evidence; the specified S2 comparative gate failed and no short rollout exists. |
| 21 | Enter ESR-GRPO? | No. No validated runtime gain or reliable reward signal was established here. |
| 22 | Hard Search/Find/Open gating? | Still unsupported and prohibited; no hard masks were tested. |

## Interpretation and limits

S1 used the unchanged local BC+ backend, k=5, one run per query, no Search
errors. Its 71 arm-masked top-five reviews are single-reviewer judgments over
eight correlated qids; some previews show a plausible source without giving
the required answer. For example, a Forbes-related article mentioning 65
albums did not prove that the May Forbes feature reported 65. The review
never used later trajectories or a full-document source audit.

S2 used exact historical Observation text from 40 transitions across 11 qids,
but its TestCards and previous query strings were controlled challenges.
The 24 positive slots all had short literal values in W, and 16 negative
slots were clear relation or NoGain traps. This may be too easy to expose a
difference between treatments. All three prompts explicitly warned that
query history is not evidence; L obeyed that warning. The paired criterion
required at least six reductions, but X had zero improvements and zero
worsenings. The Verifier was query-blind in every arm, so this comparison
isolates Binder input more than the whole state pipeline.

The strongest validated boundary rule is semantic and structural: action
arguments never acquire evidence status from having been issued. Exact new
Observation text, slot relation, and verification are the intended path to
persistent TestCard bindings. This experiment establishes that the boundary
can be enforced in the 80 I/X requests, while it does not establish that it
improves behavior over a cautious L prompt in this bank. A longer runtime,
context expiry policy, and hard action masks remain outside the evidence.

See [S1 results](speculation_utility/RESULTS.md), [S2 results](persistence_boundary/RESULTS.md),
the two stage `freeze.json` files, and the append-only event traces for all
requests, responses, reviewed decisions, and failure accounting.
