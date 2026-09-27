# Freeze / execution record

- Branch: `experiment/onegap-recovery-control`.
- Base: remote `experiment/minimal-recoverable-loop`,
  `1fb9c886fa3744aeed2422f654954e5579ee2e37`. This is storage/history ancestry,
  not an empirical prerequisite and not adoption of that Writer/Admission path.
- Preparation commit: `85052294`.
- Request/rubric/code freeze commit: `eed0e3db` (before any Actor HTTP call).
- Raw calls and single-reviewer annotations committed at `2629ba84`, before
  aggregate metric calculation.
- Request set SHA-256:
  `5871db9ac344868e3e57a099d517f35b0e2a3384bb32a0549ac03933e95af269`.
- 42 requests:16 P0,8 P1,16 P2,2 P3;16 states /10 qids;one response per condition.
- `deepseek-flash`,temperature0,max_retries0,maximum concurrency42,no tools.
- Historical remote heads and read-document hashes:
  [HISTORICAL_READ_AUDIT.json](HISTORICAL_READ_AUDIT.json).
- Exact frozen files: [FREEZE.json](FREEZE.json). Historical input content hashes:
  [SOURCE_HASHES.json](e0_state_bank/SOURCE_HASHES.json).
- Existing standing API authorization and exact batch binding:
  [AUTHORIZATION.json](AUTHORIZATION.json).
- Empirical outcome: FAIL. Integrity/replay outcome: PASS. No Stage5-C/5-L calls.

Post-call reports and diagnostics are new artifacts outside the input freeze.
Frozen inputs, rubric, prompt, raw results and historical experiments are unchanged.
