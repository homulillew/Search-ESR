# Q1 complementary query robustness

K0's Single Query@10 gate failed, so all 40 frozen inputs received one DeepSeek `deepseek-flash` Query2 call. All 40 returned schema-valid queries, with zero retries or repairs. The calls and outputs were committed before any Query2 retrieval. DeepSeek reported 7,424 prompt-cache-hit tokens and 11,427 prompt-cache-miss tokens, an aggregate token hit rate of **39.4%**.

| Arm | Overall candidate recall | A/B | C/D | Fused top5 |
|---|---:|---:|---:|---:|
| S10: Query1 top10 | 36/40 | 19/20 | 17/20 | n/a |
| D5+5: Query1 top5 + Query2 top5 | 36/40 | 19/20 | 17/20 | 34/40 (18/20 A/B; 16/20 C/D) |

The mean Jaccard overlap of the two top5 sets is 0.513. There is **one** frozen-target rescue, U1_C01 q435, and **one** regression, U1_D01 q435: paired net rescue is zero. Q1 rescues the Forbes album-count source for C01 at Query2 rank5 (D51535), but the source sits outside the RRF top5. For D01, the formerly rank6 sufficient source is excluded by both top5 lists. No other previously missed qid is rescued: q186 remains 1/3 and q1094 remains 2/3; q435 remains 7/8. The remaining seven qids are unchanged and fully covered by both arms. The full per-qid counts are in `summary.json`.

D5+5 misses its frozen deployment gate: 17/20 C/D <18/20, 36/40 overall <37/40, and net paired rescue 0 <2. The additional Search is not selected. This comparison holds the candidate inspection budget to at most ten unique documents, so the null net gain cannot be attributed to inspecting fewer candidates. Query2 diversified some candidate sets but did not reliably improve sufficient-document ranking; in the only rescue, RRF top5 would still hide the target. Q1's q186 A11 query also retained most of the original conjunction, and q1094 C12 used a French formulation; these are descriptive observations from frozen outputs, not grounds for output filtering.
