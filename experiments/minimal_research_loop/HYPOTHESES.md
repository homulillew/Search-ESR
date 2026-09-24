# Frozen research hypotheses

- Natural Gap-conditioned Reader Findings may already be precise enough that a second LLM Verify call has little marginal value; stress negatives from prior F2 are not a substitute for natural runtime Findings.
- When natural unsupported Findings are common, a Question/Gap-blind Verifier may reject them without losing many genuinely supported Findings.
- A single selected `gap_id` Frontier may improve real useful evidence in multi-Gap checkpoints; an extra selector call is justified only by retrieval outcomes, not by cleaner-looking State.
- Missing-first Claim-only Gap Review may prevent premature closure, but a simpler binary reviewer remains preferable if it already meets the reliability gate.
- The minimal single-Gap loop is an integration test. Its core failure modes are useful W not converted to valid Claim, valid Claims not closing Gap, and retrieval issued despite pending evidence.
