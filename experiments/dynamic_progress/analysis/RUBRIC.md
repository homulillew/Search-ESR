# Frozen offline semantic rubric

Single Codex reviewer, Q+Claims-only frozen labels. Packets hide condition IDs and use deterministic opaque IDs. Output schema may reveal condition, so no claim of full blinding or independent raters. Prior question familiarity remains. No external facts, future outcomes, raw source audit, gold answer or Hypothesis may establish a relation.

## Materiality and closure

Identity must be discriminatively established and the requested final relation must be directly scoped/bound. A likely name or literal answer value alone cannot close. Redundant corroborating clauses need not have one Claim each, but a realistic identity alternative, explicit role/event/count/date binding or material Claim contradiction still blocks. Frozen labels are nonexhaustive exemplars. Semantically new blockers can pass without exact wording match; explain each deviation. No post-result label changes.

True closure: resolved=true on a gold_resolved State. False closure: resolved=true on a gold_unresolved State. Correct closure denominator all planned resolved slots. Completion accuracy counts any absent/invalid result incorrect. Missed closure: resolved=false on resolved State. Closure witness: cited subset jointly forms a reasonable main identity/final-relation support chain, not just any valid indices. R has no witness field: N/A, not zero.

## Blocker units and metrics

B: one blocking_gaps item is one unit. FULL: one missing/conflict requirement item is one blocker; all requirements reviewed additionally for invented requirements/false-supported relation. R: reviewer segments clearly separate semantic uncertainties into units, preserving exact quoted text; a single whole-question paraphrase remains one over-broad unit and cannot be subdivided post hoc into successes. Closely bound attributes of one identity or event relation may form one unit; multiple independent chains or almost the whole question in one unit are over-broad.

A content-valid unit describes an actually unestablished, material relation without asserting an unsupported candidate/date/event premise, contradicting present Claims, inventing extra requirements, reasking a solved relation, or an over-broad bundle. Do not reject a test of whether candidate X satisfies Y simply because X is provisional; reject presupposing X already satisfies Y. Merely quoting question conditions as missing is not false evidence promotion. Existing observed local facts cannot be labelled absent. Negative candidate evidence may justify qualification failure; question-vs-Claim mismatch is not an inter-Claim conflict.

Valid blocker presence: gold-unresolved outputs with>=1content-valid unit / all planned gold-unresolved outputs. Blocker precision: valid units / all generated blocker units (including unnecessary units on resolved States). Both denominators shown. No generated units on provider failure or falseclosure; separate completion/failure metrics prevent vacuous success. Unsupported-premise/broad/invented/solved-as-missing are peroutput and perunit. An invented requirement includes unnecessary extra corroboration/different objective; a solved requirement relisted missing is a separate stale-coverage error.

Status fidelity (B/FULL): missing if no actual part of that relation is established; partial only if a genuine part lacks a necessary scope/time/role/count/endpoint; conflict requires incompatible current Claims about a material relation. Incorrect status does not erase a genuinely material textual blocker in content precision, but strict validity additionally requires correct status and truthful reference semantics. Report both. FULL has no partial status: incomplete relations are missing.

Ref validity separates index existence (runtime) and semantic adequacy (review). Empty refs allowed for an absent relation. Nonempty refs should support the observed part/counterevidence used to justify the gap, not imply the whole missing relation is established. False evidence promotion is claiming stronger support than any cited/joint Claim entails; flag independently even if a different blocker is valid. Ref set need not equal reviewer exemplars.

Replicate categories: bothcorrectclosure; bothunresolved with compatiblevalidblockers; oneadequate/oneinadequate; bothinadequate. Adequate unresolved requires correct completion+validpresence+no invalidunits/unsupportedpremise; additionally report completion-only agreement and strict-status/ref stability. Different valid material blockers are compatible, no string-equality test.

## FULL sensitivity

Same12inputs paired with B. Compare output-level inventedrequirement, no-valid-blocker omission (unresolved output lacks any valid blocker), falseclosure and tokens. FULL additionally claims completeness: review omitted material blocker families among the frozen nonexhaustive exemplars and any clear necessary relation; B is not penalized for failing to exhaust all blockers once>=1validblocker exists. Report this distinction, not an unfair completeness score against capped B. Supported requirements reviewed for stronger-than-Claims promotion. Requirements on known solved States cannot create a new objective.

## Error taxonomy

completion(false/missed), unsupportedpremise, falseevidencepromotion, inventedrequirement, already-supported-as-gap, over-broadbundle, statuserror, semanticreferror, transport/schema. Laterstages, ifreached: Progress/Frontier/Retrieval/Localization/Admission/Hypothesis-control/falseclosure/missedclosure/horizonexhausted. Do not infer retrieval failures from P1.
