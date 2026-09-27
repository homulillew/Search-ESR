# Ephemeral Obligation Decomposition

Task: question-only source-faithful canonicalization. Primary arm D2 exact-span
grouping; D0 free prose; D1 anchored prose. See PROTOCOL.md and TASK.md.

Preparation: select.py → reference.py → prepare.py prepare → offline tests →
prepare.py freeze → git commit. Execute with `python -m
experiments.ephemeral_obligation_decomposition.run execute e1_development`.

Masked review must be committed before provenance review and evaluate.py.
E2 uses the already frozen schedule only after the E1 gate passes and is committed.

Final findings and limitations: analysis/FINAL_CONCLUSION.md (written after review).
All historical experiment artifacts are read-only.
