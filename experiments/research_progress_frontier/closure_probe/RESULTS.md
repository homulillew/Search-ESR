# Stage A: Evidence → Closure

The case bank and rubric were committed at `87be8d7` before the freeze and any new call. The frozen request used DeepSeek `deepseek-flash`, the verified provider profile, no tools, one response per case and zero SDK retries. `gate.txt` passes all seven source/provider/request checks. All 29 requests returned responses; no provider errors or invalid status fields occurred.

| Reviewer label | Correct | Cases |
| --- | ---: | ---: |
| supported | 13 | 13 |
| refuted | 8 | 8 |
| open | 8 | 8 |
| **Overall** | **29** | **29** |

False close was **0/8** reviewer-open cases. Missed closure was **0/21** reviewer-closed cases. The five stale-gap *subclaims* were recognized as supported **5/5**; excluding the one medium-ambiguity stale-action case gives **4/4**. Every model-cited ref was among the exact currently visible refs. The prespecified practical gate passes all three conditions: overall ≥80%, false-close ≤10%, stale closure ≥4/5.

The model correctly kept conjunctions open in the reviewed responses: Ding's single 4-3 opening win did not close the later match chain, and PSG–Lille's 95th-minute kick plus a separate Inter split did not establish the required joint fixture. In the latter explanation, the phrase “goal chronology” slightly overstates what W38 alone proves; the status and identified missing club-history link remain correct. There was no false close under the frozen label rubric.

This is a local semantic capability diagnostic, not a population estimate. Eight qids supplied multiple supported/refuted/open siblings from the same windows, and two stale cases repeat the Rangers 13-player fact at different historical checkpoints. Several refutations deliberately negate an explicit sentence. These make the test easier and reduce effective independent evidence diversity. `stale_1034_model` is medium ambiguity as an *action-redundancy* diagnosis because the repeated query also contains unresolved clues; its closure label itself is clear. No gold answer or later source result was used for labels.

DeepSeek reported prompt-cache usage for all 29 responses: 0 hit and 17,837 miss tokens, weighted hit rate **0%**. This describes short, varied Stage A requests and is unrelated to closure accuracy. The gate result authorizes a separate frozen Stage B Frontier diagnostic, with no claim that a runtime Progress State is ready.
