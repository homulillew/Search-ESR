# M0 Atria tool-protocol preflight

The pre-call `freeze_protocol.json` passed all 10 offline gate checks. The
model was `Atria-Dawn-Preview` at `api.atria-asi.ai`; OpenAI SDK 1.109.1,
Python 3.12, 120-second timeout, zero retries, and explicit acceptance of
complete `stop`-finished tool batches. The actual key was read from ignored
`.env.atria` and never entered a tracked artifact.

Four live synthetic-context calls completed. Ordinary Chat Completion
returned nonempty content with raw `finish_reason=stop`. `tool_choice=auto`
returned one valid `search` call with raw `tool_calls`. A forced single tool
returned one valid `search` call with **raw `finish_reason=stop`**; the
reason was kept verbatim, and the full call was accepted under the frozen
compatibility flag. The multi-tool prompt returned **two valid calls in one
batch**, both with raw `tool_calls`. These requests used fake tool results:
no BC+ search was executed in this preflight.

The independent strict validator also passed injected batches for
`stop+tool_calls`, malformed JSON, an undeclared name, a missing required
field, and an invalid second call after a valid first call. In the last four
invalid cases, **zero** calls executed. It validates the entire batch
against the declared JSON schemas before execution; there is no argument
repair or implicit default for required fields. Live requests/responses,
raw tool calls, validation outcomes and synthetic execution results are in
`protocol_events.jsonl`; `protocol_summary.json` holds the mechanical gate.

**Decision:** M0 passed. Atria provider serialization differs from the
historical Qwen endpoint on at least the forced-tool response. The new
experiment runner must use this validator and preserve raw finish reasons.
This preflight establishes transport/protocol viability, not Search–Find
reasoning quality. The prior 2026-09-23 real BC+ smoke test is separate
from this prospective M0 batch.
