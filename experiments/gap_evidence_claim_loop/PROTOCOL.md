# Gap → Evidence → Claim

This branch studies whether a semantic Active Gap helps a reader select new,
observed facts before any persistent Claim is created. The sequence is F1
finding extraction, conditional F2 verifier and minimal Claim commit, then
conditional F3 single-Gap short rollout. Historical branches remain append-only.

Research State is only original Question, committed factual Claims, semantic
Active Gap and an optional historically observed Working Hypothesis. Raw tool
observations and source handles belong to WorldLedger/Workspace. A Finding is
temporary, cites the current W, and must be supported by that W. A Claim is
created only after Verify and has exactly `claim_id`, `statement`,
`evidence_refs`, `version`. No pre-evidence open Claim or TestCard lifecycle is
introduced. Query arguments are not evidence.

F1 uses 41 exact historical Observation transitions from State v2 M1 (12
qids). Four T6 cells carry controlled, independently source-supported seed
Claims from the historical closure review, giving duplicate-evidence probes.
Their prior and new W may be the same source shown twice; this is disclosed
and tests redundancy, not novel retrieval. Every source excerpt is copied
without editing. Semantic Gaps and single-reviewer labels are frozen before
the first model call. F1 arm A sees Question+W; B adds Gap; C adds Gap and
committed Claims. All use one `deepseek-flash` call, zero retries and 0–3
Findings. Failures remain in denominator. F2/F3 have independent freezes only
if their prerequisite gates pass.
