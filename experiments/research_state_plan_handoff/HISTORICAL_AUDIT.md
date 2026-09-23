# Read-only historical audit before intervention

`origin` was fetched and the new branch was cut at DeepSeek HEAD `3272200`.
The P1 freeze contains SHA-256 hashes of the original DeepSeek M1 plan events
and summary, M2 natural-action events, the M3 selection, the prefix-only
annotations, the Orthogonal checkpoint freeze, the tool schema and prompt.
Its offline gate verified all 13 unique M1 plans and exact H0 requests before
the first new P1 call. The P2 freeze separately locks the four M3 selection
IDs and H0 partial-rollout events before P2 calls.

The read-only checks confirmed 13 DeepSeek M1 responses and 13 DeepSeek M2
responses. M1 had four document-scope plans; M2 returned 32 Search calls and
zero Find. The frozen M3 selection is 546:33, 1094:69, 1094:23 and 1094:77.
No Atria response is reused as a DeepSeek observation. Qwen and historical
Query Initialization files are not rewritten.

The historical Query Initialization README and single-entry README report no
stable quality gain from replacing the default initializer; the latter treats
zero proposed directions (`no_direction`) as legitimate. Its prior evidence
does not establish that a question-only atomic commitment is safe. P3 therefore
permits `none` and scores unsupported specificity explicitly.
