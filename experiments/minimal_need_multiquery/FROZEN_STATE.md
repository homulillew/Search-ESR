# E1 development freeze

- Remote inspected after fetch: `origin/main = 8021aca19a1ee5201730e40b338012c65ecd51cf`.
- Research base/local and matching remote: `05d2eeec297c06ce7fa8d2cdd40bc7acb676b88c`.
- New branch: `experiment/minimal-need-multiquery`.
- Base contains remote main; no research history discarded or rewritten.
- Provider/model: `https://api.deepseek.com` / `deepseek-flash`; temperature 0, JSON mode, stream false, retries 0, max_tokens omitted, HTTP inactivity timeout 240s.
- E1: 18 exposed natural states, 9 qids, 8 No-H; four arms; one response; 72 planned calls; zero tools.
- B0: byte-identical old B5 prompt and historical request payload. B1/B2/B3 only append exact task rules.
- Constant `decision: research` is a compatibility envelope; `need` is the only variable semantic field.
- `FREEZE.json` records file hashes for protocols, prompts, bank, source provenance, schema/rubric, schedule, code and accounting estimate.
- The first commit containing that manifest must precede execution. `analysis/PREPARATION_RECEIPT.json` records that exact commit after it exists. A real `RUN.json` records actual execution HEAD and manifest digest before first send; dry run is not a request.
- No real-call authorization in this preparation. Status: `PREPARED_FOR_REAL_RUN` after offline verification.

## Failure policy

No retry, semantic repair, sample replacement, best-of, failed-cell deletion, existing-directory overwrite or implicit resume. First scheduled call serves as formal auth check; typed 401/403 blocks unsent cells. Timeout, HTTP, invalid JSON/schema, empty/length/model mismatch and interruption are retained. Unknown usage remains unknown. Future credentials or transport changes require explicit version/freeze; they do not replace failed records.

## Gates

Only E1 development v1 is request-ready. No automatic progression from this freeze to fresh, E2, E3 or E4. Each requires its own qualified bank and pre-call commit. E1 development failures trigger analysis and at most one bounded revision. E1 fresh gate is conjunctive and uses all planned cells; it is not a statistical significance threshold.
