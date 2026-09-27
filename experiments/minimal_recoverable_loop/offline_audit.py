"""Read-only preparation audit; no HTTP, credentials, GPU or retrieval."""
import re
from .common import *
from .select_bank import skeleton
from .requests import writer_jobs

def check():
    bank=read(P/'e0_reference/ADMISSION_BANK.json');refs=read(P/'e0_reference/ADMISSION_REFERENCE.json')
    assert len(bank)==len(refs)==53 and len({r['qid'] for r in bank})==20
    source_ids={r['source_id'] for r in bank};assert len(source_ids)==53
    reference={r['source_id']:r for r in refs};question_rows={r['qid']:r for r in read(P/'e0_reference/QUESTION_SKELETONS.json')}
    for r in bank:
        assert r['observation_sha256']==text_hash(r['source_observation']['text'])
        assert r['question_sha256']==text_hash(r['question'])
        assert question_rows[r['qid']]['Q']==r['question']
        assert question_rows[r['qid']]['R']==skeleton(r['question'])
        p=r['provenance'];assert sha(ROOT/p['path'])==p['sha256']
        u=p['upstream'];assert sha(ROOT/u['path'])==u['sha256']
        if r['selection_family']=='task_named_semantic_risks':
            old=read(ROOT/u['path'])['observations'][u['observation_index']]
            assert all(old[k]==v for k,v in r['source_observation'].items())
        else:
            old=next(x for x in read(ROOT/p['path']) if x['case_id']==p['row_id'])
            assert all(old['observation'][k]==v for k,v in r['source_observation'].items())
        ref=reference[r['source_id']]
        assert ref['observation_sha256']==r['observation_sha256']
        for a in ref['acceptable_claim_atoms']:
            start=a['source_anchor_start'];assert r['source_observation']['text'][start:start+len(a['source_anchor'])]==a['source_anchor']
        req=ref['relevant_requirement'];assert req in question_rows[r['qid']]['R']
        assert req['text']==r['question'][req['source_start']:req['source_end']]
    assert sum(len(r['acceptable_claim_atoms']) for r in refs)==56
    exact=read(P/'e1_admission/WRITER_REQUESTS.json');assert exact==writer_jobs() and len(exact)==106
    forbidden={'H','hypothesis','hypotheses','C','claims','gold','acceptable_claim_atoms','forbidden_upgrades','answer','Trace','Residual'}
    for j in exact:
        req=j['request'];assert digest(req)==j['request_sha256']
        inp=json.loads(req['messages'][1]['content']);assert not (set(inp)&forbidden)
        assert set(inp)=={'original_question','relevant_requirement','source_id','source_observation'}
        assert req['model']=='deepseek-flash' and req['temperature']==0 and req['response_format']=={'type':'json_object'}
        assert 'max_tokens' not in req and 'tools' not in req
    task=(P/'TASK.md').read_text()
    for num,name in [(11,'writer'),(13,'admission'),(19,'actor'),(27,'closure'),(34,'hypothesis'),(39,'answer')]:
        section=task.split('# '+str(num)+'.',1)[1].split('\n# ',1)[0]
        blocks=re.findall(r'```text\n(.*?)\n```',section,re.S)
        assert (P/'prompts'/f'{name}.txt').read_text().rstrip('\n') in blocks
    selection=read(P/'e0_reference/FRESH_SELECTION.json');fresh=read(P/'e0_reference/FRESH_QUESTIONS.json')
    assert len(fresh)==selection['actual']==10
    assert [r['qid'] for r in fresh]==selection['selected_qids']
    exposure=read(P/'e0_reference/EXPOSURE_AUDIT.json')
    assert sha(ROOT/exposure['corpus'])==exposure['corpus_sha256']
    assert not set(selection['selected_qids'])&set(exposure['exposure_provenance'])
    for r in fresh:assert text_hash(r['Q'])==r['question_sha256']
    for r in read(P/'e0_reference/RECOVERY_COHORT.json')['sources']:assert sha(ROOT/r['path'])==r['sha256']
    for r in read(P/'e0_reference/CLOSURE_COHORT.json')['selected']:assert sha(ROOT/r['path'])==r['sha256']
    assert not list((P/'e1_admission').glob('*/calls/*.attempt.json'))
    return {'status':'PASS','scope':'offline preparation and invariants; no empirical model gate result',
            'checked_head':git('rev-parse','HEAD'),'source_observations':53,'qid_count':20,'gold_semantic_atoms':56,
            'recall_slots':112,'actual_writer_requests':106,'fresh_qids':10,
            'history_files_unchanged':verify_history(),'actual_API_calls':0,'actual_retrieval_calls':0,
            'all_sources_match_historical_bytes':True,'all_reference_anchors_exact':True,
            'all_QR_source_anchors_exact':True,'base_task_prompts_verbatim':True,'format_only_schema_appendix_disclosed':True,
            'writer_inputs_exclude_H_and_gold':True,'requests_recompile_identically':True,'future_semantic_stage_labels_not_fabricated':True}

if __name__=='__main__':print(json.dumps(check(),indent=2))
