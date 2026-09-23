# Current stage status

| Stage | State | Evidence |
|---|---|---|
| Remote and Qwen history audit | complete | `HISTORICAL_AUDIT.md` |
| M0 Atria protocol preflight | complete; 10/10 frozen gate and 4/4 live requests | `PROTOCOL_COMPATIBILITY.md`, `protocol_events.jsonl` |
| Prefix-only semantic annotation | complete; 13/13 Codex reviewed under clarified authorization | `PREFIX_ONLY_ANNOTATIONS.json`, `ANNOTATION_REVIEW.md`, `ANNOTATION_FREEZE.json` |
| M1 paired explicit planning | complete; 26 attempts, 23 responses | `planning_probe/RESULTS.md` |
| M2 natural action | complete; 26 terminal cells after frozen interruption recovery | `natural_action_probe/RESULTS.md` |
| M3 orthogonal partial | skipped by model-signal/provider-availability gate | `orthogonal_partial/DECISION.md` |
| M4 evidence update | paused at user request after 3 terminal cells | `evidence_update/freeze.json`, `evidence_update/events.jsonl`, `evidence_update/INTERRUPTION.json` |
| M5 Atria-native | not run | Conditional on material model effect |

The user clarified that Codex may perform the prefix-only semantic review
without external human signoff. This is a single-reviewer diagnostic label
set. The M1 runner checks all 13 rows against the frozen checkpoints and
visible D# refs before the first paired call.
