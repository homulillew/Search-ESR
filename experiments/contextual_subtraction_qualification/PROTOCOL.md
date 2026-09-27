# Contextual Subtraction Qualification — frozen E1 protocol

## Material Passport

User-directed code mechanism experiment. Base50f11b58a554223d8c2ac91a2d0ec8ad41dc1289. Branch experiment/contextual-subtraction-qualification. Gold certificates/reference policy committed at6776c897 before any new model call. Historical experiments are immutable. One task-familiar Codex reviewer; no independent-review claim.

## Hypotheses and scope

H1/H2: interpreting a candidate locator in its governing Parent context avoids accepting locally true but contextually unbound facts. H3: multiple observed Claims can jointly establish a condition. H4: a later high-recall proposer plus strict qualifier may combine safe precision and recall, conditional on E1 success. E1 tests only frozen candidate qualification; no proposer, residualizer, retrieval, Writer, Bootstrap, graph, training or persistent-state write.

## Bank and semantic reference

48 certificates from the same24 Parent–State cells,16 snapshots,9 questions.22 positives,26 negatives:15 binding missing,6 qualifier incomplete,5 background/irrelevant. No invented Claim text. ClaimSets have1–3 actual current Claims. A certificate exposes only its specified subset; withheld current Claims cannot supply a missing operand. Exact Parent substring locators never become standalone propositions in Q1.

Full dependency/reference decisions, false-full-risk registry and three predeclared ambiguities are in e0_reference/REFERENCE_POLICY.md and CERTIFICATES.json. A condition inherits its own necessary dependencies; independent unresolved conjuncts do not become prerequisites to every partial fact. Task explicitly requires clinical-history, Ding-marriage and local DLC positive certificates while preserving their other unresolved obligations. Q1 receives none of these annotation explanations or task-specific examples.

Certificates with overlapping evidence/locators are correlated. Main unit is certificate×replicate; report by question/category/replicate and descriptive paired contrasts. No inference based on192 independent questions or fresh validation. Keep the three ambiguous references in primary scoring and show exclusion sensitivity separately.

## Arms and actual requests

Q0: locator + candidate Verified Claims only. Generic standalone-fragment prompt, no Original Q/Parent or metadata.
Q1: Original Q + full unchanged Parent + same locator + same ClaimSet. System prompt is exactly user TASK13 (line endings normalized for API text). No hardcoded task types, examples, named gates or requested dependency checklist. Q1 output is verdict plus missing_or_unsupported only.

48×2 arms×2 replicates =192 requests. Q0 replicate2 is retained, decided before freeze. Balanced deterministic arm order. Same DeepSeek deepseek-flash, temperature0, JSON mode, omit max_tokens, retries0, at most8 concurrent independent calls. Record all raw requests/responses, finish/model identifier, parsed content, usage, cache hit/miss and latency. No best-of, majority vote, repair, resampling, timeout retry or provider change.

Q0 versus Q1 intentionally changes access to Q/Parent *and* the context interpretation instruction. This is the specified diagnostic package, not an isolated estimate of Parent text independent of Original Q/prompt wording. A Q0 acceptance is scored against the full-context Gold even when the standalone local fact is true; that is the mechanism under test.

## Authorization and failure policy

The current user task directs E1 execution and specifies its call design; unlike the preceding task, it contains no additional pre-E1 approval gate. Record this current-task basis, not a reuse of the prior scoped96-call permission. E1 sends only after current Gold, prompts, requests, config, scoring rubric and code are SHA-frozen and committed. The actual192-call estimate is reported before sending.

TASK21 requires separate E2 authorization after E1 PASS. No E2 or E3 call is included in E1. E1 failure stops the cascade; there is no recall-only exception in this task. Subsequent stage contracts/actual requests require their own pre-call freeze.

