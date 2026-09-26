# Execution provenance: contract v2

The requested starting commands were executed against origin/experiment/goal-residual-control. Actual base was f53a43c9342fa643c117b9362dce1164abaf3e4a. Local experiment/goal-residual-control-contract-v2 was created and all freezes/calls began under that name. Frozen files retain the historical branch name as written at freeze time.

After G4 completed and G5 started, the first push to that name was rejected (fetch first). A read-only fetch revealed a concurrently created remote branch with independent commits d1c04fc and 9f19560 (Actor contract repair and G2v2 freeze), sharing the original base but a different implementation and overlapping artifact paths. No remote commit or result was overwritten, rebased, merged or force-pushed.

To preserve both independent histories and the exact running freeze, this local branch was renamed to **experiment/goal-residual-control-contract-v2-executed** and published there. Branch renaming does not change a commit, model input, freeze or running process. The other remote branch is not a source of labels, prompts or results for this run. All analyses here refer exclusively to the local frozen requests and actual archived responses.

## Commit sequence

- 4346276: isolated engineering contract repair, no live responses.
- db41eda: freeze G2v2 exact requests and object-level equivalence.
- 53d7c0a: downstream v2 adaptive runners and offline controller checks.
- 632db6f: G2v2 results (118/120).
- df78090: freeze G3v2.
- 9f2f8fe: archive G3 outputs before downstream execution.
- 52c335f: freeze G4v2.
- 0008756: G3 semantic progress review.
- f6feda0: G4 source-supported state review; no production repair.
- 67c7801: freeze G5v2.
- 9dad8ee: complete G4 raw outputs; G5 starts at this HEAD.
- a6c8868: G4 integrated decision/progress analysis.
- ecf6909: execution provenance and claim-scope interpretation.
- 51a4f6e: incremental semantic review and append-only G3 evidence-scoring correction.
- 7b7a9bf: all completed G5 raw requests, responses, intermediate states and terminal results; no final-analysis edits included.

G5 completed with 30 terminal cells (STOP, open horizon, or retained failure), 70 Actor calls, 372 Updater calls, 30 Reviewer calls and 110 tool actions. No re-run or output repair followed review. Final analysis and the search-status accounting erratum are committed after raw execution. The old G1/G2/FINAL and all frozen code/request hashes remain unchanged.

Main's existing authentication fix 8021aca was already an ancestor. No cherry-pick/merge was required; its latch was extracted and reused as documented in PROTOCOL_AMENDMENT. No Evidence Pointer state fields were imported.

During offline evidence review, Ding career support was split into separate professional-start and century/maximum-count atoms to prevent double-counting an overlapping second action. No aggregate G3/G4 Progress count changed. This is analysis bookkeeping, with no model, tool, source-pool or truth change.

In the clause audit, a dated film-role attribution is treated as one relational proposition; the two T17 claims were corrected from non-atomic to atomic (G4 atomic count 36/52). Source support, closure and progress counts are unchanged. Stage-specific evidence-label snapshots prevent later G5 alternative-source review from silently revising G3/G4 sensitivity estimates.
