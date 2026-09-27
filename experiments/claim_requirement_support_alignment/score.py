"""Deterministic E1 scoring after all blinded semantic judgments are sealed."""
from collections import Counter
from .common import *
from .inputs import support_ids,bank

TAXONOMY=['false_support_entity_overlap','false_support_generic_background','false_support_wrong_relation','false_support_wrong_argument','false_support_wrong_temporal_attachment','false_support_wrong_object','false_support_cross_candidate_merge','missed_true_support','support_scope_overreach','binding_context_promoted_to_support','background_promoted_to_support','false_full_support']

def aggregate(rows,refs):
 """Every row remains in denominators; only valid contracts emit assignments."""
 out={};inputs=bank()
 for arm in ('S0','S1'):
  rs=[r for r in rows if r['arm']==arm];tp=pred=gold_n=neg=fp=exact=roles_ok=roles_n=bind_ok=bind_n=bg_ok=bg_n=scope_ok=scope_n=0
  confusion={a:{b:0 for b in ROLES+['INVALID_OR_MISSING']} for a in ROLES};fullhaz=corrupt=mix=0;tags=Counter();claim_errors=Counter();zfp=zneg=fragment_ok=fragment_n=0
  for r in rs:
   g=refs[r['cell_id']];gs=set(g['gold_support_claim_ids']);ids=set(g['claims']);valid=r['valid_output'];ps=support_ids(r['output'],arm) if valid else set();j=r['judgment']
   true=ps&gs;tp+=len(true);pred+=len(ps);gold_n+=len(gs);neg+=len(ids-gs);fp+=len(ps-gs);exact+=int(valid and ps==gs)
   if g['stratum']=='Z':zfp+=len(ps);zneg+=len(ids)
   for c in gs-ps:claim_errors['missed_true_support']+=1
   for c in ps-gs:
    role=g['claims'][c]['epistemic_role']
    if role=='BINDING_CONTEXT':claim_errors['binding_context_promoted_to_support']+=1
    if role=='BACKGROUND':claim_errors['background_promoted_to_support']+=1
   tags.update(j['error_tags'])
   corrupt+=int(valid and j['relation_argument_corruption']);mix+=int(valid and j['candidate_branch_mixing'])
   if arm=='S1':
    raw_claims=r['output'].get('claims',[]) if isinstance(r['output'],dict) else []
    for c in raw_claims if isinstance(raw_claims,list) else []:
     if isinstance(c,dict) and c.get('role')=='SUBSTANTIVE_SUPPORT':
      fs=c.get('supported_requirement_fragments',[])
      for f in fs if isinstance(fs,list) else [fs]:
       fragment_n+=1;fragment_ok+=int(isinstance(f,str) and bool(f.strip()) and f in inputs[r['cell_id']]['parent_requirement']['text'])
    got={c['claim_id']:c['role'] for c in r['output']['claims']} if valid else {}
    for c,a in g['claims'].items():
     gr=a['epistemic_role'];pr=got.get(c,'INVALID_OR_MISSING');confusion[gr][pr]+=1;roles_n+=1;roles_ok+=int(pr==gr)
     if gr=='BINDING_CONTEXT':bind_n+=1;bind_ok+=int(pr==gr)
     if gr=='BACKGROUND':bg_n+=1;bg_ok+=int(pr==gr)
    scope_n+=len(true);scope_ok+=len(true&set(j['scope_correct_claim_ids']))
    fullhaz+=int(valid and not g['parent_fully_supported'] and j['false_full_support_hazard'])
  out[arm]={'planned_outputs':len(rs),'valid_outputs':sum(r['valid_output'] for r in rs),'invalid_or_missing_outputs':sum(not r['valid_output'] for r in rs),'support_precision':metric(tp,pred),'support_recall':metric(tp,gold_n),'hard_negative_false_promotion':metric(fp,neg),'Z_only_false_promotion':metric(zfp,zneg),'exact_state_support_set':metric(exact,len(rs)),'schema_validity':metric(sum(r['valid_output'] for r in rs),len(rs)),'relation_argument_corruption':metric(corrupt,len(rs)),'candidate_branch_mixing':metric(mix,len(rs)),'false_full_support_hazard_count':fullhaz if arm=='S1' else None,'false_full_support_hazard_identifiability':'S1 semantic coverage of unresolved Parent; S0 ID-only assignment does not expose a claimed support scope/closure','error_tag_counts':dict(sorted(tags.items()))}
  out[arm]['automatic_claim_error_counts']=dict(sorted(claim_errors.items()))
  out[arm]['semantic_output_error_tags']=out[arm].pop('error_tag_counts')
  if arm=='S1':out[arm].update(support_scope_correctness=metric(scope_ok,scope_n),exact_fragment_validity=metric(fragment_ok,fragment_n),role_accuracy=metric(roles_ok,roles_n),binding_context_recall=metric(bind_ok,bind_n),background_accuracy=metric(bg_ok,bg_n),role_confusion=confusion)
 return out

