# U1 private truth and scoring rubric

The target document must contain the specific fact or exclusion needed by the frozen semantic Gap, not merely the same entity. `PRIVATE_TRUTH.json` records the corpus docid, exact source-content hash and an independently verified supporting anchor. Known alternative sufficient documents are included before model calls; unlisted documents in top five will be audited against the same rubric and reported separately, without changing the preregistered primary metric.

For A, the anchor is inside the historically observed W and no matching Claim is supplied to the Query Writer. For B, the source D was observed but the anchor lies outside that W. For C, the observed D lacks the anchor and is not a strongly related candidate for the new Gap. For D, the observed D concerns the same central entity or series but lacks the new Gap's required fact. Checkpoint identity is the frozen observation case and text hash. These are one-window diagnostic prefixes, not entire historical agent workspaces.

The primary denominator is 40 case cells. Report qid and document clustering. If an observation or corpus anchor is missing, reject the cell before calls. If an alternative source appears after retrieval, preserve the original primary truth and give a separate sensitivity result rather than silently expanding the label. A model/query/tool failure is a miss, never removed from the denominator.

Candidate document recall is not evidence recovery. U1 does not execute Find and makes no claim about what window the localizer would return.
