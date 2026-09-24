# F1 Gap-conditioned Finding extraction

The pre-call bank contained 41 exact historical W excerpts across 12 qids,
all eight E1–E8 types, 32 required semantic atoms, eight E6 NoGain cells and
four controlled duplicate-evidence cells. All 123 DeepSeek `deepseek-flash`
calls succeeded, used one response per cell and had no schema failures. The
single reviewer scored 194 arm-masked Finding statements against the exact W,
semantic Gap and pre-call labels. No full source, future trajectory or gold
answer was used. `REVIEWS.json` contains individual reasons.

| Metric | A: Q+W | B: Q+Gap+W | C: Q+Gap+Claims+W |
|---|---:|---:|---:|
| Finding count | 110 | 46 | 38 |
| Precision | 43/110 (39.1%) | 45/46 (97.8%) | 38/38 (100%) |
| Required finding recall | 28/32 (87.5%) | 30/32 (93.8%) | 29/32 (90.6%) |
| Unsupported inference | 0/110 | 0/46 | 0/38 |
| Gap-irrelevant facts | 67/110 | 1/46 | 0/38 |
| E6 NoGain silence | 2/8 | 8/8 | 8/8 |
| Duplicate error cases | 4 | 4 | 0 |
| Mean Findings / case | 2.68 | 1.12 | 0.93 |

B eliminated Gap-irrelevant output in 31 paired cases where A emitted it,
with no reverse cases; C did so in 32. C eliminated all four B duplicate
case errors, with no reverse cases. All five absolute C thresholds and both
triggered comparative thresholds passed. Weighted reported prompt-cache hit
rates were A 33.9%, B 37.2%, C 36.8%.

The clear mechanism is *selection*: A often extracted true facts about the
right entity or a wholly unrelated retrieved page; B/C usually stayed with
the active semantic Gap. The source snippets and short explicit prompts were
easy enough that no observed arm hallucinated an unsupported relation. C's
recall was one atom below B's, so Claims context helped duplication at a
small coverage cost here. These correlated sibling cases and single-reviewer
labels are a bounded diagnostic, not a general accuracy estimate. F1 passing
permits F2, but does not by itself validate persistent Claim admission.
