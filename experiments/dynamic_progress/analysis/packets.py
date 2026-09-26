"""Build masked output packets; no model calls or semantic labels generated."""
import sys,json,hashlib
from pathlib import Path
T=Path(__file__).resolve().parents[1]
def rd(p):return json.loads(p.read_text())
def wr(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def opaque(i):return hashlib.sha256(('dynamic-progress-review-v1:'+i).encode()).hexdigest()[:12]
bank={c['case_id']:c for name in ['PRIMARY','CHALLENGE'] for c in rd(T/'bank'/f'{name}.json')}
labels={k:v for name in ['PRIMARY','CHALLENGE'] for k,v in rd(T/'bank'/f'{name}_LABELS.json').items()}
rows=[]
log=T/'p1_progress/progress_events.jsonl'
if log.exists():
 for l in log.read_text().splitlines():
  try:e=json.loads(l)
  except json.JSONDecodeError:continue
  if e['kind']=='completed':rows.append(e['result'])
key={opaque(r['id']):r['id'] for r in rows};wr(T/'analysis/private_review_key.json',key)
review=T/'analysis/semantic_review.json'
review=rd(review) if review.exists() else {}
packets=[]
for r in rows:
 uid=opaque(r['id']);c=bank[r['case_id']]
 packets.append({'review_id':uid,'qid':c['qid'],'checkpoint':c['checkpoint_id'],'Q':c['question'],'Claims':[x['statement'] for x in c['state']['verified_claims']],'frozen_label':labels[c['case_id']],'output':r['output'],'error':r['error']})
wr(T/'analysis/review_packets.json',sorted(packets,key=lambda p:p['review_id']))
# concise pending output view grouped by qid/checkpoint; full Claims remain in packets.
lines=[]
for p in sorted(packets,key=lambda p:(int(p['qid']),p['checkpoint'],p['review_id'])):
 if p['review_id'] in review:continue
 lines += [f"\n{p['review_id']} q{p['qid']} {p['checkpoint']} gold={p['frozen_label']['gold_resolved']}",json.dumps(p['output'],ensure_ascii=False) if p['output'] else str(p['error'])]
(T/'analysis/pending.txt').write_text('\n'.join(lines)+'\n')
print('completed',len(rows),'reviewed',len(review),'pending',len(rows)-len(review),'failed',sum(r['error'] is not None for r in rows))
