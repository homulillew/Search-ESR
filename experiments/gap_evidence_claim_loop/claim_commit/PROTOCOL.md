# F2 Verify → Claim commit

F1 passed its pre-registered gate. F2 includes every actual C Finding from
F1, with no cherry-picking, plus 15 pre-call negative/ambiguous proposals
over exact real W excerpts. Stress categories cover incidental mention,
partial conjunction, sequence overreach, wrong identity and conflict or
source-role ambiguity. Stress proposals are controlled verifier challenges,
not historical model outputs; no webpage text is fabricated.

The same query-blind Verifier sees Active Gap, one Finding, exact W and
relevant existing Claims. It sees no model rationale or F1 review label. It
returns only `supported|insufficient` and a reason. D commits every
mechanically valid Finding; V commits only `supported`. Each packet is an
independent state step. Harness-created Claim objects contain exactly
`claim_id`, `statement`, `evidence_refs`, `version`; rejected Findings expire.
Every verifier call is single-shot (`max_retries=0`), and all errors reject
commit while remaining in recall denominators.

V gate: committed precision >=95%, valid-Finding commit recall >=90%, false
promotion <=5%, and >=90% of stress negatives rejected. Comparative D/V
superiority is assessed only if D has at least four false promotions. F2
passing is necessary before any F3 rollout.
