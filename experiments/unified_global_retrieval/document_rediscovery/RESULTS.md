# U1 Document Rediscovery results

## Execution and fidelity

The bank and all private truth were committed before calls. Forty independent Query Writer requests to DeepSeek `deepseek-flash` returned parseable two-field JSON; there were no API/format failures, retries or query rewrites. Its response-reported prompt cache was 4,736 hit tokens and 10,659 miss tokens, a weighted 30.76% hit rate. `QUERIES.json` was separately committed before retrieval.

The first retriever initialization failed before any Search because GPU 1 ran out of memory; `initialization_failure.json` preserves it. The same frozen Qwen3 model, FAISS index and queries then ran on CPU. This uses the backend's CPU float32 path rather than its GPU float16 path, so small rank differences relative to a future GPU run are possible. G and H used the same CPU query vector and IP scoring. All 40 paired retrievals completed without query/tool failure. CPU retrieval latency was 78.30 seconds summed over cells, median 1.92 seconds per cell; H reused each G embedding. No Find was called.

## Frozen primary metrics

| Measure | G full corpus | H one observed historical document |
|---|---:|---:|
| Sufficient D Recall@1 | 23/40 = 57.5% | 20/40 = 50.0% |
| Recall@3 | 32/40 = 80.0% | 20/40 = 50.0% |
| Recall@5 | 35/40 = 87.5% | 20/40 = 50.0% |
| MRR@5 | 0.6854 | 0.5000 |
| A/B old sufficient D @5 | 19/20 = 95.0% | 20/20 = 100% |
| C/D new sufficient D @5 | 16/20 = 80.0% | 0/20 by construction |

G type counts at @1/@3/@5: A 8/9/11 of 12; B 5/7/8 of 8; C 5/9/9 of 12; D 5/7/7 of 8. In D, a sufficient new document ranked before the old misleading document (or the old document was absent from top five) in 7/8 cells. D01, q435, was the exception: old retrospective rank 3, no sufficient Forbes source in top five. The 200 G top-five positions contained 26 historically seen and 174 unseen documents. Every qid had at least one hit; q186 was weakest at 1/3, q435 6/8 and q1094 2/3.

The five primary misses were A11/q186, C09/q186, C01/q435, D01/q435 and C12/q1094. [SOURCE_AUDIT.md](SOURCE_AUDIT.md) records their independent top-five source review. An alternative new source answers A11's publisher Gap, yielding exploratory any-sufficient recall 36/40; it does not restore the old D or alter new-source recall. The primary frozen metric remains 35/40.

## Gate and interpretation

The old-source threshold passed (95% ≥90%). New-source discovery failed (80% <85%). Overall Recall@5 also missed narrowly (87.5% <88%). H's 100% A/B recall is largely built into the one-document historical candidate set, so it cannot establish a deployed history-prior benefit. U1b's trigger requires G old-source recall below 90%; it was not met. U2 and U3 are barred by the U1 gate.

The old source was rediscovered at rank 1 for q387's 5TB fact and q517's Peter King role document. That demonstrates document routing only: neither 5TB nor the filmography role was reacquired as a W because Find was not run. q435 showed query-sensitive source competition: list-inclusion D02 retrieved a Forbes document at rank 1, while album-count D01 ranked the old retrospective at 3 and missed the Forbes documents. q177 escaped its signing article in all three D cells. The q546 cells tested professional-year and related document facts, not the hard multi-match sequence; they do not identify the prior q546 bottleneck.

These 40 cells cover ten qids and only 19 distinct primary target documents. Some diagnostic Gaps test auxiliary facts rather than the original answer constraint, and a few answer clues are already explicit in the raw Question (for example age 66, thirteen signings and 8×11 paper). The one-window reconstructed checkpoints also make H unusually easy. Accordingly these are diagnostic rates, not independent population estimates or evidence of full task success. Five missed top-five sets support retrieval failure at fixed k, but without a permitted query rewrite or larger-k search the design cannot separate query wording from embedding/index ranking or determine exact rank beyond five.
