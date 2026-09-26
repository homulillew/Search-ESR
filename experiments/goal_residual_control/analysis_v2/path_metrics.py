from progress import *
def norm(a):
 return (a.get('tool'),a.get('doc_ref'),a.get('window_ref'),a.get('direction'),' '.join(a.get('query','').lower().split()))
def evaluate(rows):
 stats={}
 for arm in sorted({r['arm'] for r in rows}):
  rr=[r for r in rows if r['arm']==arm];aa=[a for r in rr for a in r['actions']];hits=[h for a in aa if a['action']['tool']=='search' for h in a['result'].get('results',[])]
  known=lambda h:h.get('status')=='already_discovered' or h.get('previously_discovered') is True
  stats[arm]={'tool_calls':len(aa),'search_result_items':len(hits),'previously_discovered_items':sum(known(h) for h in hits),'previously_discovered_rate':sum(known(h) for h in hits)/len(hits) if hits else None,'search_calls_only_known_results':sum(bool(a['result'].get('results')) and all(known(h) for h in a['result']['results']) for a in aa if a['action']['tool']=='search'),'tool_errors':sum(bool(a['error']) for a in aa)}
 return stats
if __name__=='__main__':
 for stage,fn in [('one_step_acquisition_v2','outputs.json'),('transition_replan_v2','tool_outputs.json')]:
  p=TOP/stage/fn
  if p.exists():write(p.parent/'review_corrected_path_metrics.json',evaluate(read(p)))
