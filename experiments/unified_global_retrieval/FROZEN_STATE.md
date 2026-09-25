# Frozen state and stage boundaries

Base: remote `origin/experiment/minimal-research-loop` at `b364cdde9c138d5d330521d9ea770fa836fa5dea`. All prior experiments remain read-only. The executable U1 manifest is `document_rediscovery/freeze.json`, generated and committed before any new model request. It records the stage's git HEAD, model/provider, per-field input hashes, checkpoint and private truth hashes, prompt and request hashes, retriever code and FAISS/SQLite content hashes, k=5, sample order, gates and zero-retry failure policy.

The bank is frozen at 40 diagnostic cells from ten qids: A=12, B=8, C=12, D=8. Checkpoints are authentic historical observations reconstructed into one-window prefixes. They are deliberately narrower than full trajectories; historical-only H has one old document per cell. Query Writer sees only Question, current semantic Gap, committed Claims (empty in this bank), and an optional hypothesis whose literal text is present in the observed W. It never sees source handles, titles, URLs or private sufficient-doc labels. Case choice and source audit precede new model calls.

After the forty query calls, `QUERIES.json` and the raw request/response/error log must be committed before Search. `retrieval_freeze.json` records query hashes and retrieval policy. G and H use the same Qwen3 embedding and IP score, with candidate sets differing only in scope. U1 invokes no Find. The U1 gate determines whether U1b, U2 or neither may run. Unrun stages receive a reasoned `NOT_RUN.md`.

The exact index comprises four frozen embedding shards and one BC+ SQLite corpus snapshot. The source hashes in the executable manifest are authoritative. Tool/schema changes, query rewrites, rescored gold-dependent selection and retries are prohibited.
