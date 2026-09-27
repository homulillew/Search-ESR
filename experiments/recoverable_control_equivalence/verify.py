"""Independent raw-content recount and provenance checks, no network."""
from collections import Counter
import re
from .common import *
from .e0 import compute
from .selection import build_schedule

def verify():
    result=verify_sources(); rows,times,m=compute()
    assert rows==read(P/'e0_control_equivalence/CONTROL_EQUIVALENT_MASKS.json')
    assert times==read(P/'e0_control_equivalence/RECOVERABILITY.json')
    assert m==read(P/'e0_control_equivalence/METRICS.json')
    source_jobs=read(OLD/'e1_alignment/SCHEDULE.json')
    gold={(g['case_id'],g['skeleton_arm']):g['requirements'] for g in read(OLD/'e1_alignment/GOLD_MASKS.json')}
    raw_counts={a:Counter() for a in ('A0','A1')}
    for j in source_jobs:
        raw=read(OLD/'e1_alignment/calls'/f"{j['id']}.response.json")
        assert raw['status']==200
        body=json.loads(raw['body']); content=json.loads(body['choices'][0]['message']['content'])
        result_row=read(OLD/'e1_alignment/calls'/f"{j['id']}.result.json")
        assert content==result_row['output']; c=raw_counts[j['arm']];g=gold[j['case_id'],j['arm']]
        equal3=[];equal2=[]
        for p in content['requirements']:
            gs=g[p['requirement_id']]['status'];ps=p['status']
            equal3.append(gs==ps);equal2.append((gs==F)==(ps==F))
            c['nodes']+=1;c['semantic_errors']+=gs!=ps;c['binary_errors']+=(gs==F)!=(ps==F)
            c['pred_closed']+=ps==F;c['true_closed']+=ps==F and gs==F
        c['exact3']+=all(equal3);c['exact2']+=all(equal2)
    old=read(OLD/'e1_alignment/METRICS.json')
    for a,c in raw_counts.items():
        mm=m['arms'][a]['metrics'];oldm=old['arms'][a]['metrics']
        assert c['semantic_errors']==mm['counts']['three_way_status_errors']
        assert c['binary_errors']==mm['counts']['binary_control_errors']
        assert c['exact3']==mm['exact_three_way_mask']['numerator']==oldm['exact_state_mask']['numerator']
        assert c['exact2']==mm['exact_binary_mask']['numerator']
        assert metric(c['true_closed'],c['pred_closed'])==mm['closure_precision']
        assert mm['open_requirement_recall']==oldm['residual_recall']
    schedule=read(P/'e1_selection/SCHEDULE.json');assert schedule==build_schedule()
    assert Counter((j['arm'],j['replicate']) for j in schedule)=={('S0',1):27,('S0',2):27,('S1',1):27,('S1',2):27}
    assert (P/'e1_selection/SELECTION_REFERENCE.json').read_bytes()==(OLD/'e2_selection/SELECTION_REFERENCE.json').read_bytes()
    prompt=re.search(r'# 27\. .*?```text\n(.*?)```',(P/'TASK.md').read_text(),re.S).group(1)
    assert (P/'prompts/selection.txt').read_text()==prompt
    by={(j['arm'],j['case_id'],j['replicate']):j for j in schedule}
    differences=[]
    for sid in {j['case_id'] for j in schedule}:
        for a in ('S0','S1'):assert by[a,sid,1]['request']==by[a,sid,2]['request']
        p0=json.loads(by['S0',sid,1]['request']['messages'][1]['content']);p1=json.loads(by['S1',sid,1]['request']['messages'][1]['content'])
        assert p0['Task Skeleton']==p1['Task Skeleton'] and p0['Original Question']==p1['Original Question']
        for payload in (p0,p1):assert set(payload)=={'Original Question','Task Skeleton','Control Mask'}
        if p0['Control Mask']!=p1['Control Mask']:differences.append(sid)
    assert not (P/'e1_selection/calls').exists() and not (P/'e1_selection/RUN.json').exists()
    assert not (P/'e1_selection/METRICS.json').exists() and not (P/'AUTHORIZATION.json').exists()
    return {'status':'PASS',**result,'raw_responses_reparsed':108,'raw_independent_counts':{a:dict(c) for a,c in raw_counts.items()},
        'E0_metrics_reproduced':True,'E1_exact_requests_rebuilt':108,'prompt_exact_from_task':True,
        'selection_reference_byte_identical':True,'symmetric_inputs_except_mask':True,'S0_S1_different_mask_cases':sorted(differences),
        'S1_uses_replicate':1,'no_new_paid_calls':True,'new_authorization_required':True}
if __name__=='__main__':print(json.dumps(verify(),indent=2))
