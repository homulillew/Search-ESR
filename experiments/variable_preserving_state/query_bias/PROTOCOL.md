# V2 one-query bias probe

The 16 cases and 8 qids in `V2_SELECTION.json` were selected and hashed before
V1 calls. All have source uncertainty and no known suitable D for the current
Gap. `prepare_cases.py` materializes exactly that selection, preserves any V1
state failure as empty state plus error marker, and adds a frozen expected
source type for each qid. It does not select by V1 output quality.

Q0 receives the same question/prefix, provisional H, SemanticGap and expected
source type as the other arms. Q1 additionally receives the contemporaneous
C0 Claims; Q2 receives the V1 gate-selected C1 natural TestCards. One
`deepseek-flash` completion produces one query and reason; Search is never
executed. Arm order rotates per case, one call per cell, zero retries.

The arm-masked reviewer judges exact query strings using `REVIEW_RUBRIC.md`.
The pre-call freeze records all requests, source hashes, state hashes, order,
provider, schema and gate. If Q2 fails the paired leakage/retained-alignment
gate, V3 and V4 receive `NOT_RUN.md` and no model calls.
