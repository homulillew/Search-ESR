# Skeleton–Claims Alignment / Plan–State Reconciliation

**PREPARED_FOR_EXECUTION — no new paid calls.** TASK §70 requires authorization
explicitly covering this experiment's budget after offline preparation.

## Offline findings

| Control addressability | D1 | D2 primary |
|---|---:|---:|
| Direct | 10/27 (37.0%) | 12/27 (44.4%) |
| Direct + coherent multi-node | 23/27 (85.2%) | 16/27 (59.3%) |
| Subnode-only | 4/27 (14.8%) | 11/27 (40.7%) |
| Not addressable | 0/27 | 0/27 |

D2 triggers the preregistered granularity warning. E1 still proceeds with fixed
D2 replicate1. No historical output was changed. G04/G05 have no admissible
single D2 action under the frozen locality rule; keep both in the denominator.
No natural positive STOP controls in this bank.

## Prepared budget

- E1: 27 states × Oracle/D2 × 2 replicates = **108 calls**.
- E2: only if both E1 gates pass, 27 states × Gold/model mask × 2 = **108 calls**.
- Maximum **216** calls, DeepSeek `deepseek-flash`, concurrency up to8, retries0.
- Approximate input exposure: E1 113,968 tokens; conditional E2 84,224 tokens.
  Prior completion median/p95 scenarios per stage: 488,916 / 1,134,972 tokens.
  These are proxy estimates, not caps; `max_tokens` is omitted. No currency estimate.

See [PROTOCOL.md](PROTOCOL.md), [PRE_EXECUTION_AUDIT.md](PRE_EXECUTION_AUDIT.md),
[E0 report](e0_addressability/REPORT.md), [call estimate](analysis/CALL_ESTIMATE.json),
[prepared conclusion](analysis/FINAL_CONCLUSION.md) and [FREEZE.json](FREEZE.json).
E1/E2 METRICS/REPORT/raw/review artifacts are created only after real execution;
no fabricated zero-score model results or placeholder responses are present.

## Execution handoff

1. Record the actual new user approval in `AUTHORIZATION.json` and commit it:
   `status=APPROVED_BY_USER`, `experiment=skeleton-state-alignment`, current
   `freeze_sha256`, `authorized_stages` mapping approved stages to108, and the
   verbatim applicable `user_instruction`. Do not create this record from an
   older experiment's approval. E2 still requires its frozen gate regardless.
2. `python -m experiments.skeleton_state_alignment.run audit e1_alignment`
3. `python -m experiments.skeleton_state_alignment.run execute e1_alignment`
4. `python -m experiments.skeleton_state_alignment.run export_review e1_alignment`
5. Follow REVIEW_RUBRIC.md using masked packets only; write/commit JUDGMENTS.
6. `python -m experiments.skeleton_state_alignment.score seal_review e1_alignment`
7. `python -m experiments.skeleton_state_alignment.score aggregate e1_alignment`
8. Commit E1 results/review/seal/metrics; if either gate fails, stop. Otherwise:
   `python -m experiments.skeleton_state_alignment.prepare materialize_e2`
   then commit the actual E2 request schedule and execution freeze.
9. Repeat audit/execute/export_review/seal_review/aggregate for `e2_selection`.
10. Run `python -m experiments.skeleton_state_alignment.analyze e1_alignment`
    (and `e2_selection` if executed). Answer all20 questions with actual evidence,
    commit/push the report, and stop. No rollout this task.

Preparation scripts use exclusive writes and are not rerunnable over artifacts.
`python -m unittest experiments.skeleton_state_alignment.test_contracts -q`
is repeatable and entirely offline. The run command refuses to resume, retry or
overwrite and refuses paid execution without a committed applicable approval.
