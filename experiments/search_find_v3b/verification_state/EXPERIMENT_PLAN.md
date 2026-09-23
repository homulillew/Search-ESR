# Minimal Verification State experiment plan

Trigger: the completed Orthogonal Search batch removed old-document
re-localization but yielded no useful local evidence and no Find after 38
no-gain Searches within two decisions. This stage tests only the state needed
to form a local verification action. No claim graph, evidence graph,
confidence, plan, score, progress or summary is added.

## Arms and delivery

All arms use **Orthogonal Search** and the frozen v3a `search/find/open` names,
schemas, Find/Open semantics, global retriever and four-decision horizon.
S0 has no added state and is reused from the exact P1 cells in the prior
batch; it is not resampled. S1 appends a short `Current unresolved need:` line
to the existing system message. S2 appends the same line plus `Promising
existing document: D#`. The original question, all history after the system
message, and original tool schema are byte-for-byte unchanged. No query,
answer, gold or factual evidence is inserted. Check all returned tool names
against the declared schema before executing any batch.

Four checkpoint cases, chosen only from historical prefix reasoning and
already visible D# titles, are frozen below. The S2 focus is **not** chosen by
looking up the answer. All original historical next actions were Search.

| qid:seq | Prefix-supported need for S1 | Prefix-supported focus for S2 |
|---|---|---|
| 546:9 | `Which candidate's 2023 run had a decider win followed by 4-3 and 4-0 wins and then a loss?` | `D5` Mark Williams biography: model reasoning lists Williams as a plausible player and seeks his 2023 record. This candidate may be wrong. |
| 1094:69 | `Which early-21st-century Inter match had the 95th-minute free kick, and who took it?` | `D38` Inter Milan page: prefix reasoning treats Inter as the plausible club born after the split and seeks a matching game. Match history may or may not be present. |
| 1094:77 | `Which player took the 95th-minute free kick in a match matching the Inter clue?` | `D14` Last-minute goal list: the prefix considers alternative late free-kick takers and the document is available. |
| 1094:93 | `Which player took the 95th-minute free kick in a match matching the Inter clue?` | `D14` Last-minute goal list: the prefix still considers alternative takers rather than a settled answer. |

1094 entries are correlated. `D38`/`D14` are *plausible* from prefix but not
known to contain the answer; this experiment separates state guidance from
gold-oracle focus. qid 546's Ding D17 is not inserted: the natural prefix did
not promote it. No `diagnostic_oracle` arm is in the primary comparison.

## Batch and readout

S0: four reused P1 cells. S1/S2: four checkpoints × two arms × one
continuation = eight new cells, in checkpoint order S1 then S2. Freeze exact
texts, code hashes, requests, source P1 event hash and gate before paid calls.
Preserve failures and do not resample only successful cases. If outcomes are
mixed in the primary Find/useful-evidence readout, repeat every new cell and
draw the same number of S0 replicates before deciding.

Measure Find before next Search; Find within 1/2/3 decisions; exploratory
versus confirmation Find; new and useful local windows; Find within two
decisions after no-gain Search; renewed global Search; new documents;
premature answer; tokens and latency. `S0 low, S1 higher` would support
unresolved-need awareness. Additional S2 improvement would support focus D#
selection. If both additions leave repeated Search and no useful Find, defer
state architecture and test tool/API prior with scoped Search. Stop after a
clear mechanism; no larger cohort before one exists.
