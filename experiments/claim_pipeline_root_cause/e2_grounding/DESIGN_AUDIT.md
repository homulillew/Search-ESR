# E2 design audit

## Material Passport

Mode: experiment execution. Sources: frozen corrected E1 run002 reviewer outputs and original historical candidates. New paid scope: E2 only. Source base: `343b5a3d2ff4e05ec04302be9eb35534b71b86a1`.

`git fetch origin --prune` confirmed the expected remote HEAD with no additional commits. This experiment uses a new isolated worktree and branch. Historical experiments, production runtime, Reader and all three semantic prompt files remain unchanged.

The original `freeze_e2_candidates` is imported unchanged. Recomputed: 35 pairs, 15 distinct Evidence inputs, 85 calls. D has 15 positives / 3 negatives; H_diagnostic has 15 / 2. Both strata have an identifiable source-negative opportunity. All five negatives are ambiguous, from only q435 (temporal binding) and q673 (attribution/modality). This sharply limits generalization.

Candidate truth is copied from source reviews and cannot change after model outputs. Gap relevance is never a Grounding truth criterion. No synthetic negatives, extra paraphrases, re-sampling, or confirmation cases are added. Historical C namespace issues do not enter these roles: no role accepts C.

The treatment changes information order/visibility and introduces an intermediate, potentially lossy inventory. Any result supports or fails to support evidence-first commitment separation; it cannot identify a psychological mechanism independently of representation loss and the extra model call.

The user's task explicitly authorizes code adapters and 85 paid calls. This authorization takes precedence over generic skill confirmation instructions. The academic-research-suite execution/review roles are performed inline; there is no paid probe or additional model reviewer.
