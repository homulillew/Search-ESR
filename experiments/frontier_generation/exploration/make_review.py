import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from runtime import *
b=TOP/'exploration';req={x['id']:x for x in rd(b/'requests.json')}
rows=rd(b/'frontier_outputs.json') if (b/'frontier_outputs.json').exists() else [json.loads(l)['result'] for l in (b/'frontier_events.jsonl').read_text().splitlines() if json.loads(l)['kind']=='completed']
oldctx=rd(TOP/'f1_state_sufficiency/masked_contexts.json');ctxbyhash={dg(v['view']):v for v in oldctx.values()}
key={};packets=[];contexts={}
for r in rows:
    it=req[r['id']];ctxid='V'+it['view_sha256'][:10];contexts[ctxid]=ctxbyhash[it['view_sha256']]
    rid='E'+dg(['exploration-A-masked',r['id']])[:12];key[rid]=r['id']
    packets.append({'review_id':rid,'context_id':ctxid,'output':r['output'],'failure':r['error']})
wr(b/'masked_contexts.json',contexts);wr(b/'masked_packets.json',sorted(packets,key=lambda p:p['review_id']));wr(b/'private_review_key.json',key)
lines=[]
for cid,c in sorted(contexts.items()):
    v=c['view'];lines += [f"\n{cid} qid={c['qid']} complete={c['complete']} resolved={[k for k,x in c['coverage'].items() if x['resolved']]}",'Hypothesis: '+str(v.get('Working Hypothesis','[not exposed]'))]
    for p in sorted([p for p in packets if p['context_id']==cid],key=lambda p:p['review_id']):lines.append(p['review_id']+' '+json.dumps(p['output'] or p['failure'],ensure_ascii=False))
(b/'masked_brief.txt').write_text('\n'.join(lines)+'\n');print(len(rows),'masked exploration responses')
