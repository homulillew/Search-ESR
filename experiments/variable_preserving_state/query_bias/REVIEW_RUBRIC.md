# Frozen V2 query review rubric

The reviewer sees the original question, visible prefix, provisional H, semantic
Gap, expected source type, and one anonymous query. No future result, gold
answer, or arm name may be used. Review each single Search query for:

- `gap_alignment`: likely to retrieve information resolving the current Gap.
- `source_type_alignment`: seeks the expected evidence source type, rather than
  a generic entity page or a source unrelated to the missing relation.
- `unsupported_binding_leakage`: includes a concrete name, title, date, count,
  opponent, event, season, or candidate-relation not grounded by question,
  observed W, or the explicit provisional H. A provisional H may appear in a
  query but remains provisional; linking it to an unobserved answer is leakage.
- `confirmation_bias`: primarily seeks confirmation of such an unsupported
  concrete value. This implies leakage, but leakage need not imply confirmation.
- `unknown_targeting`: seeks the missing value or relation without presupposing
  a specific unsupported answer.
- `specificity`: low, medium, or high, descriptive only.

Record the exact leaking substring(s) and one reason. Invalid/provider failed
responses get false alignment and unknown targeting, and are retained in
paired comparisons. A failed Claim/Test state from V1 is passed as empty state
with an explicit error marker, never silently repaired.

Gate Q2 vs Q1: at least 6 net paired improvements in leakage, with reverse
worsening fewer than half the improvements; mean gap and source-type alignment
must each be no lower than Q1. If the state representation does not change
queries, stop before V3.
