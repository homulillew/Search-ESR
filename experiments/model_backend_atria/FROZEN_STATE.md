# Freeze register

The parent historical checkpoint freeze is
`../search_find_v3b/orthogonal_search/freeze.json` at commit `a63ca25`.
The exact 13 checkpoint request hashes and original event hashes are copied
into `freeze_protocol.json`. `provider.json` gives the Atria model spelling
and endpoint; the key is deliberately excluded. The active qwen3.7-flash
configuration and historical experiment files are not changed.

The M0 freeze is written by `python experiments/model_backend_atria/preflight.py
freeze`; `gate` verifies it before `run`. Each later paid stage requires a
separate freeze file. A missing or failed gate is a stop condition.

M0 was frozen and gated **10/10 PASS** before its four live calls. Its
`protocol_summary.json` records a passed compatibility gate, including the
real forced-tool `stop + tool_calls` response and a real two-call batch.
`PROTOCOL_COMPATIBILITY.md` is the human-readable audit.

The 13 prefix-only annotations were semantically reviewed by Codex under the
user's clarified authorization and frozen in `PREFIX_ONLY_ANNOTATIONS.json`
and `ANNOTATION_FREEZE.json`. This is a single-reviewer diagnostic annotation.
M1 has not yet been frozen or run. The M1 runner checks the annotation freeze
and refuses to run when a hash or source-ref check fails.
M2/M4 code and exact evidence candidates are preparatory only; neither stage
has a freeze or API events.

The current provider has a known possible `finish_reason=stop` alongside
`tool_calls`. The new experiment validator accepts that only when explicitly
enabled and only after full-batch name, JSON-object, required-field and
schema checks. Raw provider reasons are kept verbatim.
