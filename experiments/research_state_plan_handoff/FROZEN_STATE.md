# Historical handoff state

Base commit: `3272200` on `experiment/model-backend-deepseek-search-find`,
verified against `origin` before the new branch was created. The DeepSeek
provider is `deepseek-flash` at `api.deepseek.com`; `.env.deepseek` is ignored.
All P1 historical M1/M2 files, the four M3 selection cells, the original
checkpoint logs, and source code are hashed by each stage freeze. No old file
will be rewritten.

The P1 control card carries the four M1 field values from the frozen
`planning_probe/mechanical_summary.json` verbatim. It adds one descriptive
user message to the exact historical M2 request. The old M2 tool menu and
parameters are unchanged, and no tool is executed in P1.
