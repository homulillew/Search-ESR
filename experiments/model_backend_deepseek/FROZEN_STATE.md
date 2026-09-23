# Preflight state

Provider: `deepseek-flash` at host `api.deepseek.com`, OpenAI-compatible Chat
Completions API, 240-second timeout, zero SDK retries. Credential source is
ignored `.env.deepseek` / `DEEPSEEK_API_KEY`; the value is not recorded.
The model was listed by the authenticated `/models` endpoint and returned a
minimal `PONG` chat response before this experimental branch was created.
Those smoke calls are connectivity checks, not M0 experimental samples.

`BASELINE_FINGERPRINTS.json` locks the 13 prefix packets, Codex's
single-reviewer prefix labels, original M1/M2 Qwen events and scoring, eight
M4 evidence cases and their rubric, and the two completed Qwen M4 cells.
The DeepSeek arm must verify these fingerprints before each paid stage.
No Atria model response is treated as a DeepSeek observation.

Per [DeepSeek's Chat Completions usage schema](https://api-docs.deepseek.com/api/create-chat-completion/),
`prompt_cache_hit_tokens + prompt_cache_miss_tokens = prompt_tokens`.
The experiment reports the token-weighted hit fraction only when both
fields are present and consistent. The provider's [context-cache guide](https://api-docs.deepseek.com/guides/kv_cache/)
says cache matching is automatic and best-effort; experiment requests are not
artificially warmed or reordered to inflate a hit rate.
