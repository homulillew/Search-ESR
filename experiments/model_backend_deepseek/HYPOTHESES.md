# Pre-call hypotheses and stopping rules

M1: With identical prefix and diagnostic prompt, DeepSeek may identify the
unresolved need, expected source, scope and plausible local D# more reliably
than the fixed qwen3.7-flash baseline. The existing prefix-only labels and
rubric remain unchanged. The prior strong-signal threshold is at least four
more acceptable scopes out of 13, not all Stop, plus two improved source or
target judgments. Provider errors are separated from semantic outcomes.

M2: If DeepSeek explicitly plans Document scope, a natural next decision may
realize it as a valid `find(D#, query)` more often than Qwen. Single actions,
multi-tool batches, invalid calls, and provider failures are distinct.

M3: DeepSeek may exploit Orthogonal Search after no-gain Search more than Qwen.
Run a four-decision v3a × Orthogonal partial rollout only if M1 or M2 gives at
least moderate, interpretable model signal and M0/M2 tool transport is stable.

M4: Given the same exact source excerpt, DeepSeek may classify support,
refutation, inconclusive and irrelevant evidence and update candidate belief
more reliably than Qwen. This is an evidence-utilization upper-bound probe,
not evidence acquisition. Apply the existing eight-case labels and frozen
rubric without seeing the model outputs first.

M5: Run native qid 546/1094 trajectories only if M1–M4 establish a material
model mechanism difference and DeepSeek tool transport supports it. Never
expand to 10–20 questions on this arm without that signal.

Prompt-cache usage is descriptive provider telemetry, not a semantic success
metric or a cross-model token comparison. Report per-call hit/miss counts,
weighted hit fraction, missing usage, and response/error counts by stage.
