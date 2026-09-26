# Review bookkeeping

Single Codex semantic reviewer. Arm-hidden exports are an aid, not independent human blinding or independent errors. The production pipeline never imports this directory. All source support judgments use the actual returned Observation (visible title/URL/body), with prior Claims for explicit task identification only. Source-supported does not mean externally fact-checked truth.

## Stable update reviews

`update_queue.py` exports completed Updater calls as packets keyed by digest(request hash, proposed output). Identical request+output pairs can share a semantic review, but all original calls/claims remain separately counted. `UPDATER_LABELS.json` is an explicit per-packet review ledger. `mark_updates.py` is only a recording helper; its IDs must be deliberately supplied after reading each packet. Empty keep proposals contain no positive Claim to assess and can be recorded as vacuous support cases.

Additional error dimensions are separate from entailment:

- material_qualifier_omission: true sentence loses a crucial year or relationship scope;
- incidental: supported fact that does not reduce the original goal;
- title_only_support: narrow Claim is licensed by the observed title, while the body is a placeholder;
- contradicted_hypothesis_set / spurious_hypothesis_clear / missed_material_rejection / correct_material_rejection: control-state judgment independent of Claim precision.

The 2012/2013 PTC Finals 4–3/4–0 pair must never be silently treated as 2023. A 2017 article's 65-album fact plus existence of a May 2017 feature may lose the exact feature-count binding when stored as separate sentences. Review literal Claims-based closure separately from source-provenance reconstruction; do not replace either with answer-name correctness. The original q435 strict interview-quote sensitivity is additionally retained.

## Evidence progress

Known-pool windows are read in full. All positives have reviewer-authored factual updates and next-decision implications. Outside-pool title/topic screening with selected full-text follow-up yields a non-exhaustive alternative-source sensitivity. These sensitivity estimates are lower bounds. Stage-specific `evidence_labels.json` snapshots prevent later G5 observations from revising G3/G4 estimates. Exact observation text may be reused across review packets; novelty is always evaluated against that packet's current Claims.

Source-level progress is not automatically a persisted-state improvement. For example an Observation can refute PSG–Lille while the Updater keeps only another Messi free-kick fact. Conversely, a supported state update can be incidental or duplicate and still increase storage/context and invalidate the operational residual cache.
