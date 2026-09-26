from pathlib import Path
import json,collections,hashlib
T=Path(__file__).resolve().parents[1];R=T.parents[1]
def rd(p):return json.loads(p.read_text())
def wr(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
s=rd(T/'f1_state_sufficiency/summary.json');pairs=rd(T/'f1_state_sufficiency/replicate_stability.json')
out=rd(T/'analysis/HISTORY_LENGTH_SENSITIVITY.json')
out['replicate_categories']={q:{a:dict(collections.Counter(p['category'] for p in pairs if p['arm']==a and s['quartile_membership'][p['case_id']]==q)) for a in ['H','S','SH']} for q in ['Q1','Q2','Q3','Q4']}
wr(T/'analysis/HISTORY_LENGTH_SENSITIVITY.json',out)
bank=rd(T/'bank/CHECKPOINT_BANK.json');cache={};checked=[]
for c in bank:
    p=c['provenance'];path=R/p['path']
    if str(path) not in cache:cache[str(path)]=rd(path)
    blob=cache[str(path)]
    v=blob[p['cell']] if 'cell' in p else blob[p['index']]
    if p['pointer']=='seed_snapshot':
        snaps={x['case_id']:x for x in rd(R/'experiments/goal_residual_control/bank/SNAPSHOTS.json')};v=snaps[v['seed_snapshot']]
    else:
        for part in p['pointer'].split('/'):v=v[int(part)] if isinstance(v,list) else v[part]
    assert v==c['state'],c['case_id'];checked.append(c['case_id'])
wr(T/'analysis/PROVENANCE_CHECK.json',{'states_exactly_equal_historical_pointer':len(checked),'cases':checked,'no_normalization_applied':True})
rows=[]
for q,byarm in out['replicate_categories'].items():
    rows.append('| '+q+' | '+' | '.join(str(byarm[a].get('one_valid',0))+'/6' for a in ['H','S','SH'])+' |')
text='''# Additional diagnostics

## Actual-history quartile replicate instability

Mixed-validity replicate pairs (one valid, one invalid); six checkpoint pairs per arm per quartile. Different valid requirements are not instability failures.

| Quartile | H | S | SH |
|---|---|---|---|
'''+ '\n'.join(rows)+'''

Full category counts are in analysis/HISTORY_LENGTH_SENSITIVITY.json. These small, correlated strata have different qids and closure states; no causal length trend is inferred.

## Critical repair decomposition

The frozen gate flags F06,F13,F15,F16 across3qids. F15/F16 have identical STOP outputs in S and SH, but SH has source evidence for total seasons that S cannot see. They are differences in evidence-relative admissibility, not changed behavior. F06 changes from S STOP to SH character testing; F13 has one S unsupported premise with another S replicate valid. This decomposition explains the gate without changing its definition.

## Exact provenance

All24selected full States compare equal to their original historical JSON pointer, not merely to an internally generated hash. Production exposes only authorized view fields. See analysis/PROVENANCE_CHECK.json.
'''
(T/'f1_state_sufficiency/ADDITIONAL_DIAGNOSTICS.md').write_text(text)
print('verified24historical state pointers; quartile mixed-validity pairs', {q:{a:x.get('one_valid',0) for a,x in b.items()} for q,b in out['replicate_categories'].items()})
