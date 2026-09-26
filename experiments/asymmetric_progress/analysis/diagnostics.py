"""Descriptive diagnostics only; no post-result gate changes."""
import collections,json
import score as s

def main():
 out={};mapping=s.M
 for stage in ['primary','challenge']:
  rows=s.rd(s.T/stage/(stage+'_outputs.json'));groups={a:[r for r in rows if r['arm']==a] for a in ['L0','L1','Audit']}
  data={}
  for arm,rs in groups.items():
   units=[u for r in rs for u in s.semantic(stage,r)['units']]
   # Bound for sensitivity, not a replacement rubric: pardon only breadth errors.
   pardoned=sum(u['content_valid'] or set(u['errors'])=={'over_broad'} for u in units)
   data[arm]={'posthoc_breadth_pardoned_precision_bound':s.rat(pardoned,len(units)),
    'by_qid':{q:s.armmetrics(stage,[r for r in rs if r['qid']==q]) for q in sorted({r['qid'] for r in rs},key=int)},
    'false_closure_ids':[r['id'] for r in rs if s.pred(r) is True and not s.LABEL[r['case_id']]['gold_resolved']],
    'missed_closure_ids':[r['id'] for r in rs if s.pred(r) is False and s.LABEL[r['case_id']]['gold_resolved']],
    'whole_valid_unresolved_outputs':sum(s.pred(r) is False and not s.LABEL[r['case_id']]['gold_resolved'] and s.semantic(stage,r)['units'] and all(u['content_valid'] for u in s.semantic(stage,r)['units']) for r in rs)}
  pol=s.policy(stage,rows);ld={d['case_id']:d for d in pol['L']['decisions']}
  for policy in ['LL','LA']:
   pol[policy]['false_stops_fixed_vs_L']=[d['case_id'] for d in pol[policy]['decisions'] if not d['gold'] and ld[d['case_id']]['stop'] and not d['stop'] and d['valid']]
   pol[policy]['true_stops_lost_vs_L']=[d['case_id'] for d in pol[policy]['decisions'] if d['gold'] and ld[d['case_id']]['stop'] and not d['stop']]
  out[stage]={'arms':data,'policy_comparison':{k:{x:v for x,v in p.items() if x in ['false_stops_fixed_vs_L','true_stops_lost_vs_L']} for k,p in pol.items()}}
  if stage=='challenge':
   bank={c['case_id']:c for c in s.rd(s.T/'bank/CHALLENGE.json')}
   out['challenge_case_details']={cid:{'prior_case_id':bank[cid]['prior_case_id'],'qid':bank[cid]['qid'],'gold_resolved':s.LABEL[cid]['gold_resolved'],'outputs':[{ 'id':r['id'],'decision':s.pred(r),'valid_blocker_present':any(u['content_valid'] for u in s.semantic(stage,r)['units']),'review_reason':s.semantic(stage,r)['reason']} for r in sorted(rows,key=lambda r:r['id']) if r['case_id']==cid],'policies':{p:next(d for d in vals['decisions'] if d['case_id']==cid) for p,vals in pol.items()}} for cid in sorted(bank)}
 s.wr(s.T/'analysis/diagnostics.json',out)
 print('diagnostics written')
if __name__=='__main__':main()
