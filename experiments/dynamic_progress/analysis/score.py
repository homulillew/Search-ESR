"""Aggregate reviewed annotations; semantic decisions live in semantic_review.json."""
import json,hashlib,collections,statistics
from pathlib import Path
T=Path(__file__).resolve().parents[1]
def rd(p):return json.loads(p.read_text())
def wr(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def uid(i):return hashlib.sha256(('dynamic-progress-review-v1:'+i).encode()).hexdigest()[:12]
L={k:v for name in ['PRIMARY','CHALLENGE'] for k,v in rd(T/'bank'/f'{name}_LABELS.json').items()}
REV=rd(T/'analysis/semantic_review.json')
def rows_from_log(path):
 rows=[]
 if not path.exists():return rows
 for line in path.read_text().splitlines():
  try:e=json.loads(line)
  except json.JSONDecodeError:continue
  if e['kind']=='completed':rows.append(e['result'])
 return rows

def enrich(row):
 r=dict(row);g=L[r['case_id']]['gold_resolved'];s=REV.get(uid(r['id']));o=r['output'];r['review']=s;r['gold_resolved']=g
 r['correct_completion']=o is not None and o['resolved']==g
 r['false_closure']=bool(o and o['resolved'] and not g)
 r['missed_closure']=bool(o and not o['resolved'] and g)
 r['units']=s['units'] if s else []
 r['blockers']=[u for u in r['units'] if u['is_blocker']]
 r['valid_presence']=not g and bool(o) and not o['resolved'] and any(u['content_valid'] for u in r['blockers'])
 r['adequate']=bool(s and r['correct_completion'] and (g or (r['valid_presence'] and all(u['content_valid'] for u in r['units']))))
 r['adequate']=r['adequate'] and not (s or {}).get('context_errors')
 r['strict_adequate']=r['adequate'] and (not g or s['closure_witness_valid'] is not False) and all(u['status_valid'] is not False and u['refs_valid'] is not False for u in r['units'])
 return r

def metric(rs):
 n=len(rs);un=sum(not r['gold_resolved'] for r in rs);re=n-un;b=[u for r in rs for u in r['blockers']];us=[r['usage'] for r in rs if r.get('usage')];errs=collections.Counter(e for u in b for e in u['errors'])
 ep=collections.Counter(e for r in rs for e in ({e for u in r['units'] for e in u['errors']} | set((r['review'] or {}).get('context_errors',[]))))
 pairs=collections.defaultdict(list)
 for r in rs:pairs[r['case_id']].append(r)
 stability=collections.Counter()
 for pair in pairs.values():
  if len(pair)!=2:stability['incomplete_pair']+=1;continue
  if all(r['adequate'] for r in pair):stability['both_correct_closure' if pair[0]['gold_resolved'] else 'both_unresolved_compatible_valid']+=1
  elif any(r['adequate'] for r in pair):stability['one_adequate_one_inadequate']+=1
  else:stability['both_inadequate']+=1
 sums={k:sum(u.get(k) or 0 for u in us) for k in ['input','output','hit','miss','reasoning']}
 return {'planned_or_completed':n,'gold_unresolved':un,'gold_resolved':re,'semantic_reviews':sum(r['review'] is not None for r in rs),'failed':sum(r['output'] is None for r in rs),'correct_completion':sum(r['correct_completion'] for r in rs),'false_closure':sum(r['false_closure'] for r in rs),'correct_closure':sum(r['correct_completion'] and r['gold_resolved'] for r in rs),'missed_closure':sum(r['missed_closure'] for r in rs),'valid_blocker_presence':sum(r['valid_presence'] for r in rs),'blocker_valid':sum(u['content_valid'] for u in b),'blocker_total':len(b),'blocker_precision':sum(u['content_valid'] for u in b)/len(b) if b else None,'adequate':sum(r['adequate'] for r in rs),'strict_adequate':sum(r['strict_adequate'] for r in rs),'unit_errors':dict(errs),'output_errors':dict(ep),'status_errors':sum(u['status_valid'] is False for r in rs for u in r['units']),'semantic_ref_errors':sum(u['refs_valid'] is False for r in rs for u in r['units']),'false_evidence_promotion':sum(bool(r['review'] and r['review'].get('false_evidence_promotion')) for r in rs),'valid_closure_witness':sum(bool(r['review'] and r['review']['closure_witness_valid']) for r in rs),'closure_witness_denominator':sum(bool(r['output'] and r['output']['resolved'] and r['arm']!='R') for r in rs),'replicate_stability':dict(stability),'completion_agreement_pairs':sum(len(p)==2 and all(r['output'] for r in p) and p[0]['output']['resolved']==p[1]['output']['resolved'] for p in pairs.values()),'usage':sums,'cache_hit_rate':sums['hit']/(sums['hit']+sums['miss']) if sums['hit']+sums['miss'] else None,'elapsed_mean':statistics.mean(r['elapsed_seconds'] for r in rs) if rs else None}

def main():
 original=rows_from_log(T/'p1_progress/progress_events.jsonl');corrected=rows_from_log(T/'transport_correction/corrected_events.jsonl')
 replacement={r['id'].removeprefix('TC_'):r for r in corrected}
 tables={};allreviewed=[]
 for name,rows in [('original',original),('transport_corrected_diagnostic',[replacement.get(r['id'],r) for r in original])]:
  rs=[enrich(r) for r in rows];tables[name]={}
  for group in ['fresh_primary','challenge']:
   for arm in ['R','B','FULL']:
    selected=[r for r in rs if r['set']==group and r['arm']==arm]
    if selected:tables[name][group+'_'+arm]=metric(selected)
  if name=='transport_corrected_diagnostic':allreviewed=rs
 tables['per_qid']={f'{g}_{a}_{q}':metric([r for r in allreviewed if r['set']==g and r['arm']==a and r['qid']==q]) for g,a,q in sorted({(r['set'],r['arm'],r['qid']) for r in allreviewed})}
 fullids=set(rd(T/'bank/SELECTION.json')['full_sensitivity'])
 tables['FULL_sensitivity']={a:metric([r for r in allreviewed if r['case_id'] in fullids and r['arm']==a]) for a in ['B','FULL']}
 wr(T/'analysis/metrics.json',tables);wr(T/'analysis/reviewed_outputs.json',allreviewed)
 for k,v in tables['transport_corrected_diagnostic'].items():print(k,{x:v[x] for x in ['planned_or_completed','failed','correct_completion','false_closure','correct_closure','valid_blocker_presence','blocker_valid','blocker_total','output_errors']})
if __name__=='__main__':main()
