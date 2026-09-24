# E1 Complete Evidence Packet result

The pre-call freeze is `freeze.json`; 44 historical observations cover 12 qids. Case mix: M1 26, M2 1, M3 2, M4 15. DeepSeek `deepseek-flash` produced 88 valid single responses, with zero retries, errors, or repaired outputs. T and P used the same system prompt; only P received D, title, and URL. Exact requests and responses are in `events.jsonl`, with semantic judgments in `REVIEWS.json`.

| Measure | T text only | P full packet |
|---|---:|---:|
| Complete source support | 40/40 | 46/46 |
| Frozen support **and** Gap relevance precision | 40/40 | 42/46 = 91.3% |
| Required Finding recall | 33/37 = 89.2% | 35/37 = 94.6% |
| M2 source identity | 0/1 | 1/1 |
| M3 temporal/source binding | 0/2 | 2/2 |
| Metadata overreach | 0/40 | 0/46 |

The three M2/M3 pairs improve with P and none reverse. T has only three such clear errors, below the frozen five-error superiority trigger. This is a useful mechanism signal with very small category denominators, not a population-level estimate.

Four P findings were fully source-supported but not new and material to the current Gap: an AC Milan split fact while checking PSG/Lille, an unrelated song title while checking a television program, and two details about Ding's opening match after that result was already committed. These are marked per finding in `REVIEWS.json`. P also omitted the word *shareware* in one required Galacta finding and omitted the retrospective 67-albums partial clue in one case.

The task text defines Finding Precision as source support and separately lists Gap Relevance. Our pre-call local rubric deliberately combined both in the frozen precision gate. Under the task's support-only definition, the P absolute thresholds pass. Under the binding local frozen rubric, 42/46 is below 95%, so **E1 gate fails**. This stricter criterion is a design choice that should have been made explicit before freezing; it cannot be changed after seeing responses. The failure demonstrates a relevance/novelty risk from the fuller packet, but does not show that its facts are unsupported. Later stages remain unrun per the frozen stage order.

DeepSeek reported 14,208 prompt cache-hit tokens and 56,813 prompt cache-miss tokens across 88 calls (20.0% hit share of those two fields). This is provider telemetry, not a performance metric.
