from progress import *
from path_metrics import norm,evaluate
from update_queue import queue

def evaluate_loop():
 b=TOP/'three_round_loop_v2';cells=read(b/'results.json');judgments=read(b/'LOOP_ADJUDICATION.json');labels=read(TOP/'analysis_v2/UPDATER_LABELS.json');progress_rows=read(b/'progress_reviews.json');pm={r['case_id']:r for r in progress_rows};records=[];claimrows=[]
 # Empty proposals have no admitted claim; do not pretend they were positive support judgments.
 stream=queue();smap={}
 for r in stream:smap[r['review_id']]=r
 for key,c in cells.items():
  j=judgments[key];resolved_r=j['resolved_after_round'];source_r=j.get('source_only_resolved_after_round');strict_r=j.get('strict_resolved_after_round');aa=[];repeats=0;seen=set();late=0;np=0;acts=0;drift=0
  for di,d in enumerate(c['decisions']):
   o=d['actor']['output'];isact=bool(o and o['decision']=='act');acts+=isact
   late+=bool(isact and resolved_r is not None and di>resolved_r)
   pp=pm[key+':'+str(di)];np+=bool(isact and not pp['any_progress']);drift+=di in j.get('goal_drift_rounds',[])
   for a in d['actions']:
    n=norm(a['action']);repeats+=n in seen;seen.add(n);aa.append(a)
  stop=c['status'] in ['actor_stop','goal_stop'];stop_round=c['decisions'][-1]['round'] if c['status']=='actor_stop' else c['goal_reviews'][-1]['round'] if c['status']=='goal_stop' else None
  correct=bool(stop and resolved_r is not None and stop_round>resolved_r);premature=bool(stop and not correct)
  claims=c['state']['verified_claims'];semantic={'Question':c['state']['question'],'Verified Claims':[x['statement'] for x in claims],'Working Hypothesis':c['state']['working_hypothesis']}
  records.append({'cell':key,'qid':c['qid'],'arm':c['arm'],'status':c['status'],'decisions':len(c['decisions']),'acting_decisions':acts,'resolved':resolved_r is not None,'strict_resolved':strict_r is not None,'source_only_resolved':source_r is not None,'correct_stop':correct,'premature_stop':premature,'late_research_decisions':late,'resolved_at_horizon_without_stop':bool(resolved_r is not None and c['status']=='horizon_exhausted'),'goal_drift_decisions':drift,'no_progress_acting_decisions':np,'progress_decisions':sum(pm[key+':'+str(i)]['any_progress'] for i in range(len(c['decisions']))),'tool_calls':len(aa),'tools':dict(collections.Counter(a['action']['tool'] for a in aa)),'tool_calls_to_resolution':sum(len(d['actions']) for d in c['decisions'] if d['round']<=resolved_r) if resolved_r is not None else None,'repeated_normalized_actions':repeats,'final_claims':len(claims),'final_semantic_state_characters':len(json.dumps(semantic,ensure_ascii=False)),'final_workspace_windows':len(c['state']['available_workspace']['observed_windows']),'notes':j['reason']})
  for u in c['updates']:
   r=u['proposal'];o=r['output']
   if not o:continue
   uid=digest([r['request_sha256'],o])[:16]
   if o['claims_to_add']:assert uid in labels,('unreviewed',uid)
   for ci,claim in enumerate(o['claims_to_add']):claimrows.append({'cell':key,'arm':c['arm'],'round':u['round'],'wave':u['wave'],'review_id':uid,'claim_index':ci,'claim':claim,**labels[uid]['claims'][ci]})
 metrics={};hypothesis_events=[];reviewer_rows=[]
 for key,c in cells.items():
  rr=judgments[key]['resolved_after_round']
  for gr in c['goal_reviews']:
   o=gr['result']['output'];truth=rr is not None and gr['round']>rr
   reviewer_rows.append({'cell':key,'round':gr['round'],'true_resolved':truth,'output':o,'closure_agreement':bool(o is not None and o['resolved']==truth)})
  for u in c['updates']:
   r=u['proposal'];o=r['output']
   if not o:continue
   uid=digest([r['request_sha256'],o])[:16];lab=labels.get(uid,{})
   flags={k:v for k,v in lab.items() if isinstance(v,bool)}
   if flags:hypothesis_events.append({'cell':key,'arm':c['arm'],'round':u['round'],'wave':u['wave'],'review_id':uid,**flags,'reason':lab.get('hypothesis_reason','')})
 for arm in ['L0','L1','L2']:
  rr=[r for r in records if r['arm']==arm];cr=[r for r in claimrows if r['arm']==arm]
  metrics[arm]={'planned_qids':10,**{k:sum(r[k] for r in rr) for k in ['resolved','strict_resolved','source_only_resolved','correct_stop','premature_stop','late_research_decisions','resolved_at_horizon_without_stop','goal_drift_decisions','no_progress_acting_decisions','progress_decisions','acting_decisions','decisions','tool_calls','repeated_normalized_actions']},'failed_cells':sum('failure' in r['status'] for r in rr),'horizon_exhausted':sum(r['status']=='horizon_exhausted' for r in rr),'final_claims_total':sum(r['final_claims'] for r in rr),'final_semantic_state_characters_total':sum(r['final_semantic_state_characters'] for r in rr),'admitted_claims':len(cr),'supported_claims':sum(r['source_supported'] for r in cr),'unsupported_joins':sum(r['unsupported_join'] for r in cr),'candidate_overpromotion':sum(r['candidate_overpromotion'] for r in cr),'incidental_admissions':sum(r['incidental'] for r in cr),'material_qualifier_omissions':sum(r.get('material_qualifier_omission',False) for r in cr)}
  metrics[arm]['source_supported_precision']=metrics[arm]['supported_claims']/len(cr) if cr else None
 write(b/'claim_reviews.json',claimrows);write(b/'loop_reviews.json',records);write(b/'loop_metrics.json',metrics)
 write(b/'hypothesis_control_reviews.json',hypothesis_events);write(b/'goal_reviewer_reviews.json',reviewer_rows)
 write(b/'path_metrics.json',evaluate([{'arm':c['arm'],'actions':d['actions']} for c in cells.values() for d in c['decisions']]))
 print(json.dumps(metrics,indent=2));return records,metrics
if __name__=='__main__':evaluate_loop()
