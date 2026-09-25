You are updating a minimal Research State after reading one source window.

The Research State should keep only verified facts that materially change the next research decision.

From the current Observation, propose at most 2 new persistent Claims.

A proposed Claim must satisfy all of the following:

1. It is directly supported by the Observation.
2. It binds or constrains an unresolved research variable, resolves an important clue, or rules out an important hypothesis.
3. Knowing it would materially change the next Gap, Search query, or source choice.
4. It is not merely an interesting or task-related side fact.
5. It must not infer a future answer not explicitly supported by the Observation.

Prefer:
- candidate/referent bindings,
- discriminative constraint resolution,
- hypothesis elimination.

Do not store:
- incidental biography,
- decorative details,
- generic summaries,
- facts whose only justification is that they may possibly be useful later.

Return only:
{
  "claims": [
    {
      "statement": "...",
      "decision_effect": "candidate_binding | constraint_resolution | hypothesis_exclusion"
    }
  ]
}
