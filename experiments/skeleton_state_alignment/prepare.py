"""Offline schedules, estimates and commit-bound manifests. No network calls."""
import argparse
import math
import re
from .common import *
from .inputs import alignment_input, selection_input, gold_mask, request_for
from .contracts import validate_output
from experiments.obligation_context_sufficiency.prepare import credential

def build_schedule(stage):
    rows=[]
    for c in bank().values():
        for arm in (('A0','A1') if stage==STAGES[0] else ('S0','S1')):
            for rep in (1,2):
                row={k:c[k] for k in ('case_id','state_id','qid')}
                row.update(id=f"{arm}__{c['case_id']}__R{rep}",stage=stage,arm=arm,replicate=rep)
                if stage==STAGES[0]:req=request_for(stage,alignment_input(c,arm))
                elif arm=='S0':req=request_for(stage,selection_input(c,gold_mask(c['case_id'])))
                else:
                    req=None
                    row['mask_source']=f"e1_alignment/calls/A1__{c['case_id']}__R1.result.json"
                row.update(request=req,request_sha256=digest(req) if req else None)
                rows.append(row)
    return sorted(rows,key=lambda j:digest(['skeleton-alignment-mixed-v1',stage,j['id']]))

def prepare():
    task=(P/'TASK.md').read_text()
    for stage,section in zip(STAGES,(28,52)):
        prompt=re.search(r'# '+str(section)+r'\. .*?```text\n(.*?)```',task,re.S).group(1)
        write(P/'prompts'/f'{stage}.txt',prompt)
    config=read(PREV/'CONFIG.json')
    config.pop('paid_authorization')
    config.update(planned_calls=108,planned_E1=108,conditional_E2=108,maximum_total_calls_if_E1_pass=216,
      authorization_policy='TASK section70: new experiment budget requires explicitly applicable user authorization; no inherited authorization.',
      paid_authorization_artifact='AUTHORIZATION.json',selection_mask_projection='requirement_id/status only, identical for Gold and predicted masks')
    write(P/'CONFIG.json',config)
    for s in STAGES:write(P/s/'SCHEDULE.json',build_schedule(s))
    write(P/'e2_selection/STATUS.json',{'status':'FROZEN_CONDITIONAL_NOT_EXECUTED','planned':108,'requires':'E1 A0 AND A1 gates PASS, committed blind review, explicit applicable paid authorization',
       'S1_source':'A1 replicate1; actual requests freeze after E1 pass. Invalid source blocks its two planned slots; no fallback.'})
    try:credential();available=True
    except ValueError:available=False
    write(P/'analysis/PROVIDER_PREFLIGHT.json',{'status':'OFFLINE_PASS' if available else 'CREDENTIAL_MISSING','credential_available':available,
      'credential_logged':False,'network_requests':0,'authentication_verified_this_experiment':False,
      'provider_contract':'Reuse frozen endpoint/JSON request shape; live access not inferred from credential presence.',
      'auth_preflight':'First scheduled request counts as formal replicate. No extra canary. Halt unsent queue on400/401/402/403/404/422.',
      'retries':0,'max_concurrency':8,'timeout_seconds':240,'timeout_semantics':config['timeout_semantics']})
    import tiktoken
    enc=tiktoken.get_encoding('cl100k_base')
    scenarios={}
    old=sorted(r['usage']['completion_tokens'] for stage in ('e1_development','e2_fresh') for p in (PREV/stage/'calls').glob('*.result.json') if (r:=read(p)).get('usage',{}).get('completion_tokens') is not None)
    quant=lambda p:old[min(len(old)-1,math.ceil(p*len(old))-1)]
    for stage in STAGES:
        reqs=[j['request'] for j in read(P/stage/'SCHEDULE.json') if j['request']]
        est=[sum(len(enc.encode(m['content']))+4 for m in r['messages'])+3 for r in reqs]
        scenarios[stage]={'planned_calls':108,'estimated_input_tokens':sum(est)*(2 if stage==STAGES[1] else 1),
          'input_estimate_scope':'E2 S1 uses S0-length proxy; actual model masks not yet known' if stage==STAGES[1] else 'All108 frozen request texts',
          'prompt_range_per_request':[min(est),max(est)],'completion_tokens_at_previous_median':108*quant(.5),
          'completion_tokens_at_previous_p95':108*quant(.95),'completion_tokens_at_observed_65535_tail':108*65535}
    write(P/'analysis/CALL_ESTIMATE.json',{'stages':scenarios,'maximum_requests':216,'max_concurrency':8,'tokenizer':'cl100k_base proxy; not provider-exact',
      'historical_sample_n':len(old),'historical_completion_quantiles':{'p50':quant(.5),'p95':quant(.95),'max':max(old)},
      'tail_note':'Scenarios only, not token or currency ceilings; max_tokens omitted. Reasoning is included in completion.',
      'currency_cost':None,'currency_note':'No price verification; no monetary estimate.'})
    history={s:sha(ROOT/s) for s in git('ls-files','experiments').splitlines() if s and not s.startswith(rel(P)+'/') and (ROOT/s).is_file()}
    write(P/'analysis/HISTORICAL_HASHES.json',history)

