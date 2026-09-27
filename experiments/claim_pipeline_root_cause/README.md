# Claim pipeline diagnostic harness

Status: **prepared offline; new authorization required; no causal results yet**.
See TASK.md section50, PROTOCOL.md, bank/manifest.json and READY_FOR_AUTHORIZATION.md.
Python3.11+,httpx,jsonschema,pytest; python-dotenv only for optional authorized key loading.
The repository environment already supplies these dependencies. No package install needed.

From the repository root:

```bash
python -m pytest -q experiments/claim_pipeline_root_cause/tests
python -m experiments.claim_pipeline_root_cause.runner preflight
```

These are offline. Bank preparation scripts are append-only build records: do not
rerun them into the frozen directory. Tests use temporary files and explicit mock
HTTP transports; no API key is read and no external request is sent.

## Future execution after a NEW user authorization

Record `AUTHORIZATION.json` only after the user explicitly authorizes this experiment.
Required fields: `authorized:true`, `stages:["E1","E2","E3"]` (or a narrower grant),
`freeze_sha256` of FREEZE.json, `authorized_at_utc` (timezone-aware, after the freeze),
and `user_message_reference`. Do not invent authorization or reuse standing authority.
No such file exists in this preparation commit. It never contains an API key.

Use a new output directory for every authorized stage. Existing directories/IDs
cannot be resumed or overwritten. `--account-available` is remaining account-wide
quota after other jobs; actual concurrency also respects stage readiness and cap256.

```bash
python -m experiments.claim_pipeline_root_cause.runner run E1 \
  --authorization experiments/claim_pipeline_root_cause/AUTHORIZATION.json \
  --out experiments/claim_pipeline_root_cause/e1/run001 --account-available 256
```

Runner produces RESULTS.json, raw request/response archives, accounting and blind
review packets. Review `review/source/` first with only Candidate+Observation;
freeze those labels before opening `review/relevance/`. Keep private_mapping.json
out of reviewer input. Each label keyed by opaque review ID must include:

```json
{
  "source_supported": true,
  "semantic_strengthening": false,
  "strengthening_type": [],
  "gap_relevant": true,
  "duplicate_with_C": false,
  "gap_useful_if_supported": true,
  "ambiguous_relation": false,
  "covered_atom_ids": [],
  "duplicate_group": null,
  "reason": "Source-relative review justification"
}
```

Atom IDs are taken from the frozen annotation only in the separate usefulness
pass. Type names use the eight families in bank/manifest.json. Do not label support
from an atom description. Any modified source/schema/prompt fails freeze preflight.

Analyze E1 with `runner analyze-e1 --run DIR --labels FILE --report FILE`.
Then `runner freeze-e2 --run DIR --labels FILE --e1-report FILE --candidates FILE
--out STAGE_FREEZE.json` mechanically deduplicates/stratifies candidates. It stops
if required source-label strata are absent. Do not fill the gap with invented claims.

Run E2 with `runner run E2 --authorization FILE --out NEW_DIR --candidates FILE
--stage-freeze FILE`. Review generated `inventory_review/source/` separately, giving
one `facts` entry (`source_supported`, `reason`) per commitment, plus
`omitted_observed_commitments` (list) and overall `reason` per opaque inventory ID.
Analyze using `runner analyze-e2 --run DIR --candidates FILE --inventory-labels FILE
--report FILE`. Candidate source labels remain those frozen before Grounding calls.

`runner freeze-e3 --e1-report FILE --e2-report FILE --decision FILE --out FILE`
requires complete valid stages and a full mechanism gate. It chooses components
mechanically and records report hashes. E3 uses only the reserved12 packets:
`runner run E3 --authorization FILE --out NEW_DIR --decision FILE --stage-freeze FILE`.
Review raw candidates in the same two-pass way, then `runner analyze-e3 --run DIR
--labels FILE --report FILE`. Do not invoke E3 merely because its budget is available.

After authorized execution, manually synthesize ROOT_CAUSE_CONCLUSION.md using all
17 questions in TASK section53. A result with undefined rates or failed requests
cannot be called a passed gate. Passing does not authorize production changes.
