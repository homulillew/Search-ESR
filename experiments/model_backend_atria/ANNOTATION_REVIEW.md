# Prefix-only semantic annotation review

Reviewed 13/13 frozen checkpoint packets against the AI draft. Reviewer: `Codex prefix-only semantic review`. This is a **single-reviewer diagnostic annotation**, not human consensus or independent multi-annotator agreement.

This review used only the question, checkpoint prefix messages, already visible D#/W#, reasoning in that prefix, and the draft. It did not consult future trajectory, later tool calls, gold/reference/final answers, post-run full-source audit, or later model responses. Prior study context was not used to decide labels.

| Checkpoint | Decision | Prefix-only rationale |
|---|---|---|
| 546:9 | Kept | The question is still split between career filters and an unidentified 2023 match run. D5 is a visible player biography; corpus and document scopes are both defensible. |
| 546:17 | Kept | The result-page preview in D11 is a plausible local lead despite the uncertain tournament identity. |
| 546:25 | Kept | The same D11 result page remains visible; local verification should not be ruled out solely because reasoning prefers search. |
| 546:33 | Kept | New D17 biography and earlier D5/D11 provide local checks for different constraints. |
| 546:41 | Kept | The existing biographies and D11 result page still permit targeted inspection. |
| 1094:23 | Kept | The prefix contains guesses and a Messi title but no source that connects the split-founded club to the requested match. |
| 1094:34 | Kept | Inter is a reasoning hypothesis, but no visible Inter origin page or matching report is yet available. |
| 1094:45 | Kept | D37 and D34 are more focused than the draft D38 trophies page. |
| 1094:53 | Kept | The Inter and Messi leads coexist but do not identify the requested match. |
| 1094:61 | Kept | The focused D34/D37 previews justify local scopes; the video placeholder and trophies page do not. |
| 1094:69 | Kept | The generic D14 goal list is weaker than D34/D37 for the current need. |
| 1094:77 | Kept | The reasoning explicitly doubts the Messi answer despite a visible 95th-minute source; no stop label is warranted. |
| 1094:93 | Kept | The same mismatch remains unresolved in the visible prefix. |

Fields changed: 23 across 10 checkpoints. Each entry records its old and new value and its prefix-only reason.

