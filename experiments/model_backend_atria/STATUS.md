# Current stage status

| Stage | State | Evidence |
|---|---|---|
| Remote and Qwen history audit | complete | `HISTORICAL_AUDIT.md` |
| M0 Atria protocol preflight | complete; 10/10 frozen gate and 4/4 live requests | `PROTOCOL_COMPATIBILITY.md`, `protocol_events.jsonl` |
| Prefix-only human annotation | awaiting independent human review | `PREFIX_REVIEW_INDEX.md`, `PREFIX_ONLY_PACKETS.json`, `PREFIX_ONLY_ANNOTATIONS_DRAFT.json`, `PREFIX_ANNOTATION_REVIEW.md` |
| M1 paired explicit planning | not run | Runner prepared; freeze blocked by annotation guard |
| M2 natural action | not run | Runner prepared; selection requires M1 results |
| M3 orthogonal partial | not run | Conditional on M1/M2 model signal |
| M4 evidence update | not run | Eight exact source cases prepared; no freeze/API events |
| M5 Atria-native | not run | Conditional on material model effect |

The requested human review is a methodological gate, not an inference from
elapsed time. No M1 or later model call is permitted until it is supplied.
The M1 runner also checks that all 13 reviewed rows refer to the frozen
checkpoint set and that any proposed D# was visible in its prefix.
