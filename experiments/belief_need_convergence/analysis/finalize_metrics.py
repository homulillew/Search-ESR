from aggregate import P,rd,wr,reviews,metric,usage
import copy,collections,json,math
r0=rd(P/'round_0/REVIEW.json');r1=reviews('round_1',['P5']);M={(r['case_id'],r['arm']):r for r in r0};ids=[r['case_id'] for r in r1];base=[M[c,'P1'] for c in ids];new={r['case_id']:r for r in r1}
target=['N004','N015','N016','N018','N020'];controls=['N003','N007','N014','N021','N024'];repaired=[c for c in target if new[c]['STRICT_VALID']];regressed=[c for c in controls if not new[c]['STRICT_VALID']]
metrics={'bank':'exposed development exploration; not confirmation','baseline':metric(base),'P5_locality':metric(r1),'B5_targets':target,'B5_repaired':repaired,'valid_controls':controls,'valid_controls_regressed':regressed,'numeric_improvement_is_not_confirmation':True,'mechanism_rule_passed':len(repaired)>=3 and len(regressed)<=1 and sum(r['P'] is True for r in r1)<=sum(r['P'] is True for r in base),'decision':'STOP: exploratory repair insufficient and qualified fresh confirmation qids exhausted','usage':usage(['round_1']),'no_H':metric([new[c] for c in ['N001','N006','N015','N020']]),'U4':metric([new['N014']])}
wr(P/'round_1/REVIEW.json',r1);wr(P/'round_1/METRICS.json',metrics)
# Append-only boundary sensitivity; never replace frozen/reported primary labels.
sets={'alias_relaxed':{('N012','P0'),('N012','P3'),('N012','P4'),('N044','P3')},'calendar_background_relaxed':{('N013','P0'),('N013','P1'),('N044','P0'),('N045','P1'),('N046','P0')}}
dev=rd(P/'bank/MEMBERSHIP.json')['development'];sens={}
for name,keys in sets.items():
 rows=copy.deepcopy(r0)
 for r in rows:
  if (r['case_id'],r['arm']) in keys:
   r['P']=False
   if name=='alias_relaxed':r['H']=False;r['V']=not r['S'] and not r['I']
   r['STRICT_VALID']=r['V'] and r['A'] and not any(r[k] for k in ['S','P','W','I','H'])
 sens[name]={'affected_cells':sorted([list(k) for k in keys]),'development':{a:metric([r for r in rows if r['arm']==a and r['case_id'] in dev]) for a in ['P0','P1','P2','P3','P4']}}
wr(P/'analysis/SENSITIVITY.json',{'status':'Alternative boundary interpretations, not post-call gold correction','frozen_labels_unchanged':True,'variants':sens,'historical_multiplayer_rule':{'cell':'N026/P4','new_strict_label':'valid; exclusivity not in Claims','historical_broad_rule_label':'stale if one offline player treated as full exclusivity','P4_challenge_original_historical_rule':6,'P4_challenge_new_precalled_strict_rule':7,'denominator':10},'caution':'Alias-boundary relaxation removes the strongest paired H-premise effect; broadness regression remains. Calendar relaxation improves P1 by one dev state. No alternative meets gates.'})
metrics0=rd(P/'round_0/METRICS.json');pair=rd(P/'analysis/PAIR_METRICS.json');gates={}
for a,b in metrics0['paths'].items():
 d=b['development'];s=b['development_strata'];g={'strict_21_of_24':d['strict_valid']>=21,'P_at_most_1':d['dimensions']['P']<=1,'S_at_most_1':d['dimensions']['S']<=1,'W_at_most_2':d['dimensions']['W']<=2,'U4_1_of_1':s['U4']['strict_valid']>=1,'coverage_pairs_11_of_12':pair[a]['pair_correct']>=11,'no_H_6_of_7':s['U1']['strict_valid']>=6}
 gates[a]={'numeric_gates':g,'all_numeric_gates':all(g.values()),'production_eligible':a!='P4','fresh_confirmation_coverage':False}
wr(P/'analysis/GATES.json',{'development':gates,'selected_baseline':'P1','P3_cost_gate':{'P3_strict':8,'best_single_strict':7,'denominator':24,'required_difference':2,'observed_difference':1,'passes':False},'final_classification':'FAIL under tested configuration; EVIDENCE_EXHAUSTED for confirmation','closure':'NOT RUN','autonomous_simulation':'NOT RUN','held_out_end_to_end':'NOT ELIGIBLE'})
wr(P/'analysis/TOTAL_USAGE.json',usage(['round_0','round_0_p3_format_repair','round_1']))
print(json.dumps(metrics,indent=2));print(json.dumps(rd(P/'analysis/TOTAL_USAGE.json'),indent=2))