def freeze():
    assert all(not (P/s/'calls').exists() for s in STAGES)
    assert read(P/'analysis/OFFLINE_TESTS.json')['passed']
    for s in STAGES:assert read(P/s/'SCHEDULE.json')==build_schedule(s)
    # The provisional conclusion is a report, not an input or scoring artifact.
    # Keep an immutable copy while allowing the final report to cite real results later.
    write(P/'analysis/PREPARED_CONCLUSION.md',(P/'analysis/FINAL_CONCLUSION.md').read_text())
    files={rel(p):sha(p) for p in sorted(P.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name!='FREEZE.json' and p!=P/'analysis/FINAL_CONCLUSION.md'}
    write(P/'FREEZE.json',{'experiment':'skeleton-state-alignment','source_head':'7fdb048e856545facd4acfb590e8cf28c46f1013',
      'preparation_head':git('rev-parse','HEAD'),'oracle_commit':git('rev-parse','81caa52'),'gold_mask_commit':git('rev-parse','4b8e9d8'),
      'files':files,'provider':read(P/'CONFIG.json'),'gates':read(P/'GATES.json'),'planned_E1':108,'conditional_E2':108,
      'stage1_inputs':'Actual108 payloads committed now','stage2_inputs':'Logical108 schedule and S0 payloads frozen now; actual S1 payloads require successful E1 and separate committed EXECUTION_FREEZE before E2 calls.',
      'authorization':'Pending under TASK section70; preparation is not paid authorization.'})

def materialize_e2():
    # This is offline, but is deliberately impossible before the frozen E1 gate.
    from .run import audit
    from .score import calculate_stage, assert_review_sealed
    audit('e1_alignment');assert_review_sealed('e1_alignment')
    metrics=read(P/'e1_alignment/METRICS.json')
    assert metrics==calculate_stage('e1_alignment') and metrics['joint_gate_pass']
    head=git('rev-parse','HEAD')
    metrics_path=P/'e1_alignment/METRICS.json'
    assert subprocess.check_output(['git','show',head+':'+rel(metrics_path)],cwd=ROOT)==metrics_path.read_bytes()
    rows=build_schedule('e2_selection');sources={rel(metrics_path):sha(metrics_path)}
    for row in rows:
        if row['arm']=='S0':continue
        path=P/row['mask_source'];result=read(path)
        assert subprocess.check_output(['git','show',head+':'+rel(path)],cwd=ROOT)==path.read_bytes()
        sources[rel(path)]=sha(path);row['mask_source_sha256']=sha(path)
        if result['valid_output']:
            c=bank()[row['case_id']]
            e1job=next(j for j in read(P/'e1_alignment/SCHEDULE.json') if j['id']==result['id'])
            assert validate_output(result['output'],e1job)
            row['request']=request_for('e2_selection',selection_input(c,result['output']))
            row['request_sha256']=digest(row['request'])
        else:row['blocked_reason']='invalid_A1_replicate1_mask'
    write(P/'e2_selection/EXECUTION_SCHEDULE.json',rows)
    write(P/'e2_selection/EXECUTION_FREEZE.json',{'parent_freeze_sha256':sha(P/'FREEZE.json'),'preparation_head':head,
       'source_files':sources,'execution_schedule_sha256':sha(P/'e2_selection/EXECUTION_SCHEDULE.json'),
       'blocked_slots':sum(j['request'] is None for j in rows),'planned_slots':108,'no_fallback_or_repair':True})

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['prepare','freeze','materialize_e2'])
    globals()[parser.parse_args().mode]()
