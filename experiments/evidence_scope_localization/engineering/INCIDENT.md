# R1 harness incident and proposed compatibility fix

## Observed failures

Three frozen historical contexts encode Recent Attempts as an opaque dictionary
of provenance fields rather than a list: `K_VP01`, `N_VP08`, `N_VP15`.
The original runner restored their Workspace successfully but called `.append`
on the dictionary **after** executing and saving the first tool result.

Nine trajectories ended with `AttributeError`: K_VP01 A0/A2/A3, N_VP08 A0/A1/A2,
N_VP15 A0/A1/A2. All nine actually returned exact evidence in that first action.
Their evidence successes therefore count under the **pre-existing** any-evidence
rule; the report also gives failure-free operational and paired sensitivities.
The interrupted decision 2, subsequent behavior and full-horizon cost are unknown.
Raw observations are preserved in RESULT.json; no successful completion is claimed.

Two other trajectories failed response schema validation before any tool:
K_VP01 A1 and K_VN09 A0 included an extra `type: json_object` property. All 156
HTTP responses were 200. These are schema failures, not API timeouts. They count
as failures; no repair, retry or replacement sample was made.

The preflight verified document restoration, tool handles and raw bytes but did
not exercise the attempts update against every legacy shape. This was an
engineering omission. It is independent of the model's scope choice, but does
limit operational conclusions and cost comparisons.

## Effect on the comparison

| Failure-free common cases | A1 | Comparator | A1 only / comparator only |
|---|---:|---:|---:|
| K vs A0 | 7/8 | 8/8 | 0 / 1 |
| K vs A2 | 8/9 | 9/9 | 0 / 1 |
| N vs A0 | 4/6 | 4/6 | 0 / 0 |
| N vs A2 | 4/6 | 4/6 | 0 / 0 |
| Challenge vs A0 or A2 | 5/5 | 3/5 | 2 / 0 |

Excluding failures is a sensitivity, not the formal denominator. It does not
reverse the lack of a fresh A1 benefit. Treating every runtime failure as overall
operational failure gives K A0/A1/A2/A3 = 8/8/9/8 successes out of ten, and all
N arms = 4/8. These operational figures must not be confused with returned-evidence
success (9/8/10/9 and 6/8).

## Reusable fix, no historical mutation

`attempts_compat.py` preserves a list history or the original dictionary fields,
and appends real actions to a separate `current_run_attempts` list when necessary.
`FUTURE_RUNTIME.patch` is an exact two-site integration patch against the frozen
runner. It is **not applied to the R1 runner**: doing so would invalidate its code
freeze. A future run must apply the patch in its own frozen stage/version.

`python experiments/evidence_scope_localization/engineering/check_attempts.py`
verified two successive updates for all 23 actual contexts, original-input
immutability, retained legacy provenance and correct action ordering; the patched
runner compiles. The regression check uses zero API/retrieval calls. It is not a
claim that a corrected live experiment has been run.
