# Stage freezes

Each stage has its own `freeze.json` written before its first real call. The
freeze pins git HEAD, case IDs and ordering, qids/checkpoints, prefix/TestCard/
observation/query hashes, provider/model and schemas, relevant source and
retriever/index hashes, rubric, gate, and zero-retry failure policy. A stage
runner checks its freeze before execution and records all errors.
