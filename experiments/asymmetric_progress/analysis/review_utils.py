import json
from pathlib import Path
T=Path(__file__).resolve().parents[1]
def rd(p):return json.loads(p.read_text())
def wr(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
P={p['review_id']:p for p in rd(T/'analysis/review_packets.json')}
path=T/'analysis/semantic_review.json';REV=rd(path) if path.exists() else {}

def review(uid,reason,*,bad=None,status=None,refs=None,witness=None,promotion=False,certificate_errors=None):
 p=P[uid];o=p['output'];assert o is not None,uid
 bad=bad or {};status=status or {};refs=refs or {}
 raw=o.get('blocking_gaps',([o['blocking_gap']] if o.get('blocking_gap') else []))
 units=[]
 for i,g in enumerate(raw,1):
  err=bad.get(i,[]);err=[err] if isinstance(err,str) else err
  units.append({'index':i,'text':g['gap'],'content_valid':not err,'errors':err,'status_valid':i not in status if 'status' in g else None,'status_reason':status.get(i),'refs_valid':i not in refs,'refs_reason':refs.get(i)})
 confirmed=o.get('resolved',o.get('confirmed'))
 if confirmed:assert witness is not None,'Explicit certificate review needed'
 REV[uid]={'review_id':uid,'units':units,'closure_witness_valid':witness if confirmed else None,'certificate_errors':certificate_errors or [],'false_evidence_promotion':promotion,'reason':reason,'reviewer':'Single Codex Q+Claims-only semantic review; opaque IDs, visible schema, not fully blind.'}

def save():
 for uid,p in P.items():
  if p['output'] is None:REV[uid]={'review_id':uid,'units':[],'closure_witness_valid':None,'false_evidence_promotion':False,'mechanical_failure':True,'reason':'No valid parsed output; no semantic credit; raw failure retained.'}
 wr(path,REV)