def gate(metrics):
 gates=read(P/'GATES.json');s=metrics['S1'];checks={}
 for name,threshold in gates['E1_S1'].items():
  key,op=name.rsplit('_',1);raw=s.get(key);v=raw.get('value') if isinstance(raw,dict) else raw
  checks[name]=v is not None and (v>=threshold if op=='min' else v<=threshold)
 v0=metrics['S0']['hard_negative_false_promotion']['value'];v1=s['hard_negative_false_promotion']['value'];near=gates['comparative']['near_zero_both_max']
 comparative=v0 is not None and v1 is not None and (v1<=v0 if max(v0,v1)<=near else v1<v0)
 return {'absolute_checks':checks,'S1_absolute_pass':all(checks.values()),'comparative_pass':comparative,'S1_primary_pass':all(checks.values()) and comparative,'E2_safety_entry_pass':all(v for k,v in checks.items() if k!='support_recall_min'),'E2_authorized':False}

def validate_judgment(j,arm,valid,output):
 assert set(j)=={'scope_correct_claim_ids','relation_argument_corruption','candidate_branch_mixing','false_full_support_hazard','error_tags','reason','ambiguous_reference'}
 assert all(type(j[k]) is bool for k in ('relation_argument_corruption','candidate_branch_mixing','ambiguous_reference'))
 assert isinstance(j['scope_correct_claim_ids'],list) and len(j['scope_correct_claim_ids'])==len(set(j['scope_correct_claim_ids']))
 assert isinstance(j['reason'],str) and j['reason'].strip()
 assert isinstance(j['error_tags'],list) and all(t in TAXONOMY for t in j['error_tags']) and len(j['error_tags'])==len(set(j['error_tags']))
 if arm=='S1':
  assert type(j['false_full_support_hazard']) is bool
  assert set(j['scope_correct_claim_ids']) <= (support_ids(output,arm) if valid else set())
 else:assert j['false_full_support_hazard'] is None and not j['scope_correct_claim_ids']

def results():
 from .run import jobs,load_rows,OUT
 js=jobs();key=read(OUT/'review/KEY.json');judgments=read(OUT/'review/JUDGMENTS.json');seal=read(OUT/'review/REVIEW_SEAL.json')
 assert set(key)==set(judgments) and set(key.values())=={j['id'] for j in js}
 assert {rel(OUT/'review'/f) for f in ('PACKETS.json','KEY.json','JUDGMENTS.json')}<=set(seal['files'])
 for name,h in seal['files'].items():assert sha(ROOT/name)==h;committed(ROOT/name)
 committed(OUT/'review/REVIEW_SEAL.json')
 inv={v:k for k,v in key.items()};rows=load_rows();refs={g['cell_id']:g for g in read(P/'e0_reference/CLAIM_ROLE_REFERENCE.json')}
 for r in rows:
  j=judgments[inv[r['id']]];validate_judgment(j,r['arm'],r['valid_output'],r['output']);r['judgment']=j
 metrics=aggregate(rows,refs);by_qid={q:aggregate([r for r in rows if r['qid']==q],refs) for q in sorted({r['qid'] for r in rows})}
 by_stratum={st:aggregate([r for r in rows if refs[r['cell_id']]['stratum']==st],refs) for st in ('Z','P','F')}
 return {'primary':metrics,'gate':gate(metrics),'by_qid':by_qid,'by_stratum':by_stratum,'by_replicate':{str(k):aggregate([r for r in rows if r['replicate']==k],refs) for k in (1,2)},'nonambiguous_sensitivity':aggregate([r for r in rows if not refs[r['cell_id']]['ambiguity_flag']],refs),'error_ledger':[{'id':r['id'],'cell_id':r['cell_id'],'failure':r['failure'],'judgment':r['judgment']} for r in rows]}

def main():
 a=results();b=results();assert a==b
 write(P/'e1_support_alignment/METRICS.json',a)
 write(P/'analysis/ERROR_LEDGER.json',a['error_ledger'])
 write(P/'analysis/SENSITIVITY.json',{'primary_unchanged':True,'nonambiguous':a['nonambiguous_sensitivity']})
 print(json.dumps(a['gate'],indent=2))
if __name__=='__main__':main()
