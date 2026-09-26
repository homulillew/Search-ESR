import json,collections
from pathlib import Path
T=Path(__file__).resolve().parents[1]
def rd(p):return json.loads(p.read_text())
def wr(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
M=rd(T/'analysis/review_map.json');REV=rd(T/'analysis/semantic_review.json')
LOOK={(v['stage'],v['id']):REV[k] for k,v in M.items() if k in REV}
LABEL={k:v for b in ['PRIMARY','CHALLENGE'] for k,v in rd(T/f'bank/{b}_LABELS.json').items()}
PAIR=rd(T/'bank/PAIRING.json')
def pred(r):return r['output'].get('resolved',r['output'].get('confirmed')) if r['output'] else None
def rat(n,d):return {'n':n,'d':d,'rate':n/d if d else None}
def cost(rows):
 a={k:sum((r.get('usage') or {}).get(k) or 0 for r in rows) for k in ['input','output','reasoning','hit','miss']}
 a.update(slots=len(rows),attempted=sum(r['attempted'] for r in rows),usage_missing=sum(r.get('usage') is None for r in rows),cache_hit_rate=a['hit']/(a['hit']+a['miss']) if a['hit']+a['miss'] else None)
 return a
def semantic(stage,r):return LOOK[(stage,r['id'])]
def armmetrics(stage,rows):
 n=len(rows);un=[r for r in rows if not LABEL[r['case_id']]['gold_resolved']];res=[r for r in rows if LABEL[r['case_id']]['gold_resolved']]
 units=[u for r in rows for u in semantic(stage,r)['units']];confirm=[r for r in rows if pred(r) is True]
 def anyerr(r,e):return any(e in u['errors'] for u in semantic(stage,r)['units'])
 out={'slots':n,'valid_outputs':rat(sum(r['output'] is not None for r in rows),n),'completion_accuracy':rat(sum(pred(r)==LABEL[r['case_id']]['gold_resolved'] for r in rows if pred(r) is not None),n),'false_closure':rat(sum(pred(r) is True for r in un),len(un)),'correct_closure':rat(sum(pred(r) is True for r in res),len(res)), 'missed_closure':rat(sum(pred(r) is False for r in res),len(res)), 'valid_blocker_presence':rat(sum(any(u['content_valid'] for u in semantic(stage,r)['units']) for r in un),len(un)),'blocker_precision':rat(sum(u['content_valid'] for u in units),len(units)),'strict_blocker_precision':rat(sum(u['content_valid'] and u['status_valid'] is not False and u['refs_valid'] for u in units),len(units)), 'certificate_adequacy':rat(sum(semantic(stage,r)['closure_witness_valid'] is True for r in confirm),len(confirm)),'certificate_on_true_closure':rat(sum(semantic(stage,r)['closure_witness_valid'] is True for r in confirm if LABEL[r['case_id']]['gold_resolved']),sum(LABEL[r['case_id']]['gold_resolved'] for r in confirm)), 'false_evidence_promotion_outputs':sum(semantic(stage,r).get('false_evidence_promotion',False) for r in rows),'status_error_units':sum(u['status_valid'] is False for u in units),'semantic_ref_error_units':sum(not u['refs_valid'] for u in units),'cost':cost(rows)}
 for e in ['over_broad','unsupported_premise','invented_requirement','already_supported']:
  out[e]={'outputs':sum(anyerr(r,e) for r in rows),'units':sum(e in u['errors'] for u in units)}
 groups=collections.defaultdict(list)
 for r in rows:groups[r['case_id']].append(r)
 out['replicate_completion_agreement']=rat(sum(len(g)==2 and pred(g[0]) is not None and pred(g[0])==pred(g[1]) for g in groups.values()),len(groups))
 out['by_qid']={q:{'n':len(g),'false_closure':sum(pred(r) is True and not LABEL[r['case_id']]['gold_resolved'] for r in g),'correct_closure':sum(pred(r) is True and LABEL[r['case_id']]['gold_resolved'] for r in g)} for q in sorted({r['qid'] for r in rows},key=int) for g in [[r for r in rows if r['qid']==q]]}
 return out
def policy(stage,rows):
 by={(r['case_id'],r['arm'],r['replicate']):r for r in rows};cases=sorted({r['case_id'] for r in rows});out={}
 for pol in ['L','LL','LA']:
  decisions=[];used=[]
  for cid in cases:
   p=PAIR[cid];first=by[(cid,'L1',p['L1_primary'])];calls=[first];stop=pred(first) is True;valid=pred(first) is not None
   if stop and pol!='L':
    second=by[(cid,'L1',3-p['L1_primary'])] if pol=='LL' else by[(cid,'Audit',p['Audit_primary'])]
    calls.append(second);stop=pred(second) is True;valid=valid and pred(second) is not None
   used+=calls;decisions.append({'case_id':cid,'gold':LABEL[cid]['gold_resolved'],'stop':stop,'valid':valid,'calls':[r['id'] for r in calls]})
  n=len(cases);u=sum(not d['gold'] for d in decisions);s=n-u
  out[pol]={'false_stop':rat(sum(d['stop'] and not d['gold'] for d in decisions),u),'correct_stop':rat(sum(d['stop'] and d['gold'] for d in decisions),s),'missed_stop':rat(sum(not d['stop'] and d['gold'] for d in decisions),s),'invalid_decisions':sum(not d['valid'] for d in decisions),'decision_accuracy':rat(sum(d['valid'] and d['stop']==d['gold'] for d in decisions),n),'conditional_second_call_rate':rat(len(used)-n,n),'expected_calls_per_decision':len(used)/n,'logical_cost':cost(used),'mean_tokens_per_decision':{k:cost(used)[k]/n for k in ['input','output','reasoning']},'decisions':decisions}
 return out
def critical(stage,r):
 rv=semantic(stage,r);gold=LABEL[r['case_id']]['gold_resolved'];p=pred(r)
 # Invalid output is separately a mechanical failure, not fabricated semantic regression.
 return p is not None and (p!=gold or (not gold and not any(u['content_valid'] for u in rv['units'])) or rv.get('false_evidence_promotion',False) or any('unsupported_premise' in u['errors'] for u in rv['units']))
def main():
 allrows=[];results={}
 for stage in ['primary','challenge']:
  rows=rd(T/stage/(stage+'_outputs.json'));assert all((stage,r['id']) in LOOK for r in rows),'Unreviewed output'
  allrows+=rows;a={arm:armmetrics(stage,[r for r in rows if r['arm']==arm]) for arm in ['L0','L1','Audit']};p=policy(stage,rows)
  results[stage]={'arms':a,'policies':p}
  wr(T/stage/'metrics.json',results[stage])
 a=results['primary']['arms'];p=results['primary']['policies'];rows=rd(T/'primary/primary_outputs.json');by={(r['case_id'],r['arm'],r['replicate']):r for r in rows}
 regressions=[r['id'] for r in rows if r['arm']=='L1' and critical('primary',r) and not critical('primary',by[(r['case_id'],'L0',r['replicate'])])]
 rqids={r['qid'] for r in rows if r['id'] in regressions}
 def ge(v,x):return v['rate'] is not None and v['rate']>=x
 c1={'false_closure':a['L1']['false_closure']['n']<=3,'presence':a['L1']['valid_blocker_presence']['n']>=35,'precision':ge(a['L1']['blocker_precision'],.9),'correct_closure':a['L1']['correct_closure']['n']>=9,'critical_regression':not(len(regressions)>=3 and len(rqids)>=2)}
 c2={'false_closure':a['Audit']['false_closure']['n']<=1,'presence':a['Audit']['valid_blocker_presence']['n']>=35,'correct_closure':a['Audit']['correct_closure']['n']>=9,'precision':ge(a['Audit']['blocker_precision'],.9),'certificate':ge(a['Audit']['certificate_adequacy'],.9)}
 c3={'false_stop':p['LA']['false_stop']['n']==0,'correct_stop':p['LA']['correct_stop']['n']>=5,'accuracy':p['LA']['decision_accuracy']['n']>=23,'noninferior_to_LL':p['LA']['decision_accuracy']['n']>=p['LL']['decision_accuracy']['n'] and p['LA']['false_stop']['n']<=p['LL']['false_stop']['n']}
 gate={'C1':{'pass':all(c1.values()),'checks':c1,'new_critical_regressions':regressions,'regression_qids':sorted(rqids)},'C2':{'pass':all(c2.values()),'checks':c2},'C3':{'pass':all(c3.values()),'checks':c3}}
 gate['enter_frontier']=all(gate[k]['pass'] for k in ['C1','C2','C3']);wr(T/'analysis/GATE.json',gate)
 wr(T/'analysis/cost.json',{'formal_all_calls':cost(allrows),'canary':cost(rd(T/'canary/canary_outputs.json')),'reasoning_is_subset_of_output':True})
 print(json.dumps(gate,indent=2))
if __name__=='__main__':main()
