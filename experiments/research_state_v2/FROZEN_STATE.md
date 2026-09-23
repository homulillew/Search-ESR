# M1 pre-call freeze

The M1 case bank, repaired reviewer labels, closure rules, rubric, prompts, request hashes, source hashes, deterministic case/arm order, provider/model, no-tool schema, zero-retry failure policy, sample count, and gate are recorded in `claim_mutation/freeze.json` before any new model call. The frozen base Git HEAD is `bf8eb3262da99a5a29b3b133ed89e2d04f6e755f` from `origin/experiment/transactional-research-progress`.

`CASES.json` is byte-identical to the historical 41-case bank. The historical experiments remain untouched. Any later stage requires its own pre-call freeze and passing preceding gate.
