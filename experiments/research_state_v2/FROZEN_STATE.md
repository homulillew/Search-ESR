# M1 pre-call freeze

The M1 case bank, repaired reviewer labels, closure rules, rubric, prompts, request hashes, source hashes, deterministic case/arm order, provider/model, no-tool schema, zero-retry failure policy, sample count, and gate are recorded in `claim_mutation/freeze.json` before any new model call. The frozen base Git HEAD is `bf8eb3262da99a5a29b3b133ed89e2d04f6e755f` from `origin/experiment/transactional-research-progress`.

`CASES.json` is byte-identical to the historical 41-case bank. The historical experiments remain untouched. Any later stage requires its own pre-call freeze and passing preceding gate.

A1 began only after the M1 gate passed. Its separate pre-call freeze is `claim_admission/freeze.json`, anchored to Git HEAD `1bb40be287fa2925a9352e45bd8d0ea9768d87e9` and containing the 24-case order, paired requests, prompt/source/schema/rubric hashes, DeepSeek provider/model, zero-retry policy and gate. The A1 gate failed; no C1 or R1 freeze was created.
