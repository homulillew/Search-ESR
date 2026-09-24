# F1 Finding extraction

All 41 historical M1 Observation cells are selected mechanically; the same
source text appears in correlated sibling cases with different semantic Gaps.
The single reviewer freezes a primary E1–E8 type plus required/optional
Findings, duplicate facts, forbidden inferences and NoGain before requests.
The reader only sees exact current W, original Question and arm-specific Gap/
Claims. Output schema is strictly `{findings:[{statement,evidence_refs}]}`,
0–3, with each ref equal to the current W. No semantic repair is performed.

Precision requires W grounding, current-Gap relevance and world-fact form;
for C also novelty against existing Claims. Recall is semantic coverage of
frozen required Findings. Also score unsupported/overreach, irrelevant,
duplicates, E6 silence, and mean finding count. Failures score as misses and
remain in denominator.

C absolute gate: precision >=90%, recall >=85%, unsupported inference <=5%,
E6 silence >=90%, duplicate rate <=10%. If A has >=5 Gap-irrelevant error
cases, B/C need >=4 net paired reductions. If B has >=4 duplicate cases, C
needs >=3 net paired reductions. Otherwise comparison is ceiling-limited and
does not block absolute reliability.
