"""Aggregate archived usage/integrity; no new API or retrieval calls."""
import collections,sys
from common import *

stages={};all_events=[]
for name in ['goal_review','research_decision']:
    events=[json.loads(l)['event'] for l in (TOP/name/'events.jsonl').open() if json.loads(l)['kind']=='completed']
    all_events.extend(events);reported=[e['cache_usage'] for e in events if e.get('cache_usage',{}).get('status')=='reported']
    hit=sum(x['prompt_cache_hit_tokens'] for x in reported);miss=sum(x['prompt_cache_miss_tokens'] for x in reported)
    stages[name]={'responses':sum('response' in e for e in events),'valid':sum('error' not in e for e in events),
      'api_failures':sum('response' not in e for e in events),'schema_failures':sum('response' in e and 'error' in e for e in events),
      'reported_cache_responses':len(reported),'missing_cache_responses':len(events)-len(reported),
      'hit_tokens':hit,'miss_tokens':miss,'weighted_hit_rate':hit/(hit+miss) if hit+miss else None,
      'prompt_tokens':sum(e.get('response',{}).get('usage',{}).get('prompt_tokens',0) for e in events),
      'completion_tokens':sum(e.get('response',{}).get('usage',{}).get('completion_tokens',0) for e in events)}
hit=sum(x['hit_tokens'] for x in stages.values());miss=sum(x['miss_tokens'] for x in stages.values())
write(TOP/'CACHE_USAGE.json',{'definition':'sum consistent reported prompt_cache_hit_tokens / sum(hit+miss); schema failures still incur tokens and remain counted',
 'stages':stages,'overall':{'responses':len(all_events),'hit_tokens':hit,'miss_tokens':miss,'weighted_hit_rate':hit/(hit+miss)},
 'prices_and_currency_cost':'not estimated; no current pricing source queried'})
gate=read(TOP/'EXECUTION_GATE.json');gate['final_G2']={'planned':120,'valid':75,'invalid':45,'valid_rate':75/120}
write(TOP/'EXECUTION_GATE.json',gate)
for name in ['one_step_acquisition','transition_replan','three_round_loop']:
    base=TOP/name;base.mkdir(exist_ok=True)
    write(base/'NOT_RUN.json',{'status':'not_run','reason':'G2 frozen Actor response contract valid rate 75/120=62.5% <80% integrity threshold',
      'gate_file':'../EXECUTION_GATE.json','performance_gate':False,'model_calls':0,'tool_calls':0,
      'draft_code_status':'prepared only; not execution-validated','future_freeze_required':True})
    (base/'RESULTS.md').write_text('# Not run — execution integrity gate\n\nG2 yielded 75/120 valid Actor objects (62.5%), below the task’s 80% execution integrity threshold. Root cause: the harness omitted an explicit flat action-object response contract. No performance/effect threshold caused this stop. No calls, rollouts or evidence acquisition from this stage exist. Prepared runner/selection code is unexecuted and must receive a new freeze before use. See ../research_decision/INTERFACE_FAILURE.md and ../EXECUTION_GATE.json.\n')
    (base/'PROTOCOL.md').write_text('# Planned stage, not frozen for execution\n\nThe intended design remains in ../PROTOCOL.md. This stage was not started because G2 failed the execution integrity gate. No zero-valued performance metric should be inferred from its absence.\n')
# Validate the actual immutable material, historical sources and every request.
checks={}
bf=read(TOP/'bank/freeze.json');checks['bank_files']=all(sha(TOP/'bank'/p)==h for p,h in bf['files'].items())
checks['historical_sources']=all(sha(ROOT/p)==h for p,h in bf['history_hashes'].items())
checks['audit_files']=all(sha(TOP/p)==h for p,h in bf['audit_hashes'].items())
for name in ['goal_review','research_decision']:
    f=read(TOP/name/'freeze.json');req=read(TOP/name/'REQUESTS.json');out=read(TOP/name/'outputs.json')
    checks[name+'_inputs']=sha(TOP/name/'REQUESTS.json')==f['requests_sha256'] and all(digest(x['request'])==x['request_sha256'] for x in req)
    checks[name+'_frozen_files']=all(sha(ROOT/p)==h for p,h in f['files'].items())
    checks[name+'_one_response_per_request']=len(out)==len(req)==len({(x['case_id'],x['arm']) for x in out})
    checks[name+'_same_request_hashes']={(x['case_id'],x['arm'],x['request_sha256']) for x in req}=={(x['case_id'],x['arm'],x['request_sha256']) for x in out}
checks['goal_input_isolation']=all(set(json.loads(x['request']['messages'][1]['content']))=={'Original Question','Verified Claims'} for x in read(TOP/'goal_review/REQUESTS.json'))
req=read(TOP/'research_decision/REQUESTS.json');groups=collections.defaultdict(list)
for x in req:
    v=json.loads(x['request']['messages'][1]['content']);v.pop('Goal Residual',None);v.pop('Persisted historical Gap',None);groups[x['case_id']].append(digest(v))
checks['g2_common_context_equal']=all(len(v)==3 and len(set(v))==1 for v in groups.values())
checks['historical_tracked_files_unchanged']=all(p.startswith('experiments/goal_residual_control/') for p in subprocess.check_output(['git','diff','--name-only','2d0c55995badd14ab4bc8241ca9caa97a1eef3a1','HEAD'],cwd=ROOT,text=True).splitlines())
checks['no_tool_stage_started']=not any((TOP/p/'tool_events.jsonl').exists() for p in ['one_step_acquisition','transition_replan','three_round_loop'])
assert all(checks.values()),checks
write(TOP/'INTEGRITY_CHECKS.json',{'checked_utc':now(),'checks':checks,'model_calls':160,'model_responses':160,'tool_calls':0,
 'qualified_note':'Source-backed diagnostic replay and a single reviewer, not full native trajectory replication. Passing archival checks does not cure the G2 interface failure.'})
print(json.dumps(stages,indent=2));print('integrity checks',len(checks),'PASS')
