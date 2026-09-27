# Minimal Need → Multi-Query Research Control

Status: **PREPARED_FOR_REAL_RUN**. E0 offline review completed; E1 development is frozen and ready for explicit paid-call authorization. No new external model or retrieval calls have occurred.

- [Task](TASK.md), [pre-execution audit](PRE_EXECUTION_AUDIT.md), [protocol](PROTOCOL.md), [hypotheses](HYPOTHESES.md), [freeze](FROZEN_STATE.md).
- [E0 report](e0_w_reaudit/REPORT.md): 2 independent W, 3 coherent multi-query Needs; five cases/four qids, single reviewer.
- [E1 selection](e1_need/SELECTION.json), [bank](e1_need/BANK.json), [provenance](e1_need/PROVENANCE.json), [rubric](e1_need/RUBRIC.json), [72 requests](e1_need/SCHEDULE.json).
- [Call/token estimate](analysis/CALL_ESTIMATE.json), [dry run](analysis/DRY_RUN.json), [final integrity](analysis/FINAL_INTEGRITY.json), [conclusion](FINAL_CONCLUSION.md).

## Offline checks

From the repository root:

```bash
python -m unittest experiments.minimal_need_multiquery.test_contracts -v
python -m experiments.minimal_need_multiquery.audit
```

The `prepare build`, `prepare freeze`, and `run dry-run` commands created the committed artifacts once. They use exclusive writes and are not intended to overwrite those artifacts. `audit` is repeatable and read-only. Tests use a fake HTTP transport and forbid socket connections; they are execution checks, not model effect results.

## After explicit user authorization

The following command incurs paid calls. It is documented, **not executed** in this preparation:

```bash
python -m experiments.minimal_need_multiquery.run execute \
  --paid-calls-authorized \
  --authorization-note 'Record the actual user authorization here before running'
```

It reads `DEEPSEEK_API_KEY` from the environment or existing `.env.deepseek` only after guards. It sends at most 72 scheduled requests, no extra canary or tool call. API work can run eight ways; there is no token cap. An existing run directory refuses restart even after failure.

After completion, export arm-masked review packets, fill the separate `review/REVIEW.json`, then aggregate:

```bash
python -m experiments.minimal_need_multiquery.run export-review
python -m experiments.minimal_need_multiquery.score
```

`score` requires a complete semantic review. It never upgrades parse success to strict validity or opens E2 from development results. Fresh confirmation and later stages require separate freezes; their status files state what remains unmeasured.
