"""Archive-only review material; run after acquisition QCH commit, no model calls."""
import json,hashlib,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from transport import P,ROOT,rd,save,dg,sha
states=rd(P/'acquisition/ALL_QCH.json');episodes=rd(P/'acquisition/RESULTS.json');sources={};claims=[];transitions=[]
for ep in episodes:
 for u in ep['updates']:
  w=u['observation'];h=hashlib.sha256(w['text'].encode()).hexdigest();assert h==w['text_sha256'];sources.setdefault(h,{k:w[k] for k in ['text','title','url','window_ref','doc_ref']})
  if u['writer']['output']:
   for i,c in enumerate(u['writer']['output']['claims_to_add']):claims.append({'qid':ep['qid'],'case_id':ep['case_id'],'statement':c,'statement_hash':dg(c),'observation_hash':h,'writer_id':f"writer_{u['round']}_{u['wave']}",'claim_index':i,'writer_response':str((P/'acquisition/trajectories'/ep['case_id']/'calls'/f"writer_{u['round']}_{u['wave']}.response.json").relative_to(ROOT)),'review':None})
   transitions.append({'qid':ep['qid'],'case_id':ep['case_id'],'split':ep['split'],'round':u['round'],'wave':u['wave'],'pre_state':u['pre_state'],'post_state':u['post_state'],'actual_claims_to_add':u['writer']['output']['claims_to_add'],'observation_hash':h,'writer_output':u['writer']['output']})
rows=[]
for x in states:
 s=x['state'];b={'question':s['question'],'claims':[c['statement'] for c in s['claims']],'hypothesis':s['hypothesis'] or ''}
 rows.append({'state_id':x['state_id'],'qid':x['qid'],'split':x['split'],'belief':b,'belief_sha256':dg(b),'claim_records':s['claims'],'transition':x['transition'],'natural_archived_state':True,'pending_support_review':True})
save(P/'bank/STATE_INVENTORY.json',rows);save(P/'bank/SOURCES.json',sources);save(P/'bank/CLAIM_REVIEW_PACKET.json',claims);save(P/'bank/TRANSITIONS.json',transitions)
print('states',len(rows),'claim admissions',len(claims),'unique observations',len(sources))
for ep in episodes:
 group=[r for r in rows if r['qid']==ep['qid']];lines=['QID '+ep['qid']+' '+ep['split'],ep['question']]
 for r in group:
  lines+=['\n'+r['state_id']+' H: '+r['belief']['hypothesis']]+[f'C{i+1}: {c}' for i,c in enumerate(r['belief']['claims'])]
 (P/'bank'/f"review_{ep['case_id']}.txt").write_text('\n'.join(lines)+'\n')
