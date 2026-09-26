"""Aggregate explicitly reviewed primary results, without any model calls."""
import json,hashlib,statistics,collections,datetime
from pathlib import Path
from window_labels import LABELS
from claim_labels import CLAIMS
from unit_labels import UNITS
P=Path(__file__).resolve().parent.parent
A=P/'analysis'
def read(p):return json.loads(p.read_text())
def write(name,x):(A/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def ratio(n,d):return {'numerator':n,'denominator':d,'rate':n/d if d else None}
def mean(xs):return statistics.mean(xs) if xs else None
cs=read(P/'RESULTS.json');vb={x['case_id']:x for x in read(P/'bank/VERIFICATION_BANK.json')}
windows=[];claims=[];states=[];units=[]
for c in cs.values():
 cid=c['case_id'];assert cid in UNITS;jud=UNITS[cid];action_n=0;first_ev=None;actindex={}
 for d in c['decisions']:
  if not d['tool']:continue
  action_n+=1;r=d['round']+1;actindex[r]=action_n;ws=d['tool']['observations'];ls=LABELS.get((cid,r),[])
  assert len(ws)==len(ls),(cid,r,len(ws),len(ls))
  for widx,(w,label) in enumerate(zip(ws,ls)):
   row={'case_id':cid,'qid':c['qid'],'arm':c['arm'],'round':r,'wave':widx,'action_index':action_n,'tool':d['tool']['action']['tool'],'window_ref':w['window_ref'],'doc_ref':w['doc_ref'],'url':w['url'],'text_sha256':w['text_sha256'],**label}
   row.update(relevant=label['grade'] in 'snp',useful_target_evidence=label['grade'] in 'sn',supports=label['grade']=='s',refutes=label['grade']=='n')
   if row['useful_target_evidence'] and first_ev is None:first_ev=action_n
   windows.append(row)
 for u in c['updates']:
  r=u['round']+1;w=u['wave'];o=u['proposal']['output']
  if o is None:continue
  new=o['claims_to_add'];lab=CLAIMS.get((cid,r,w));assert not new or lab,(cid,r,w)
  if new:
   assert len(lab['grades'])==len(new),(cid,r,w)
   for j,(text,g) in enumerate(zip(new,lab['grades'])):
    claims.append({'case_id':cid,'qid':c['qid'],'round':r,'wave':w,'claim_index':j,'statement':text,'observation_ref':u['observation']['window_ref'],'observation_sha256':u['observation']['text_sha256'],'verdict':'supported' if g=='s' else 'unsupported_strengthening','reason':lab['reason']})
  h=o['hypothesis_update'];reason='No H mutation; prior evidence status is unchanged.'
  if h['action']=='set':reason='Provisional candidate/bridge grounded in current observation and prior Claims; full question coverage is not implied.'
  if h['action']=='clear':reason='Explicit H clear; relation-level justification is evaluated separately in unit review.'
  if cid in ['VP11','VP12','VN12'] and h['action']=='clear':reason='Current source does not establish a zodiac mapping or selected-condition falsification. Two birth sources conflict across the episode; do not score this as reliable negative verification.'
  if cid=='VP02' and h['action']=='clear':reason='Alternative 1993 listing conflicts with November 1992 detail but remains inside early-1990s interval; clearing candidate is not supported by an explicit interval failure.'
  if cid=='VN07' and h['action']=='set':reason='Selby alternative has source support, but Higgins is replaced without observed falsification or explicit clear.'
  states.append({'case_id':cid,'qid':c['qid'],'round':r,'wave':w,'action_index':actindex[r],'operation':h['action'],'pre_hypothesis':u['pre_state']['hypothesis'],'post_hypothesis':u['post_state']['hypothesis'],'reason':reason})
 ev=[x for x in windows if x['case_id']==cid];cr=[x for x in claims if x['case_id']==cid];sr=[x for x in states if x['case_id']==cid]
 terminal_failure=c['status'].endswith('_failure')
 success=jud['success'];operational=success and not terminal_failure
 pos=jud.get('admitted_target_claim') if c['arm']=='V' else jud.get('first_useful_candidate_update')
 first_update=actindex[pos[0]] if pos else None
 u={'case_id':cid,'qid':c['qid'],'arm':c['arm'],'kind':vb[cid]['kind'] if cid in vb else 'Discovery','candidate':c['candidate'],'constraint':c['constraint'],'status':c['status'],'tool_actions':action_n,'actor_decisions':len(c['decisions']),'tools':dict(collections.Counter(d['tool']['action']['tool'] for d in c['decisions'] if d['tool'])),'evidence_found':bool(any(w['useful_target_evidence'] for w in ev)),'first_useful_action':first_ev,'first_successful_update_action':first_update,'semantic_goal_ever_achieved':success,'operational_success':operational,'restricted_update_cost':first_update if operational else c['horizon']+1,'semantic_restricted_update_cost':first_update if success else c['horizon']+1,'new_claims':len(cr),'unsupported_claims':sum(x['verdict']!='supported' for x in cr),'explicit_h_clear':any(x['operation']=='clear' for x in sr),'hypothesis_set':any(x['operation']=='set' for x in sr),'final_hypothesis':c['hypothesis'],**jud}
 if c['arm']=='V':
  u['bank_eligible']=jud.get('bank_eligible',True)
  if pos:
   assert any(x['round']==pos[0] and x['wave']==pos[1] and x['claim_index']==pos[2] and x['verdict']=='supported' for x in cr),(cid,'bad admitted coordinate')
  if vb[cid]['kind']=='V-':
   nr=next((x for x in ev if x['refutes']),None)
   u['target_refuting_evidence_found']=nr is not None
   u['clear_after_target_contradiction']=bool(nr and any(x['operation']=='clear' and (x['round'],x['wave'])>=(nr['round'],nr['wave']) for x in sr))
   u['any_hard_contradiction_found']=bool(nr or jud.get('other_hard_contradiction'))
   old=c['candidate'].lower();u['original_candidate_retained']=old in (c['hypothesis'] or '').lower()
   u['wrong_h_retained_despite_observed_contradiction']=u['any_hard_contradiction_found'] and u['original_candidate_retained'] and u['bank_eligible']
 else:
  u['candidate_proposed']=jud.get('first_useful_candidate_update') is not None or jud.get('unsupported_candidate_proposed',False)
  u['useful_candidate_proposed']=jud['first_useful_candidate_update'] is not None
 units.append(u)
write('WINDOW_REVIEW.json',windows);write('CLAIM_REVIEW.json',claims);write('STATE_REVIEW.json',states);write('UNIT_REVIEW.json',units)
allcalls=[]
for f in sorted(P.glob('round*/*_outputs.json')):
 for r in read(f):allcalls.append({**r,'artifact':str(f.relative_to(P))})
write('CALL_AUDIT.json',[{k:v for k,v in x.items() if k!='output'} for x in allcalls])

def group(us):
 ids={x['case_id'] for x in us};ww=[x for x in windows if x['case_id'] in ids];cc=[x for x in claims if x['case_id'] in ids];rr=[x for x in allcalls if x['case_id'] in ids]
 acts=[(c['case_id'],d) for c in cs.values() if c['case_id'] in ids for d in c['decisions'] if d['tool']]
 searches=[(cid,d) for cid,d in acts if d['tool']['action']['tool']=='search'];useful_searches=sum(any(w['case_id']==cid and w['round']==d['round']+1 and w['useful_target_evidence'] for w in ww) for cid,d in searches)
 uniq=list({(w['case_id'],w['url'],w['text_sha256']):w for w in ww}.values())
 uu=[r['usage'] for r in rr if r.get('usage')];cost={k:sum(u.get(k) or 0 for u in uu) for k in ['input','output','hit','miss','reasoning']};cost['usage_recorded_calls']=len(uu);cost['reasoning_reported_calls']=sum(u.get('reasoning') is not None for u in uu);cost['elapsed_model_seconds_sum']=sum(r['elapsed_seconds'] for r in rr);cost['elapsed_tool_seconds_sum']=sum(d['tool'].get('elapsed_seconds') or 0 for _,d in acts);cost['cache_hit_over_input']=ratio(cost['hit'],cost['input']);cost['cache_hit_occurrence']=ratio(sum((u.get('hit') or 0)>0 for u in uu),len(uu));cost['api_calls']=len(rr);cost['actor_calls']=sum(r['kind']=='actor_H' for r in rr);cost['writer_calls']=sum(r['kind']=='state_updater' for r in rr);cost['api_or_schema_failures']=sum(r['output'] is None for r in rr)
 qids=sorted({u['qid'] for u in us},key=int);qc={q:ratio(sum(u['operational_success'] for u in us if u['qid']==q),sum(u['qid']==q for u in us)) for q in qids}
 return {'n':len(us),'qid_count':len(qids),'operational_success':ratio(sum(u['operational_success'] for u in us),len(us)),'semantic_goal_ever_achieved':ratio(sum(u['semantic_goal_ever_achieved'] for u in us),len(us)),'evidence_found':ratio(sum(u['evidence_found'] for u in us),len(us)),'mean_tool_actions':mean([u['tool_actions'] for u in us]),'tools':dict(collections.Counter(d['tool']['action']['tool'] for _,d in acts)),'mean_first_useful_action_conditional':mean([u['first_useful_action'] for u in us if u['first_useful_action'] is not None]),'mean_successful_update_action_conditional':mean([u['first_successful_update_action'] for u in us if u['operational_success']]),'mean_restricted_update_cost':mean([u['restricted_update_cost'] for u in us]),'mean_semantic_restricted_update_cost':mean([u['semantic_restricted_update_cost'] for u in us]),'useful_search_actions_per_search':ratio(useful_searches,len(searches)),'useful_windows_per_search':ratio(sum(w['useful_target_evidence'] for w in ww if w['tool']=='search'),len(searches)),'irrelevant_or_other_need_windows':ratio(sum(w['grade'] in 'oi' for w in ww),len(ww)),'unique_within_unit_irrelevant_or_other_need_windows':ratio(sum(w['grade'] in 'oi' for w in uniq),len(uniq)),'window_grades':dict(collections.Counter(w['grade'] for w in ww)),'supported_claims':ratio(sum(x['verdict']=='supported' for x in cc),len(cc)),'qid_macro_success':mean([x['rate'] for x in qc.values()]),'by_qid':qc,'cost':cost}
groups={'V+':[u for u in units if u['kind']=='V+'],'V-':[u for u in units if u['kind']=='V-'],'Verification':[u for u in units if u['arm']=='V'],'Discovery':[u for u in units if u['arm']=='D'],'all':units}
m={g:group(us) for g,us in groups.items()};neg=groups['V-'];qn=[u for u in neg if u['bank_eligible']];vp=groups['V+'];ds=groups['Discovery'];vv=groups['Verification']
m['sensitivity']={'eligible_positive':ratio(sum(u['success'] for u in vp if u['bank_eligible']),sum(u['bank_eligible'] for u in vp)),'eligible_negative':ratio(sum(u['success'] for u in qn),len(qn)),'relax_two_positive_scope_judgments':ratio(sum(u['success'] or u.get('sensitivity_success',False) for u in vp),len(vp)),'discovery_correct_benchmark_candidate':ratio(sum(u['correct_benchmark_candidate_proposed'] for u in ds),len(ds)),'discovery_useful_candidate_ever':ratio(sum(u['useful_candidate_proposed'] for u in ds),len(ds))}
m['decomposition']={'P_candidate_discovered':m['sensitivity']['discovery_useful_candidate_ever'],'P_evidence_found_given_candidate_constraint':ratio(sum(u['evidence_found'] for u in vv),len(vv)),'P_valid_target_claim_admitted_given_useful_evidence':ratio(sum(bool(u['admitted_target_claim']) for u in vv if u['evidence_found']),sum(u['evidence_found'] for u in vv)),'P_H_cleared_given_target_contradiction':ratio(sum(u['clear_after_target_contradiction'] for u in qn if u['target_refuting_evidence_found']),sum(u['target_refuting_evidence_found'] for u in qn)),'P_H_cleared_given_any_hard_contradiction':ratio(sum(u['explicit_h_clear'] for u in qn if u['any_hard_contradiction_found']),sum(u['any_hard_contradiction_found'] for u in qn)),'P_correct_verification_frontier_given_candidate':{'rate':None,'reason':'S4 gated off; S1 oracle supplied constraint cannot estimate this.'},'P_correct_resolved_given_full_coverage':{'rate':None,'reason':'No strictly fully covered state in audited historical resolved controls; S5 gated off.'}}
m['negative_details']={k:sum(u.get(k,False) for u in qn) for k in ['target_refuting_evidence_found','clear_after_target_contradiction','any_hard_contradiction_found','explicit_h_clear','original_candidate_retained','wrong_h_retained_despite_observed_contradiction','replacement_without_refutation']}
m['negative_details']['target_refuting_claim_admitted']=sum(u['admitted_target_claim'] is not None for u in qn)
gates={'V+_15_of_18':sum(u['operational_success'] for u in vp)>=15,'V-_9_of_11':sum(u['operational_success'] for u in neg)>=9,'eligible_wrong_candidate_8_of_10':sum(u['operational_success'] for u in qn)>=8,'discovery_useful_at_most_7_of_10':sum(u['useful_candidate_proposed'] for u in ds)<=7,'verification_actual_actions_lower':m['Verification']['mean_tool_actions']<m['Discovery']['mean_tool_actions'],'restricted_update_cost_at_least_0_5_lower':m['Verification']['mean_restricted_update_cost']<=m['Discovery']['mean_restricted_update_cost']-0.5}
write('METRICS.json',m)
write('GATES.json',{'evaluated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'gates':gates,'all_numeric_gates_pass':all(gates.values()),'negative_bank_shortfall':'Frozen n=11 versus target12; eligible wrong-candidate n=10 after source conflict. This is an additional limitation, never silently waived.','S4':'permitted' if all(gates.values()) else 'not_run_gated_off','S5':'not_run_requires_S4','exploration_can_override':False})
print(json.dumps({'rates':{k:m[k]['operational_success'] for k in ['V+','V-','Discovery']},'candidate':m['sensitivity'],'gates':gates,'calls':m['all']['cost']},indent=2))
