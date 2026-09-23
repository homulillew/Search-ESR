You are updating a versioned research progress state after exactly one new observation.

Do not rewrite the full state. Only propose changes that are directly justified by the new observation. If the new observation gives no new evidence for an existing claim, leave that claim untouched. Relevant evidence does not automatically mean a claim is supported. A hypothesis is not evidence. Do not generate search queries or plan future retrieval. Every proposed semantic claim mutation must cite one or more currently observed evidence refs.

Return exactly one strict JSON object with keys `claim_updates`, `new_claims`, `gap_updates`, `active_gap_action`, and `notes`.

Each `claim_updates` entry: `{ "claim_id": "C#", "status": "open|supported|refuted", "evidence_refs": ["W#"] }`.
Each `new_claims` entry: `{ "statement": "...", "status": "open", "evidence_refs": ["W#"] }`.
Each `gap_updates` entry: `{ "gap_id": "G#", "status": "open|closed", "evidence_refs": ["W#"] }`.
`active_gap_action` is `keep` or `retire`. `notes` is one short sentence. Do not include unchanged Claims or Gaps. Do not invent refs. If nothing changes, use empty arrays and `keep`.
