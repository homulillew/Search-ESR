# Scoped Search result: parameter manipulation failed

Frozen on 2026-09-23 before calls; gate **29/29 PASS**. Four scoped API
continuations completed with a four-decision horizon. No API failures,
undeclared names or executed invalid tools. All provider responses, malformed
arguments and error observations are retained in `events.jsonl`.

The request schema declared only `search` and `open`. `search` explicitly
required `scope` to be `corpus` or `document`. The provider returned 29
`search` calls: **27 omitted `scope`** and were rejected by the harness,
**2 used legal `scope="corpus"`**, and **0 used `scope="document"`**. qid 546
seq9 had four missing-scope calls and two legal corpus calls. qid 1094 seq69,
77 and 93 had 9, 6 and 8 missing-scope calls, respectively, with no legal
calls. Some qid 546 calls included `doc_ref=D5` but still omitted `scope`,
showing a document-level intention in the arguments without a valid scoped
action. No local backend was executed and no new local window was produced.

S2 with independent `find` had local calls in 2/4 checkpoints, though no
useful evidence. The scoped arm had 0/4 valid local actions. Prompt tokens
were 970,518 for reused S2 versus 904,236 for scoped; the latter spent many
rounds on rejected calls, so token totals are not a useful efficiency
comparison.

This is an **API/schema adherence failure**, not a clean test of whether a
familiar `search` function name improves local action adoption. The actual
provider-returned call name was `search`, but the required field was absent.
The trace cannot distinguish the model's internal generation from provider
normalization. Harness validation prevented an invalid call from silently
becoming corpus or document Search. The scoped package also changes name,
schema and prompt descriptions together; even a positive result would not
isolate the name alone.

One final bounded alias probe will keep Find's original `(doc_ref, query)`
arguments and backend while changing only the model-facing local function
name to `search_document`. It will reuse the same S2 need/focus and four
checkpoint prefixes. After that, stop API variants regardless of outcome;
there is no basis yet for a larger cohort.
