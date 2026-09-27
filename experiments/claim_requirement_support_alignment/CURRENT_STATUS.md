# Current status

**E1 COMPLETE — SAFETY FAIL. E2 NOT RUN.**

96 authorized E1 calls completed with no transport/schema failure or retry. S1 precision35/38=92.11%, recall35/36=97.22%, promotion3/128=2.34%, scope32/35=91.43%, relation/source-binding corruption3/48=6.25%, false-full assignment hazards2. Safety entry failed; no E2 authorization requested or model calls made. DeepSeek cache hit rate55.01%.

- [Final conclusion — all18 task questions](analysis/FINAL_CONCLUSION.md)
- [E1 report](e1_support_alignment/REPORT.md) and [sealed-score metrics](e1_support_alignment/METRICS.json)
- [E2 safety-stop decision](e2_downstream_residual/DECISION.json)
- [Execution accounting](analysis/EXECUTION_ACCOUNTING.json) and [post-execution integrity](analysis/E1_INTEGRITY.json)

README.md, initial STATUS.json and initial INTEGRITY.json remain frozen preparation snapshots. They are retained verbatim for provenance. This file and the stage reports describe the completed execution. No historical results, Gold, requests or gate thresholds were changed.
