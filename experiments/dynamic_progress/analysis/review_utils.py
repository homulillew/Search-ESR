import json
from pathlib import Path
T=Path(__file__).resolve().parents[1]
def rd(p):return json.loads(p.read_text())
def wr(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
P={p['review_id']:p for p in rd(T/'analysis/review_packets.json')}
f=T/'analysis/semantic_review.json';REV=rd(f) if f.exists() else {}
def review(uid,reason,*,bad=None,status=None,refs=None,witness=None,promotion=False,omitted=None,segments=None,missing_conflict=False,context_errors=None):
 p=P[uid];o=p['output'];assert o is not None,uid
 bad=bad or {};status=status or {};refs=refs or {};units=[]
 if 'blocking_gaps' in o: raw=o['blocking_gaps']
 elif 'requirements' in o:raw=o['requirements']
 else:raw=[{'gap':s} for s in (segments if segments is not None else ([o['residual']] if o['residual'] else []))]
 for i,g in enumerate(raw,1):
  err=bad.get(i,[]);err=[err] if isinstance(err,str) else err
  units.append({'index':i,'text':g.get('gap',g.get('requirement','')),'is_blocker':g.get('status')!='supported','content_valid':not err,'errors':err,'status_valid':i not in status if 'status' in g else None,'status_reason':status.get(i),'refs_valid':i not in refs if 'claim_refs' in g else None,'refs_reason':refs.get(i)})
 REV[uid]={'review_id':uid,'units':units,'closure_witness_valid':witness,'false_evidence_promotion':promotion,'omitted_material_blocker_families':omitted,'missing_material_conflict':missing_conflict,'context_errors':context_errors or [],'reason':reason,'reviewer':'single Codex semantic review; frozen Q+Claims rubric; condition IDs masked, schemas visible'}
def save():
 # Infrastructure failures are mechanical, no invented semantic judgment.
 for uid,p in P.items():
  if p['output'] is None and uid not in REV:REV[uid]={'review_id':uid,'units':[],'closure_witness_valid':None,'false_evidence_promotion':False,'reason':'No model output; transport/schema failure retained, no semantic credit.','mechanical_failure':True}
 wr(f,REV)
