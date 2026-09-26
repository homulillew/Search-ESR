# Protocol

Follow the user specification archived in TASK.md. No model/backend/schema expansion, repairs, retries, resampling, or hard gating. Canary has 24 unchanged historical contexts and no tools. Admission target six real packets per qid; preserve shortfalls. Freeze semantic atoms before replay. Uc semantic prompt/context is byte-identical to v2; U1 adds the exact producing Gap and supplied selective-admission semantics. G4 and G5 remain conditional. The initial audit and all live-stage freezes must be committed before calls.

Failures: transport_structural_failure, harness_control_violation, semantic_failure, provider/API failure, length/incomplete failure, tool failure. keep/clear statement invariant is exactly v2 (no new rule silently introduced). Existing registry checks enforce prebatch references. Semantic validation is offline and never repairs state.
