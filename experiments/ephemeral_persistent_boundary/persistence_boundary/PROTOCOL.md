# S2 Persistence Boundary

Selection is all 41 frozen `research_state_v2/claim_mutation/CASES.json`
transition observations except the sole qid 776 case: 40 cases, 11 qids.
No new source content was invented. TestCards and prior bindings are controlled
challenge packets over real W text, not reconstructed historical state. The
previous query string is a controlled action-history intervention, not a
claim that it historically produced that W. Four P6 old bindings are seeded
conflicts and carry no historical evidence claim. This limits the study to
boundary behavior, not live end-to-end accuracy.

P1 direct support; P2 incidental mention; P3 partial; P4 unrelated/NoGain;
P5 guessed X while W supports Y; P6 old X conflicts with new Y. Each W is
exactly the historical observation; reviewer truth is frozen before calls.
L receives prior query as action history. I and X omit it. X rejects every
proposed value not a case-insensitive contiguous substring of exact new W.
All arms use the same query-blind semantic verifier. Binder rationale is never
passed to verifier. Verifier errors or ambiguous decisions cannot commit.
One binder call per arm per case, zero retries; failed calls score as misses.

X gate: committed precision >=95%, recall >=85%, false promotion <=5%,
P4 NoGain preservation >=90%, P5 alternative recovery >=80%, >=3/4 P6
recovered; versus L >=6 paired false-proposal/promotion improvements and
reverse worsenings < half of improvements. Gate controls S3, never S1.
