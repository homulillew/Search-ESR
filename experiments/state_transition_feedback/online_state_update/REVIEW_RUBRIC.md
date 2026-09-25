# Frozen T3 offline review rubric

- `source_supported`: observation text or observed URL directly supports the complete claim; model world knowledge and future documents do not count.
- `decision_relevant`: the claim binds the currently unresolved referent, resolves a discriminative constraint, or excludes a significant hypothesis so that next Gap/query/source choice changes.
- `target_leak`: the proposal contains the next-Gap answer or an answer-bearing source detail absent from the observed window.
- `duplicate`: the same fact already exists in `S_pre` or repeats another proposal from this call.
- `over_specific`: unsupported entity/date/relation detail is asserted beyond the observation.
- `oracle_binding_recovered`: at least one supported proposal names the frozen bound referent and has the right decision effect; lexical spelling variations are accepted only if semantically identical.

Precision denominators are all parsed proposals. API/format failures are preserved and scored as zero recovered bindings. An empty list is a valid zero-proposal update. Reviews are offline diagnostics; no after-result mutation of proposals occurs.
