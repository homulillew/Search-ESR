# Pre-execution audit

- Fetched origin with prune. Remote baseline: `dd442dd62082e5923c98bd553b38fc4de3ad309d`, exactly the task's expected HEAD; no intervening commits or same-family new experiment.
- New branch: `experiment/recoverable-control-equivalence` from that remote HEAD.
- Prior result: A0 FAIL / A1 PASS / Joint FAIL; E2 NOT RUN. No historical artifact modified.
- Historical tracked files protected by SHA256: 19111. Existing unrelated untracked auto_research/, research_loop/ and user notes are outside this task.
- No applicable AGENTS.md found in workspace ancestors or experiment tree.
- Task's thresholds/data are already exposed. Freeze is for reproducibility and prospective Selection; E0 is explicitly retrospective reanalysis.
- D2-only selection reference cannot be numerically reused on A0. A0 frontier metrics are unavailable; this does not affect primary A1.
- Paid authorization: absent for this new experiment under TASK46. E0 is offline. E1 preparation is authorized; paid dispatch remains disabled until a new approval.
- Academic-research-suite experiment workflow applied inline for provenance, monitoring and reproducibility. User's explicit implementation/analysis task governs code creation; no extra role agents or redundant approval for offline analysis.
