# Offline validation

Runtime HEAD: `4e91b59c0d1ea15d46aaf31e802e394e30de2232`.
Base: `d4351e2dfc8c886dcd6a14cd51a8ae9a78a23652`.

## Result

**144 passed, 0 failed**, including the unchanged 10 mocked transport tests.
No live API calls, no retrieval backend calls, no model token/cache usage.
Cache hit rate is **not applicable**, not an inferred zero-percent hit rate.

```bash
python -m pytest tests/recoverable_loop_clean tests/test_search_find_v3b.py \
  experiments/recoverable_loop_clean/micro_recovery/test_transport.py -q \
  --junitxml=experiments/recoverable_loop_clean/h_fix/offline_validation/run001/PYTEST.xml

python -m experiments.recoverable_loop_clean.h_fix.replay_failures \
  --output /tmp/h-isolation-replay-fresh-directory
```

The replay output directory must not exist; existing evidence is never overwritten.
Results: [pytest text](offline_validation/run001/PYTEST.txt),
[JUnit XML](offline_validation/run001/PYTEST.xml),
[replay summary](offline_validation/run001/SUMMARY.json).

## Mandatory coverage

| Requirement | Evidence |
|---|---|
| 1. Valid W-only ADD | test_h_isolation::test_valid_add_keeps_low_authority |
| 2. Valid W-only REJECT | test_b_f_loop::test_wrong_h_recovery_with_real_mock_acquisition; semantic positive control |
| 3. NoGain DEPRIORITIZE | test_active_h_allows_nogain_deprioritization_without_new_evidence |
| 4. Question-inspired empty basis | test_valid_add_keeps_low_authority |
| 5–7. C3/D4/R1 rejected | parameterized test_whole_h_transaction_rejected_preserves_claim_gain_and_next_actor |
| 8. Unknown W rejected | same parameterized test; W999, W0 and W01 |
| 9. H unchanged | same test, full tuple equality and replay |
| 10. New C preserved | same test; all 5 historical new C replays |
| 11. Gain preserved, no fatal failure | same test; q228/q637/q538/q922 historical replays |
| 12. Next Actor reachable | same test and all 12 unchanged invalid outputs |
| 13. Bad opportunity atomic | invalid D999/W1 plus valid ADD; inspected-current-source rejection |
| 14. Old D17 not new | test_old_pending_d17_rejected_without_partial_h_or_opportunity_loss |
| 15. Pending D17 survives | same test and both q546 fault replays |
| 16. Duplicate H operations atomic | valid ADD then two KEEP H1 operations rejected together |
| 17. More than six active H atomic | seven distinct ADDs rejected together; legacy boundary regression |
| 18. Integrity remains fatal | five corruption cases; three corrupt-during-H paths; valid-hash ungrounded commit |
| 19. Identical Trace replay | all new replay traces and all 12 original traces round-trip exactly |
| 20. Closure roundtrip | test_closure_veto_acquisition_claim_invalid_h_next_actor; 10 historical fixtures; q922 |
| 21. Reader/Grounding unchanged | old regression suite plus provider-fatal tests; AST/prompt/schema comparisons |
| 22. Search/Find/Open unchanged | unchanged test_a_tools.py and tests/test_search_find_v3b.py; file hashes |

Additional coverage: H provider timeout with and without C progress, retained raw
output hashes, malformed JSON/duplicate keys/null/extra state-write fields, unknown
H ID, active-H updates despite no new evidence, no READY authority, persistent state
exactly Q/R/C/H/T, and real scripted route change following R1 NoGain.

## Distinguishing three forms of evidence

1. **Contract and authority tests:** model outputs are scripted, tools in unit tests
   use actual Search/Find/Open implementations with a mock Searcher and whitespace
   tokenizer. No claim of original retrieval quality or tokenizer equivalence.
2. **Historical byte replay:** original actions, role outputs and normalized tool
   observations are consumed in their original order. A separate RecordedBridge
   bypasses retrieval. Four R1 fault replays explicitly override only the skip
   predicate; four additional replays use the real production skip policy.
3. **Semantic counterexamples:** human-specified cases for q546, Euler, q637 and
   memo/letter, plus a direct-contradiction positive control. They specify intended
   H behavior and prove no C/READY leakage under scripted behavior. They do not
   evaluate a live semantic model or automatically enforce English entailment.

## Preservation and development notes

[INTEGRITY.json](offline_validation/run001/INTEGRITY.json) verifies 313 historical
files against base Git blobs, records SHA-256, confirms all non-H role prompts/
schemas and protected tool/state files are identical, and compares core method
ASTs for claim chain, Closure and Finalizer.

Existing tests expecting fatal H outcomes or mandatory no-novelty H calls were
updated for the new explicit contract; their other factual/Closure assertions were
retained. Early development failures were these old expectations and one new test
fixture using an invalid k=17; the fixture now discovers 17 documents through two
valid k<=10 searches. No production action contract was relaxed to fit the test.

The formal offline evidence comes from the final committed runtime, not the earlier
development attempts. No historical tests' recorded results were overwritten.
