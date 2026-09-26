# Explicit Research State → Research Frontier Generation

[Final conclusion](FINAL_CONCLUSION.md) · [Protocol](PROTOCOL.md) · [Pre-implementation audit](DESIGN_AUDIT.md) · [Frozen state](FROZEN_STATE.md)

- F0:114real archived checkpoints,24selected across10qids; prefix-only coverage frozen before requests. See [bank](bank/RESULTS.md).
- F1:144single-attempt DeepSeek Frontier calls, three matched views with two independent replicates. [Results](f1_state_sufficiency/RESULTS.md). Failed qualification gate.
- One permitted A exploration:9failure-conditioned checkpoints,18fresh paired control/narrow-prompt calls. [Plan](EXPLORATION_PLAN.md), [results](exploration/RESULTS.md). Cannot override F1.
- F2/F3/F4 unmeasured because F1 failed. No retrieval or Writer call, no new State field or backend modification.

## Reproducibility

Frozen input reconstruction: `python experiments/frontier_generation/test_contracts.py`.

Derived F1 analysis: `python experiments/frontier_generation/analysis/summarize.py` and `analysis/report_tables.py` (from this directory use the corresponding paths). Integrity: `python experiments/frontier_generation/analysis/integrity.py`.

The live runners intentionally refuse an existing request journal. Do not delete journals or re-execute to replace failures. Exact request bodies, hashes, run HEAD, raw responses/errors, usage and masked judgments are committed. Credentials remain outside the artifacts. Actual provider model ID was deepseek-flash.

History means the complete archived replay episode, not unrecoverable ancestral history. Some initial States were historically reviewer-normalized and later States use the legacy Writer; this is not a fresh minimal-U1 cohort. Single-reviewer masking is imperfect because view format reveals treatment. Primary conclusions use all144planned outputs and frozen coverage.
