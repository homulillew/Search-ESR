# Ephemeral Premise Audit / Need Type Checker

Independent experiment from remote `a12167e`. The old minimal_need_multiquery experiment remains closed.

- [Task](TASK.md), [pre-execution audit](PRE_EXECUTION_AUDIT.md), [protocol](PROTOCOL.md), [hypotheses](HYPOTHESES.md).
- [Reference bank](e0_reference/CANDIDATES.json), [reference audits](e0_reference/REFERENCE_AUDIT.json), [selection](e0_reference/SELECTION.json).
- E1:22 candidates ×2 verifier arms ×2 replicates =88 real calls after commit. Exact user prompts; deepseek-flash; no retries or tools.
- E2 and E3 are conditional on the preceding frozen gates. Final execution findings will be in `analysis/FINAL_CONCLUSION.md`; preparation alone makes no performance claim.

Commands from repo root: `python -m experiments.need_premise_audit.run audit` is read-only. `run execute` is paid and guarded against overwrite. `run export_review` and `score` write once after complete execution/review. Prepare commands are one-time artifact construction, not rerun/resume commands.

The user's TASK §40 authorizes this bounded experiment. No persistent semantic fields are added. All premise structures are ephemeral computation/private experiment trace.
