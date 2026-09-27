# Pre-call evidence-to-claim review rubric

One task-familiar Codex reviewer; no independent reviewer/blinding claim. No provider reasoning. These rules and source references are frozen before Writer calls. Actual candidate-level judgments are made after Writer but before Admission requests are executed, then committed and sealed.

For every actual candidate, including mechanically rejected candidates, record:

```json
{
  "candidate_id": "W_S001_r1_C1",
  "claim_entailed_by_observation": false,
  "claim_entailed_by_excerpt": false,
  "error_tags": ["entity_binding_unproven"],
  "high_risk": true,
  "candidate_hardening": true,
  "useful": false,
  "matched_atom_ids": [],
  "reason": "Content-based explanation with the actual source scope."
}
```

The reference claim texts are semantic recall atoms, not exact wording targets. Judge every proposition in the output statement. Narrower safe Claims may be admitted, but only a Claim or collection of Claims establishing the full frozen atom earns that atom's recall credit. An anchor in the reference is a locator into the source, not necessarily a complete proof excerpt. A longer exact span from the same source is legal.

The review file also contains `atom_support_sets`, exactly one row for each of112(atom, replicate) slots. Each row has `atom_id`, `replicate`, `sufficient_candidate_sets`, and `observation_sufficient_candidate_sets`. Each set is a nonempty list of actual same-source, same-replicate candidate IDs jointly establishing that atom. The first type requires every candidate to be entailed by its own excerpt; the second measures Writer recall against the whole source before Admission. Empty lists mean no support in Writer output. Freeze these judgments before seeing Admission decisions. After Admission, a reference atom is covered only if one frozen sufficient set survives in full. This permits factual splitting without post-output relabeling or cross-source composition.

No outside facts, future source, gold answer, guessed identity, or Question-as-evidence. Title/URL metadata identifies the observation; it cannot silently supply a predicate, participant, date or relation absent from the actual quoted excerpt. A quotation can come verbatim from the observed text or title field, but cannot concatenate separate fields/spans. A title-only quotation proves at most what that title itself says.

Distinguish source fidelity from factual-world truth: faithfully scoped “this source reports X” is not a verified universal truth. Preserve temporal, modal, quantifier, conditional and attribution scope. If source statements conflict, preserve attribution/conflict or only their supported common ground; do not pick a unique value silently.

High-risk false admissions include candidate hardening, unsupported identity/relation, argument swap, cross-source composition, temporal/modal/quantifier/conditional strengthening, population generalization or inferred causation. An incorrect observation-level Claim cannot become correct by using a shorter excerpt. Correct whole-observation meaning with an insufficient quoted witness also fails excerpt-level admission fidelity.

Relevant negative or discriminative facts can be useful without identifying the answer. Source-relative statements with unresolved names may be valid. Missing relation evidence does not make every literal biography attribute invalid.

Matched atom IDs must belong to the same source. Unlisted but directly entailed outputs are not automatically false; review them and include them in Precision. Incidental safe Claims are reported separately for usefulness, not mislabeled hallucinations. All empty Writer outputs and failures keep their predefined recall slots. No relabeling or atom deletion based on model output.

Q/R-induced candidate hardening is the E1 diagnostic proxy. H is absent from Writer and Admission, so E1 has no experimental estimate of a true H-to-C intervention effect. Later stages must test that separately.

Zero-risk and null-denominator cases remain distinct. No hypothetical Admission rescue, Recall or live recovery scores may be reported before those stages run.
