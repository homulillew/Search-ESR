# Research State v2 staged experiment

Run M1, then gate A1, C1, and R1 in that order. A failed gate stops every later stage and requires `NOT_RUN.md`. Historical experiment inputs and outputs are read-only. No generic state updater, retrieval backend modification, hard tool gating, or full rollout is allowed.

M1 compares concurrent W (the prior Delta plus triggered Verify protocol, unchanged) and N (Evidence Router plus authoritative Claim Verifier) on the same 41 historical packets. One request per case per arm, alternating arm order; zero retries. The router may select existing Claims and observed refs only. Its selections trigger separate semantic verification. The harness commits verifier status even if that status is `open`, applies frozen `all_supported` gap rules, and retires closed active gaps.

Primary gate: routing recall ≥ .90; N final mutation precision ≥ .85 and recall ≥ .90; T4 NoGain preservation ≥ .90; at-risk false closure ≤ .10; paired N-vs-W unrelated churn improves in ≥ 6 cases with reverse worsening < half improvements. Provider and schema failures stay in denominator. See `claim_mutation/RUBRIC.md` for scoring details.
