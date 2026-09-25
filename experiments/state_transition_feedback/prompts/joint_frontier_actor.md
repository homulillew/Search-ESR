You are conducting a multi-step research search.

Use the original Question and the current verified Research State.

Choose the next unresolved question that is both:
- useful for ultimately answering the Question,
- and actionable given what is currently known.

Do not jump to a downstream question whose main referent is still unresolved if a nearer uncertainty must first be resolved.

Then write one concise full-corpus Search query for that next Gap.

Prefer already verified entity bindings over repeating the original clue list.

Do not invent candidates or answer values.

Return only:
{
  "next_gap": "...",
  "search_query": "..."
}
