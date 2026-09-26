import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1]
def rd(p):return json.loads(p.read_text())
def add(rows,version='round_0'):
 path=P/'analysis'/f'{version}_manual.jsonl';existing=[json.loads(l) for l in path.read_text().splitlines()] if path.exists() else [];seen={(x['case_id'],x['arm']) for x in existing}
 with path.open('a') as f:
  for cid,arm,flags,mechanism,reason in rows:
   assert (cid,arm) not in seen,(cid,arm)
   folder=P/('round_0_p3_format_repair' if arm=='P3' else version)
   r=rd(folder/f'{cid}_{arm}.json');assert r['output']
   row={'case_id':cid,'arm':arm,'output':r['output'],'output_sha256':hashlib.sha256(json.dumps(r['output'],sort_keys=True,ensure_ascii=False).encode()).hexdigest(),'V':not any(t in flags for t in ['S','I','H']),'S':'S' in flags,'P':'P' in flags,'W':'W' in flags,'I':'I' in flags,'H':'H' in flags,'A':True,'STRICT_VALID':not flags,'mechanisms':mechanism.split(',') if mechanism else [],'reason':reason,'reviewer':'single Codex reviewer, unblinded; QCH and frozen rubric reviewed'}
   f.write(json.dumps(row,ensure_ascii=False)+'\n');seen.add((cid,arm))
def remaining(start=1,end=55):
 done=set()
 p=P/'analysis/round_0_manual.jsonl'
 if p.exists():done={(x['case_id'],x['arm']) for x in [json.loads(l) for l in p.read_text().splitlines()]}
 for n in range(start,end+1):
  cid=f'N{n:03}'
  for arm in ['P0','P1','P2','P3','P4']:
   path=P/('round_0_p3_format_repair' if arm=='P3' else 'round_0')/f'{cid}_{arm}.json'
   if path.exists() and (cid,arm) not in done:
    r=rd(path)
    if r['output']:print(cid,arm,r['output']['need'])
if __name__=='__main__':
 import sys
 remaining(*[int(s) for s in sys.argv[1:]])
