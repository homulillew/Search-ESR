# Scoped Search API-prior probe

Trigger: Orthogonal Search alone did not yield useful local evidence; S1/S2
minimal state changed a few actions but also yielded no useful local evidence.
This is the last bounded Search–Find mechanism probe before stopping the
direction. Freeze code, exact prompts/requests and gate before paid calls.

## Comparison

Reuse the four S2 cells from `../verification_state/events.jsonl` as A.
For B, retain their exact question, checkpoint history, CurrentNeed,
FocusDocument, retriever, orthogonal old-document handling, local BM25 top-1,
Open behavior and four-decision horizon. Replace the model-facing `find`
function with a single `search` function requiring an explicit
`scope="corpus"` or `scope="document"`. Document scope requires `doc_ref` and
calls the **same** v3a Find backend. Corpus scope calls the same orthogonal
global Search backend. The model-facing prompt and usage hints are rewritten
only as necessary to describe the coherent scoped API. This is a **tool/API
package** intervention; any effect cannot separately identify the function
name, parameter schema and coherent descriptions.

No default or fuzzy repair for missing/invalid scope. Undeclared function
names are recorded and never executed. A malformed declared call receives a
recorded error, not a silently repaired corpus or document action. Retain
failed cells. No gold or candidate answer is injected. B has four cells, one
continuation each, in the same checkpoint order as S2. No selective reruns.

Measure document-scope Search adoption, local new/useful windows, first local
before corpus Search, switch after no-gain corpus Search, invalid/undeclared
calls, premature answer, new documents, tokens and latency. Treat S2's
independent Find as the comparable local action. A positive API-prior signal
requires a clear shift to document scope **and useful evidence** at more than
one checkpoint without increased premature answer. If B remains globally
searching, uses invalid calls, or produces local misses/irrelevant windows,
stop this Search–Find branch. A useful result on only the wrong qid 546 focus
does not justify a larger cohort.
