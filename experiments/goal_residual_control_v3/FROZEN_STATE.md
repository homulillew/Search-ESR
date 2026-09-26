# Freeze ledger

- Stable v2 base: `32de7c8c7fb3ff197b16632079e43a33c52f372e`.
- Design audit committed first: `52f8911`.
- Offline capability tests: 39 passed; no live model/tool call during those tests.
- Structured preflight: exact historical requests, capability requests, code/prompt/schema hashes and model/API settings in `structured_output_preflight/freeze.json` (generated and committed before execution).
- Conditional stages: Admission Replay, Transition Replay and three-round loop are not frozen or authorized to execute through their gates yet. Their pending status is not a zero-effect result.

Old tracked historical artifacts are protected by `analysis/HISTORICAL_HASHES.json`. Each stage uses zero retries and append-only event files. A failed capability probe will not be rerun under the same ID.
