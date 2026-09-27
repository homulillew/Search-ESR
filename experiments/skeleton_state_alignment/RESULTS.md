# Completed: E1 A0 FAIL / A1 PASS

E2 was not run because its frozen A0 AND A1 entry gate failed.108 real requests,
all returned, no retries or mechanical failures. Weighted cache hit rate73.49%.

| Metric | A0 | A1 |
|---|---:|---:|
| Node accuracy | 92.55% | 93.94% |
| Exact state mask | 70.37% | 77.78% |
| Support precision | 86.58% | 87.59% |
| Full-support sufficiency | 86.27% | 92.31% |
| Residual recall | 97.48% | 98.68% |

See [final conclusion and20 answers](analysis/FINAL_CONCLUSION.md),
[E1 gates](e1_alignment/REPORT.md), [E2 stopped outcome](e2_selection/REPORT.md),
[error ledger](analysis/ERROR_LEDGER.json), and [actual accounting](analysis/EXECUTION_ACCOUNTING.json).

README.md and e2_selection/STATUS.json are immutable pre-call preparation
snapshots covered by FREEZE.json. STATUS.json and this file record current status.
No frozen reference, prompt, schedule, scorer or historical experiment was edited.
