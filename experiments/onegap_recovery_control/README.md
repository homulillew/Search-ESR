# Stage 5-R: OneGap Recoverability

**Completed — Gate FAIL.** 16 historical states,10 qids,42 one-attempt Actor calls;
no retrieval, Writer, Admission, Closure or live rollout. All HTTP200;31/42 valid
action outputs. Historical studies unchanged.

Start with [FINAL_CONCLUSION.md](FINAL_CONCLUSION.md). Formal numbers are in
[METRICS.json](e1_actor/METRICS.json); full reviewer reasons in
[REVIEW.json](e1_actor/REVIEW.json). Inputs and rubric were committed before calls.

Offline checks:

```bash
python -m experiments.onegap_recovery_control.harness audit
python -m unittest experiments.onegap_recovery_control.test_contracts -v
python -m experiments.onegap_recovery_control.validate
```

Do not rerun `execute`: it rejects existing archives. `prepare`, `requests`,
`freeze`, `record_review`, `score`, and `diagnostics` use exclusive writes.
Stage5-C and Stage5-L were not executed.
