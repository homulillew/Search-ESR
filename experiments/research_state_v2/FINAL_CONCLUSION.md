# Search-ESR Research State v2: staged conclusion

## Decision

M1 passed; A1 failed. Stop before C1 and R1. Narrow Evidence Routing plus authoritative verification is a promising **existing Claim mutation** edge. Gap-driven Claim Admission remains unsafe because it often invents exact candidate-specific details from a thin prefix. The branch does not establish Actor or retrieval benefit for full State v2.

## Answers to the required questions

1. **Wide Delta failure from State Scope Expansion?** The concurrent W arm created 16 unrequested new Claims and had 19 unrelated mutation units; N created none and had one. Paired churn improved in 11 cases with no reverse worsening. This supports scope expansion as a major E1 mechanism, while W's one invalid cell is a limitation.
2. **Narrow routing recall?** 35/35 = 100%, with routing precision 35/41 = 85.4%.
3. **Final mutation precision?** N 38/39 = 97.4% versus W 35/54 = 64.8%; N recall 38/38 versus W 35/38. The 41 sibling packets are not independent observations.
4. **Conflict reopening?** Yes in `T7_186`: N committed C1 `supported → open` and reopened G1 after conflicting release-year evidence. W retained the old supported C1 under reject-and-retain verification. Identity equivalence remains ambiguous.
5. **NoGain zero mutation?** N preserved 8/8 T4 packets; W also preserved 8/8.
6. **Gap-driven admission less unrelated?** A1 G had 13/37 progress-appropriate Claims versus O 2/37, with 8 paired precision improvements and 1 worsening. Six invalid O cells partly confound this comparison.
7. **Most common Claim Admission error?** In G, premature unsupported specificity: 18/37 (48.6%). O more often copied local observations outside the Gap; it also had six anchor-schema failures. G redundancy was 1/37; undercoverage remained substantial (mean 35.4%).
8. **Fewer Claims with maintained coverage?** No. Both arms admitted 37 schema-valid Claims; G had higher mean coverage, 35.4% versus 8.3%, but it missed the 15% premature-Claim gate.
9. **Oracle State v2 improves Actor?** Not measured; C1 was prohibited by the A1 failure.
10. **Model State retains Oracle gain?** Not measured.
11. **State Construction loss?** Not estimable without C1 B0/B1/B2.
12. **Short-rollout Useful Evidence per Retrieval?** Not measured; R1 was prohibited.
13. **Verified Claim Growth?** Not measured in a rollout.
14. **Stale Gap reduction?** Not measured in a rollout. M1 mechanically retired closed active Gaps, but this is not a runtime outcome.
15. **Redundant Retrieval reduction?** Not measured.
16. **State Bloat controlled?** M1 prevented Observation-triggered new Claim expansion (0 N versus 16 W). A1 still admitted 37 G Claims, including 18 premature ones, so full lifecycle bloat is not controlled.
17. **Largest remaining bottleneck?** Claim Admission, specifically unsupported exact candidate commitment from a Gap-driven compiler. Existing Claim routing performed well; verification still had one false closure on a malformed meta Claim. Hypothesis, Frontier, Actor, source retrieval and Find/localizer bottlenecks were not causally tested here.
18. **Enter formal ESR runtime?** No. The A1 gate failed before causal Actor and rollout probes.
19. **Evidence for ESR-GRPO?** Insufficient. No reliable State v2 runtime or useful-evidence gain has been demonstrated.
20. **Hard Search/Find/Open gating?** Still prohibited. No C1/R1 evidence supports limiting tools.

## Mechanistic interpretation

The tested boundary is useful: Observation may route evidence to existing registered Claims, and the Verifier may authoritatively change their status, including reopening. This gave a high-precision state mutation path without generic `update_state`. It does not follow that a model can safely decide which new exact Claims deserve persistent status. In A1, a Gap made the model more focused but also encouraged unsupported exact answers to be encoded as open Claims. An open status is not enough protection when the Claim definition itself can steer source selection.

The next research edge, if pursued, is Claim Admission calibration: distinguish a question-anchored *test condition* from an invented candidate-specific fact, and require a visible basis for every specificity beyond the original question. This branch does not implement a new prompt or continue to later gates. Historical experiments and retrieval semantics remain untouched.

## Audit trail and limits

- M1: `claim_mutation/freeze.json`, `REVIEW_LABELS_V2.json`, `events.jsonl`, `results.json`, `RESULTS.md`.
- A1: `claim_admission/freeze.json`, `events.jsonl`, `REVIEW_PACKETS.json`, `REVIEWS.json`, `results.json`, `RESULTS.md`.
- Reviewer labels are single-reviewer, prefix-only and case-correlated. Two malformed qid-186 credit Claims were frozen as routing-positive but status-unscorable without changing the historical inputs; a sensitivity excluding both full cases leaves M1 precision 33/34 and recall 33/33 for N.
- DeepSeek `deepseek-flash`, provider `api.deepseek.com`, 0 retries. Every first-stage call and failure is preserved. No downstream C1 or R1 calls occurred.
