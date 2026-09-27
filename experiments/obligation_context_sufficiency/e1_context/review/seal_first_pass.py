"""Seal manual masked labels before any semantic aggregation or unmasking."""
from experiments.obligation_context_sufficiency.common import *
from experiments.minimal_need_multiquery.run import now
from experiments.obligation_context_sufficiency.score import DIMENSIONS,ERRORS
rows=[]
for p in sorted((P/'e1_context/review').glob('PART*.json')):rows.extend(read(p))
packets=read(P/'e1_context/review/PACKETS.json')
assert len(rows)==len(packets)==216
assert {r['review_id'] for r in rows}=={p['review_id'] for p in packets}
for r in rows:
 assert set(r['dimensions'])==set(DIMENSIONS) and all(type(v)is bool for v in r['dimensions'].values())
 assert set(r['errors'])<=set(ERRORS) and r['reason'] and r['ambiguity'] in ('low','medium','high')
write(P/'e1_context/review/FIRST_PASS.json',sorted(rows,key=lambda r:r['review_id']))
write(P/'e1_context/review/FIRST_PASS_ATTESTATION.json',{'utc':now(),'reviewer':'Codex single semantic reviewer','items':216,
 'visible_for_semantic_rating':['Original Question','Verified Claims','Generated Obligation','mechanical validity'],
 'hidden_in_packets':['arm','replicate','Recent Context','case/state ID','Gold','aggregate metrics','provider reasoning'],
 'procedure':'Each rating explicitly transcribed with reason and ambiguity; grouped only by identical Q/C for consistency. Primary labels committed before key/context review and aggregation. No automated semantic scoring.',
 'limitations':'Reviewer knows prior bank/references and reconstructed contexts before execution; perfect blindness and independence are not claimed. Executor observed one arm-labelled provider length failure during transport troubleshooting; mechanical zero credit fixed by protocol.',
 'first_pass_sha256':sha(P/'e1_context/review/FIRST_PASS.json'),'no_primary_post_unmask_edits':True})
print('Sealed 216 masked judgments; commit required before unmask/aggregate.')
