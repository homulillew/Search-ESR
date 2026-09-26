"""Stable arm-hidden packets; invalid responses retain execution-failure labels."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import *
base=TOP/'research_decision'
states={s['case_id']:s for s in read(TOP/'bank/SNAPSHOTS.json')};truth=read(TOP/'bank/PRIVATE_TRUTH.json')['snapshots']
requests=read(base/'REQUESTS.json');ordered=sorted(requests,key=lambda x:digest([x['case_id'],x['arm']]))
mapping={f'B{i:03}':{'case_id':x['case_id'],'arm':x['arm']} for i,x in enumerate(ordered,1)}
results={}
for line in (base/'events.jsonl').open():
    x=json.loads(line)
    if x['kind']=='completed':r=x['result'];results[r['case_id'],r['arm']]=r
packets=[]
for pid,key in mapping.items():
    cid=key['case_id'];r=results.get((cid,key['arm']))
    if r is None:continue
    s=states[cid];packets.append({'packet_id':pid,'qid':s['qid'],'question':s['question'],
      'verified_claims':claims(s),'working_hypothesis':s['working_hypothesis'],'gold_residual':truth[cid],
      'workspace':public_workspace(s['available_workspace']),'decision':r['output'],'error':r['error']})
write(base/'REVIEW_PACKETS.json',packets);write(base/'PRIVATE_PACKET_MAP.json',mapping)
for p in packets:
    if p['decision'] is not None:
        print(p['packet_id'],p['qid'],p['gold_residual']['goal_status'],json.dumps(p['decision'],ensure_ascii=False))
