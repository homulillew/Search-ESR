# E1: Full Rewrite versus Delta versus Delta + Verify

The pre-call freeze names commit `721e37c`; offline gate 7/7 passed after a separately recorded pre-call tuple/list serialization correction. All **123/123** A/B/C Updater requests returned provider responses. Two C responses violated the new-Claim schema (`new_claims` attempted a status other than `open`); they were retained as invalid, without repair or retry. The C protocol made **42** triggered Verify requests, all of which returned. DeepSeek reported Updater prompt cache hits/misses of 42,235/83,955 tokens (33.47% weighted hit rate) and Verifier 1,792/24,057 (6.93%).

| Frozen metric | A: Full Rewrite | B: Delta | C: Delta + Verify |
| --- | ---: | ---: | ---: |
| Correct / all committed mutation units | 36/52 | 36/69 | 36/60 |
| Mutation precision | 69.2% | 52.2% | 60.0% |
| Mutation recall | 94.7% | 94.7% | 94.7% |
| Cases with unrelated-state churn | 10/41 | 19/41 | 14/41 |
| Frozen-label false-closure cases | 4/41 | 4/41 | 2/41 |
| NoGain preserved | 8/8 | 8/8 | 8/8 |
| Narrow ActiveGap retired | 0/4 | 4/4 | 4/4 |

The paired churn comparison is unfavorable to Delta: B versus A improved **2**, worsened **14**, tied **25**; C versus A improved **4**, worsened **10**, tied **27**. C's at-risk frozen-label false closure was **1/17**; semantic audit identifies that qid-186 case as mislabeled because the observed source actually supports the credit Claim. C's correct refs among its committed claim status changes were **34/34**; the most common issue was unnecessary extra Claim creation and broad Gap mutation, rather than invalid W references. C had 17 unrequested new Claims, B 18; the post-call audit cautions that these are mostly text-supported and should not be called unsupported evidence promotion.

The preregistered gate result is **G1 fail, G2 pass, G3 fail, G4 pass**. G1 required at least four paired reductions in unrelated churn with reverse worsening below half the improvements; neither Delta arm met it. G3 required C mutation precision ≥80%; observed 60%. The qid-186 label defect cannot be silently repaired. Excluding both affected cases still leaves G1 and G3 failed, as detailed in `POSTHOC_AUDIT.md`. Accordingly E2–E4 are stopped.

Interpretation: the clean input lets all three arms close many directly supported/refuted target Claims, and C's verifier can block some unjustified transitions. This does not establish that transactional Delta is a better state-maintenance protocol than Full Rewrite. A/B/C all preserved the eight NoGain states, so the hypothesized NoGain advantage did not appear. The model's Delta often expanded the State with additional observed facts even when the narrow update did not require them. This bank used reviewer-authored previous states and correlated source siblings; T7 has only one medium-ambiguity conflict case. The E1 gate is a mechanism stop rule, not a general statistical test.
