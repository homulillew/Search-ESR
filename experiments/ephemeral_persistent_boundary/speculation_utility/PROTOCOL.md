# S1: speculation retrieval utility

The 48 V2 Q0/Q1/Q2 query strings are reused without regeneration. For every
query with `unsupported_binding_leakage=true` in the frozen V2 reviewer, a D
query is made by deleting each exact `leaking_values` substring, collapsing
whitespace, and removing duplicate punctuation. No term is added or rewritten.
The 48 originals and all D variants are run once through the same local BC+
Qwen3-Embedding-8B retriever, `k=5`, with the unchanged v3b Orthogonal Search
front end and 400-token source-derived raw previews. A fresh workspace is used
for every query; with no already discovered documents, Orthogonal and v3a
Search return the same initial ranked hits and previews. No Find/Open or
DeepSeek call is made in S1. S2 proceeds regardless of this stage's result.
