# P1 result: exact frozen M1 plan handed to DeepSeek actor

All 13 H1 responses arrived, all batches passed the unchanged Search/Find/Open
schema validator, and no tool ran. H0 is the 13 historical DeepSeek M2 cells.
On the four frozen document plans, any-Find realization rose from H0 **0/4**
to H1 **3/4**; first-call Find was 2/4. H1 made 5 Find, 2 Open and 29 Search
calls across all cells, versus 32 Search and no Find/Open in H0. The 13-cell
plan-consistent-action count was 8/13 to 11/13; three H1 cells also included
conflicting actions in mixed batches. Search persisted in 3/4 non-corpus-plan
cells, compared with 4/4 in H0.

| Checkpoint | Frozen document target | Prefix-plausible target? | H0 calls | H1 calls | H1 interpretation |
| --- | --- | --- | --- | --- | --- |
| 546:17 | D12 | no | Search+Search | Search+Search | No control realization. |
| 546:25 | D10 | no | four Search | Search+Find(D10) | Plan and target realized; target fails the prefix-only plausible-D check. |
| 546:33 | D10 | no | Search+Search | Find(D12)+Find(D17)+Search | Document scope realized, original target ignored; D17 is prefix-plausible. |
| 546:41 | D17 | yes | Search+Search | Find(D17)+Find(D17) | Scope and target realized; D17 is prefix-plausible. |

Two H1 cells with Find touched a prefix-plausible D# (546:33 and 546:41).
Only one frozen document plan itself named a prefix-plausible D# (546:41).
P1 contains no observation feedback, so this proxy does not establish that a
Find window would answer the need. Its causal evidence is narrower: making
the exact prior plan visible changed the next tool distribution on these fixed
prefixes, while the plan's target quality remained a separate bottleneck.

Every per-cell batch, first call, target, validation and paired H0/H1 result is
in `mechanical_summary.json`; raw provider responses and cache usage are in
`events.jsonl`. No historical experiment file changed.
