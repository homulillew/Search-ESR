"""Read sealed E1 scores; archive a safety stop and descriptive diagnostics."""
from .common import *
from .run import load_rows
from .inputs import support_ids
from .score import TAXONOMY,aggregate

def main():
 m=read(P/'e1_support_alignment/METRICS.json');assert not m['gate']['E2_safety_entry_pass']
 rows=load_rows();by={(r['cell_id'],r['arm'],r['replicate']):r for r in rows};refs={g['cell_id']:g for g in read(P/'e0_reference/CLAIM_ROLE_REFERENCE.json')}
 decisions={'status':'STOPPED_AFTER_E1_SAFETY_FAILURE','E1_primary_pass':False,'E2_safety_entry_pass':False,'failed_absolute_checks':[k for k,v in m['gate']['absolute_checks'].items() if not v],'comparative_pass':m['gate']['comparative_pass'],'E2_model_calls':0,'E2_actual_requests':0,'authorization_requested':False,'reason':'TASK24 Case D / TASK25 / frozen GATES: precision, relation/source binding and false-full hazard fail. No residual, Search, Probe, Writer or Bootstrap run.'}
 write(P/'e2_downstream_residual/DECISION.json',decisions)
 write(P/'e2_downstream_residual/METRICS.json',{'status':'NOT_RUN_SAFETY_STOP','planned_conditional_outcome_slots':192,'actual_requests':0,'attempted':0,'strict_residual_validity':None,'false_subtraction':None,'supported_content_leakage':None,'full_support_accuracy':None,'false_full_support':None,'state_discrimination':None,'note':'Not measured is not zero error. E1 hazards are not observed residualizer false closures.'})
 write(P/'e2_downstream_residual/REPORT.md','# E2 — Not run\n\nE1 failed its frozen safety entry gate. No E2 requests were prepared or sent, and no E2 authorization was requested. False subtraction, actual false FULLY_SUPPORTED, D0/D1/D2/D3 residual validity and residual state discrimination are **not measured**, not zero. Initial STATUS.json remains the immutable preparation snapshot; DECISION.json is the final stage decision.\n')
 trans=[]
 for before,after in [('A05','A07'),('A16','A17')]:
  for arm in ('S0','S1'):
   for rep in (1,2):
    a,b=by[before,arm,rep],by[after,arm,rep];aa=sorted(support_ids(a['output'],arm));bb=sorted(support_ids(b['output'],arm))
    trans.append({'before_cell':before,'after_cell':after,'arm':arm,'replicate':rep,'before_support_ids':aa,'after_support_ids':bb,'both_support_sets_correct':aa==refs[before]['gold_support_claim_ids'] and bb==refs[after]['gold_support_claim_ids']})
 write(P/'analysis/E1_TRANSITIONS.json',{'status':'E1_ASSIGNMENT_DIAGNOSTIC_ONLY','rows':trans,'E2_residual_state_discrimination':None,'note':'Correct changed support assignments are not evidence that downstream residuals discriminate state.'})
 repeat={}
 for arm in ('S0','S1'):
  same_ids=same_content=0
  for cell in refs:
   a,b=by[cell,arm,1],by[cell,arm,2]
   same_ids+=support_ids(a['output'],arm)==support_ids(b['output'],arm)
   same_content+=a['output']==b['output']
  repeat[arm]={'support_set_agreement':metric(same_ids,24),'complete_parsed_output_agreement':metric(same_content,24)}
 write(P/'analysis/REPLICATE_DIAGNOSTIC.json',{'status':'DESCRIPTIVE_NOT_A_GATE','replicates':repeat,'note':'Temperature0 is not a determinism guarantee; no best-of or output repair.'})
 contributions=[]
 for cell,g in refs.items():
  if g['ambiguity_flag']:
   augmented=[]
   for r in rows:
    if r['cell_id']==cell:
     judgment=next(e['judgment'] for e in m['error_ledger'] if e['id']==r['id']);augmented.append({**r,'judgment':judgment})
   contributions.append({'cell_id':cell,'reason':g['ambiguity_reason'],'metrics':aggregate(augmented,refs)})
 write(P/'analysis/AMBIGUITY_CONTRIBUTIONS.json',{'primary_labels_unchanged':True,'cells':contributions,'primary_gate_replaced':False})
 tax={a:{t:m['primary'][a]['semantic_output_error_tags'].get(t,0) for t in TAXONOMY} for a in ('S0','S1')}
 write(P/'analysis/ERROR_TAXONOMY.json',{'unit':'manual per-output tag counts; categories overlap','counts':tax,'automatic_claim_errors':{a:m['primary'][a]['automatic_claim_error_counts'] for a in ('S0','S1')},'false_full_support_note':'Taxonomy tag denotes E1 assignment-coverage hazard; no downstream closure was run.'})
 print(json.dumps(decisions,indent=2))
if __name__=='__main__':main()
