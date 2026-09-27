# V2 offline validation

Command: `python -m pytest -q experiments/claim_pipeline_root_cause/contract_rerun/tests experiments/claim_pipeline_root_cause/tests`

Result: **84 passed in4.46s** (57 V2 checks including parametrized cases plus27
original contract tests). All network exercise used explicit httpx.MockTransport;
offline semantic calls=0. Test code and replay report are versioned with this file.

Coverage includes all30 requested contract categories: public fields/private-field
exclusion, optional existing date preservation, exact full text, W1/W12 acceptance,
wrong-namespace/zero/leading-zero rejection, duplicates, dynamic enum and independent
runtime membership, all arm information boundaries, unchanged bank/prompts/rubric/
threshold code/old run/conclusion, and rejection of H-confirmation by the E1 DAG.

The original eight invalid outputs remain rejected; no mapping was applied. Each
offending alias is absent from the corresponding projected input. A full mock
24×3 DAG produced72 valid chains and96 calls when every selector selected evidence;
an empty selector skips formulation. A failure stops unsent requests with zero
retries. G1 schema was aligned offline but this runner rejects non-E1 role calls.

New schemas only change reference constraints; selector schema is byte-identical.
Semantic prompts are read directly from their immutable old files. Original DAG,
review exporter and metric/gate implementation are reused unchanged. The V2
transport is a local snapshot of the original, with V2 authorization/freeze imports,
an E1-only guard, private input archival, and public projection before wire creation.
No timeout, parsing, retry, failure-stop or accounting behavior was relaxed.

This proves mechanical isolation/rejection properties, not semantic model quality.
Real E1 must still pass the complete72-chain gate before any semantic scoring.