- `546:17` `acceptable_scopes`: `["corpus"]` → `["corpus", "document"]`. prefix-only: The result-page preview in D11 is a plausible local lead despite the uncertain tournament identity.
- `546:17` `plausible_document_refs`: `[]` → `["D11"]`. prefix-only: The result-page preview in D11 is a plausible local lead despite the uncertain tournament identity.
- `546:17` `ambiguity`: `"medium"` → `"high"`. prefix-only: The result-page preview in D11 is a plausible local lead despite the uncertain tournament identity.
- `546:17` `reason`: `"The reasoning hypothesizes Championship League but the visible documents do not clearly identify an event log containing the whole sequence."` → `"D11 is a visible 2023 British Open result page with a 4-3 match preview, so local inspection is defensible; the visible prefix does not establish the full score sequence or its event, so corpus search remains defensible."`. prefix-only: The result-page preview in D11 is a plausible local lead despite the uncertain tournament identity.
- `546:25` `acceptable_scopes`: `["corpus"]` → `["corpus", "document"]`. prefix-only: The same D11 result page remains visible; local verification should not be ruled out solely because reasoning prefers search.
- `546:25` `plausible_document_refs`: `[]` → `["D11"]`. prefix-only: The same D11 result page remains visible; local verification should not be ruled out solely because reasoning prefers search.
- `546:25` `reason`: `"The visible material contains broad snooker pages and unrelated match headlines; no specific result document is promoted as a likely local source."` → `"D11 remains a visible 2023 tournament result page with a 4-3 preview. It may be checked locally, while the candidate and full 4-3/4-0 sequence remain unresolved and justify broader retrieval."`. prefix-only: The same D11 result page remains visible; local verification should not be ruled out solely because reasoning prefers search.
- `546:33` `plausible_document_refs`: `["D5", "D17"]` → `["D5", "D11", "D17"]`. prefix-only: New D17 biography and earlier D5/D11 provide local checks for different constraints.
- `546:33` `reason`: `"Several player biographies, including newly visible D17, exist. Local checking of career constraints is plausible, but no visible result page clearly carries the required match sequence."` → `"The prefix contains candidate biographies D5 and D17 and the 2023 result page D11 with a 4-3 preview. Each permits a local check, but no visible passage establishes the complete requested run."`. prefix-only: New D17 biography and earlier D5/D11 provide local checks for different constraints.
- `546:41` `plausible_document_refs`: `["D5", "D17"]` → `["D5", "D11", "D17"]`. prefix-only: The existing biographies and D11 result page still permit targeted inspection.
- `546:41` `reason`: `"The reasoning remains uncertain about the event and candidate. Existing biographies might answer career filters, while the match run still likely needs a result source."` → `"The visible D11 result page and D5/D17 biographies can test parts of the score and career clues locally; the event and full match sequence remain uncertain, so corpus search is also reasonable."`. prefix-only: The existing biographies and D11 result page still permit targeted inspection.
- `1094:45` `plausible_document_refs`: `["D37", "D38"]` → `["D34", "D37"]`. prefix-only: D37 and D34 are more focused than the draft D38 trophies page.
- `1094:45` `reason`: `"Visible AC Milan/Inter pages can test club identity, but the player needs a matching event report; local and corpus scopes both have a rationale."` → `"D37 preview directly describes the Milan split that produced Inter. D34 preview names Messi and the 95th-minute PSG–Lille free kick; checking these sources can test the competing clues, while the requested match is not yet established."`. prefix-only: D37 and D34 are more focused than the draft D38 trophies page.
- `1094:53` `plausible_document_refs`: `["D38"]` → `["D34", "D37"]`. prefix-only: The Inter and Messi leads coexist but do not identify the requested match.
- `1094:53` `reason`: `"The club hypothesis persists and D38 exists, but no visible match source securely links it to the late free kick."` → `"D37 visibly supports the Inter split hypothesis and D34 identifies a 95th-minute PSG–Lille kick. The two leads conflict on team identity, so inspecting them or retrieving a matching report are both defensible."`. prefix-only: The Inter and Messi leads coexist but do not identify the requested match.
- `1094:61` `plausible_document_refs`: `["D11", "D38"]` → `["D34", "D37"]`. prefix-only: The focused D34/D37 previews justify local scopes; the video placeholder and trophies page do not.
- `1094:61` `reason`: `"Visible Messi article titles address the kick while D38 addresses the club clue; reading those sources further or searching for a distinct match are all defensible."` → `"D34 is a substantive 95th-minute match preview and D37 states the Inter split; D11 is only a video placeholder and D38 is a trophies page. Local inspection or further retrieval can resolve the mismatch."`. prefix-only: The focused D34/D37 previews justify local scopes; the video placeholder and trophies page do not.
- `1094:69` `plausible_document_refs`: `["D38", "D14"]` → `["D34", "D37"]`. prefix-only: The generic D14 goal list is weaker than D34/D37 for the current need.
- `1094:69` `reason`: `"The current reasoning explicitly considers Inter and a late free kick; a club page or last-minute-goal list may be worth checking, but a match report may still need discovery."` → `"D34 provides the concrete Messi PSG–Lille event and D37 the Inter split clue. D14 is a generic last-minute-goal list, so the two focused pages are the plausible local checks while corpus discovery remains possible."`. prefix-only: The generic D14 goal list is weaker than D34/D37 for the current need.
- `1094:77` `plausible_document_refs`: `["D11", "D14", "D38"]` → `["D34", "D37"]`. prefix-only: The reasoning explicitly doubts the Messi answer despite a visible 95th-minute source; no stop label is warranted.
- `1094:77` `reason`: `"The visible Messi source titles support a 95th-minute kick, but the reasoning itself notes a mismatch with the split-founded team, so stopping is not yet grounded."` → `"The visible D34 preview identifies a PSG–Lille 95th-minute kick; D37 documents the separate Inter origin clue. The reasoning notices a team mismatch, so the candidate still needs local or corpus verification."`. prefix-only: The reasoning explicitly doubts the Messi answer despite a visible 95th-minute source; no stop label is warranted.
- `1094:93` `plausible_document_refs`: `["D11", "D14", "D38"]` → `["D34", "D37"]`. prefix-only: The same mismatch remains unresolved in the visible prefix.
- `1094:93` `reason`: `"The prefix still contrasts Inter with Messi articles. Existing pages could be inspected locally, while further match retrieval remains a reasonable route."` → `"D34 and D37 are the visible focused sources for the 95th-minute event and split-founded club. The prefix has not reconciled them with one match; local checks and further discovery remain reasonable."`. prefix-only: The same mismatch remains unresolved in the visible prefix.

All 13 fields were checked. Multiple acceptable scopes and high ambiguity remain where the prefix does not determine a unique next action.
