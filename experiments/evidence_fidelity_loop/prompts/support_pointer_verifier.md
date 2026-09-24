Decide whether one candidate Finding is sufficiently supported by the supplied observed source to become a persistent factual Claim.

A Claim may be reused in later research, so every substantive identity, date, quantity, temporal relation and entity relation in the Finding must be supported.

Do not treat two separately true statements in the same document as evidence for a relationship between them unless the source establishes that relationship.

If supported, identify the smallest one or two exact text spans that establish the Finding. Source metadata such as the title may be used only when it directly supplies necessary source identity or temporal context.

If the exact source does not establish the complete Finding, return insufficient.

Return only:
{
  "verdict": "supported|insufficient",
  "support": [
    {
      "window_ref": "W1",
      "start": 0,
      "end": 10
    }
  ],
  "source_metadata_used": ["title"],
  "reason": "..."
}
