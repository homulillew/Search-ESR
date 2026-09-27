# Gold Obligation → Evidence Gap

Independent development mechanism test: frozen human-scoped O + unchanged historical C → three-field ephemeral gap. G0 primary; G1 adds original H. 27 natural snapshots, 108 planned responses. No search or persistent state change.

Preparation: `python -m experiments.evidence_gap_gold_obligation.prepare prepare`

Tests: `python -m unittest experiments.evidence_gap_gold_obligation.test_contracts -v`

Freeze: `python -m experiments.evidence_gap_gold_obligation.prepare freeze`, commit, then `python -m experiments.evidence_gap_gold_obligation.run execute` once. Export masked review, commit all first-pass labels, perform pair/H review, then score. Calls are never resumed or resampled.

See PROTOCOL.md and TASK.md for scope and immutable gates. Final result is in analysis/FINAL_CONCLUSION.md after completion.
