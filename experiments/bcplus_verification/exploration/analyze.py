"""Offline review of the single bounded probe. No calls."""
import json,statistics,collections
from pathlib import Path
P=Path(__file__).resolve().parent
cs=json.loads((P/'RESULTS.json').read_text());out=[];windows=[];claims=[]
manual={
 'VN01':('i',False,'Correct D1 but Find returns plot/origins instead of production credits. Existing H was already clear for another constraint; this is not new falsification.'),
 'VN07':('iiiii',False,'Same global query and same off-target windows as control. Williams pro-year cannot establish Higgins pro-year; no evidence-based Higgins clear.'),
 'VP06':('s',True,'Find D1 returns explicit normal 8x11 printing paper plus keyboard context. Same dated source and prior correctly admitted keyboard Claim establish the combined condition.'),
 'VP12':('s',True,'Find D1 returns exact 2005 Constant Gardener / Policeman1 row; U1 admits it without strengthening.')}
for c in cs.values():
 cid=c['case_id'];grades,success,reason=manual[cid];d=c['decisions'][-1];w=d['tool']['observations'];assert len(w)==len(grades)
 for ix,(obs,g) in enumerate(zip(w,grades)):
  windows.append({'case_id':cid,'wave':ix,'window_ref':obs['window_ref'],'doc_ref':obs['doc_ref'],'url':obs['url'],'text_sha256':obs['text_sha256'],'grade':g,'useful_target_evidence':g=='s','reason':reason if len(w)==1 else ['Ding match history, no Higgins debut.','Video placeholder.','Later Higgins match, not debut.','Explicit year belongs to Williams.','Maximum table does not establish Higgins debut.'][ix]})
 for u in c['updates']:
  if u['round']!=1:continue
  o=u['proposal']['output'];assert o is not None
  for text in o['claims_to_add']:
   claims.append({'case_id':cid,'wave':u['wave'],'statement':text,'observation_ref':u['observation']['window_ref'],'observation_sha256':u['observation']['text_sha256'],'verdict':'supported','reason':'Explicit paper-medium statement in dated source, linked to prior source-scoped Claims.' if cid=='VP06' else 'Exact filmography row supports role/year/film.' if cid=='VP12' else 'Williams year only; correctly not attributed to Higgins.'})
 out.append({'case_id':cid,'qid':c['qid'],'control_success':False,'exploration_success':success,'control_action':json.loads((P/'CONTROLS.json').read_text())[cid]['decisions'][-1]['tool']['action'],'exploration_action':d['tool']['action'],'reason':reason,'new_target_claim_admitted':success,'new_hypothesis_clear':any(u['proposal']['output']['hypothesis_update']['action']=='clear' for u in c['updates'] if u['round']==1)})
rows=[r for p in P.glob('*_outputs.json') for r in json.loads(p.read_text())];usage={k:sum((r.get('usage') or {}).get(k) or 0 for r in rows) for k in ['input','output','reasoning','hit','miss']}
usage.update(calls=len(rows),actor_calls=sum(r['kind']=='actor_H' for r in rows),writer_calls=sum(r['kind']=='state_updater' for r in rows),elapsed_model_seconds_sum=sum(r['elapsed_seconds'] for r in rows),weighted_cache_hit=usage['hit']/usage['input'],cache_hit_requests=sum((r.get('usage') or {}).get('hit',0)>0 for r in rows),failures=sum(r['error'] is not None for r in rows))
result={'units':out,'control_success':{'n':0,'d':4},'exploration_success':{'n':sum(x['exploration_success'] for x in out),'d':4},'control_inspections':sum(x['control_action']['tool'] in ['find','open'] for x in out),'exploration_inspections':sum(x['exploration_action']['tool'] in ['find','open'] for x in out),'useful_inspections':sum(x['exploration_success'] and x['exploration_action']['tool'] in ['find','open'] for x in out),'cost':usage,'interpretation':'Selected failure states, one sample, no new control sampling. Narrow recoverability/policy signal only; all formal gates remain failed.','window_review':windows,'claim_review':claims}
(P/'REVIEW.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['window_review','claim_review']},ensure_ascii=False,indent=2))
