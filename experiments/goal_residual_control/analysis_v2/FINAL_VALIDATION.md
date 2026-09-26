# Final validation

- All 65 historical artifact hashes match; old G1/G2/FINAL are unchanged.
- All four stage freezes match their recorded code and request hashes.
- All 741 completed model requests match their archived hashes, with no duplicate submission within a batch; all responses identify `deepseek-flash`.
- All 30 G5 cells are terminal; 70 Actor calls, 372 Updater calls, 30 Reviewer calls and 110 tools reconcile with costs and raw records. Three decisions/two actions budgets hold.
- All admitted Claim proposals have explicit single-Codex-reviewer labels. Empty `keep` proposals add no Claim and are not included in precision denominators; no independent human-review accuracy is claimed.
- Corrected Search rediscovery counts independently match the `already_discovered` statuses in the raw backend audit for G3/G4/G5. Original G3/G4 metric files remain intact.
- All 42 final questions are numbered exactly once; all local report links exist.
- `git diff --check` passes. Production was not edited after stage freeze; no further live call or broad optional test run was needed for the analysis-only closeout.

The pre-live maintained suite passed 427 tests, and the later adaptive-controller check passed two tests. Root-level discovery of archived test copies had 19 collection errors; see the original offline validation record. This final accounting does not remove the documented L2 review-scheduling deviation or the limits of a small, single-reviewer diagnostic cohort.
