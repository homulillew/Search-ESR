"""Replay sealed semantic judgments; all planned slots retained."""
from .common import *
from .bootstrap_runtime import load_rows

def aggregate(directory='e2_bootstrap'):
 d=P/directory;review=d/'review';committed(review/'JUDGMENTS.json');committed(review/'PACKETS.json')
 if not (review/'SEAL.json').exists():write(review/'SEAL.json',{'head':git('rev-parse','HEAD'),'files':{rel(p):sha(p) for p in sorted(review.glob('*.json'))},'reviewer':'single familiar Codex, partial mask'})
 key=read(review/'KEY.json');ann={key[r['review_id']]:r for r in read(review/'JUDGMENTS.json')};rows=load_rows(directory);regs=read(P/'e2_bootstrap/PREFIX_REGISTRIES.json');scored=[]
 for r in rows:
  a=ann[r['id']];ret=read(d/'retrieval'/f"{r['id']}.json");valid=ret['attempted'] and not ret['error'];known={v['docid'] for v in regs[r['case_id']]['documents']};docs=[]
  if valid:
   lookup={x['doc_ref']:x['docid'] for x in ret['registry']['documents']};docs=[lookup[w['doc_ref']] for w in ret['tool']['observations']]
  scored.append({**{k:r[k] for k in ['id','case_id','qid','arm','failure','valid_output']},**a,'retrieval_valid':valid,'real_no_gain':bool(valid and not a['new_material'] and not a['binding']),'docids':docs,'repeat_count':sum(x in known for x in docs)})
 out={'arms':{},'rows':scored,'scope':'all planned accessible-state slots; opportunity review, no Writer'}
 for arm in ['P0','P1']:
  rs=[r for r in scored if r['arm']==arm];n=len(rs)
  if not n:continue
  ms={k:metric(sum(bool(r[k]) for r in rs),n) for k in ['new_material','binding','direct','bridge','real_no_gain','query_drift','candidate_commitment','objective_only_rule_violation','retrieval_valid']}
  ms['repeated_document_rate']=metric(sum(r['repeat_count'] for r in rs),sum(len(r['docids']) for r in rs));ms['query_failures']=sum(not r['valid_output'] for r in rs)
  out['arms'][arm]=ms
 if set(out['arms'])=={'P0','P1'}:
  pairs=[]
  for cid in sorted({r['case_id'] for r in scored}):
   a=next(r for r in scored if r['case_id']==cid and r['arm']=='P0');b=next(r for r in scored if r['case_id']==cid and r['arm']=='P1')
   pairs.append({'case_id':cid,'P0':a['new_material'],'P1':b['new_material'],'outcome':'P1_win' if b['new_material'] and not a['new_material'] else 'P0_win' if a['new_material'] and not b['new_material'] else 'tie','doc_overlap':len(set(a['docids'])&set(b['docids']))})
  out['paired']=pairs;out['P1_minus_P0_material']=out['arms']['P1']['new_material']['value']-out['arms']['P0']['new_material']['value']
  g=read(P/'GATES.json')['E2'];ms=out['arms']['P1'];out['gate_checks']={'minimum_states':len(pairs)>=g['minimum_accessible_states'],'minimum_qids':len({r['qid'] for r in scored})>=g['minimum_qids'], 'material':ms['new_material']['value']>=g['P1_new_material'],'binding':ms['binding']['value']>=g['P1_binding'],'drift':ms['query_drift']['value']<=g['drift_max'],'commitment':ms['candidate_commitment']['value']<=g['candidate_commitment_max'],'improvement':out['P1_minus_P0_material']>=g['P1_minus_P0_material_min']};out['gate_pass']=all(out['gate_checks'].values())
 out['sensitivities']={}
 for arm in out['arms']:
  rs=[r for r in scored if r['arm']==arm]
  out['sensitivities'][arm]={'remove_medium_ambiguity_gains':metric(sum(r['new_material'] and r['ambiguity']=='low' for r in rs),len(rs)), 'require_objective_only_query_compliance':metric(sum(r['new_material'] and not r['objective_only_rule_violation'] for r in rs),len(rs))}
 write(d/'METRICS.json',out)
 print(json.dumps({k:v for k,v in out.items() if k!='rows'},indent=2))
if __name__=='__main__':
 import sys
 aggregate(sys.argv[1] if len(sys.argv)>1 else 'e2_bootstrap')
