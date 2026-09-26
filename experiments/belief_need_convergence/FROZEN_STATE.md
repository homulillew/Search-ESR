# Frozen state

Remote base verified: 99202167ab1c693514ef87534ca9f346f0813638.
Branch: experiment/belief-to-need-convergence.
Round 0 immutable dependency manifest: round_0/FREEZE.json.
The preregistration commit precedes all calls; actual committed run HEAD and
freeze digest are written to round_0/RUN.json before the first HTTP request.
Every request additionally records its exact HEAD and request hash.

Selection/annotations: bank/SELECTION.json, LABELS.json, MEMBERSHIP.json,
DELTA_PAIRS.json, CLAIM_SUPPORT_REVIEW.json, DELTA_SUPPORT_REVIEW.json.
Runtime input: bank/RUNTIME_INPUTS.json. Source hashes and source provenance are
in bank; every tracked historical experiment is protected by HISTORICAL_HASHES.json.
Rubric/protocol/hypotheses, provider/model, timeout, no-retry policy, prompts,
sample count, parallelism and no-tools horizon are covered by the manifest.

No new model request was made during extraction, curation or offline preflight.
No freeze artifact includes a credential. Confirmation coverage is insufficient
before calls (5 eligible qids versus minimum 8); this cannot be changed by success.
