# Frozen state

Base `9e4b48c197d4248e2ccf34850948761706252cfd`; audit `0c51e4c`. New branch `experiment/frontier-generation-state-sufficiency`.

F0: 114 real archived checkpoints; 24 selected / 10 qids. Exact States/history hashes and provenance in bank. Requirement Map and State/History/Combined coverage reviewed before new calls. Two all-material resolved S checkpoints (F04,F23), additional H closure F15/F16; F24 alternative historical closure only as declared sensitivity. Neither gold nor future source truth used.

F1: deepseek-flash at existing DeepSeek endpoint, existing credential config (secret not included), provider defaults, JSON mode, deterministic local schema, 144 independent requests, one Frontier each, tools0, retries0, workers4, timeout240s. Identical replicates are separate submissions, not retries. No context truncation or output selection.

`f1_state_sufficiency/freeze.json` pins construction HEAD, file hashes, exact requests, selection, annotations, prompt/schema/rubric and unchanged historical source code. Commit this manifest before calls; the transport verifies pins equal committed HEAD and journals that HEAD for every request. Raw events are append-only and cannot be resubmitted. Historical files are pinned in `historical_baseline_hashes.json` for final integrity checking. Corpus/index/embeddings are not accessed or changed by Frontier-only stages; previous full binary manifest is inherited and must be checked before any F4 retrieval.

Coverage primary requires all material clues; reported sensitivity cannot replace the frozen gate. F1 critical added failures count checkpoints once; long-term omission remains unmeasured. F2–F4 await their gates and individual freezes.
