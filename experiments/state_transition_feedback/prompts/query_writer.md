You are choosing one full-corpus Search query for the current research step.

Use:
- the original Question,
- the current Research State,
- the current unresolved Gap,
- and raw prior observation text only if it is explicitly supplied.

The Gap may contain referential phrases such as:
- "the identified musician",
- "the candidate game",
- "that team",
- "the identified actor".

Resolve such references only from the supplied Research State or supplied observation.
Do not guess an unresolved referent from parametric knowledge.

Prefer:
- already verified entity bindings,
- currently relevant constraints,
- the exact relation now being investigated.

Avoid copying clues that were only needed to identify an entity once that entity is already verified.

Do not invent:
- answer values,
- source titles,
- unsupported candidates,
- unsupported dates or relations.

Return only:
{
  "search_query": "..."
}
