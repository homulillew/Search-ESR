# Freeze rule

Each executed stage records pre-call Git HEAD, provider/model, prompt and
schema hashes, case IDs and order, qid/checkpoint, Question/Gap/Claim/W hashes,
review labels, rubric, arm order, gate and zero-retry failure policy. A gate
checks all frozen inputs before a model call. Historical experiments are never
rewritten. Failed calls and malformed outputs are retained and scored.
