# DeepSeek model backend intervention

This arm substitutes `deepseek-flash` for the previously attempted
`Atria-Dawn-Preview` on the frozen Search–Find mechanism probes. The Atria
artifacts remain immutable in `../model_backend_atria/`. This arm shares the
13 historical checkpoint messages, prefix-only annotations, Search/Find/Open
tool schema, and diagnostic instructions. Completed Qwen cells from the Atria
study are a fixed baseline; they are not selectively rerun. Qwen M4 cells
that never ran in the paused Atria study will be filled once.

The exact DeepSeek endpoint/model are in `provider.json`. The API key stays
in ignored, mode-600 `.env.deepseek` and is never copied into experiment
artifacts. All DeepSeek responses retain raw `usage`; `cache_usage.py` records
`prompt_cache_hit_tokens`, `prompt_cache_miss_tokens`, and the hit fraction
`hit / (hit + miss)` per response and as a token-weighted aggregate. Missing
usage and API errors are reported as unknown, not zero cache hits. Provider
caching is best-effort and may reflect requests outside this experiment.

The stage order is M0 protocol preflight, M1 same-prefix planning, M2 natural
next action, conditional M3 partial rollout, independent M4 evidence update,
and conditional M5 native trajectories. Each API stage is frozen before its
first call. No historical Atria or Qwen event is modified.

Execution and limitations are in `RESULTS.md`. The authoritative cache
aggregate, including the separately frozen M0b forced-choice diagnostic, is
`CACHE_USAGE_FINAL.json`; each stage event retains the original provider
`usage` object. M4 began before M3 because the M3 entry rule was initially
misread; the order deviation and M3 selection timing are recorded there.
