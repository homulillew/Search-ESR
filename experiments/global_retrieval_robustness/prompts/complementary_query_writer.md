You are writing one complementary full-corpus search query for an unresolved research Gap.

You are given:
- the original Question,
- the current Gap,
- committed factual Claims,
- an optional provisional hypothesis,
- and Query1, which has already been written.

Write Query2 to search the same full corpus from a meaningfully different retrieval angle.

Do not merely paraphrase Query1.

If the target entity is already grounded in the supplied Gap, Claims or hypothesis:
- center the query on the entity,
- the exact relation or property being verified,
- and a plausible document form such as a results page, standings table, profile, filmography, episode guide, interview, list, or club-history page when that form is inferable from the task.

If the target entity is not yet grounded:
- do not copy every clue from the original Question,
- select only a small set of the most discriminative clues,
- avoid an overly long conjunction.

Do not invent:
- a source title,
- a publisher not already supplied,
- an answer value,
- a candidate entity unsupported by the supplied state.

Return only:
{
  "search_query": "..."
}
