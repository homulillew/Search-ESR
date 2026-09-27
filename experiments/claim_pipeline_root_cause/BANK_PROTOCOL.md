# Frozen mechanical selection rule, before new model calls

Candidate inventory: every observed window in the base's minimal_research_loop
verify_necessity OBSERVATIONS and every actual Reader request in clean
micro_recovery, H1 and H2. Full per-window text/metadata remain exact. A multi-window
acquisition supplies one full-window packet per observed W, sharing its actual
OneGap and pre-Reader C. This changes acquisition granularity, equally in all arms;
no clipping, metadata enrichment, source rewriting or future state is allowed.
Legacy review-designed contexts are flagged, never called natural live trajectories.
The primary bank is natural **evidence**, with mixed real and archived-designed
Gap/C contexts. Report results by that context kind as a sensitivity.

Other requested experiment branches are inventoried at immutable commits. Their
state-to-requirement inputs and evidence-only Writer bank lack the same jointly
observed OneGap/C/Observation tuple; they are audit/provenance corroboration, not
silently reconstructed current Reader packets. No new source is retrieved.

Inventory dedup key is exact canonical(qid,OneGap,C,Observation). Identical byte
content with different real C/Gap remains a distinct potential packet. Dedup never
uses model accuracy. Frozen ID=sha256 of that tuple. All exclusions retained.

## Assignment

D-only known design-exposure qids:228,435,517,538,546,637,922,1094. They cover
identity, temporal, role, document, sequence, qualifier, attribution, cross-entity
target relations respectively. These are routing strata; source-relative review
confirms actual family and positive/trap/no-new labels before bank freeze.

D first pass: one packet per available D qid, preferring a legacy T6 duplicate
challenge if present, otherwise the smallest packet SHA. D second pass: visit D
qids by sha256(`claim-root-v1:D:`+qid), select one additional smallest-SHA packet
with nonempty C and a real historical candidate if available, otherwise next
smallest SHA, until D=12. Cap2/qid globally. This explicitly enriches the diagnostic
portion for novelty opportunities without selecting new-arm successes/failures.

H pool: all other inventory qids having at least two distinct eligible packets.
Order qids by sha256(`claim-root-v1:H:`+qid); first six qids form H-diagnostic,
next six H-confirmation. Take the smallest two packet SHA per qid. Further qids
remain unselected; never fill slots from D or backfill from later outputs.
H contains archived cases previously used by other studies, but no D design
examples. It is not a newly collected benchmark or a claim of zero reviewer exposure.

Target: D12 + H-diagnostic12 + H-confirmation12 =36, at most2/qid. E1/E2 run only
D+H-diagnostic. H-confirmation input/atoms are reviewed and frozen now, but its
model outputs are not requested before the conditional E3 component decision.

After mechanical selection, review full observed text, expected useful atoms,
ambiguity, positivity/trap/no-new strata, and each provenance edge. Do not read
future tools/final answers/gold. If fewer than36, fewer than18 qids, fewer than6
verified relation families, fewer than12 held-out packets/6 qids, absent positive
or trap or no-new strata, or unrecoverable provenance: stop, report reason; no
ad-hoc replacement. Bank/protocol/annotations commit precedes harness/live freeze.
