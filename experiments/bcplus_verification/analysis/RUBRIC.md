# Frozen offline rubric (before calls)

## Boundaries

Review actual emitted windows, complete pre/post Claims and H, actual actions, and frozen unit target. Private reference corpus evidence certifies bank eligibility; it is not credited to the Actor unless emitted. Single reviewer, not blind to unit polarity. Corpus validity, structural output validity, and semantic success are distinct.

S1 starts from the same real Q-only historical initial checkpoint as its qid's Discovery unit. No observed facts or supported H are deleted. Candidate + one explicit condition is an oracle intervention; it is never a Claim. S1 selection is answerability-conditioned and clustered by qid, candidate and shared source. It is an upper-bound diagnostic, not a random BC+ accuracy cohort. Article date, career cutoff, event binding and numerical boundaries are retained where part of the chosen relation.

## Per window / Writer update

- relevant: supplies direct subject-relation evidence, a necessary bridge or concrete candidate identity evidence for the active task; name-only or unrelated subject facts are not sufficient.
- useful_target_evidence: supports or refutes the chosen S1 relation (partial bridge recorded separately); S2 evidence makes an actual named candidate useful to test against at least one target-defining clue.
- direct_support / direct_refutation: actual returned content, or its explicit logical combination with prior source-supported Claims, establishes the selected relation or its negation. Mere omission is neither.
- admitted_target_claim: a new U1 statement correctly preserves the needed relation. A newly collected source remaining only in Workspace is not success.
- unsupported_strengthening: a Claim adds identity/date/role/quantity/scope not in its Observation or explicitly available prior Claims. An unqualified answer-identification Claim from one clue is promotion, not harmless shorthand. Source statements may be translated or logically combined, but outside model memory is not evidence.
- For contradiction: record admitted falsifying Claim, explicit H clear, H later reinstated, wrong H retained, unrelated-support redirect. A replacement with another candidate is reported separately from required clear.

## Unit success

V+: direct supporting evidence found within <=2 actions, correct condition enters Claims, and no target-related unsupported strengthening. Report evidence-only and admission-only separately.

V-: direct falsifying evidence found within <=2 actions, correct falsifying Claim admitted, explicit H clear, and original candidate not reinstated at episode end. Absence is never falsification. VN12 is a benchmark/condition inconsistency; report with and without it. All failures, including early stops and API/schema/tool failures, remain failures in intended denominators.

Discovery: U1 proposes a concrete, real, source-backed candidate useful to test; the statement must have actual observed support for a defining clue. Report name proposed, useful candidate proposed, correct benchmark target proposed, and final retention separately. Being a plausible temporary candidate does not require full verification. Source-backed wrong candidates remain Discovery successes at the useful-candidate level; they are not benchmark-candidate successes. Identity hallucination without source support fails.

## Costs / comparison

Action cost counts each dispatched tool call including tool failures; Stop is a model decision, not a tool action. First-useful and first-successful-update action indices are recorded; failures are right-censored. Restricted update cost is first successful semantic-update action if the unit succeeds, else horizon+1. Also report actual average actions and success-only action cost. Unequal horizons make restricted costs budget-dependent; never claim an unbiased causal speedup from this alone.

Useful evidence per Search reports both successful-evidence Search actions/Search actions and useful returned windows/Search actions (the latter can exceed one). Irrelevant window rate uses all emitted windows, including duplicate returns; unique-window sensitivity is separate. Count input/output tokens, provider reasoning tokens when reported (null is unknown), elapsed model seconds, elapsed tool seconds, raw provider cache hit/miss tokens, weighted hit/input and per-request hit occurrence.

## Entry gates

Use integer gates in bank/SELECTION.json. V+>=15/18; V->=9/11; wrong-benchmark-candidate sensitivity>=8/10. Source-backed Discovery success <=7/10. Verification actual mean actions < Discovery; restricted update cost at least 0.5 action lower. All must pass before S4. No threshold substitution or exploratory rescue.