Transport: HTTP retries0, no redirect; inherited240-second inactivity timeout (not total wall deadline). Halt new queued sends on HTTP400/401/402/403/404/422; in-flight requests complete. Preserve all other HTTP/timeouts/output failures as planned outcomes. Exclusive files prevent overwrite/restart. A request with durable send intent is never automatically resent. Every planned slot remains in denominators.

Schema requires exactly verdict and missing_or_unsupported. SUBTRACTABLE requires null; NOT_SUBTRACTABLE requires nonempty text. Wrong model, non-stop finish, empty/invalid JSON, unknown verdict, extra fields or inconsistent rationale invalidate the output. Invalid output is neither an accepted certificate nor a successful rejection; it fails schema and exact verdict, misses a Gold positive, and remains in its planned negative/category denominator. Never report a failed batch as safe because it accepted nothing. Null precision/recall denominators cannot pass a gate.

## E1 scoring and gate

Precision=correct accepted certificates/all accepted certificates. Recall=correct accepted/all Gold positive slots. Hard-negative rejection=valid correct rejections/all Gold negative slots. Category false acceptance=accepted Gold negatives/all planned negatives in that category. False-full-risk acceptance is acceptance in the13 frozen negative risk certificates; potential control risk only, not observed downstream closure. Euler/book-article counts are from preregistered negative case tags. Replicate agreement counts both-valid matching verdict pairs/all48 pairs; failures never disappear from the denominator.

Q1: precision>=97%, recall>=90%, binding false acceptance<=3%, qualifier false acceptance<=5%, Euler=0, book→article=0, false-full-risk=0, schema>=95%. Both comparisons must hold: Q1 precision>=Q0 precision; Q1 recall>=Q0 recall−5 percentage points. Equality is allowed. All absolute and comparative gates must PASS to enter E2; GATES.json is executable authority. Report subgroups without replacing primary gates.

## Review and error diagnosis

Primary verdict agreement is mechanically scored against pre-call Gold. Additional semantic review explains rejection reasons and errors, without modifying verdict references. Review packets hide arm, replicate, certificate ID and actual model context mode. All show the full evaluation Q/R/locator/ClaimSet plus content-only output; provider reasoning excluded. Exact identical context/output packets may share a manual reason review, but all planned slots remain scored.

One task-familiar reviewer classifies diagnostics as consistent, local_fact_missing, semantic_binding_missing, qualifier_or_scope_missing or other; assesses returned missing semantics as faithful/partly_faithful/unfaithful/not_applicable. Over-requiring unrelated Parent conjuncts is explained under other, not silently accepted as a Gold change. Review judgments are sealed and committed before aggregate scores are inspected. Masking is imperfect because wording may reveal context awareness. Retain every disagreement and ambiguity.

## Conditional later stages (no execution yet)

E2: high-recall proposer up to4 candidates, each1–3 Claims and exact locator; no solved/subtractable output. Each candidate goes through the unchanged Q1 qualifier. Keep accepted groups, never auto-close by fragment union. Reuse historical S0/S1 calls without paying again. ClaimSet members with binding roles are not automatically standalone substantive Claims; stage-specific coverage/compatibility scoring must respect that distinction and preserve the frozen historical references. E2 uses the same states, not fresh confirmation, and requires separate authorization with actual budget before calls.

E3 only after E2 PASS: model versus Gold qualified evidence, common TASK32 residual prompt, gates as provided. Historic residualization R0 is descriptive only, not rerun. Actual residual false subtraction/false FULLY_SUPPORTED cannot be inferred from E1 acceptance. Persistent state remains Q/R/C/H with H unused; certificates and outputs are ephemeral throughout.

## Integrity and completion

Protect all previously tracked experiment files with HISTORICAL_HASHES.json. Reparse saved raw responses, replay scores/accounting, verify prompt/request/Gold hashes and no excluded failures. Cache rate=sum hit/sum prompt tokens over complete consistent counters; report coverage and missing usage separately. No current monetary price is assumed. Stop on E1 failure; even positive interpretation is limited to this enriched familiar bank.
