import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from runtime import *
b=TOP/'admission_exploration';bank=read(TOP/'admission_replay/BANK.json');idx={p['packet_id']:i for i,p in enumerate(bank)}
old=read(TOP/'admission_replay/REVIEWS.json');new=read(b/'REVIEWS.json') if (b/'REVIEWS.json').exists() else {};rows=[];mapping={}
for l in (b/'U2_events.jsonl').open():
 e=json.loads(l)
 if e['kind']!='completed':continue
 r=e['result'];uid=digest(['admission-review',r['case_id'],r['output']])[:16]
 row={'review_id':uid,'packet_id':r['case_id'],'packet_index':idx[r['case_id']],'qid':r['qid'],'output':r['output'],'error':r['error']};rows.append(row);mapping[uid]={'packet_id':r['case_id'],'arm':'U2'}
 if uid in old:new[uid]=old[uid]
write(b/'OUTPUT_REVIEW_PACKETS.json',rows);write(b/'REVIEWS.json',new);write(b/'PRIVATE_REVIEW_MAP.json',mapping)
for r in sorted(rows,key=lambda r:r['packet_index']):
 if r['review_id'] not in new:print(r['packet_index'],r['review_id'],json.dumps(r['output'],ensure_ascii=False),r['error'] or '')
print('Completed',len(rows),'/27; exact-output reused or reviewed',len(new))
