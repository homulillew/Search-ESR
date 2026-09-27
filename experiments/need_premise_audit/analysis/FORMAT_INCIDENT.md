# V0 JSON-mode integration incident

## What happened

All44 frozen V0 requests returned HTTP400 with this provider error:

> Prompt must contain the word 'json' in some form to use 'response_format' of type 'json_object'.

The task-supplied V0 system prompt said `Return only:` before its object example and did not contain the literal `json`. V1's supplied prompt did. Requests used JSON mode in both arms. The pre-call tests checked exact task text, schema, reference IDs, failures and gates, but **missed this provider input requirement**. This was Codex's integration/preflight omission. It is neither a model reasoning failure nor a defect attributable to the user.

No V0 model output was produced. There is no valid V0 detection, specificity, agreement or comparative-effect estimate. METRICS.json retains zero success counts for failed planned slots under the frozen denominator rule; **those zeros are execution outcomes, not measured verifier accuracy**. In particular, the arithmetical `V1_balanced_accuracy_not_below_V0=true` is scientifically uninformative with a missing control arm.

## Preservation and correction

All44 rejected requests/responses are retained with request IDs and original frozen payloads. The run's registered access/billing halt covered401/402/403, not400; the fixed schedule completed without alteration or retry. No later V0 replacement, best-of selection, changed primary denominator or revised prompt is hidden in the results.

The minimal mechanical correction is `Return only:` → `Return only JSON:`. The exact proposed text is archived in `FORMAT_CORRECTION_PROPOSAL.json`. `json_mode_precheck.py` is a read-only preflight guard: it catches all44 original V0 payloads and accepts all44 V1 payloads and all88 hypothetical corrected payloads without network access. The proposal adds no target/presupposition decomposition to V0. The guard and proposal are new diagnostic artifacts; the historical request files and frozen prompts are unchanged.

This proposal was **not executed**. V1 independently fails recall, specificity, distinction, binding and exact replicate-agreement thresholds. Therefore another paid V0 batch could not make the existing V1 pass its absolute gate. The task forbids adaptive prompt changes/replacement after outcomes and closes E1 here; there is no repair/fresh progression. Any later separately registered experiment must integrate the input guard before its first request.

V0 rejected responses contain no usage. Their billing cannot be inferred to be zero; accounting totals/cache rate are explicitly limited to the44 V1 usage records. No currency amount is invented.
