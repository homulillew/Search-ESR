"""Mechanical metrics over explicit offline semantic labels, never model self-score."""
import json,hashlib,statistics
from collections import Counter,defaultdict
from pathlib import Path
TOP=Path(__file__).resolve().parents[1]
def rd(p):return json.loads(p.read_text())
def wr(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def dg(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
def main():
 bank={b['case_id']:b for b in rd(TOP/'bank/RECOVERY_BANK.json')};cs=rd(TOP/'r2/post_writer_cells.json')
 evidence={};writers={}
 for stage in ['r1','r2']:
  evidence.update(rd(TOP/stage/'EVIDENCE_LABELS.json'))
  for r in rd(TOP/stage/'WRITER_LABELS.json'):writers[r['cell'],r['round'],r['wave']]=r
 results=[];actions=[];cost=defaultdict(Counter)
 for stage in ['r1','r2']:
  for path in (TOP/stage).glob('*_events.jsonl'):
   if path.name=='tool_events.jsonl':continue
   for line in path.open():
    e=json.loads(line)
    if e['kind']!='completed':continue
    r=e['result'];key=r['case_id']+':'+r['arm'];k=cost[key];k['actor_calls' if r['kind'].startswith('actor_') else 'updater_calls']+=int(r['attempted']);k['model_seconds']+=r['elapsed_seconds']
    if r['error']:k['model_failures']+=1
    if r.get('usage'):
     k['usage_known']+=1
     for name in ['input','output','hit','miss','reasoning']:k[name]+=r['usage'].get(name) or 0
 for key,c in cs.items():
  b=bank[c['case_id']];first_evidence=None;first_claim=None;first_claim_source=None;paths=set();eviddocs=set();new_supports=0;oldids={d['docid'] for d in b['registry']['documents']}
  dmap={d['doc_ref']:d['docid'] for d in c['registry']['documents']};observed_events={}
  for d in c['decisions']:
   t=d['tool'];row={'cell':key,'case_id':c['case_id'],'qid':c['qid'],'arm':c['arm'],'round':d['round'],'tool':d['actor']['output']['actions'][0]['tool'] if d['actor']['output'] and d['actor']['output']['actions'] else 'stop' if d['actor']['output'] else 'failure', 'source_outcome':'no_useful_source','evidence_outcome':'no_progress','target_rank':None,'target_returned':False,'target_evidence_visible':False,'sufficient':False,'old_sufficient':False,'new_sufficient':False}
   if t:
    cost[key]['tool_calls']+=1;cost[key]['tool_seconds']+=t['elapsed_seconds'];cost[key][row['tool']+'_calls']+=1
    if t['error']:cost[key]['tool_failures']+=1
    for i,w in enumerate(t['observations']):
     lab=evidence[dg([c['case_id'],w['url'],w['text']])[:16]];did=dmap[w['doc_ref']]
     observed_events[d['round'],w['window_ref']]=(did,row['tool'])
     if row['tool']=='search' and did==b['private_recovery_truth']['historical_support_doc']:
      row.update(target_rank=i+1,target_returned=True,target_evidence_visible=lab['sufficient_need_evidence'])
     if lab['evidence_outcome']=='decision_progress' and row['evidence_outcome']=='no_progress':row['evidence_outcome']='decision_progress'
     if lab['sufficient_need_evidence']:
      row.update(sufficient=True,evidence_outcome='direct_need_support');first_evidence=first_evidence or d['round']+1;eviddocs.add(did)
      path='local_reuse' if row['tool'] in ['find','open'] else 'old_source_rediscovery' if did in oldids else 'new_source_recovery'
      paths.add(path);row['old_sufficient' if did in oldids else 'new_sufficient']=True
      if did not in oldids:new_supports+=1
    if row['sufficient']:row['source_outcome']='old_source' if row['old_sufficient'] else 'new_source'
    elif row['evidence_outcome']=='decision_progress':row['source_outcome']='old_source' if any(dmap[w['doc_ref']] in oldids for w in t['observations']) else 'new_source'
   actions.append(row)
  for u in c['updates']:
   lab=writers[key,u['round'],u['wave']]
   if lab['strict_recovery_contribution'] and first_claim is None:
    first_claim=u['round']+1;did,tool=observed_events[u['round'],u['observation']['window_ref']]
    first_claim_source='local_reuse' if tool in ['find','open'] else 'old_source_rediscovery' if did in oldids else 'new_source_recovery'
  # The explicit final semantic review checks that contributions remain grounded/available.
  final=rd(TOP/'analysis/FINAL_CASE_LABELS.json')[key]
  assert bool(first_claim)==final['strict_need_claim_recovery'],key
  results.append({'cell':key,'case_id':c['case_id'],'qid':c['qid'],'arm':c['arm'],'category':b['category'],'cohort':b['cohort'],
   'evidence_visible':first_evidence is not None,'strict_recovered':final['strict_need_claim_recovery'],'lenient_count_recovered':final['lenient_count_recovery'],
   'old_omitted_fact_recovered':final['old_omitted_fact_recovered'],'decisions_to_evidence':first_evidence,'decisions_to_claim':first_claim,
   'first_claim_path':first_claim_source,'evidence_paths':sorted(paths),'new_source_evidence_observations':new_supports,
   'retrieval_failure':first_evidence is None,'admission_failure':first_evidence is not None and not final['strict_need_claim_recovery'],
   'actor_stopped':c['status']=='actor_stop','premature_claim_stop':c['status']=='actor_stop' and not final['strict_need_claim_recovery'],
   'premature_evidence_stop':c['status']=='actor_stop' and first_evidence is None,
   'recorded_runtime_status':c['status'],'final_status':'horizon_exhausted' if c['status']=='active' and len(c['decisions'])==2 else c['status'],
   'cost':dict(cost[key]),'review':final})
 def aggregate(ids,arm):
  rows=[r for r in results if r['case_id'] in ids and r['arm']==arm];keys={r['cell'] for r in rows};aa=[a for a in actions if a['cell'] in keys];sc=[a for a in aa if a['tool']=='search'];kc=sum((Counter(r['cost']) for r in rows),Counter());n=len(rows);ev=sum(r['evidence_visible'] for r in rows);s=sum(r['strict_recovered'] for r in rows)
  def div(a,b):return a/b if b else None
  kc['total_tokens']=kc['input']+kc['output'];cr=div(kc['hit'],kc['input'])
  return {'planned':n,'need_claim_recovery':s,'success_rate':div(s,n),'evidence_visible':ev,'evidence_visibility_rate':div(ev,n),
   'evidence_to_claim_conversion':div(s,ev),'lenient_count_recovery':sum(r['lenient_count_recovered'] for r in rows),'old_omitted_fact_recovered':sum(r['old_omitted_fact_recovered'] for r in rows),
   'first_claim_paths':dict(Counter(r['first_claim_path'] for r in rows if r['strict_recovered'])),
   'old_doc_hits':sum(a['target_returned'] for a in sc),'old_evidence_hits':sum(a['target_evidence_visible'] for a in sc),'global_search_calls':len(sc),
   'OldDocRecall@5':div(sum(a['target_returned'] for a in sc),len(sc)),'OldEvidenceVisibility@5':div(sum(a['target_evidence_visible'] for a in sc),len(sc)),
   'first_step_old_doc_hits':sum(a['target_returned'] for a in sc if a['round']==0),'first_step_old_evidence_hits':sum(a['target_evidence_visible'] for a in sc if a['round']==0),
   'first_step_search_calls':sum(a['round']==0 for a in sc),
   'useful_find':sum(a['sufficient'] for a in aa if a['tool']=='find'),'find_calls':sum(a['tool']=='find' for a in aa),
   'useful_open':sum(a['sufficient'] for a in aa if a['tool']=='open'),'open_calls':sum(a['tool']=='open' for a in aa),
   'retrieval_failures':sum(r['retrieval_failure'] for r in rows),'admission_failures':sum(r['admission_failure'] for r in rows),
   'premature_claim_stops':sum(r['premature_claim_stop'] for r in rows),'premature_evidence_stops':sum(r['premature_evidence_stop'] for r in rows),
   'cost':dict(kc),'cache_rate':cr}
 cohorts={'D3_D4_diagnostic':[b['case_id'] for b in bank.values() if b['category'] in ['D3','D4']],
   'fresh':[b['case_id'] for b in bank.values() if b['cohort']=='fresh'],'known_D3_D4':[b['case_id'] for b in bank.values() if b['category'] in ['D3','D4'] and b['cohort']!='fresh'],
   'safety_D2':['DR06'],'immediate_D1':['DR07'],'all_diagnostic':list(bank)}
 aggregates={k:{arm:aggregate(ids,arm) for arm in ['G','H']} for k,ids in cohorts.items()}
 paired=[]
 for cid in bank:
  g=next(r for r in results if r['cell']==cid+':G');h=next(r for r in results if r['cell']==cid+':H')
  cmp=lambda x,y:'G_cheaper' if x<y else 'H_cheaper' if y<x else 'tie'
  ha=[a for a in actions if a['cell']==cid+':H' and a['tool'] in ['find','open']]
  localfail=bool(ha) and all(not a['sufficient'] for a in ha)
  paired.append({'case_id':cid,'qid':bank[cid]['qid'],'cohort':bank[cid]['cohort'],'strict_outcome':('both_success' if h['strict_recovered'] else 'G_only') if g['strict_recovered'] else 'H_only' if h['strict_recovered'] else 'both_fail',
   'tool_cost_comparison':cmp(g['cost'].get('tool_calls',0),h['cost'].get('tool_calls',0)),
   'token_cost_comparison':cmp(g['cost']['input']+g['cost']['output'],h['cost']['input']+h['cost']['output']),
   'first_local_waste_with_G_success':bool(ha and ha[0]['round']==0 and not ha[0]['sufficient'] and g['decisions_to_evidence']==1),
   'end_to_end_local_lock_regression':localfail and not h['strict_recovered'] and g['strict_recovered'],
   'repeated_local_no_progress':len(ha)>1 and localfail})
 wr(TOP/'analysis/PER_ACTION_METRICS.json',actions);wr(TOP/'analysis/PER_CASE_METRICS.json',results);wr(TOP/'analysis/PAIRED.json',paired)
 wr(TOP/'analysis/METRICS.json',{'cohorts':aggregates,'paired':paired,'primary_gate':'UNASSESSABLE_INSUFFICIENT_FRESH_BANK','independent_p_values':False})
 print(json.dumps(aggregates,indent=2))
if __name__=='__main__':main()
