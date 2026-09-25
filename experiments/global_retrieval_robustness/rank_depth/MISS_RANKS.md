# Five frozen U1 top5 misses

The rank and score are for the highest ranked **frozen sufficient doc ID**, not a semantic re-adjudication of every other retrieved document. `>50` has no observed target score or score gap.

| Case | qid | Frozen sufficient D | First rank | Score | Rank5 threshold | Target minus rank5 | Depth |
|---|---:|---|---:|---:|---:|---:|---|
| U1_A11 | 186 | 39978 | >50 | n/a | 0.522255 | n/a | absent |
| U1_C09 | 186 | 39978 | 18 | 0.483286 | 0.511500 | -0.028214 | medium |
| U1_C01 | 435 | 48151, 51535, 56154 | >50 | n/a | 0.556937 | n/a | absent |
| U1_D01 | 435 | 48151, 51535, 56154 | 6 (51535) | 0.682466 | 0.683054 | -0.000588 | shallow |
| U1_C12 | 1094 | 24763 | >50 | n/a | 0.438320 | n/a | absent |

For q435, the shared frozen sufficient docs D48151 and D51535 ranked 11 and 6 in U1_D01's album-count query; they ranked 10 and 1 in U1_D02's richest-musicians-list query. The D51535 movement from rank6 to rank1 with a change of wording is direct wording sensitivity. U1_C01 remained beyond top50 despite seeking the same album count.

For q186, canonical D39978 ranked >50 in U1_A11 and 18 in U1_C09. In both top50 lists, five *noncanonical* documents mention both “Galacta” and “Albino Frog”; the company page D3079 ranks 1 in both, and Galacta game pages D22411/D2855 rank 10/18 (A11) and 4/12 (C09). These documents overlap the query clues. D22411 and D2855 also state some target facts, so they must be reviewed as possible alternative useful sources in Find; calling all of them retrieval failures would overstate the canonical-document miss. The frozen sufficient-doc metric is retained without retroactive truth edits.

For q1094, D24763 containing the PSG merger sentence remains beyond rank50 for U1_C12 despite the explicit entity-and-relation query. This is a deep ranking or document-representation warning, not evidence that another hand-written query will necessarily fix it.
