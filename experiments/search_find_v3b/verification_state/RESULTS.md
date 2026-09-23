# Minimal Verification State results

Run 2026-09-23. `freeze.json` preceded all new calls; offline gate **45/45
PASS**. S0 reuses four exact Orthogonal Search P1 cells (source event SHA
frozen). S1 and S2 each add four new four-decision continuations from the
same prefixes. All **8/8 new cells** completed; no API/tool/undeclared-call
errors. Full requests, responses, tool results and private audits are in
`events.jsonl`; `mechanical_summary.json` is recomputed by
`analyze_results.py`.

| Arm | Find in cells | Find before next Search | new Find W# | no-gain Searches | cells searching again after no-gain | stop |
|---|---:|---:|---:|---:|---:|---:|
| S0 no state | 1/4 | 1/4 | 2 | 16 | 3/4 | 0/4 |
| S1 CurrentNeed | 1/4 | 0/4 | 1 | 12 | 3/4 | 1/4 |
| S2 Need + FocusDocument | 2/4 | 1/4 | 2 | 14 | 3/4 | 0/4 |

S0 Find is entirely qid 546 seq9. S1 Find is also only 546 seq9. S2 Find
occurs at 546 seq9 and 1094 seq69. In the other two 1094 checkpoints, all
arms continued global Search. P1/State Search created **zero old-document new
W#** in every cell; global Search still found new documents (S0 15, S1 27,
S2 16). S2 had one cell that switched to Find within two decisions of a
no-gain Search; all three local calls in that cell returned `no_match`.

## Window and answer review

At **546 seq9**, S1 made two D5 Mark Williams Finds. Its only new window
listed a 2021 Championship League Invitational final; its next Find returned
the already seen W5 (2023 Championship League runner-up row). Neither shows
the requested decider → 4–3 → 4–0 → loss sequence. S1 then stopped and named
**Mark Williams**, inventing opponent names and exact scores while citing W5,
which does not support those claims. This is a concrete **premature,
unsupported answer after Find**.

S2 at 546 seq9 used D5 on its first decision and made two new local windows.
One listed the same irrelevant non-ranking finals; another showed 1994/1995
finals rather than a reliable professional-start statement. The first Find
returned already observed W5. No new window established the requested match
sequence or changed the candidate assessment. S0 likewise used D5 without
useful match evidence.

At **1094 seq69**, S1 made eight global Searches and no Find. S2 searched
globally first, then tried `find(D38, "95th minute")`, `find(D38,
"free-kick")`, and `find(D38, "born out of discord")`. All three returned
`no_match`, hence **zero new local windows**. D38 had been a plausible
prefix-visible Inter page, but it was not a useful source for the missing
match/player fact. At seq77 and seq93, S1/S2 made no Find.

No S1 or S2 cell obtained a **useful new Find window** by the frozen
unresolved-need criterion. S2's extra Find in one 1094 cell demonstrates a
small action-selection response to an explicit D#, not successful evidence
retrieval. S1's Mark Williams answer demonstrates that more Find calls can
coexist with worse grounding. Prompt tokens across the four cells were S0
937,871; S1 935,687; S2 970,518. The sample is selected and correlated,
so these totals are workload descriptions, not efficiency estimates.

## Decision

CurrentNeed alone did **not** improve the Find checkpoint count or obtain
useful evidence. Adding FocusDocument raised Find from 1/4 to 2/4, but the
additional case was three local lexical misses in a plausible but unhelpful
document. There is no supported minimal State mechanism yet. This does not
prove FocusDocument has no value: the focus came from fallible prefix belief,
and qid 546 illustrates a separate Document Triage failure. It does rule out
claiming the present S1/S2 cards solve the observed failure.

The primary useful-evidence readout is uniformly zero, so the frozen
replicate trigger for a *mixed* success signal was not met. No selective
replicate is run. With orthogonalization and minimal State both tested, the
next bounded test is the tool/API prior: preserve the same S2 need and focus
but expose local search as `search(scope="document", doc_ref=...)` rather
than an independent `find` name.
