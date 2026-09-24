# Frozen F2 reviewer truth

For every actual F1 C Finding, use the pre-call F1 W/review and the exact
Finding statement. All are included, including any mistakes. A Finding is
supportable only if exact W establishes its complete stated relation and it
is a factual, new, Gap-useful belief. For stress packets, the reviewer freezes
`expected_supported=false` before verifier calls, with a specific missing or
wrong relation. Incidental co-mentions, partial conjunctions, unsupported
sequence completion, wrong entity bindings, and unresolved title equivalence
cannot become a stable Claim. Do not use outside knowledge or final answers.

Commit precision counts supported committed packets / all committed packets.
Recall counts supported packets committed / all supported packets. False
promotion is unsupported committed packets / all unsupported packets.
Stress rejection is negative packets rejected / all stress packets. Verifier
errors and malformed verdicts cannot commit and remain in all denominators.
Evidence binding requires the new W ref carried by the Finding. Claim bloat
is unsupported committed Claims, not merely total number of Claims.
