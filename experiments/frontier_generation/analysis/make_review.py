"""Construct masked review artifacts; key is only used after labels are finalized."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from runtime import *

base=TOP/'f1_state_sufficiency'
rows=rd(base/'frontier_outputs.json') if (base/'frontier_outputs.json').exists() else [json.loads(line)['result'] for line in (base/'frontier_events.jsonl').read_text().splitlines() if json.loads(line)['kind']=='completed']
requests={x['id']:x for x in rd(base/'requests.json')}
coverage=rd(TOP/'bank/COVERAGE.json');maps=rd(TOP/'bank/REQUIREMENT_MAP.json')
# Question IDs are public grouping metadata, but case/arm/replicate/condition IDs are hidden.
contexts={};key={};packets=[]
for r in requests.values():
    v=json.loads(requests[r['id']]['request']['messages'][1]['content'])
    vh=dg(v)
    if vh not in contexts:
        c=coverage[r['case_id']];col={'H':'history','S':'state','SH':'combined'}[r['arm']]
        contexts[vh]={'view':v,'qid':r['qid'],'coverage':{k:{'resolved':x[col+'_resolved'],
            'supported_and_missing_parts':x['supported_and_missing_parts']} for k,x in c['coverage'].items()},
            'complete':c[col+'_complete'],'requirements':maps[str(r['qid'])]['requirements']}
for r in rows:
    vh=requests[r['id']]['view_sha256']
    rid='M'+dg(['frontier-masked-review-20260926',r['id']])[:12]
    key[rid]=r['id']
    packets.append({'review_id':rid,'context_hash':vh,'output':r['output'],'failure':r['error']})
ordered=sorted(contexts,key=lambda h:dg(['context-order',h]))
ctids={h:f'K{i:03}' for i,h in enumerate(ordered,1)}
for p in packets:p['context_id']=ctids[p.pop('context_hash')]
ctx={ctids[h]:contexts[h] for h in ordered}
wr(base/'masked_contexts.json',ctx);wr(base/'masked_packets.json',sorted(packets,key=lambda x:x['review_id']));wr(base/'private_review_key.json',key)
lines=[]
for cid,c in ctx.items():
    if not any(x['context_id']==cid for x in packets):continue
    v=c['view'];lines += [f"\n{cid} qid={c['qid']} complete={c['complete']} resolved={[k for k,x in c['coverage'].items() if x['resolved']]}",
      'Hypothesis: '+str(v.get('Working Hypothesis','[not exposed]')),
      f"Visible claims={len(v.get('Verified Claims',[]))}; history events={len(v.get('Chronological Research History',[]))}"]
    for p in sorted([x for x in packets if x['context_id']==cid],key=lambda x:x['review_id']):
        lines += [p['review_id']+' '+json.dumps(p['output'] or p['failure'],ensure_ascii=False)]
(base/'masked_brief.txt').write_text('\n'.join(lines)+'\n')
print('Masked',len(ctx),'contexts and',len(packets),'responses; no labels assigned')
