# K0 results

All 40 frozen Query1 strings were embedded once on GPU1 with the unchanged Qwen3-Embedding-8B model and FAISS index; every top5 docid exactly matched the historical U1 GPU run. Full ordered top50 docids and scores are in `results.json`.

| Group | @5 | @10 | @20 | @50 |
|---|---:|---:|---:|---:|
| Overall | 35/40 | 36/40 | 37/40 | 37/40 |
| A/B old-source | 19/20 | 19/20 | 19/20 | 19/20 |
| C/D new-source | 16/20 | 17/20 | 18/20 | 18/20 |
| A | 11/12 | 11/12 | 11/12 | 11/12 |
| B | 8/8 | 8/8 | 8/8 | 8/8 |
| C | 9/12 | 9/12 | 10/12 | 10/12 |
| D | 7/8 | 8/8 | 8/8 | 8/8 |
| Grounded hypothesis | 13/14 | 14/14 | 14/14 | 14/14 |
| Ungrounded | 22/26 | 22/26 | 23/26 | 23/26 |

MRR@50 is 0.69097. A/B and C/D group labels follow U1 case type; “grounded” means a non-null frozen working hypothesis. Single Query@10 fails its predeclared gate: 36/40 overall and 17/20 C/D, below 37/40 and 18/20. Only one of five prior top5 misses moves into top10; the other four require deeper investigation. Q1 is therefore triggered for all 40 cells. Exact misses and qid analysis are in `MISS_RANKS.md`.
