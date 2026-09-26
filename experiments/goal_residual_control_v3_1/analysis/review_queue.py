"""Mask arm names for single-reviewer scoring; deduplicate exact packet/output pairs."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from runtime import *
B=TOP/'admission_replay';bank=read(B/'BANK.json');mapping={};q={}
new=[]
if (B/'paired_events.jsonl').exists():
 for l in (B/'paired_events.jsonl').open():
  e=json.loads(l)
  if e['kind']=='completed':new.append(e['result'])
for i,p in enumerate(bank):
 rows=[{'arm':'U0','output':p['U0']['output'],'error':p['U0']['error']}]+[r for r in new if r['case_id']==p['packet_id']]
 for r in rows:
  uid=digest(['admission-review',p['packet_id'],r['output']])[:16]
  mapping.setdefault(uid,[]).append({'packet_id':p['packet_id'],'arm':r['arm']})
  q[uid]={'review_id':uid,'packet_index':i,'packet_id':p['packet_id'],'qid':p['qid'],'output':r['output'],'error':r['error']}
write(B/'PRIVATE_REVIEW_MAP.json',mapping);write(B/'OUTPUT_REVIEW_PACKETS.json',list(q.values()))
reviewed=read(B/'REVIEWS.json') if (B/'REVIEWS.json').exists() else {}
lo=int(sys.argv[1]) if len(sys.argv)>1 else 0;hi=int(sys.argv[2]) if len(sys.argv)>2 else 55
for r in sorted(q.values(),key=lambda x:(x['packet_index'],x['review_id'])):
 if lo<=r['packet_index']<hi and r['review_id'] not in reviewed:print(r['packet_index'],r['review_id'],json.dumps(r['output'],ensure_ascii=False),r['error'] or '')
print('finished calls',len(new),'/110; unique review packets',len(q),'reviewed',len(reviewed))
