"""Aggregate frozen calls and explicit human semantic judgments; no API."""
import sys,collections
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from transport import P,rd,save
def ratio(a,b):return a/b if b else None
def distribution(xs):
 xs=[x for x in xs if x is not None]
 return {'n':len(xs),'p50':float(np.percentile(xs,50)) if xs else None,'p90':float(np.percentile(xs,90)) if xs else None,'max':max(xs) if xs else None,'total':sum(xs)}
def metrics(rows):
 n=len(rows);exists=sum(r['final_output_exists'] for r in rows);valid=sum(r['strict_valid'] for r in rows);tok=[r.get('token_accounting',{}) for r in rows]
 out={'n':n,'valid':valid,'final_output_exists':exists,'final_JSON':sum(r['final_valid_JSON'] for r in rows),'parse_valid':sum(r['parse_valid'] for r in rows),'schema_valid':sum(r['schema_valid'] for r in rows),
 'FinalJSONCompletionRate':ratio(sum(r['final_valid_JSON'] for r in rows),n),'ITT_strict':ratio(valid,n),'SemanticValidity_given_final_output':ratio(valid,exists),
 'length':sum(r['finish_reason']=='length' for r in rows),'LengthFailureRate':ratio(sum(r['finish_reason']=='length' for r in rows),n),
 'schema_valid_given_parsed':ratio(sum(r['schema_valid'] for r in rows),sum(r['parse_valid'] for r in rows)),
 'errors':{e:sum(e in r['codes'] for r in rows) for e in ['P','S','W','R','A','FORMAT','NO_OUTPUT']},
 'completion_tokens':distribution([u.get('output') for u in tok]),'reasoning_tokens':distribution([u.get('reasoning') for u in tok]),'final_tokens':distribution([u.get('final') for u in tok])}
 out['Reasoning_Output_ratio']=ratio(out['reasoning_tokens']['total'],out['completion_tokens']['total']);inp=sum(u.get('input') or 0 for u in tok);hit=sum(u.get('hit') or 0 for u in tok)
 out.update({'input_tokens':inp,'cache_hit_tokens':hit,'cache_miss_tokens':sum(u.get('miss') or 0 for u in tok),'cache_hit_rate':ratio(hit,inp)})
 return out
def analyze(stage):
 D=P/'need'/stage;jobs=rd(D/'JOBS.json');annotations=rd(D/'REVIEW.json');inputs=rd(D/'INPUTS.json');bank=rd(P/'bank'/('CONFIRMATION.json' if stage.startswith('confirmation') else 'DEVELOPMENT.json'));primary={s['state_id']:s for s in bank}
 assert set(annotations)=={j['id'] for j in jobs},(len(annotations),len(jobs))
 rows=[]
 for j in jobs:
  r=rd(D/'calls'/(j['id']+'.result.json'));a=annotations[j['id']];assert a['reason'];codes=a['codes'];assert set(codes)<=set(['P','S','W','R','A','FORMAT','NO_OUTPUT'])
  if not r['final_output_exists']:assert codes==['NO_OUTPUT']
  if not r['final_valid_JSON'] and r['final_output_exists']:assert 'FORMAT' in codes
  rows.append(dict(r,arm=j['arm'],input_id=j['input_id'],codes=codes,reason=a['reason'],strict_valid=r['final_valid_JSON'] and not codes,no_h=not bool(inputs[j['input_id']]['hypothesis'])))
 idx={r['id']:r for r in rows};arms=sorted({r['arm'] for r in rows});out={}
 for arm in arms:
  rs=[r for r in rows if r['arm']==arm and r['input_id'] in primary];no=[r for r in rs if r['no_h']];gap=[r for r in rs if primary[r['input_id']]['label']['strong_h_one_gap']]
  out[arm]={'primary':metrics(rs),'no_h':metrics(no),'strong_h_one_gap':metrics(gap),'all_unique_including_delta':metrics([r for r in rows if r['arm']==arm])}
 pairjudgments=rd(D/'DELTA_REVIEW.json');refs=rd(D/'PAIR_REFS.json');pr=[]
 for a in pairjudgments:
  p=a['pair_id'];arm=a['arm'];ra=idx[arm+'__'+refs[p+'_A']];rb=idx[arm+'__'+refs[p+'_B']]
  assert isinstance(a['A_activated_g'],bool) and isinstance(a['B_activated_g'],bool) and a['reason']
  pr.append(dict(a,A_valid=ra['strict_valid'],B_valid=rb['strict_valid'],A_activated_valid=a['A_activated_g'] and ra['strict_valid'],B_retired_g=rb['final_valid_JSON'] and not a['B_activated_g'],both_valid=ra['strict_valid'] and rb['strict_valid']))
 for arm in arms:
  ps=[p for p in pr if p['arm']==arm]
  if not ps:continue
  act=[p for p in ps if p['A_activated_g']];av=[p for p in ps if p['A_activated_valid']]
  out[arm]['delta']={'n':len(ps),'A_activated_g':len(act),'A_activated_g_and_valid':len(av),'B_retired_g_all':sum(p['B_retired_g'] for p in ps),'B_strict_valid':sum(p['B_valid'] for p in ps),'both_valid':sum(p['both_valid'] for p in ps),
 'B_strict_rate':ratio(sum(p['B_valid'] for p in ps),len(ps)),'retirement_given_A_activated':ratio(sum(p['B_retired_g'] for p in act),len(act)),
 'retirement_given_A_valid_activation':ratio(sum(p['B_retired_g'] for p in av),len(av)),
 'B_valid_and_retired_given_A_valid_activation':ratio(sum(p['B_retired_g'] and p['B_valid'] for p in av),len(av)),
 'retired_count_given_A_valid_activation':sum(p['B_retired_g'] for p in av)}
 save(D/'SCORED.json',rows);save(D/'DELTA_SCORED.json',pr);save(D/'METRICS.json',out)
 for a,x in out.items():print(a,'primary',x['primary']['valid'],'/',x['primary']['n'],'noH',x['no_h']['valid'],'/',x['no_h']['n'],'errors',x['primary']['errors'],'P90',x['primary']['reasoning_tokens']['p90'],'delta',x.get('delta'))
if __name__=='__main__':analyze(sys.argv[1])
