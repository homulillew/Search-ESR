from score import *
main()
original=[enrich(x) for x in rows_from_log(T/'p1_progress/progress_events.jsonl')]
assert len(original)==216
corrected=rows_from_log(T/'transport_correction/corrected_events.jsonl');assert len(corrected)==120
B=[r for r in original if r['arm']=='B' and r['set']=='fresh_primary'];C=[r for r in original if r['arm']=='B' and r['set']=='challenge'];bm=metric(B);cm=metric(C)
direct=rd(T/'p1_progress/historical_direct_completion.json');gain=cm['correct_completion']/48-sum(r['correct_completion'] for r in direct)/48
bycase={cid:{'B':sum(r['correct_completion'] for r in C if r['case_id']==cid),'Direct':sum(r['correct_completion'] for r in direct if r['case_id']==cid),'qid':next(r['qid'] for r in C if r['case_id']==cid)} for cid in {r['case_id'] for r in C}}
reg=[cid for cid,v in bycase.items() if v['B']<v['Direct']]
checks={'false_closure':bm['false_closure']<=4,'valid_blocker_presence':bm['valid_blocker_presence']>=36,'blocker_precision':bm['blocker_precision']>=.9,'correct_closure':bm['correct_closure']==6,'challenge_completion_improvement':gain>=.1,'challenge_no_systematic_regression':not(len(reg)>=3 and len({bycase[c]['qid'] for c in reg})>=2)}
critical={r['case_id'] for r in B if any('unsupported_premise' in u['errors'] for u in r['units']) or (r['review'] or {}).get('missing_material_conflict')}
checks['no_systematic_critical_errors']=not(len(critical)>=3 and len({r['qid'] for r in B if r['case_id'] in critical})>=2)
wr(T/'analysis/GATE.json',{'primary_B':bm,'checks':checks,'passed':all(checks.values()),'P2_P3_P4':'not run','challenge_B':cm,'historical_direct':{'correct_completion':sum(r['correct_completion'] for r in direct),'false_closure':sum(r['false_closure'] for r in direct),'total':48},'challenge_gain_pp':100*gain,'challenge_case_comparison':bycase,'regression_case_ids':reg,'critical_case_ids':sorted(critical),'transport_deviation':'OriginalR/FULLrejected; correcteddiagnosticneveroverridesprimarygate.'})
# Post-hoc descriptive relaxation explicitly cannot change frozen precision gate.
wr(T/'analysis/breadth_sensitivity.json',{'pre_registered':False,'purpose':'Separate over-breadth from material factual/support error; not a revised gate.','primary_B':{'all_units':bm['blocker_total'],'valid_under_frozen_rubric':bm['blocker_valid'],'valid_if_only_over_broad_is_excused':sum(not(set(u['errors'])-{'over_broad'}) for r in B for u in r['blockers'])},'failure_gate_unchanged':True})
ex=[enrich(x) for x in rows_from_log(T/'exploration/exploration_events.jsonl')]
if len(ex)==24 and all(r['review'] for r in ex):
 base=[enrich(r) for r in rd(T/'exploration/baseline.json')];a=metric(base);b=metric(ex)
 criteria={'precision_gain_ge10pp':b['blocker_precision']-a['blocker_precision']>=.1,'presence_not_lower':b['valid_blocker_presence']>=a['valid_blocker_presence'],'false_closure_not_higher':b['false_closure']<=a['false_closure'],'correct_closure_not_lower':b['correct_closure']>=a['correct_closure'],'unsupported_not_higher':b['output_errors'].get('unsupported_premise',0)<=a['output_errors'].get('unsupported_premise',0)}
 wr(T/'exploration/metrics.json',{'baseline':a,'one_relation':b,'criteria':criteria,'local_diagnostic_positive':all(criteria.values()),'primary_gate_override':False,'heldout':False,'uncovered_failures':'OriginalfalseclosureP17/P19notinthisbreadth-selectedsample.'})
 wr(T/'exploration/reviewed_outputs.json',ex)
allrows=rows_from_log(T/'p1_progress/progress_events.jsonl')+corrected+rows_from_log(T/'exploration/exploration_events.jsonl')
u=[r['usage'] for r in allrows if r['usage']];sums={k:sum(x.get(k) or 0 for x in u) for k in ['input','output','hit','miss','reasoning']}
wr(T/'analysis/usage.json',{'HTTP_attempts':len(allrows),'with_usage':len(u),'usage_not_returned':len(allrows)-len(u),'totals':sums,'cache_hit_rate':sums['hit']/(sums['hit']+sums['miss']),'reasoning_is_proxy':True,'charges':'No billing estimate; usage absent for rejectedrequests.'})
print('Gate',checks,'gainpp',100*gain)
