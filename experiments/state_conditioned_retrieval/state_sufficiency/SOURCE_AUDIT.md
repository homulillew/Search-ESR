# Post-retrieval source-truth audit (exploratory)

The frozen sufficient-document sets remain unchanged in every primary score. This audit checks whether a canonical miss was nevertheless a useful source. It is post-retrieval and cannot be used to relabel the registered metric.

## U1_B06 / q186: canonical truth was too narrow

S0 ranked frozen sufficient document D39978 at 13. At rank 3 it retrieved D51927, the `classicdosgames.com/game/Galacta.html` page. That page explicitly lists `Episode 2: Last Stand on Mars`, directly answering the fixed B06 Gap. S1/S3 rank D39978 first. Thus the registered canonical Recall@5 improves for B06, but actual answer-bearing Recall@5 was already positive under S0. This is CS8/CS9, not an acquired-evidence rescue. It also limits the q186 conclusion: this B06 Gap concerns the planned second episode, while the original historical q186 publisher problem was excluded from SC0 for leakage reasons.

## U1_C01 / q435: visible genuine top5 rescue

S0 ranked sufficient D51535 at 9; its top5 contained no exact `65 albums` statement in the reviewed corpus texts. S1/S3 ranked D51535 at 4 with the query `Oliver Mtukudzi Forbes Africa May 2017 albums`. D51535 reports 65 albums and cites Forbes's May 2017 listing. This is the cleanest observed case in which prior candidate grounding changed the query and promoted directly useful evidence into top5. The direct Forbes Africa feature D56154 is also in the frozen sufficient set but was not the first hit here.

## U1_C12 / q1094: canonical deep miss and possible alternate partial evidence

Every arm kept canonical merger document D24763 below top50. S0 and S3 retrieved D68186, a football-club establishment list, at ranks 18 and 16. Its row says Stade Saint-Germain merged with Paris FC in 1970, while a separate row lists Paris Saint-Germain FC in 1970. This is plausible partial or alternative support for the yes/no merger Gap, but it is not the frozen canonical document and the relationship to PSG is split across rows. The clean query still fails to surface the canonical source. The S3 match facts concern PSG–Lille and do not ground the merger relation, so this cell cannot by itself prove a fully decision-sufficient State was defeated by the retriever.

## Bridge annotation limitation

SC0 assigned the observed prior document as a bridge whenever it was not a frozen sufficient document. That mechanical rule is broader than the protocol's decision-relevance definition. U1_C12's PSG–Lille match article cannot materially reduce uncertainty about the already named merger clubs. Similarly, several D cells already name the candidate in their target Gap; their old roster, match, or biography source is not necessarily a bridge for that Gap. The frozen bridge IDs are kept for auditability, but ProgressHit is descriptive only. At top5 it equals registered DirectHit in every main arm (S0 21, S1 23, S2 23, S3 23), so this issue does not change the primary S1 gate. No bridge-to-direct closed-loop claim is made.
