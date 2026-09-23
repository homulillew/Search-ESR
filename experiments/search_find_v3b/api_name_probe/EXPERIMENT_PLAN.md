# Final local-action name probe

The scoped-search arm failed at the parameter layer: 27/29 returned `search`
calls omitted required `scope`, so it never exposed a valid document action.
This final diagnostic keeps the successful original argument shape
`(doc_ref, query)` and changes only the model-facing local function name from
`find` to `search_document`. Its backend remains exactly v3a Find over an
already discovered D#. Global `search` stays orthogonal; `open` is unchanged.
Tool descriptions, prompt and usage hints receive mechanical name
substitution for coherence. No other state, query, retriever or stopping rule
changes.

Use the same four S2 checkpoint prefixes, CurrentNeed and FocusDocument;
reuse S2 outcomes. One four-decision continuation per checkpoint. Freeze
code/request/source hash and pass offline gate before paid calls. Require
declared tool names at the harness, record malformed arguments and all
failures, and execute no undeclared function. No oracle document or gold is
injected.

Read out `search_document` adoption, local new/useful evidence,
no-gain-to-local switching, global persistence, premature answers, tokens and
errors. If the alias produces more useful evidence in multiple checkpoints,
tool/API presentation is a plausible factor. If it only increases attempts
on wrong/irrelevant documents, or does not increase attempts, stop this
Search–Find branch. This is the last API variant, irrespective of outcome.
