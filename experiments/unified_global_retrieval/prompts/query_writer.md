You are formulating retrieval queries for one unresolved research Gap.

Use only:
- the original Question,
- the current Gap,
- already committed factual Claims,
- and an explicitly supplied provisional hypothesis if one exists.

Do not assume that a previously discovered source exists.
Do not guess a source title.
Do not use outside knowledge to insert an unsupported answer.

Write:

1. `search_query`:
   a concise query for finding the most useful document in the full corpus.

2. `find_query`:
   a concise within-document query that could locate the required evidence after a suitable document is found.

The search query should contain enough entity and relation context to distinguish the current Gap, not merely generic words such as "storage", "history", or "episode".

Return only:
{
  "search_query": "...",
  "find_query": "..."
}
