"""Read completed records; never change requests/raw outputs. Can run during a batch."""
import json,hashlib
from pathlib import Path
T=Path(__file__).resolve().parents[1]
def rd(p):return json.loads(p.read_text())
def wr(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
packets=[];mapping={}
for stage in ['primary','challenge','exploration']:
 f=T/stage/(stage+'_events.jsonl')
 if not f.exists():continue
 bank={c['case_id']:c for b in ['PRIMARY','CHALLENGE'] for c in rd(T/f'bank/{b}.json')}
 labels={k:v for b in ['PRIMARY','CHALLENGE'] for k,v in rd(T/f'bank/{b}_LABELS.json').items()}
 for line in f.read_text().splitlines():
  try:e=json.loads(line)
  except json.JSONDecodeError:continue
  if e['kind']!='completed':continue
  r=e['result'];uid=hashlib.sha256(('asymmetric-review:'+stage+':'+r['id']).encode()).hexdigest()[:10];c=bank[r['case_id']]
  p={'review_id':uid,'case_id':c['case_id'],'qid':c['qid'],'question':c['question'],'claims':[{'index':i,'statement':x['statement']} for i,x in enumerate(c['state']['verified_claims'],1)],'label':labels[c['case_id']],'output':r['output'],'error':r['error']}
  packets.append(p);mapping[uid]={'stage':stage,'id':r['id'],'arm':r['arm'],'replicate':r['replicate'],'case_id':r['case_id']}
packets.sort(key=lambda p:(int(p['qid']),p['case_id'],p['review_id']))
wr(T/'analysis/review_packets.json',packets);wr(T/'analysis/review_map.json',mapping)
for q in sorted({p['qid'] for p in packets},key=int):
 ps=[p for p in packets if p['qid']==q];lines=[]
 for c in sorted({p['case_id'] for p in ps}):
  group=[p for p in ps if p['case_id']==c]
  lines += [f'\nCASE {c} gold_resolved={group[0]["label"]["gold_resolved"]}']
  for p in group:lines += [p['review_id']+' '+json.dumps(p['output'] if p['output'] is not None else p['error'],ensure_ascii=False)]
 (T/'analysis'/f'outputs_{q}.txt').write_text('\n'.join(lines)+'\n')
print('completed packets',len(packets))
