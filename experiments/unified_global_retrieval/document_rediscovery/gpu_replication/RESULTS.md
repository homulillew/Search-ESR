# GPU 1 replay of frozen U1 retrieval

At replay start, GPU 1 had 19,380 MiB free. The existing `BCPlusSearcher` loaded Qwen3-Embedding-8B on `cuda:1` with float16 weights and completed all 40 previously frozen queries. No Query Writer call, query rewrite, backend change or retrieval error occurred. The CPU result and earlier GPU initialization failure remain preserved.

All **40 global top-five lists had exactly the same docids in the same order** as CPU float32. All 40 historical-document rankings were also identical. Across 240 paired document scores, the largest absolute CPU/GPU difference was 0.0005702; mean absolute difference was 0.0001994. Thus the measured rankings are insensitive to this device/precision change in this bank.

| GPU metric | Result |
|---|---:|
| G Recall@1 / @3 / @5 | 23/40, 32/40, 35/40 |
| A/B old-source recall@5 | 19/20 = 95% |
| C/D new-source discovery@5 | 16/20 = 80% |
| Retrieval errors | 0/40 |
| Changed top-five lists versus CPU | 0/40 |
| Frozen U1 gate | STOP_U1 |

GPU query inference and scoring took 3.29 seconds summed over 40 cases after model initialization, median 0.071 seconds per case. This timing excludes model loading, index loading and Query Writer API latency. The earlier CUDA failure was an available-memory condition during model initialization: GPU 1 then had roughly 13 GiB free and was unable to complete the last allocation. It does not indicate that GPU 1 was unusable once more memory became available. U1b remains untriggered; U2 and U3 remain blocked by the unchanged new-source and overall recall gates.
