# Additive resume record

The user interrupted the active turn while the frozen alias batch was
running. The operating process was terminated. `events.jsonl` retains two
completed cells (`546:9:AL`, `1094:69:AL`) and an incomplete third
(`1094:77:AL`, API request for decision 3 without response). An explicit
`cell_interrupted` event was appended. `1094:93:AL` had not begun.

The two completed cells remain the sole samples for those checkpoints. The
partial 1094:77 attempt is a recorded interruption, **not** an outcome and
will not be used in the mechanism denominator. One new attempt will be made
for each of the two incomplete cells, using exactly the frozen executor,
request and checkpoint order. This selection is mechanical based on missing
`cell_end`, not on whether the partial trajectory looked promising. It is
neither a selective replicate nor best-of. The original partial events are
not deleted or overwritten. The resume script writes a separate event file,
with its own pre-call freeze and gate. No protocol code, state text or
checkpoint is changed.
