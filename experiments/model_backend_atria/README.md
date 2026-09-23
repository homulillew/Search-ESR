# Model backend intervention: Atria versus qwen3.7-flash

This branch studies the model/provider variable using the frozen Search–Find
checkpoint set from `../search_find_v3b/orthogonal_search/`. The first paid
stage is a tiny tool-protocol preflight. The next stage, only after a
prefix-only annotation freeze, is paired explicit planning on identical
messages. Later stages have separate prospective freezes and stop gates.

The active `.env` remains qwen3.7-flash. `provider.json` identifies the Atria
model and endpoint; the key is read only from ignored, mode-600 `.env.atria`.
No key is written to tracked artifacts. No historical v3a/v3b file is edited.

Historical Qwen results are fixed comparison evidence, not a new Qwen run:
v3a Find 0/88; Orthogonal P1 Find 2/13, 0/38 Find within two decisions
after no-gain Search, 11/13 cells searched again, and zero useful Find
evidence. See `../search_find_v3b/FINAL_CONCLUSION.md` and the raw events.

The 13 labels were reviewed from frozen request prefixes by Codex under the
user's clarified authorization. `ANNOTATION_REVIEW.md` records every changed
field; `ANNOTATION_FREEZE.json` hashes the resulting labels. This is a
single-reviewer diagnostic annotation, not independent human consensus.
