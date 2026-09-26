# Deferred Recovery: Global Search versus optional local reuse

Branch: `experiment/deferred-recovery-global-vs-local`

Base: `2544fbf0c5488d8b1c84f36577ea36f1beee2da2`

**Completed limited diagnostic; primary gate remains unassessable because the
fresh bank is insufficient.** Five D3/D4 cases cover four qids, with only one
fresh case. D1 and D2 controls are reported separately. No synthetic omission
was created to fill the bank.

Start with [FINAL_CONCLUSION.md](FINAL_CONCLUSION.md). Protocol and evidence:

- [TASK.md](TASK.md), [DESIGN_AUDIT.md](DESIGN_AUDIT.md), [PROTOCOL.md](PROTOCOL.md)
- [Bank and exclusions](bank/RESULTS.md), [frozen inputs](freeze.json)
- [First decision](r1/RESULTS.md), [two-decision outcome](r2/RESULTS.md)
- [Costs and cache](analysis/COSTS.md), [paired cases](analysis/PAIRED.json)
- [Exploration decision](EXPLORATION_DECISION.md), [integrity](FINAL_INTEGRITY.md)

G and H share existing v3a Global Search. H additionally exposes Find/Open.
No semantic router, old raw-window context, retry, repair, backend change or
gold-triggered stopping. All 100 model requests and 21 tool calls are retained.
R1 results became the actual R2 prefix; the first step was never resampled.

## Offline reproduction

From the repository root, with the experiment's existing Python dependencies:

```bash
python experiments/deferred_recovery/analysis/metrics.py
python experiments/deferred_recovery/analysis/report_tables.py
python experiments/deferred_recovery/analysis/integrity.py
python experiments/deferred_recovery/test_contracts.py
```

Integrity reads the frozen corpus, index and embedding assets at their recorded
local paths. It does not call a model or execute research tools. Semantic labels
are a single Codex review, with no claim of independent or blinded replication.
The live runner refuses existing event paths; do not delete traces to rerun it.
