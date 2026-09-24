# F1 Research Frontier Control: result

The 24 paired cells span ten qids and 24 distinct, exact corpus windows. A single reviewer checked all 253 newly returned W against the frozen Claims, initial W and semantic Open Gaps. These were reconstructed one-W diagnostic prefixes from genuine historical Observations; they are not full historical runtime trajectories. All 48 Actor responses and all 24 A1 Selector responses were retained, including nine Actor responses that proposed two tools and therefore executed none under the one-action rule. There were no API timeouts.

| Measure | A0 all Gaps | A1 selected Gap |
| --- | ---: | ---: |
| Action yields new Useful Evidence | 15/24 | 16/24 |
| NoGain | 9/24 | 8/24 |
| Selected Frontier specifically advanced | n/a | 11/24 |
| Scope-correct action | 18/24 | 19/24 |
| Scattered query | 6/24 | 5/24 |
| Valid single tool action executed | 19/24 | 20/24 |
| Search / Find / Open actions | 18 / 1 / 0 | 19 / 1 / 0 |

Paired comparison: A1 alone gained in four cells across qids 177, 435 and 580; A0 alone gained in three cells across qids 1094, 311 and 580. Both gained in twelve, neither in five. Net useful-evidence improvement was **+1 pair**, with **three reverse worsenings**. A0 had twelve NoGain/scattered/scope-error diagnostic failures, so the pre-registered non-ceiling gate applies; A1 fails both the required net improvement of four and reverse-worsening maximum of one. The small NoGain reduction does not rescue the gate.

The Selector produced a valid open `gap_id` in 24/24 calls and matched the reviewer's preferred diagnostic Gap in 16/24. Five A1 actions gained only outside their selected Frontier. For example, a query for a May Forbes album count instead returned Mtukudzi biography facts; a query for a tied-points table instead returned the 13-player signing article. The selected Gap can be sensible while source routing and localization remain poor. Conversely, at the Peter Nzioki biography checkpoint, A0's `find(D1, ...)` exposed the exact 2005 filmography role while A1 searched director background; the latter supplied a useful film-identity prerequisite but did not obtain the role.

There were 24 extra Selector calls. Provider-reported model usage was 163,708 total tokens for A0 Actor, versus 115,047 Selector plus 78,428 A1 Actor tokens (193,475 total), a 29,767-token increase. Reported prompt-cache hit fractions were 50.79% for A0 Actor, 5.91% for A1 Selector and 54.39% for A1 Actor. Sums of model-call latencies were 554.81 seconds for A0 and 628.01 seconds for A1 Selector plus Actor. These are sums, not elapsed wall time or a price estimate. Nine two-tool Actor outputs were counted as failures without repair (five A0, four A1), showing an action-format bottleneck that a Gap ID alone did not solve.

**Decision:** explicit Research Frontier is feasible as a single `gap_id`, but this diagnostic does not justify an extra Selector call or a multi-Gap runtime. The strongest remaining weakness is choosing a useful source and local passage, not merely selecting a semantic Gap. The one-W reconstructed prefixes, correlated qids, source-date oddities in the corpus and single-reviewer labels limit generalization. Removing a borderline partial-evidence label such as the director/Iracema clue can only weaken A1 and does not reverse the gate result.
