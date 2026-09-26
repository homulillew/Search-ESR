# Offline capability preflight

Command: `python -m pytest -q experiments/goal_residual_control_v3/test_capability.py`

Result before live calls: **39 passed in 0.78 s**.

Checks include all ten historical output categories; exact system/user text and role-order preservation; unchanged model and absent sampling overrides; Actor STOP/Search/Find/Open/two actions; required/extra keys; enums; oneOf; array lengths; integer Search k bounds; forbidden Find k; valid-looking unknown D rejected by runtime registry; Updater action enum/two-Claim bound; Reviewer typed keys; incomplete and malformed JSON rejected without repair.

Fallback schema transformations preserve the local accepted language for the frozen disjoint branches; fixtures check both original and compiled forms. Array bounds are never removed. These are local construction/validator checks, **not proof of server-side constrained decoding**.

Official documents inspected on 2026-09-26:

- [Responses reference](https://api-docs.deepseek.com/api/create-response/): specifies `text.format` JSON Schema output.
- [Responses compatibility](https://api-docs.deepseek.com/guides/responses_api/): format supported; unsupported options may be ignored; no model switch is needed for the named model.
- [Strict Tool Calls](https://api-docs.deepseek.com/guides/tool_calls/): beta endpoint and function strict flag; array min/max unsupported in the documented strict subset. This is a material obstacle, not permission to weaken the contract.

The upcoming frozen live probes distinguish claimed capability, accepted parameters and observed conformity. A successful HTTP response alone will not pass the gate.
