# BC+ Candidate Discovery vs Constraint Verification

Base: origin/experiment/asymmetric-progress-closure-audit at 453161c2d2335416d4f439f9419e85c2266658b5, fetched and checked before branching. Branch: experiment/bcplus-discovery-verification.

## S0 (before new calls)

Ten named historical questions plus the ten smallest numeric remaining qids in the real BC+ QA file. Classification uses Original Question only. Related attributes may remain one semantic relation, so counts depend on grouping. Ambiguous thresholds are excluded from primary verification. Single Codex reviewer; prior familiarity with the ten historical questions is disclosed. No independent-review reliability claim.

All gold_resolved=true states in Dynamic Progress and Asymmetric Progress primary/challenge banks are audited, deduplicated by exact Q plus ordered Claim statements. Hypothesis, observed but unadmitted text, and gold answer do not fill coverage. New artifacts retain old labels and occurrence provenance. Historical files are immutable.

## S1/S2 design

One trajectory per frozen unit; no retry or replacement. S1 supplies a provisional Candidate and exactly one explicit hard condition. S2 starts from real historical checkpoints without supported candidate identity and supplies no candidate. S1 horizon two decisions, S2 three, one action per decision. All Search/Find/Open remain available; global search k=5 and existing raw-window mechanics are unchanged. No semantic source filter, reranker, extra localizer, or gold stopping.

U1 Writer is byte-identical to goal_residual_control_v3_1/prompts/state_updater_gap_conditioned.md. One Writer call per returned window, in returned order; max two new Claims per call; no researcher-written Claims. S1 Current Research Gap always verifies the frozen condition for the candidate. S2 uses the Actor's current discovery gap. Hypothesis remains provisional. Old windows remain available in Workspace. An Actor stop ends this bounded task, not whole-question closure.

All semantic evaluations are offline, separately from runtime structural checks. New observations and claims must be reviewed for exact relation, subject, date/scope, and unsupported strengthening. Absence is never falsification. Candidate replacement by a different hypothesis is recorded separately from the required clear operation.

## Gates and failure policy

Concrete denominators and integer gates are fixed in bank/SELECTION.json before calls. Required minimum rates: V+ 80%, V− 75%. Compare average executed actions and restricted successful-update cost (failure=budget+1); Verification must have both lower actual mean and at least 0.5 lower restricted mean than Discovery. Also report successful-only costs with selection bias caveat. Each failed/timeout/schema/tool run remains in denominator. No retry, repair, output replacement, or best-of sampling. Authentication rejection stops subsequent submissions.

S4 requires every S1/S2/S3 gate, including adequate real negative-bank size. S5 additionally requires S4. No model call for a gated-off stage. One optional exploration only after a formal failure, separately preregistered and bounded by 12 units/24 total API calls.

## Interpretation and runtime boundary

This is a small, selected, qid-clustered diagnostic; oracle single-condition verification and unrestricted discovery have different information and horizons. The comparison tests task asymmetry, not an IID treatment effect or universal significance. Positive-bank selection requires real support and deliberately conditions on answerable relations. A benchmark answer may fail an explicit condition; such corpus/benchmark conflicts are disclosed, never silently corrected.

Persistent semantic State is only Q + Claims + Hypothesis. Offline annotations, answer keys and reference evidence are never imported by the runtime. Frontier, if permitted, is ephemeral and cached by Hash(Q, Claims, Hypothesis); no persistent mode, requirement graph, confidence, semantic router, verify tool, or closure verifier.
