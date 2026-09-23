# Prefix-only annotation review

Review each packet using its question, checkpoint messages, visible D/W refs and reasoning. The packets stop at the historical API request. Do not inspect later trajectories, gold, full documents or post-run audits. Proposed labels are AI-authored and require human review before the M1 freeze.

| Checkpoint | Prefix packet | Proposed scopes | Proposed D# | Ambiguity |
|---|---|---|---|---|
| 546:9 | [qid_546_seq_9.json](prefix_review_packets/qid_546_seq_9.json) | corpus, document | D5 | high |
| 546:17 | [qid_546_seq_17.json](prefix_review_packets/qid_546_seq_17.json) | corpus | — | medium |
| 546:25 | [qid_546_seq_25.json](prefix_review_packets/qid_546_seq_25.json) | corpus | — | high |
| 546:33 | [qid_546_seq_33.json](prefix_review_packets/qid_546_seq_33.json) | corpus, document | D5, D17 | high |
| 546:41 | [qid_546_seq_41.json](prefix_review_packets/qid_546_seq_41.json) | corpus, document | D5, D17 | high |
| 1094:23 | [qid_1094_seq_23.json](prefix_review_packets/qid_1094_seq_23.json) | corpus | — | high |
| 1094:34 | [qid_1094_seq_34.json](prefix_review_packets/qid_1094_seq_34.json) | corpus | — | high |
| 1094:45 | [qid_1094_seq_45.json](prefix_review_packets/qid_1094_seq_45.json) | corpus, document | D37, D38 | high |
| 1094:53 | [qid_1094_seq_53.json](prefix_review_packets/qid_1094_seq_53.json) | corpus, document | D38 | high |
| 1094:61 | [qid_1094_seq_61.json](prefix_review_packets/qid_1094_seq_61.json) | corpus, document, window | D11, D38 | high |
| 1094:69 | [qid_1094_seq_69.json](prefix_review_packets/qid_1094_seq_69.json) | corpus, document | D38, D14 | high |
| 1094:77 | [qid_1094_seq_77.json](prefix_review_packets/qid_1094_seq_77.json) | corpus, document, window | D11, D14, D38 | high |
| 1094:93 | [qid_1094_seq_93.json](prefix_review_packets/qid_1094_seq_93.json) | corpus, document, window | D11, D14, D38 | high |

The editable proposal is [`PREFIX_ONLY_ANNOTATIONS_DRAFT.json`](PREFIX_ONLY_ANNOTATIONS_DRAFT.json). Each reviewed row must retain `current_need`, `expected_source_type`, `acceptable_scopes`, `plausible_document_refs`, `ambiguity`, and `reason`.
