# Cross-contract matrix

| Node | Prompt fields/example | Machine schema | Exact parser | Offline checks |
|---|---|---|---|---|
| Goal Reviewer | Original resolved/residual typed example; prompt unchanged | GOAL_RESPONSE_SCHEMA.json | Closed keys, boolean, string, resolved iff residual empty | Both valid forms; type, extra key, inconsistent closure rejected |
| Research Actor | Complete schema plus Search, Find, Open, independent pair and STOP examples | ../research_decision_v2/ACTION_RESPONSE_SCHEMA.json | Flat tool discriminator only; 0/1/2 coupling; pre-batch refs | Valid forms, forbidden wrappers, required keys, illegal tool, dependent batch, extra keys, ranges |
| State Updater | Original semantic prompt plus exact keep/set/clear objects | UPDATER_RESPONSE_SCHEMA.json | Closed keys, ≤2 nonempty claims, keep/set/clear, nonempty set | All three actions; bad enum, too many claims and empty set rejected |

Goal Reviewer and Updater consistency conditions supplement JSON Schema without reinterpreting values. No fuzzy parsing, Markdown extraction, alias mapping or fallback tool inference. Tests make no API or retrieval calls.
