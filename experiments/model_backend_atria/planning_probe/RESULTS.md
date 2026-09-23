# M1 same-prefix explicit planning results

Freeze: `freeze.json`; raw attempts and provider responses: `events.jsonl`;
pre-registered rules: `EVALUATION_RULES.json`; deterministic accounting:
`mechanical_summary.json`; single-reviewer diagnostic semantic judgments:
`semantic_scores.json`. Each of 13 checkpoints was attempted once per model
with identical prefix messages and diagnostic instruction, without an
executable tool menu. All 13 annotation rows are marked high ambiguity.

| Measure | qwen3.7-flash | Atria-Dawn-Preview |
|---|---:|---:|
| API responses / attempts | 10/13 | 13/13 |
| Need agreement / responses | 5/10 | 11/13 |
| Source-type agreement / responses | 7/10 | 12/13 |
| Parsed, acceptable scope / attempts | 5/13 | 12/13 |
| Document plans | 4 | 4 |
| Plausible D# among document plans | 1/4 | 2/4 |
| Over-search / premature-local intent | 0 / 0 | 0 / 0 |

Qwen timed out at 546:25, 1094:34 and 1094:45, under its frozen 180-second
SDK timeout. Two other Qwen responses (546:33, 1094:69) emitted `tool_calls`
with no diagnostic content despite the no-tool request; no tool was run.
1094:93 returned only `Lionel Messi`, without requested fields. Atria
546:25 returned empty content with `finish_reason=stop`. These are
provider/interface or instruction-adherence outcomes, not valid evidence
that a model reasoned incorrectly about scope. Errors remain in the attempt
denominator for the pre-registered mechanical measure; semantic fields are
null for the three requests with no response.

Across all 13 pairs, Atria alone has an acceptable parsed scope in 7 cells;
Qwen alone in 0 (exact two-sided McNemar p=0.015625). **Five of those seven
Atria-only cells have no parsed Qwen scope**, including two timeouts and two
unexpected tool-call responses. Restricting to the seven pairs where both
returned a parsed scope gives Atria 7/7 and Qwen 5/7: the two differences are
1094:61 and 1094:77, where Qwen proposed `stop` despite explicitly naming
unresolved match/team evidence, while Atria proposed `corpus` (exact McNemar
p=0.5 on these complete pairs). Thus the nominal strong scope threshold is
met as an all-attempt/interface result, but it does not establish a clean
model-reasoning improvement of 4/13.

The source-type difference is similarly dominated by missing or malformed
Qwen outputs. In parsed, paired cases both usually name relevant source
classes. Neither model shows a decisive local-routing gain: each proposed
`document` four times; Qwen supplied an annotated plausible D# once, Atria
twice. At 546:17, Atria chose D5 (player biography) while the reviewed local
result lead was D11; at 1094:93 it chose D11, a video placeholder, while
D34/D37 were the focused prefix-visible sources. Qwen document plans at
546:9/17/41 omitted a D# target. On 1094:53 Qwen proposed D34 while Atria
continued corpus search. The broad multi-scope annotations make
`over_search` and `premature_local` zero by construction in this cohort;
these metrics cannot resolve relative search persistence here.

**M1 decision:** mixed, with a clear provider/format-availability advantage
for Atria and a narrower semantic difference around premature `stop` in two
1094 prefixes. Proceed to the pre-registered M2 natural-action probe on all
13 checkpoints: the three requested selection strata are not all populated.
M3 remains conditional on whether M2 shows a substantive policy difference.
