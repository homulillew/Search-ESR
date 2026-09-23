# M1 result: gate passes

All 82 predeclared arm cells completed. W had one schema/parse error (`T2_1094`) retained as a failed cell; N had none. W triggered 39 verifier responses and N triggered 41. No retries were made.

| Measure | Wide Delta + triggered Verify (W) | Narrow Router + authoritative Verifier (N) |
| --- | ---: | ---: |
| Final mutation precision | 35/54 = 64.8% | 38/39 = 97.4% |
| Final mutation recall | 35/38 = 92.1% | 38/38 = 100% |
| Cases with unrelated churn | 11/41 | 1/41 |
| New Claims | 16 | 0 |
| T4 NoGain preservation | 8/8 | 8/8 |
| At-risk false closure | 0/17 | 1/17 |

N routing precision was 35/41 = 85.4% and recall was 35/35 = 100%. Paired unrelated churn improved in 11 cases, worsened in 0, and tied in 30. All six preregistered M1 conditions pass. Excluding both repaired qid-186 cases, N precision remains 33/34 = 97.1% and recall 33/33 = 100%.

The N false closure is `T3_435:C2`, a meta statement that the candidate's album total and article clues “remain unverified.” The verifier treated partial article clues as refuting the whole statement despite explicitly noting the exact album total was still missing. This is a real `SV2-6` over-interpretation under frozen scoring, and also exposes poor Claim admission wording in the inherited state. N additionally routed six Claims whose status did not need to change, mostly partial matches to broader conjunctions. The verifier kept those Claims open in five cases; the sixth is this false closure.

In `T7_186`, N routed both the release-year Claim and the malformed credit instruction. Its verifier returned `open` for the 1993 release-year Claim because W1 and W2 conflicted and identity equivalence remained uncertain. The harness committed `supported → open` and reopened G1. W rejected its proposed conflicting transition and retained the old supported status. The qid-186 credit Claims are routing-positive but status-unscorable under the frozen label repair; neither historical packet was rewritten.

DeepSeek reported weighted cache hit rates of 81.3% for W updater calls, 66.2% for W verifier calls, 2.0% for N router calls, and 8.0% for N verifier calls. Different prompt shapes and call order affect caching; these rates are operational telemetry, not outcome evidence. The 41 cells include correlated sibling packets from 12 qids and reviewer-authored prior states, so the gate is a mechanism diagnostic rather than a population estimate.
