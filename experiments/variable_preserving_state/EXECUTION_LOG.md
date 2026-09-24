# Execution and stage decisions

| Stage | Freeze / execution | Result |
| --- | --- | --- |
| V1 | `test_representation/freeze.json`; DeepSeek `deepseek-flash`, 30 cases × 3 arms, zero retries | Both TestCard arms passed. Natural C1 selected by the frozen complexity rule. |
| V2 | `query_bias/freeze.json`; same provider/model, 16 preselected cases × 3 arms, one Search query and no Search execution, zero retries | Failed paired query-leakage gate: 3 improved, 1 worsened, net 2 < 6. |
| V3 | `evidence_binding/NOT_RUN.md` | Stopped by V2 gate. |
| V4 | `state_causal_probe/NOT_RUN.md` | Stopped by V2 gate. |

V1 retained two abnormal `finish_reason=length` errors and one interrupted
in-flight request. The interrupted request was never retried. The only
unrequested V1 cell after the interruption was called once. V2 had 48 valid
responses. Raw requests, model responses, usage and failures are in each
stage's `events.jsonl`. The frozen source/request checks pass for both stages.

No Search tool call was made in V2. Historical experiment directories were
left untouched. The one-reviewer, arm-masked judgments and exact leakage
strings are in each stage's `REVIEWS.json` and `REVIEW_NOTES.md`.
