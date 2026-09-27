"""Record manual source-only review; no access to candidates or verdicts."""
from .contracts import HERE,read,save
def record(rid,reasons,unsupported=(),omitted=(),attribution=(),modality=(),relation=(),reason='All distinct substantive observed propositions are represented; no material omission found.'):
    packet=read(HERE/'review/inventory_source'/f'{rid}.json')
    assert len(reasons)==len(packet['Inventory']['facts'])
    save(HERE/'review/labels_by_inventory'/f'{rid}.json',{
        'facts':[{'index':i,'source_supported':i not in unsupported,'reason':r} for i,r in enumerate(reasons)],
        'omitted_observed_commitments':list(omitted),'attribution_loss':list(attribution),'modality_loss':list(modality),
        'relation_loss':list(relation),'severe_verdict_uninterpretability':False,'reason':reason,
        'review_context':'Only this packet Evidence and Inventory; no linked candidates or G0/G1 verdicts displayed.'})

def combine():
    paths=sorted((HERE/'review/labels_by_inventory').glob('*.json'))
    save(HERE/'review/inventory_labels.json',{p.stem:read(p) for p in paths})
