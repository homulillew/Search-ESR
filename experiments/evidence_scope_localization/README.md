# Evidence scope and local relation access

Completed experiment on branch `experiment/evidence-scope-localization`.
Base remote: `fcd195f0f0c6299f00f155c2a6ae37e915fa177e`.
Live-run preregistration commit: `5cfb9043f2f33be922ac30a87d0715fdbcf3da30`.

Start with [FINAL_CONCLUSION.md](FINAL_CONCLUSION.md), then
[analysis/RESULTS_REPORT.md](analysis/RESULTS_REPORT.md).

- Task and preregistration: TASK.md, PROTOCOL.md, HYPOTHESES.md, FROZEN_STATE.md.
- Eligibility/source audits: bank/; RUNTIME_INPUTS excludes offline labels.
- R1: r1/FREEZE.json, MANIFEST.json, initial/adaptive requests and raw responses;
  per-trajectory actual results in r1/cells/.
- Offline outcome review: analysis/WINDOW_REVIEW.json, ACTION_REVIEW.json,
  CELL_REVIEW.json, METRICS.json, GATES.json, INTEGRITY.json.
- Conditional stage not run: r2/DECISION.json.
- U1 read-only audit of earlier318 windows: writer_audit/REPORT.md and JSON.
- Preserved runtime incident and future compatibility patch: engineering/.

## Offline reproduction

From the repository root (no API calls in these commands):

```bash
python experiments/evidence_scope_localization/analysis/review.py
python experiments/evidence_scope_localization/writer_audit/build.py
python experiments/evidence_scope_localization/engineering/check_attempts.py
python experiments/evidence_scope_localization/analysis/integrity.py
python experiments/evidence_scope_localization/analysis/report.py
```

Semantic judgments are explicit reviewer annotations, not automatically regenerated
from the model. review.py/build.py validate and aggregate them. Integrity checks
need the same local corpus/model assets and credential file for a non-printing
artifact-secret scan. No secret is stored in this experiment directory.

The live runner rejects a second R1 attempt. Do not regenerate a completed stage's
freeze or mutate its frozen runner. The engineering compatibility patch must be
integrated into a separately frozen future version before any new calls.
