"""Source reconstruction and denominator checks; no network or paid calls."""
from collections import Counter
import io
import re
import unittest
from .common import *
from .prepare_controls import summarize
from .prepare import build_schedule
from experiments.ephemeral_obligation_decomposition.source_units import span_check

def check():
    source=read(P/'e0_reference/STATE_SOURCE.json');assert sha(ROOT/source['source'])==source['sha256']
    old={r['case_id']:r for r in read(ROOT/source['source'])};cases=bank();qs=questions()
    assert len(cases)==27 and len({c['qid'] for c in cases.values()})==10
    for sid,c in cases.items():
        assert c['question']==old[sid]['belief']['question']==qs[str(c['qid'])]['question']
        assert c['claims']==[{'claim_id':v['claim_id'],'statement':v['statement']} for v in old[sid]['claims']]
        assert c['claims_sha256']==digest(c['claims'])
    frozen=read(P/'e0_addressability/SKELETON_FREEZE.json')
    for name,h in {**frozen['files'],**frozen['read_only_sources']}.items():assert sha(ROOT/name)==h
    for arm in ('A0','D1','D2'):
        for q,sk in skeletons(arm).items():
            assert sk['question_sha256']==qs[q]['question_sha256']
            assert [n['requirement_id'] for n in sk['requirements']]==[f'R{i+1}' for i in range(len(sk['requirements']))]
            assert all(span_check(s,qs[q]['source_units'])['valid'] for n in sk['requirements'] for s in n['source_spans'])
            if arm!='A0':
                assert sk['replicate']==1 and sha(ROOT/sk['source'])==sk['source_sha256']
                oldnodes=read(ROOT/sk['source'])['output']['requirements']
                assert sk['requirements']==[{'requirement_id':f'R{i+1}',**n} for i,n in enumerate(oldnodes)]
    gold=read(P/'e1_alignment/GOLD_MASKS.json');assert len(gold)==54
    assert {(r['case_id'],r['skeleton_arm']) for r in gold}=={(sid,a) for sid in cases for a in ('A0','A1')}
    counts={a:Counter() for a in ('A0','A1')}
    for r in gold:
        c=cases[r['case_id']];nodes=runtime_nodes(str(c['qid']),r['skeleton_arm']);cids={x['claim_id'] for x in c['claims']}
        assert r['claims_sha256']==digest(c['claims']) and r['skeleton_sha256']==digest(nodes)
        assert set(r['requirements'])=={n['requirement_id'] for n in nodes}
        for v in r['requirements'].values():
            counts[r['skeleton_arm']][v['status']]+=1
            assert v['status'] in STATUSES and set(v['contributing_claims'])<=cids and set(v['reference_binding_context'])<=cids
            for group in v['acceptable_full_support_groups']+v['acceptable_partial_support_groups']:
                assert group and set(group)<=set(v['contributing_claims'])
            if v['status']=='fully_supported':assert v['acceptable_full_support_groups']
            if v['status']=='partially_supported':assert v['acceptable_partial_support_groups'] and not v['acceptable_full_support_groups']
            if v['status']=='unsupported':assert not v['contributing_claims'] and not v['acceptable_full_support_groups'] and not v['acceptable_partial_support_groups']
    labels=read(P/'e0_addressability/ADDRESSABILITY.json');assert len(labels)==54
    metrics=read(P/'e0_addressability/METRICS.json')
    for arm in ('D1','D2'):
        assert metrics[arm]['overall']==summarize([r for r in labels if r['skeleton_arm']==arm])
    for r in labels:assert r['gold_obligation']==old[r['case_id']]['gold_obligation']
    for stage,section in zip(STAGES,(28,52)):
        prompt=re.search(r'# '+str(section)+r'\. .*?```text\n(.*?)```',(P/'TASK.md').read_text(),re.S).group(1)
        assert (P/'prompts'/f'{stage}.txt').read_text()==prompt
        assert read(P/stage/'SCHEDULE.json')==build_schedule(stage)
        assert not (P/stage/'calls').exists() and not (P/stage/'RUN.json').exists()
    history=read(P/'analysis/HISTORICAL_HASHES.json')
    for name,h in history.items():assert sha(ROOT/name)==h
    # Every old tracked experiment byte is also identical to the remote source anchor.
    changed=git('diff','--name-only','7fdb048','--','experiments').splitlines()
    assert all(s.startswith(rel(P)+'/') for s in changed)
    return {'status':'PASS','natural_states':27,'unique_questions':10,'gold_masks':54,'addressability_judgments':54,
      'Gold_node_counts_per_replicate':{a:dict(v) for a,v in counts.items()},
      'planned_node_cells':{a:2*sum(v.values()) for a,v in counts.items()},
      'E1_planned':108,'conditional_E2':108,'all_sources_and_prompts_reconstructed':True,
      'historical_files_unchanged':len(history),'real_requests':0,'real_model_outputs':0,
      'authorization_status':'PENDING_TASK_SECTION_70','reviewer_independence':'Single familiar reviewer; construction order audited, no independent-reviewer claim'}

def main():
    result=check()
    from . import test_contracts
    output=io.StringIO();suite=unittest.defaultTestLoader.loadTestsFromModule(test_contracts)
    run=unittest.TextTestRunner(stream=output,verbosity=1).run(suite)
    write(P/'analysis/OFFLINE_TESTS.json',{'passed':run.wasSuccessful(),'tests_run':run.testsRun,
      'failures':len(run.failures),'errors':len(run.errors),'transcript':output.getvalue(),'network_calls':0,
      'scope':'Fake HTTP only via httpx.MockTransport in temporary directories; no fake result artifacts in experiment calls directories.'})
    assert run.wasSuccessful()
    write(P/'analysis/OFFLINE_AUDIT.json',result)
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
