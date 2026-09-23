# Post-call semantic audit of the frozen E1 labels

This audit does **not** amend `REVIEW_LABELS.json`, `RUBRIC.json`, `freeze.json` or the prespecified gate. It checks interpretation of the completed outcome.

## Reviewer label defect in qid 186

`T5_186` called C4 (“two people sharing a family name” credit condition) unrelated, and `T7_186` called the same condition C2 unrelated. The new real W excerpt visibly lists Sean Michael Puckett and Terri L. Puckett among the credited people. Their common surname is evident in the prefix. Therefore, closing these Claims is **not** a demonstrated false closure or unrelated mutation. The linked credit Gap may also be closable. These are reviewer label errors, not model errors. T7 additionally compares a shortened-title “Galacta” 1993 page with a full-title 1992 page, so the release-year reopening target remains medium ambiguity.

The frozen metric names `unsupported_new_claims` whenever a new Claim was outside the pre-call allowed-new-claim list. Manual review of the 35 B/C new Claims finds that **most are locally supported by the cited W excerpt**: the model often copied extra true facts from the observation into committed state. They are *unrequested state expansion*, not automatically false evidence. In T7 C, “The game is Galacta: The Battle for Saturn” is ambiguous as a full target identification because the abbreviated-title date conflict remains. The frozen precision metric still penalizes unrequested expansion under the pre-call rubric; this audit narrows the semantic interpretation of that penalty.

## Sensitivity that preserves the frozen decision

Removing both affected qid-186 cases without changing any labels gives mutation precision A **33/44 (75.0%)**, B **33/54 (61.1%)**, C **33/46 (71.7%)**. C remains below the frozen 80% G3 threshold. Paired unrelated-churn changes versus A remain B **2 improved / 12 worsened**, C **4 improved / 8 worsened**. G1 still fails its reverse-worsening condition. This is descriptive sensitivity, not a repaired gate or a new preregistration.

The real takeaway is narrower than “Delta causes unsupported facts.” The tested Delta prompt tended to add observed-but-unrequested Claims and sometimes close broad Gaps. Triggered Verify rejected two proposed Claim transitions (one insufficient conjunction, one conflicting release-year overcommitment) and five dependent Gap closes. Its refusal to commit a proposed `refuted` release-year transition left the prior `supported` status in place when the verifier returned `open`; this reveals a recovery limitation under the current reject-and-retain rule. No downstream stage was run after the frozen E1 gate failed.
