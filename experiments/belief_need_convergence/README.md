# Belief → Need Convergence

Result: **FAIL under the frozen 4096-token configuration; fresh confirmation
EVIDENCE_EXHAUSTED.** No closure or end-to-end authorization inferred.

Start with [FINAL_CONCLUSION.md](FINAL_CONCLUSION.md), then:

- [Task](TASK.md), [protocol](PROTOCOL.md), [rubric](RUBRIC.md), [freeze](FROZEN_STATE.md).
- [Selection](bank/SELECTION.json), [runtime QCH](bank/RUNTIME_INPUTS.json),
  [review-only labels](bank/LABELS.json), [actual Claim sources](bank/CLAIM_SUPPORT_PACKETS.json).
- [Round 0](round_0/METRICS.json); original P3 HTTP400s are preserved there.
- [P3 format repair](P3_FORMAT_CORRECTION.md) and its separate calls/outputs.
- [Pair metrics](analysis/PAIR_METRICS.json), [P3 issue review](analysis/P3_ISSUE_REVIEW.json).
- [Round 1 preregistration](ROUND_1_DESIGN.md), [results](round_1/METRICS.json).
- [Gates](analysis/GATES.json), [budget audit](analysis/LENGTH_FAILURE_AUDIT.json),
  [cache/usage](analysis/TOTAL_USAGE.json), [integrity](analysis/INTEGRITY_REPORT.json).

Runtime and freeze entrypoints intentionally refuse to overwrite runs. Do not
rerun a completed arm to replace a failure. Analysis scripts write exclusive
artifacts as well; review checked-in results or write a new version for reanalysis.

The only additional runtime control was an ephemeral issue within P3. All other
runtime inputs were Q + Claims + H; P4's oracle is diagnostic-only. No tools or
persistent Research State modifications were executed.
