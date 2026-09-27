# Contextual Subtraction Qualification

Initial preregistration:48 frozen certificates (22 positive,26 negative) from24 historical cells/16 snapshots/9 qids. Q0 standalone fragment versus Q1 full context; two replicates each, **192 E1 requests**, DeepSeek deepseek-flash, at most8 concurrent calls, zero retries. No persistent state changes.

- [Protocol](PROTOCOL.md), [Gold policy](e0_reference/REFERENCE_POLICY.md), [certificates](e0_reference/CERTIFICATES.json)
- [Call estimate](CALL_ESTIMATE.json), [gates](GATES.json), [audit](PRE_EXECUTION_AUDIT.md)
- [Frozen actual requests](e1_qualification/SCHEDULE.json)

Current task authorizes E1. E2 requires all E1 gates to PASS and a new separate authorization. No E2/E3 call is included in these192 requests. Initial docs remain frozen; later CURRENT_STATUS/stage reports will record observed results.

Offline check: `python -m unittest experiments.contextual_subtraction_qualification.test_harness -v`.
Execution: `python -m experiments.contextual_subtraction_qualification.run execute` after committed freeze and current-task authorization record.

No Search, Query, Probe, Find/Open, Writer, Bootstrap, graph, training, majority vote or best-of.
