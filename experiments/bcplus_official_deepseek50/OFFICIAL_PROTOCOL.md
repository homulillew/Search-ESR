# Official BC+ tool rerun protocol

This rerun uses the same 50 frozen questions as `bcplus_native_deepseek50`. The
new online agent receives only the question, never the gold answer or prior
trajectory. The original batch remains unchanged.

## BC+ components used verbatim

- `BCPlus/upstream/searcher/searchers/faiss_searcher.py`: `FaissSearcher` with
  the official Qwen3-Embedding-8B index, query prefix, normalization, EOS
  pooling, and the official `Tevatron/browsecomp-plus-corpus` dataset.
- `SearchToolHandler` from `BCPlus/upstream/search_agent/openai_client.py` is
  compiled unchanged from that file's class definition. The upstream module
  eagerly imports unrelated BM25/Pyserini code, so the class is loaded in
  isolation. The FAISS module is loaded in isolation for the same reason.
- Official tool defaults: `search(query)` only, fixed `k=5`, and a 512-token
  snippet for each hit using the Qwen3-0.6B tokenizer. `get_document` is not
  registered.
- `QUERY_TEMPLATE_NO_GET_DOCUMENT` from the upstream `prompts.py` is the sole
  user prompt. No system prompt is added.
- The official `GRADER_TEMPLATE` and `parse_judge_response` from
  `scripts_evaluation/evaluate_run.py` are used for Qwen3-32B primary scoring.
  The official decoding parameters are temperature 0.7, top_p 0.8, top_k 20,
  and 4096 maximum output tokens, with thinking disabled.

Source and index hashes, selected qids, provider settings, and the offline
retrieval preflight are retained in `FREEZE.json`. `JUDGE_FREEZE.json` is made
only after all 50 online runs finish.

## Transport and host constraints

The underlying model remains DeepSeek Flash with thinking enabled. Its API
transport uses Chat Completions, so only the official Responses API tool schema
envelope is translated; the function name, description, parameters, and strict
flag are unchanged. DeepSeek's beta endpoint is used because the provider
requires it for strict tool calls. The 50 independent API sessions, serialized
retriever, zero SDK retries, and 200-round emergency cap follow the previously
authorized experiment settings. No best-of or failed-qid replacement occurs.

The installed Tevatron defaults to FlashAttention2, which is unavailable with
this host's Torch/CUDA build. Its official `DenseModel.encode_query` and FAISS
search run with SDPA attention instead; no embedding weights or search policy
are changed.

The official Qwen3-32B judge is accessed as hosted `qwen3-32b` through the
available OpenAI-compatible API. The upstream evaluator uses local vLLM, so
the judge runtime is a documented difference. Scores here describe this
50-question project run, not an official BC+ leaderboard submission.
