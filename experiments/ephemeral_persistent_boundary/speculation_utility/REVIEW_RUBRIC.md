# S1 review rubric, frozen before Search

Review one top-5 Search result using only the original question, current Gap,
provisional H, natural TestCard, expected source type and returned titles/raw
previews. Do not inspect future trajectories, gold answers, full documents or
the query's S/D label. Record:

- `suitable_source`: at least one returned source could reasonably verify the
  current Gap, given its type and visible content. Entity related alone does
  not suffice.
- `useful_evidence`: returned raw preview actually supports, refutes, or
  effectively excludes a current Test condition or unknown relation.
- `direct_unknown_resolution`: a current unknown value and its required
  relation are both established in the returned preview.
- `speculative_value_support`: for a query with a frozen leaking value, a
  preview supports that exact value *in the current required relation*. Mere
  mention, title match, or unrelated co-occurrence is false. Use null for
  non-speculative queries.
- `no_gain`: no useful evidence and no suitable source.
- `candidate_breadth`: one_candidate, multiple_directions, or unclear, based
  on the top-5 titles/previews. Descriptive only.

Record supporting ranks, W refs, and short reasons. Failed Search cells are
retained as failure and cannot receive positive evidence or suitability.
Report the 48 original query outcomes by V2 arm and paired S versus D for
every frozen leaking query. No S1 pass/fail gate is defined.
