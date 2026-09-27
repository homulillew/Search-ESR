# Minimal Semantic Package / Scoped Partial Evaluation

**E0 complete; E1V prepared, awaiting fresh user authorization. No new model calls.**

48 historical certificates,17 immutable Parents,78 exact source units and34
evidence-independent packages. New support reference:21 positive,27 negative;
four ambiguous certificates retained in primary evaluation. One reference change
is documented without changing the historical study.

- [Current status and call scope](CURRENT_STATUS.md)
- [Protocol](PROTOCOL.md), [hypotheses](HYPOTHESES.md), [pre-execution audit](PRE_EXECUTION_AUDIT.md)
- [Source-boundary policy](e0_reference/BOUNDARY_POLICY.md), [reference review](e0_reference/REFERENCE_REVIEW.md)
- [Actual96 Verifier requests](e1_gold_support/VERIFIER_SCHEDULE.json)
- [Exact Verifier freeze](e1_gold_support/VERIFIER_FREEZE.json)
- [Call estimate](CALL_ESTIMATE.json), [authorization requirements](AUTHORIZATION_REQUIREMENTS.json)

TASK33 requires new explicit authorization after request commit/hash freeze.
The first concrete batch is **96 Verifier calls**, DeepSeek `deepseek-flash`,
temperature0, JSON mode, max8 concurrent, zero retries. Each resulting valid
SUPPORTED output then defines an Auditor request using only its cited Claims.
Those0–96 exact requests will be committed/frozen and separately authorized.

No E1 PASS/FAIL is inferred from Verifier-only results. No E2/E3/E4 or search is
authorized by the first96-call approval.

Offline checks: `python -m unittest experiments.minimal_semantic_package.test_harness -v`

Input audit, no calls: `python -m experiments.minimal_semantic_package.run audit --phase verifier`

Execution only after honest recording of a fresh user approval and its exact
scope: `python -m experiments.minimal_semantic_package.run execute --phase verifier`
