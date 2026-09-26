# Frozen state

Remote base verified at 2d0c55995badd14ab4bc8241ca9caa97a1eef3a1; new branch experiment/goal-residual-control.

G0: bank/freeze.json pins 40 snapshots, 20 transitions, 10 qids, 29 exact source-window records, historical input hashes and private truth. No new model call preceded selection, source audit or annotation.

Model: DeepSeek deepseek-flash at https://api.deepseek.com, timeout 240 seconds, max_retries=0. Secrets remain in the existing local credential file and are never copied into artifacts. Four concurrent calls at most. Cache hit/miss tokens are archived for every response.

Each stage's freeze.json pins committed input requests or adaptive request construction and all relevant code/prompt/schema hashes. See PROTOCOL.md for stage sizes, horizon, counterbalancing, failure policy, stopping and sensitivity definitions. Source audits and historical results remain immutable after first call.
