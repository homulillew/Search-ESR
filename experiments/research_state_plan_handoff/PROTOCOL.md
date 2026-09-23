# Research-control state protocol amendment

## Established observations

The historical Search–Find audits verified that global Search could relocalize
an old document and that Orthogonal Search blocked that path. Blocking alone
did not produce stable Find use from either Qwen or DeepSeek. On the frozen 13
prefixes, DeepSeek's explicit M1 planning was substantially better than
Qwen's, while its M2 natural actor remained Search-heavy. DeepSeek's M4
evidence-to-belief review improved under the original single-reviewer rubric.
Concrete source routing remained weak: correct scope did not reliably select
a suitable D#, and the observed Find windows did not resolve the target need.

Historical M1 and M2 were separate calls. The M1 plan was absent from the M2
actor context. Their difference establishes a diagnostic-planning versus
natural-action gap, not an actor's refusal to follow a visible plan.

## Research questions and boundaries

P1 tests whether handing the verbatim frozen M1 broad plan to the actor changes
its next tool batch on the same 13 prefixes. P2 tests whether a refreshed broad
plan interacts with Orthogonal Search during four-decision continuations. P3
tests question-only versus evidence-conditioned *one active atomic need*.

State specificity may increase only as visible evidence increases. Keep the
original question, seed intent, atomic need, hypothesis, observed evidence,
and target document distinct. Harness-owned D#/W# identity, SearchGain,
NoGainSearch, and validity are deterministic; semantic needs and source-type
judgments are model assessments. All actions remain available in P1–P3.

Before these probes, there is no claim that State or AtomicNeed is necessary or
effective, that DeepSeek will follow a plan, or that hard gating is correct.
Control realization, source compatibility, and useful evidence are separate
outcomes. Provider failures are recorded with zero SDK retries and are not
semantic failures. Historical experiment files remain append-only and are
read by hash; this study writes only in this directory.

Each stage freezes provider, prompt/schema, prefix, baseline, plan, rubric,
sample count, selection, and horizon before requests. No best-of, selective
retry, gold, future trajectory, source repair, or prompt change after results.

P4 Progressive Frontier requires positive P3 evidence. Guarded actions require
both P1/P2 evidence that visible soft State remains insufficient and P3
evidence of acceptable AtomicNeed/source quality. Neither is assumed here.
