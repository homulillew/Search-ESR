# BC+ official-search DeepSeek Flash rerun

Primary Qwen3-32B answer accuracy: **34/50 = 68.0%**.
95% Wilson interval: 54.2%–79.2%.
Incorrect qids: 58, 160, 275, 283, 315, 366, 428, 471, 486, 715, 763, 936, 1036, 1090, 1119, 1152.
Judge skipped for missing agent answer: 283. Judge parse/API errors on submitted answers: none.

## Protocol

Same frozen 50 questions as the prior run. Vendored BC+ `FaissSearcher` uses Qwen3-Embedding-8B and the official corpus. The vendored `SearchToolHandler` exposes search only, fixed top 5, with 512-token snippets using the Qwen3-0.6B tokenizer. The agent receives the upstream `QUERY_TEMPLATE_NO_GET_DOCUMENT` prompt. DeepSeek Flash thinking mode uses 50 independent sessions; the retriever is serialized. No API retries, question replacement, or best-of selection.

Qwen3-32B uses the upstream grader prompt and parser, temperature 0.7, top_p 0.8, top_k 20, max output 4096, thinking disabled. It runs through a hosted OpenAI-compatible endpoint because the unquantized model does not fit the available local GPUs; this runtime differs from upstream vLLM.

The DeepSeek adapter translates the upstream Responses tool schema into Chat Completions and uses the provider beta endpoint for strict tool calls. The Tevatron encoder uses SDPA attention because FlashAttention2 is unavailable on this host. These transport/runtime details are recorded in `FREEZE.json`.

## Run statistics

Statuses: {'natural_answer': 49, 'RUN_FAILED': 1}. Peak API concurrency: 50. Agent wall time: 877.5s.
Search calls: 3176 total, median 54.0/question. Tool rounds: median 38.0, p90 103.0, max 147.
DeepSeek tokens: 344,290,253 input, 1,219,076 output. Estimated DeepSeek cost: ¥20.2472 (usage-based estimate, not billed amount).
Official evidence-qrel mean recall across 50 qids: 83.1%

The earlier Search/GetDocument run scored 46/50 by a different judge. Its tool access and scoring differ, so the two percentages do not isolate a single causal effect.
