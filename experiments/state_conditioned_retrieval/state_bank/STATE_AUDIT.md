# SC0 prefix and temporal audit

Frozen before any new Query Writer or Search call. The 24 cells span 10 qids: 435 (6), 177 (4), 580 (4), 546 (3), 1094 (2), and one each for 517, 387, 311, 186, and 1034. Every arm keeps the U1 raw question and target Gap verbatim. The S0/S1/S2/S3 ladders are nested, with three short facts in S3. Each fact has an exact supporting span in a prior historical W, except q580's series identity, which is supported by the observed W's domain (`youretheworst.fandom.com`). The writer sees only statements, never provenance or private truth.

## Time ordering

Seventeen cells have a later target-supporting W in the same historical replay after the selected prior W: P05 for 435, P07 for 177, P12 for 580, P06 for 546, and P11 for 517. P06's prior W13 is decision 3 and target W35 is decision 4. The remaining seven are right-censored: their selected historical prefix does not contain the target answer, but no later target observation from that same trajectory is asserted. Their `target_evidence_first_seen_event` is null. This is a limitation of the bank; these cases test a clean pre-answer prefix, not a measured source-discovery interval.

The U1 `evidence_location.anchor` is sometimes an entity name already known before the target answer. For C02/D02 (Oliver Mtukudzi) and D03/D04 (Enugu Rangers), the audit excludes answer-bearing relation text such as Forbes inclusion or the 2014 table rather than excluding the entity name. Target replay support quotes are stored privately. A literal anchor match alone is not treated as proof of answer leakage or target support.

## Selection and exclusions

The eight U1 B cells preserve earlier observed candidate/source facts while targeting another fact or local section. C01/C02/C03/C05/C06/C07/C11/C12 and all eight D cells use a verified earlier observation that is actually relevant to their frozen Gap. Several unselected U1 C windows were merely a wrong person, wrong team, or unrelated page and could not support a truthful candidate-grounding ladder. U1 C10 was excluded because its putative prior biography already supplied the requested actor identity. The original q186 game/publisher gap was excluded: the available candidate game window disclosed the publisher. The retained q186 B06 concerns a later episode name, so it cannot adjudicate that original publisher miss. No cell was selected using S1 model output or new Search results.

All sufficient document IDs and bridge document IDs come from the frozen U1 truth and historical source mapping. A bridge ID is recorded only when the prior source is distinct from the target sufficient set. Some B cells already observed a different window of their sufficient document; report them separately when interpreting retrieval gains. Other candidate bridge documents encountered during S1 will not be promoted after seeing ranks.

## Reviewer decisions and limits

The single reviewer admitted each cell because its S3 facts are source supported, decision relevant to at least identifying the referent or narrowing the next evidence need, and omit the target answer. The factual support and forbidden answer-bearing strings are checked by `build_bank.py`. Nested S1 is candidate grounding; S2 adds a clue or constraint; S3 adds one more relation or context fact. This is a deliberately small projection, not a production State schema. Some S3 facts, especially q580's season-four context, may fail to help the later target Gap; that is a possible experimental failure, not a reason to revise the State after retrieval.

The bank reuses qids and sometimes the same target document under different fixed Gaps. It is a paired diagnostic rather than 24 independent questions. Raw historical W may contain additional true details that were intentionally omitted from S3; the raw-history control tests the cost of this compression.
