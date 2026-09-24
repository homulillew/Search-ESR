Read exactly one observed source in light of the current Active Gap and already committed relevant Claims.

Extract 0–3 NEW factual findings only when:
1. the supplied observation directly supports the fact,
2. the fact materially advances the Active Gap, and
3. the fact is not already adequately represented by an existing Claim.

The observation may include source identity such as document title, URL and document reference. Those fields are evidence only for what they directly establish. Do not infer a missing relationship merely because related words appear in metadata and text.

Do not fill missing names, dates, identities, temporal relations or causal relations from outside knowledge.

Do not output plans, questions, searches, or "still unverified" statements.

If the observation adds no new Gap-relevant fact, return an empty list.

Return only:
{
  "findings": [
    {
      "statement": "...",
      "evidence_refs": ["W1"]
    }
  ]
}
