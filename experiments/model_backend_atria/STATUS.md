# Current stage status

| Stage | State | Evidence |
|---|---|---|
| Remote and Qwen history audit | complete | `HISTORICAL_AUDIT.md` |
| M0 Atria protocol preflight | complete; 10/10 frozen gate and 4/4 live requests | `PROTOCOL_COMPATIBILITY.md`, `protocol_events.jsonl` |
| Prefix-only semantic annotation | complete; 13/13 Codex reviewed under clarified authorization | `PREFIX_ONLY_ANNOTATIONS.json`, `ANNOTATION_REVIEW.md`, `ANNOTATION_FREEZE.json` |
| M1 paired explicit planning | ready to freeze and run | Evaluation rules and runner prepared |
| M2 natural action | not run | Runner prepared; selection requires M1 results |
| M3 orthogonal partial | not run | Conditional on M1/M2 model signal |
| M4 evidence update | not run | Eight exact source cases prepared; no freeze/API events |
| M5 Atria-native | not run | Conditional on material model effect |

The user clarified that Codex may perform the prefix-only semantic review
without external human signoff. This is a single-reviewer diagnostic label
set. The M1 runner checks all 13 rows against the frozen checkpoints and
visible D# refs before the first paired call.
