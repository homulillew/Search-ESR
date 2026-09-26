"""Aggregate explicit manual labels, never infer semantic verdicts from keywords."""
import json,collections,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1]
def rd(p):return json.loads(p.read_text())
def wr(p,x):
 with p.open('x') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
def reviews(folder='round_0',arms=None,allow_incomplete=False):
 manual=[json.loads(l) for l in (P/'analysis'/f'{folder}_manual.jsonl').read_text().splitlines()];M={(x['case_id'],x['arm']):x for x in manual};rows=[]
 arms=arms or ['P0','P1','P2','P3','P4']
 for arm in arms:
  f=P/('round_0_p3_format_repair' if folder=='round_0' and arm=='P3' else folder)
  output=f/'OUTPUTS.json'
  if not output.exists():
   if allow_incomplete:continue
   raise AssertionError(output)
  for r in rd(output):
   if r['arm']!=arm:continue
   key=r['case_id'],arm
   if r['output']:
    assert key in M,key;v=M[key];assert v['output']==r['output'];rows.append(v)
   else:
    rows.append({'case_id':r['case_id'],'arm':arm,'STRICT_VALID':False,**{k:None for k in ['V','S','P','W','I','H','A']},'mechanisms':['B11_output_unavailable'],'reason':str(r['errors']),'output':None})
 return rows
def metric(rows):
 n=len(rows);a=sum(r['output'] is not None for r in rows)
 return {'n':n,'strict_valid':sum(r['STRICT_VALID'] for r in rows),'rate':sum(r['STRICT_VALID'] for r in rows)/n if n else None,'assessable':a,'unavailable':n-a,'semantic_given_output':sum(r['STRICT_VALID'] for r in rows)/a if a else None,'dimensions':{k:sum(r[k] is True for r in rows) for k in ['V','S','P','W','I','H','A']},'mechanisms':dict(collections.Counter(m for r in rows for m in r['mechanisms']))}
def usage(folders):
 rows=[rd(f) for d in folders for f in (P/d/'calls').glob('*.result.json')];usage=[r['usage'] for r in rows if r.get('usage')];inp=sum(u.get('prompt_tokens',0) for u in usage);hit=sum(u.get('prompt_cache_hit_tokens',0) for u in usage)
 return {'attempts':sum(r['attempted'] for r in rows),'completed_records':len(rows),'input_tokens':inp,'output_tokens':sum(u.get('completion_tokens',0) for u in usage),'cache_hit_tokens':hit,'cache_miss_tokens':sum(u.get('prompt_cache_miss_tokens',0) for u in usage),'cache_hit_rate':hit/inp if inp else None,'errors':dict(collections.Counter(r['error']['category'] for r in rows if r['error'])),'by_stage':{s:{'calls':sum(r['stage']==s for r in rows),'errors':sum(r['stage']==s and bool(r['error']) for r in rows)} for s in sorted({r['stage'] for r in rows})}}
def aggregate(allow=False):
 rows=reviews(allow_incomplete=allow);labels={r['case_id']:r for r in rd(P/'bank/LABELS.json')};members=rd(P/'bank/MEMBERSHIP.json');out={}
 for arm in sorted({r['arm'] for r in rows}):
  ar=[r for r in rows if r['arm']==arm];b={}
  for name,cids in members.items():
   selected=[r for r in ar if r['case_id'] in cids];b[name]=metric(selected)
  dev=[r for r in ar if r['case_id'] in members['development']]
  b['development_by_qid']={q:metric([r for r in dev if labels[r['case_id']]['qid']==q]) for q in sorted({labels[r['case_id']]['qid'] for r in dev})}
  b['development_strata']={s:metric([r for r in dev if s in labels[r['case_id']]['strata']]) for s in ['U1','U2','U3','U4','U5','U6']};out[arm]=b
 return {'paths':out,'usage':usage(['round_0','round_0_p3_format_repair']),'coverage_qualification':'insufficient: five eligible primary qids; formal fresh confirmation requires eight','original_P3_rejections':55}
if __name__=='__main__':
 import sys
 x=aggregate('--partial' in sys.argv)
 for a,b in x['paths'].items():print(a,'dev',b['development'],'challenge',b['challenge']['strict_valid'])
 if '--partial' not in sys.argv:
  wr(P/'round_0/METRICS.json',x);wr(P/'round_0/REVIEW.json',reviews())
 print(x['usage'])
