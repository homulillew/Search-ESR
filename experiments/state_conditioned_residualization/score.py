"""Sealed semantic flags + frozen class sets. No after-output reference changes."""
import argparse
from collections import Counter
from .common import *
from .run import OUT,jobs,load_rows,audit
FLAGS=('parent_faithful','unresolved','local_coherent','non_downstream','scope_faithful','no_invented_premise')
ERRORS=('supported_content_leakage','broad_residual','downstream','relation_object_temporal_corruption','control_over_decomposition','candidate_hardening')
def seal_review():
 assert not (OUT/'METRICS.json').exists();packets=read(OUT/'review/PACKETS.json');labels=read(OUT/'review/JUDGMENTS.json')
 assert set(labels)=={p['review_id'] for p in packets} and len(labels)==114
 for p in packets:
  x=labels[p['review_id']]
  assert isinstance(x['reason'],str) and x['reason'].strip()
  for f in FLAGS+ERRORS+('mode_correct','used_claims_substantive'):assert type(x[f]) is bool or (p['no_response'] and x[f] is None)
  assert isinstance(x['class_id'],str) or p['no_response']
 paths=[OUT/'review'/n for n in ('PACKETS.json','KEY.json','JUDGMENTS.json')]
 for p in paths:committed(p)
 write(OUT/'review/REVIEW_SEAL.json',{'judgment_commit':git('rev-parse','HEAD'),'files':{rel(p):sha(p) for p in paths},
  'scope':'Single familiar reviewer. Full currentClaims shown for unresolved/leakage truth; actual model input separately shown for premise provenance. Arm names, replicate, case IDs, Gold class sets, aggregates and provider reasoning hidden.'})
def assert_review():
 seal=read(OUT/'review/REVIEW_SEAL.json')
 for p,h in seal['files'].items():assert sha(ROOT/p)==h;committed(ROOT/p,seal['judgment_commit'])
def scored_rows():
 key=read(OUT/'review/KEY.json');reverse={v:k for k,v in key.items()};labels=read(OUT/'review/JUDGMENTS.json')
 refs={g['case_id']:g for g in read(P/'e0_reference/RESIDUAL_REFERENCE.json')};states={s['case_id']:s for s in read(P/'e0_reference/STATES.json')};rows=[]
 for r in load_rows():
  x=labels[reverse[r['id']]];ref=refs[r['case_id']];accepted=x['class_id'] in {c['class_id'] for c in ref['acceptable_residual_classes']}
  strict=bool(r['valid_output'] and accepted and all(x[f] for f in FLAGS))
  rows.append({**{k:r[k] for k in ('id','case_id','qid','arm','replicate')},'bank_group':states[r['case_id']]['bank_group'],
    'support_stratum':states[r['case_id']]['support_stratum'],'schema':bool(r['valid_output']),'strict':strict,
    'accepted_class':accepted,'review_id':reverse[r['id']],'review':x,'failure':r.get('failure')})
 return rows
def measure(rows):
 n=len(rows);sub=[r for r in rows if r['bank_group']=='primary_subnode'];controls=[r for r in rows if r['bank_group']=='control']
 m={'strict_validity':metric(sum(r['strict'] for r in rows),n),'schema':metric(sum(r['schema'] for r in rows),n),
   'residual_addressability':metric(sum(r['strict'] for r in sub),len(sub)),
   'control_over_decomposition':metric(sum(bool(r['review']['control_over_decomposition']) for r in controls),len(controls)),
   'mode_accuracy':metric(sum(r['schema'] and r['review']['mode_correct'] for r in rows),n),
   'used_claims_substantive':metric(sum(r['schema'] and r['review']['used_claims_substantive'] for r in rows),n)}
 for e in ERRORS:
  if e!='control_over_decomposition':m[e]=metric(sum(bool(r['review'][e]) for r in rows),n)
 m['six_conditions_only']=metric(sum(r['schema'] and all(r['review'][f] for f in FLAGS) for r in rows),n)
 return m
def discrimination(rows,arm):
 by={(r['case_id'],r['replicate']):r for r in rows if r['arm']==arm};events=[]
 for pair in read(P/'analysis/STATE_DISCRIMINATION_REFERENCE.json'):
  for rep in (1,2):
   a=by[pair['from'],rep];b=by[pair['to'],rep];retired=a['review']['class_id'] in pair['removed_classes']
   valid=a['strict'] and b['strict'];kind='correct_required_switch' if valid and retired else 'compatible_persistence_or_other_valid_switch' if valid else 'failed_pair'
   events.append({**pair,'replicate':rep,'from_class':a['review']['class_id'],'to_class':b['review']['class_id'],
    'from_strict':a['strict'],'to_strict':b['strict'],'requires_target_change':retired,'valid_transition':valid,'kind':kind})
 return {'metric':metric(sum(e['valid_transition'] for e in events),len(events)),'events':events,
   'required_change_subset':metric(sum(e['valid_transition'] for e in events if e['requires_target_change']),sum(e['requires_target_change'] for e in events))}
def check(m,rules,extra=None):
 values={k:v['value'] for k,v in m.items() if isinstance(v,dict) and 'value' in v};values.update(extra or {});checks={}
 for name,(op,t) in rules.items():
  v=values.get(name);checks[name]={'value':v,'operator':op,'threshold':t,'pass':v is not None and (v>=t-1e-12 if op=='>=' else v<=t+1e-12)}
 return {'pass':all(c['pass'] for c in checks.values()),'checks':checks}
def calculate():
 rows=scored_rows();rules=read(P/'GATES.json');arms={}
 for arm in ('R0','R1','R2'):
  sub=[r for r in rows if r['arm']==arm];m=measure(sub);disc=discrimination(rows,arm);m['state_discrimination']=disc['metric']
  arms[arm]={'metrics':m,'state_discrimination':disc,'strata':{f:{str(v):measure([r for r in sub if r[f]==v]) for v in sorted({r[f] for r in sub},key=str)} for f in ('support_stratum','bank_group','qid','replicate')}}
 loss=arms['R0']['metrics']['strict_validity']['value']-arms['R2']['metrics']['strict_validity']['value']
 for arm in arms:arms[arm]['gate']=check(arms[arm]['metrics'],rules[arm],{'strict_loss_R0_minus_R2':loss})
 pg={a:check(arms[a]['strata']['support_stratum']['P'],rules['P_gate_'+a]) for a in ('R0','R1')}
 return {'arms':arms,'R0_minus_R2_strict':loss,'P_gate':pg,'bootstrap_eligible':all(v['pass'] for v in pg.values()),
  'P_gate_note':'TASK28/29: P-group quality controls entry even if Z depresses total gate. Pair metric includes Z origin and is reported under full R0, not used to silently veto Case C.',
  'bank':{'states':19,'P_states':3,'Z_states':16,'primary_states':11,'controls':8,'calls':114},'scored_rows':rows}
def aggregate():
 audit();assert_review();m=calculate();write(OUT/'METRICS.json',m)
 write(P/'analysis/STATE_DISCRIMINATION.json',{a:v['state_discrimination'] for a,v in m['arms'].items()})
 write(P/'analysis/ERROR_LEDGER.json',[r for r in m['scored_rows'] if not r['strict'] or not r['review']['mode_correct'] or not r['review']['used_claims_substantive']])
 print(json.dumps({'arms':{a:{'gate':v['gate']['pass'],'strict':v['metrics']['strict_validity']} for a,v in m['arms'].items()},'P_gate':m['P_gate'],'bootstrap_eligible':m['bootstrap_eligible']},indent=2))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['seal_review','aggregate']);a=ap.parse_args();globals()[a.mode]()
