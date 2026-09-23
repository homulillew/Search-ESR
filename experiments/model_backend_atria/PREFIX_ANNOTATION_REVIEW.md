# Prefix-only annotation review preparation

The proposed labels are in `PREFIX_ONLY_ANNOTATIONS_DRAFT.json`. The exact
messages available at each checkpoint are in `PREFIX_ONLY_PACKETS.json`.
`PREFIX_REVIEW_INDEX.md` links to one exact packet per checkpoint for easier
review; the split packets have been checked to match the bundle byte-for-byte
after JSON parsing.
`make_prefix_packets.py` stops reading the event stream at that checkpoint;
it never reads a later response. The packet hashes match the historical
Orthogonal Search freeze. Please judge each row from its packet, without
consulting later trajectories, gold, full documents or post-run source audit.

| Checkpoint | Proposed acceptable scopes | Proposed local D# | Ambiguity |
|---|---|---|---|
| 546:9 | corpus, document | D5 | high |
| 546:17 | corpus | — | medium |
| 546:25 | corpus | — | high |
| 546:33 | corpus, document | D5, D17 | high |
| 546:41 | corpus, document | D5, D17 | high |
| 1094:23 | corpus | — | high |
| 1094:34 | corpus | — | high |
| 1094:45 | corpus, document | D37, D38 | high |
| 1094:53 | corpus, document | D38 | high |
| 1094:61 | corpus, document, window | D11, D38 | high |
| 1094:69 | corpus, document | D38, D14 | high |
| 1094:77 | corpus, document, window | D11, D14, D38 | high |
| 1094:93 | corpus, document, window | D11, D14, D38 | high |

The draft is deliberately broad where source containment is unclear.
`plausible_document_refs` means a prefix-plausible place to inspect, not a
claim that the full document actually contains the answer. The user later
authorized Codex to complete the semantic review without external signoff.
The completed decisions and all draft changes are in `ANNOTATION_REVIEW.md`;
the final labels are in `PREFIX_ONLY_ANNOTATIONS.json`.
