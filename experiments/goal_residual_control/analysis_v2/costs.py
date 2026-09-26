from progress import *
STAGES=['research_decision_v2','transition_replan_v2','three_round_loop_v2']
def costs():
 groups=collections.defaultdict(list)
 for stage in STAGES:
  for p in (TOP/stage).glob('*_events.jsonl'):
   for line in p.open():
    e=json.loads(line)
    if e['kind']!='completed' or 'result' not in e:continue
    r=e['result'];groups[(stage,r['arm'],r['kind'])].append(r)
 def summarize(rows):
  us=[r['usage'] for r in rows if r.get('usage')];paired=[u for u in us if u.get('prompt_cache_hit_tokens') is not None and u.get('prompt_cache_miss_tokens') is not None]
  hit=sum(u['prompt_cache_hit_tokens'] for u in paired);miss=sum(u['prompt_cache_miss_tokens'] for u in paired)
  return {'calls':len(rows),'attempted':sum(r.get('attempted',True) for r in rows),'valid':sum(r['output'] is not None for r in rows),'usage_reported':len(us),'cache_usage_missing':len(rows)-len(paired),'prompt_tokens':sum(u.get('prompt_tokens',0) for u in us),'completion_tokens':sum(u.get('completion_tokens',0) for u in us),'reasoning_tokens':sum((u.get('completion_tokens_details') or {}).get('reasoning_tokens',0) or 0 for u in us),'total_tokens':sum(u.get('total_tokens',0) for u in us),'cache_hit_tokens':hit,'cache_miss_tokens':miss,'cache_hit_rate':hit/(hit+miss) if hit+miss else None,'inconsistent_prompt_sum':sum(u.get('prompt_tokens')!=u['prompt_cache_hit_tokens']+u['prompt_cache_miss_tokens'] for u in paired)}
 details=[{'stage':k[0],'arm':k[1],'kind':k[2],**summarize(v)} for k,v in sorted(groups.items())]
 stages={s:summarize([r for k,v in groups.items() if k[0]==s for r in v]) for s in STAGES}
 arms={a:summarize([r for k,v in groups.items() if k[0]=='three_round_loop_v2' and k[1]==a for r in v]) for a in ['L0','L1','L2']}
 result={'method':'sum reported hit / sum(hit+miss); invalid outputs and all attempted call costs included; historical reused G1 cost excluded from v2 incremental spend','by_node':details,'by_stage':stages,'G5_by_arm':arms,'total':summarize([r for v in groups.values() for r in v])}
 write(TOP/'CACHE_USAGE_V2.json',result);return result
if __name__=='__main__':print(json.dumps(costs()['by_stage'],indent=2))
