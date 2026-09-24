# Pre-call freeze

V1 was frozen in `test_representation/freeze.json` from remote base HEAD `55fd5e067e49baadee3968bbc55ebac4e35f5054`. It records the 30-case/11-qid bank, exact prefixes, normalized SemanticGap and explicit hypothesis hashes, question anchors, private review requirements, prompt/schema/source/request hashes, rotating order, DeepSeek `deepseek-flash`, no-tool schema, zero-retry failure policy, and all gate thresholds. The 16-case/8-qid V2 source-uncertainty selection was saved and hashed before V1 model calls.

Historical `experiments/transactional_research_progress/` and `experiments/research_state_v2/` are read-only. Each later stage, if eligible, requires its own pre-call freeze. Failed gates stop later stages without calls.
