# Frozen state

Remote base fetched and verified: 453161c2d2335416d4f439f9419e85c2266658b5.
S0 semantic annotation/reinterpretation committed at 4069ad9 before any new model calls.

S1: 18 V+ and 11 V− units, 10 qids combined; one trajectory each, two decisions/one action. V− target of 12 could not be met with equally defensible corpus refutations. A proposed Heart Evangelista negative was excluded because a rise to stardom in one industry does not logically exclude a later break in another. No invented replacement. VN12 is an explicit question/benchmark conflict; report 11-unit condition-failure and 10-unit wrong-benchmark-candidate denominators. q311 has five negatives and q546 six total units: source/candidate clustering is a limitation, not extra independent evidence.

S2: ten real historical Q-only initial checkpoints, one per named historical qid, three decisions/one action. Same Q-only checkpoints for S1; Candidate and single condition are supplied only there. No later supported H is erased.

Provider/model, sampling defaults, U1 bytes, Search/Find/Open implementation, raw windows, embedding corpus/model and Workspace are unchanged. GPU1, float16, exact global retrieval, k=5. No hard gating. max_retries=0, timeout=240 seconds, four transport workers. At most 528 API submissions / 88 tool actions; all failures retained. Request body hashes and raw responses/usage are journaled; adaptive request builder and inputs frozen before first submission.

Explicit primary gates: V+ >=15/18; V− >=9/11; wrong-benchmark-candidate subset >=8/10; useful Discovery <=7/10; Verification actual average tool actions below Discovery; restricted successful-update cost at least 0.5 action lower. S4 requires all; S5 additionally requires positive S4. The negative sample shortfall limits generalization regardless of rates.

`freeze.json` records exact code/data hashes, source prefix hashes, provider, schemas, prompts, initial request hashes, and unchanged binary metadata/hashes. Runtime reads only `bank/RUNTIME_INPUTS.json`; hard-constraint annotations, polarity, benchmark and reference evidence stay offline.
