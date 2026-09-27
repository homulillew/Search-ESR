# Claim–Requirement Support Alignment

**Preparation snapshot: E0 complete, E1 frozen, waiting for a fresh E1-only authorization. Zero model calls.**

Branch: `experiment/claim-requirement-support-alignment`.
Base: `origin/experiment/state-conditioned-residualization` at `fc799239d41e0abd6b8306cc09f9e3b7a2126586`.

## Prepared artifacts

- [Protocol](PROTOCOL.md), [gates](GATES.json), [audit](PRE_EXECUTION_AUDIT.md).
- [E0 bank report](e0_reference/BANK_REPORT.md), [Claim roles](e0_reference/CLAIM_ROLE_REFERENCE.json), [support scope](e0_reference/SUPPORT_SCOPE_REFERENCE.json).
- [Actual E1 requests](e1_support_alignment/SCHEDULE.json), [call estimate](CALL_ESTIMATE.json), [freeze](FREEZE.json).
- [Offline validation](analysis/PREPARATION_VALIDATION.json), [integrity](analysis/INTEGRITY.json).

24 Parent–State cells / 16 natural snapshots / 9 qids; 12 Z, 7 P, 5 F. Coverage falls short of the >=10-qid target because only9 eligible qids have nonempty Claims in the supplied bank. No fabricated tenth qid. 82 cell×Claim annotations:18 support,28 binding,33 background,3 irrelevant. Six ambiguous cells are flagged before calls and retained in primary scoring.

## Actual call estimate

E1: **96 calls** =24×2 arms×2 replicates. DeepSeek `deepseek-flash`, temperature0, JSON, max_tokens omitted, max_retries0, at most8 concurrent requests. Frozen message text is339,192 characters; rough character-based input-token range67,838–113,064, excluding framing and generated output. This is not a price/spending estimate. Usage and token-weighted DeepSeek cache hits will be recorded from actual responses.

TASK20 requires new explicit approval after freeze/commit/count; earlier API permissions do not apply. E2 is **not included**: up to192 planned slots, exact send count depends on accepted E1 outputs, a sealed safety gate and a separate request freeze/authorization.

## Reproduce offline checks

```bash
python -m unittest experiments.claim_requirement_support_alignment.test_harness -v
python -m experiments.claim_requirement_support_alignment.run audit
```

Preparation scripts create exclusive files and intentionally refuse overwrite. Replaying tests/audit is read-only apart from temporary test files and Python bytecode. Gold and request reconstruction are deterministic; synthetic scoring fixtures are not model results.

## After new E1 authorization

Record the actual approval text/time, `stage: E1`, `maximum_attempts: 96`, `authorization_scope: E1 only`, current TASK/FREEZE SHA in `AUTHORIZATION_E1.json`, then commit it. This record documents consent; it cannot create consent. Never manufacture it from previous permissions.

```bash
python -m experiments.claim_requirement_support_alignment.run execute
python -m experiments.claim_requirement_support_alignment.run export_review
```

Single task-familiar semantic reviewer reads masked PACKETS only (no provider reasoning), supplies all JUDGMENTS per PROTOCOL, then runs `seal_review`, commits sealed review and raw outputs, and runs `python -m experiments.claim_requirement_support_alignment.score`. Report actual performance, failures, cache accounting, replay checks and stage gate. Initial STATUS/validation files remain frozen preparation snapshots; actual execution state is in RUN/ACCOUNTING and subsequent stage reports.

If unsafe S1: stop. If safe: prepare actual dependent E2 requests and seek its separate approval. Even if all gates pass, stop after E2. No retrieval, bootstrap, Writer, persistent fields or task-node changes in this experiment.

No model-result conclusion is available yet. The final18 research questions in TASK41 remain pending E1 and conditional E2 observations.
