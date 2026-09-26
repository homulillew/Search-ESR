# BC+ Candidate Discovery vs Constraint Verification

Start with [FINAL_CONCLUSION.md](FINAL_CONCLUSION.md).

- [TASK.md](TASK.md): exact user assignment.
- [PROTOCOL.md](PROTOCOL.md), [HYPOTHESES.md](HYPOTHESES.md), [FROZEN_STATE.md](FROZEN_STATE.md), [freeze.json](freeze.json): pre-call design and identities.
- [constraint_audit/REINTERPRETATION.md](constraint_audit/REINTERPRETATION.md): S0 question semantics and append-only historical closure reinterpretation.
- [bank/SELECTION.json](bank/SELECTION.json): pre-call counts, integer gates, exclusions and shortfall.
- [analysis/METRICS.json](analysis/METRICS.json), [analysis/GATES.json](analysis/GATES.json): primary S1–S3 results. S4/S5 are gated off.
- [analysis/UNIT_REVIEW.json](analysis/UNIT_REVIEW.json), WINDOW_REVIEW / CLAIM_REVIEW / STATE_REVIEW: offline semantic review of all units, returned windows, emitted Claims and H operations.
- `round1/`–`round3/`: exact requests, unmodified provider responses, tool results and intermediate states. `RESULTS.json` is the terminal snapshot.
- [exploration/PREREGISTRATION.md](exploration/PREREGISTRATION.md), [exploration/REVIEW.json](exploration/REVIEW.json): the sole bounded probe, four units / twelve total API calls. Does not reopen gates.
- [analysis/INTEGRITY_CHECK.json](analysis/INTEGRITY_CHECK.json): no historical/production edits, exact request intervention check, corpus spans, failure retention and secret scan.

## Reproduction

`python experiments/bcplus_verification/analysis/verify_artifacts.py` performs read-only input/result verification and writes only its integrity report. No model calls. `analysis/build.py` and `exploration/analyze.py` aggregate explicit reviewer labels; semantics were manually reviewed, not inferred by these scripts. Do not treat rerunning aggregation as a fresh independent review. In a separate copy, generated outputs can be rebuilt; timestamp-bearing reports can differ.

The real-call runners reject an existing RUN_STARTED.json. These recorded runs must not be overwritten or retried. A future replicate needs a separately frozen directory and protocol. Credentials are read locally and never committed.
