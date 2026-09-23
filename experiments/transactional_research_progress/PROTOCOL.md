# Transactional Research Progress protocol

Base: `origin/experiment/research-progress-frontier` at `eb5bddaf2e901db51c7e12b33bd4ff97fce2d204`. Historical experiments are read only. The three layers are an append-only WorldLedger, versioned VerifiedProgress (Claims/Gaps), and a disposable ControlProjection (one active gap, source type, uncertainty, optional target). Hypotheses do not enter committed state merely by being mentioned.

The stage order is E1 transition → gate → E2 free frontier → gate → E3 paired actor → gate → E4 short rollout. A failed gate stops the sequence and creates a downstream `NOT_RUN.md`. All new model calls use the frozen DeepSeek `deepseek-flash` profile with `max_retries=0`; errors are retained. No backend or localizer changes, training, initial query module, or hard tool masks occur here.

For deployable transactional arm C, a proposed semantic status transition is mechanically validated, verified on the exact cited observed excerpt, then committed with a new version. New claims start open. A rejected closure keeps the previous committed status. Evidence identity and raw observations remain append only. Arm B is an intentionally unsafe ablation that commits a mechanically valid Delta without semantic Verify; the protocol invariant requiring Verify is evaluated through B versus C, not assumed in B. Arm A is a full-rewrite comparator, checked only for JSON/schema/ref validity.

Prefix-only reviewer labels are fixed before model calls. E1 compares A/B/C on the same previous state and new observation with rotating order. Repeated claims and source siblings are clustered by qid; the bank is a diagnostic sample, not an independent population survey. Later stages are designed only if earlier gates pass.
