# Post-T3 integrity audit of the frozen transition bank

This audit was triggered by reading the T3 proposals against each **original question** and the full, already frozen T0 observation. It is separate from, and does not modify, the T0 source sets or any T1–T3 query/output. The protocol requires a Bridge observation to withhold the original final target answer and to support a decision-changing claim. Several T0 entries instead chose a new downstream Gap after the original answer was already visible. Query metrics on those entries cannot establish research feedback toward the original question.

| Case | Original target | Integrity finding | Hard exclusion |
|---|---|---|---|
| U1_B01 | Actor's popular name | Observation states “popularly known as Peter King,” the requested name. | yes |
| U1_B03 | May 2017 album count | Observation says “more than 60” and no exact May 2017 count. It supports age and broad career, but not every distinctive song/interview clue. Binding remains provisional. | no, provisional |
| U1_B04 | Free-kick player | Match article names Messi as the 95th-minute free-kick taker, the requested player. | yes |
| U1_B05 | Argentinian release name of the described programme | Hijitus source contradicts the original network, date, and writer-count clues; the oracle candidate was wrong. T3 correctly proposes exclusion. | yes |
| U1_B06 | Game name | Observation's title and first line state Galacta: The Battle for Saturn, the requested game. | yes |
| U1_B07 | Individual's birth name | Heart Evangelista source conflicts with the question's career timing and wealth clues. The candidate was unsupported. | yes |
| U1_C01 | May 2017 album count | Same partial Oliver Mtukudzi observation as B03; no exact requested count. | no, provisional |
| U1_C03 | May 2017 album count | Same partial Oliver Mtukudzi observation as B03; no exact requested count. | no, provisional |
| U1_C05 | Club founding year and country | Rangers observation supplies the 13-player clue and league identity, not the requested founding facts. Other original season constraints remain unchecked. | no, provisional |
| U1_C06 | Series name | Observation URL is `youretheworst.fandom.com`, which reveals the requested series. | yes |
| U1_C07 | Series name | Same answer-revealing URL as C06. | yes |
| U1_C11 | Player name | Observation names Ding Junhui, the requested player. | yes |

Eight of 12 transitions have an unambiguous original-answer leak or a contradicted oracle candidate (66.7%). At most four transitions across two qids remain provisionally interpretable, below the frozen Execution Gate of eight cases across five qids. The three Mtukudzi observations also do not verify every original clue, so four is an **upper bound**, not a newly certified clean cohort.

T1/T2 quantitative results remain valid as *conditional next-Gap retrieval diagnostics* because their requests and frozen source sets were real. Their earlier “clean excluding B07” cohort is not a valid cohort for the full original-question feedback hypothesis. T3 is retained as a source-support diagnostic. T4 and T5 depend on a sound T0 bank, so their model calls are stopped under the expressly allowed severe-integrity exception. The already written T4/T5 preparation code is unused and no rollouts or fabricated observations are produced.
