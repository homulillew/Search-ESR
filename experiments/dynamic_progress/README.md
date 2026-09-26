# Dynamic Research Progress → Frontier

Status: P0/P1 and FULL sensitivity completed; primary gate **failed**. One bounded exploration completed with local improvement; formal P2–P4 not run. Final report: [FINAL_CONCLUSION.md](FINAL_CONCLUSION.md).

- [Task](TASK.md), [design audit](DESIGN_AUDIT.md), [protocol](PROTOCOL.md), [frozen state](FROZEN_STATE.md), [rubric](analysis/RUBRIC.md).
- [Selection](bank/SELECTION.json), exact [primary](bank/PRIMARY.json) / [Challenge](bank/CHALLENGE.json) States and their separate pre-call labels.
- [P1 results](p1_progress/RESULTS.md), [FULL sensitivity](decomposition_sensitivity/RESULTS.md), [only exploration](exploration/RESULTS.md).
- [Gate](analysis/GATE.json), [all reviewed outputs](analysis/reviewed_outputs.json), [semantic reviews](analysis/semantic_review.json), [usage](analysis/usage.json), [integrity audit](analysis/INTEGRITY_AUDIT.json).
- Explicit implementation deviation: [JSON mode correction plan](transport_correction/PLAN.md). Original120HTTP400rejections retained; only those pre-inference rejections received120separately frozen corrected submissions. No successful inference was replaced. One additional Bschemafailure remains a failure.

Reproduce offline aggregation from repository root:

```bash
python experiments/dynamic_progress/analysis/packets.py
python experiments/dynamic_progress/analysis/finalize_metrics.py
python experiments/dynamic_progress/analysis/audit.py
```

Runtime scripts intentionally reject existing journals. Do not rerun live batches. No retrieval, Writer, Frontier or State mutation occurred. Cache code demonstrates mechanical reuse/invalidation only; semantic cache adequacy remains unmeasured.
