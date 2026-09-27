"""Offline preparation; immutable inputs for both conditional stages."""
import argparse
import re
from .common import *
from .source_units import split_units, span_check
from experiments.obligation_context_sufficiency.prepare import credential
def request_for(c,arm):
    return {'model':'deepseek-flash','temperature':0,'stream':False,'response_format':{'type':'json_object'},
      'messages':[{'role':'system','content':(P/'prompts'/PROMPTS[arm]).read_text()},
                  {'role':'user','content':json.dumps(input_for(c),ensure_ascii=False)}]}
def preflight(jobs,cases,config,stage,check_paths=True):
    assert stage in STAGES
    assert config['endpoint']=='https://api.deepseek.com/chat/completions'
    assert config['model']=='deepseek-flash' and config['temperature']==0 and config['max_retries']==0
    assert config['max_workers']==8 and config['replicates']==2 and config['max_tokens_policy']=='omit'
    assert config['response_format']=={'type':'json_object'}
    arms=ARMS if stage==STAGES[0] else ('D0','D2')
    expected={(q,a,r) for q in cases for a in arms for r in (1,2)};seen=set()
    for j in jobs:
        ident=j['qid'],j['arm'],j['replicate'];assert ident not in seen;seen.add(ident)
        assert j['id']==f"{j['arm']}__Q{j['qid']}__R{j['replicate']}"
        r=j['request'];assert r==request_for(cases[j['qid']],j['arm'])
        assert digest(r)==j['request_sha256']
        assert 'json' in '\n'.join(m['content'] for m in r['messages']).lower()
        assert not any(k in r for k in ('tools','tool_choice','max_tokens','max_completion_tokens','api_key','Authorization'))
        payload=json.loads(r['messages'][1]['content']);assert set(payload)=={'Original Question','Addressable Source Units'}
        assert cases[j['qid']]['source_units']==split_units(cases[j['qid']]['question'])
        if check_paths:
            for suffix in ('attempt','request','response','result'):assert not (P/stage/'calls'/f"{j['id']}.{suffix}.json").exists()
    assert seen==expected
    return {'status':'PASS','planned':len(jobs),'exact_cross_product':True,'input_whitelist':'Original Question + mechanical Source Units only','zero_network_calls':True,'literal_json_all':True}
def prepare():
    task=(P/'TASK.md').read_text()
    for a,n in zip(ARMS,(15,17,19)):
        prompt=re.search(r'# '+str(n)+r'\. .*?```text\n(.*?)```',task,re.S).group(1)
        write(P/'prompts'/PROMPTS[a],prompt)
    config=read(ROOT/'experiments/dynamic_local_obligation/CONFIG.json')
    config.update(planned_calls=60,maximum_total_calls_if_E1_pass=108,
      paid_authorization='Prior user explicitly authorized API calls and subsequent stages; this task authorizes 60 E1 requests plus exactly 48 E2 requests only if the frozen D2 and comparison gates pass. No extra canary, retries, repairs, replacement, prompt revisions or downstream experiment calls.')
    write(P/'CONFIG.json',config)
    checks=[]
    for stage in STAGES:
        cases=bank(stage);jobs=[]
        for q,c in cases.items():
            for a in (ARMS if stage==STAGES[0] else ('D0','D2')):
                for r in (1,2):
                    req=request_for(c,a);jobs.append(dict(id=f'{a}__Q{q}__R{r}',qid=q,arm=a,replicate=r,request=req,request_sha256=digest(req)))
        jobs.sort(key=lambda j:digest(['skeleton-schedule-v1',stage,j['id']]))
        write(P/stage/'SCHEDULE.json',jobs);checks.append(preflight(jobs,cases,config,stage))
    credential()
    write(P/'analysis/PROVIDER_PREFLIGHT.json',{'stages':checks,'credential_available':True,'credential_logged':False,'auth':'First formal scheduled call; no extra canary. Bearer header only; no redirects; transport retries=0. Model identity checked on every response.'})
    history={s:sha(ROOT/s) for s in git('ls-files','experiments').splitlines() if s and not s.startswith(rel(P)+'/') and (ROOT/s).is_file()}
    write(P/'analysis/HISTORICAL_HASHES.json',history)
    write(P/'e2_fresh/STATUS.json',{'status':'FROZEN_NOT_AUTHORIZED_UNTIL_E1_GATE_PASS','planned':48,'fresh_questions_and_references_frozen_before_E1':True})
def freeze():
    assert not any((P/s/'calls').exists() for s in STAGES)
    refs=read(P/'e0_reference/REFERENCE_TASK_STRUCTURE.json');assert set(refs)==set(bank())
    for q,ref in refs.items():
        assert ref['qid']==q
        assert all(ref.get(k) for k in ('material_units','critical_invariants','dependency_checkpoints','forbidden_inferences','answer_target'))
        for items in (ref['material_units'],ref['critical_invariants'],ref['dependency_checkpoints']):
            for item in items:
                assert all(span_check(s,bank()[q]['source_units'])['valid'] for s in item['source_spans'])
    for s in STAGES:preflight(read(P/s/'SCHEDULE.json'),bank(s),read(P/'CONFIG.json'),s)
    assert read(P/'analysis/OFFLINE_TESTS.json')['passed']
    files={rel(p):sha(p) for p in sorted(P.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name!='FREEZE.json'}
    write(P/'FREEZE.json',{'base_commit':git('rev-parse','HEAD'),'files':files,'planned_E1':60,'conditional_E2':48,
       'gates':read(P/'GATES.json'),'failure_policy':'All planned slots in denominator; no retries, repair, replacement or resume. Provider contract/access/billing errors halt unsent queue. E1 fail stops E2. No downstream experiment.'})
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['prepare','freeze']);globals()[p.parse_args().mode]()
