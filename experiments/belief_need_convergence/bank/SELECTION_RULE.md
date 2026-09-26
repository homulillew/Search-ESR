# Frozen-before-calls extraction and split rules

1. Enumerate actual archived frontier inventory states, per-observation PRE/POST
   Writer states in G4/G5, BC+ formal PRE/POST Writer states, and evidence-scope
   inputs (deduplicated projections). Do not read final answers/gold identities.
   Keep Q, Claim statements, H exactly as archived. Provenance includes file hash
   and JSON pointer. Do not turn source text into new Claims.
2. Deduplicate by Q + ordered Claim statements + H; retain all origin pointers.
   For splitting, group identical Q + Claim statements even if H differs.
   Claim-order/paraphrase-only variants are reviewed and not used to inflate N.
3. q580/q1094/q435/q311/q186 are challenge only. q324/q776 originate from older
   hand-built failure packets, not natural Q+C+H research episodes; challenge
   provenance inventory only. Newly held-out questions with no archived Belief
   are not eligible. Explicit historical frontier-review bank states are exposed
   and cannot be fresh confirmation. Novel intermediate Writer states can be
   less-exposed development/reserve; shared-qid exposure remains disclosed.
4. Primary retains actual evidence-supported Claims. Unsupported claims are not
   silently corrected: exclude contaminated states from primary and retain their
   exclusion reason; genuine conflicting supported facts remain eligible U6/B10.
   U1–U6 are overlapping descriptive strata, not an ontology given to the model.
5. Select up to24 development states, balanced round-robin across eligible qids
   and available no-H/weak-H/multi-gap/one-gap/covered-trap/contradiction strata;
   cap any qid at5. Reserve up to24 disjoint state-family groups, balanced in the
   same way, before calls. If fewer qids/states exist, report exact shortfalls.
   Reserve is never used to design an intervention. At least8 fresh qids is a
   non-waivable formal confirmation coverage requirement; fewer cannot PASS.
6. Select up to10 challenge states, including both strongest and early/misleading
   states across the five named qids. Do not use their success for a fresh gate.
7. Select12 supported coverage-delta pairs plus up to4 H-delta pairs. These are
   controlled diagnostic projections of real supported updates: B adds exactly
   one actual Claim, or H alone changes. Label constructed pairs separately from
   natural primary states; keep other fields unchanged. No invented facts/H.
8. Strict coverage uses every explicit target-defining question condition and
   requested relation. A related value, future cumulative lower bound, incomplete
   list or strong H cannot fill a gap. Zero genuine one-gap/closure states means
   unvalidated coverage, not permission to synthesize a completed primary bank.
9. All selections, semantic labels, supported Claim provenance, valid gap sets,
   prompts/contracts, sample counts, integer gates and failure policy are frozen
   and committed before the first model request. No semantic retry/best-of.
