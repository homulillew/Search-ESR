# M2 same-prefix natural next action results

The pre-call `freeze.json` selected all 13 checkpoints by the registered
short-stratum fallback. Every model used the original tool schema and prefix;
no tool was executed. `gate.txt` passed 6/6. `events.jsonl` retains 27
request events, 26 terminal events, and one explicit interruption record.
The extra request is the aborted, in-flight Atria 1094:53 attempt; the
frozen `resume_freeze.json` authorized only that unfinished cell and the
unattempted cells, without rerunning any terminal cell.

| Outcome | qwen3.7-flash | Atria-Dawn-Preview |
|---|---:|---:|
| Valid provider responses | 13/13 | 1/13 |
| Single Search | 3 | 0 |
| Single Find | 1 | 0 |
| Single Open | 0 | 0 |
| Stop | 3 | 0 |
| Valid multi-tool batch | 6 | 1 |
| API errors | 0 | 12 |
| M1 document plans in selected cells | 4 | 4 |
| Single Find realizing document plan | 0/4 | 0/4 (all four unobserved) |

Atria errors comprise six `APIConnectionError`, five `APITimeoutError`, and
one HTTP 502 `InternalServerError`. The only response, at 1094:61, had raw
`finish_reason=tool_calls` and two schema-valid `find(D14, ...)` calls. Both
calls were in one batch and D14 was not a prefix-plausible target in the
frozen annotation. This is evidence that Atria can serialize a Find batch
on a long prefix, but cannot establish single-decision policy realization.
The four Atria cells with M1 `document` planning all failed at the provider
layer; their natural-action scopes are **unobserved**, not Search or Stop.

Qwen produced six valid batches containing only Search calls, three single
Search calls, three natural Stops, and one single Find at 1094:34 (where M1
had timed out, so there is no explicit planning scope to compare). For its
four M1 `document` plans: 546:9 and 1094:53 became Search batches, 546:17
became single Search, and 546:41 became Stop. Thus strict single-Find scope
realization is 0/4; three of four continued searching. The pre-registered
single-Search policy-failure count is 1/4, with the two Search batches shown
separately rather than silently folded into that metric.

**Interpretation:** the Atria natural policy is not estimable from this
batch. M0 short synthetic tool requests worked and M1 no-tool diagnostics
mostly returned, while M2 long-prefix tool-enabled requests failed 12/13.
This is a provider/transport availability failure in the target workload;
it cannot be scored as Atria reasoning or action-selection failure. Qwen
still exhibits a planning-to-action gap on its own observed cells.
