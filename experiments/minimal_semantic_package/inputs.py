"""Minimal verifier/auditor payloads. Never expose Gold labels or sibling units."""
from .common import *

def references():
    return {r['certificate_id']: r for r in read(P/'e0_reference/SUPPORT_REFERENCES.json')}

def package_payload(package_id, claims):
    pkg = next(p for p in read(P/'e0_reference/GOLD_PACKAGES.json') if p['package_id']==package_id)
    parent = next(p for p in read(P/'e0_reference/UNITS.json') if p['parent_id']==pkg['parent_id'])
    def selected(ids):
        return [{'unit_id': u['unit_id'], 'text': u['text']} for u in parent['units'] if u['unit_id'] in ids]
    return {'target_semantics': selected(pkg['target_unit_ids']),
            'interpretive_context': selected(pkg['interpretive_context_unit_ids']),
            'verified_claims': claims}

def request(kind, payload):
    cfg = read(P/'CONFIG.json')
    return {'model':cfg['model'],'temperature':cfg['temperature'],
            'response_format':cfg['response_format'],
            'messages':[{'role':'system','content':(P/f'prompts/{kind}.txt').read_text()},
                        {'role':'user','content':json.dumps(payload,ensure_ascii=False,indent=2)}]}

def verifier_schedule():
    jobs = []
    for rep in (1, 2):
        for c in references().values():
            req=request('verifier',package_payload(c['package_id'],c['candidate_verified_claims']))
            jobs.append({'id':f"V_{c['certificate_id']}_r{rep}",'stage':'E1V','phase':'verifier',
                         **{k:c[k] for k in ('certificate_id','cell_id','case_id','qid','package_id')},
                         'replicate':rep,'request':req,'request_sha256':digest(req)})
    return jobs

def auditor_job(verifier_job, verifier_result):
    """Only a schema-valid SUPPORTED output instantiates a real auditor request.

    No second approval decision, retry, full ClaimSet restoration, response
    reasoning, original verdict or outside target semantics enter the auditor.
    """
    assert verifier_result['id']==verifier_job['id']
    assert verifier_result['request_sha256']==verifier_job['request_sha256']
    value=verifier_result.get('output')
    if not verifier_result.get('valid_output') or value['verdict']!='SUPPORTED':
        return None
    assert validate(value,verifier_job)
    original=json.loads(verifier_job['request']['messages'][1]['content'])
    selected=set(value['supporting_claim_ids'])
    payload={**original,'verified_claims':[c for c in original['verified_claims'] if c['claim_id'] in selected]}
    req=request('auditor',payload)
    return {**{k:verifier_job[k] for k in ('certificate_id','cell_id','case_id','qid','package_id','replicate')},
            'id':verifier_job['id'].replace('V_','A_',1),'stage':'E1A','phase':'auditor',
            'parent_verifier_id':verifier_job['id'],
            'parent_result_sha256':digest(verifier_result),
            'request':req,'request_sha256':digest(req)}

def id_list(value, allowed):
    return isinstance(value,list) and all(isinstance(x,str) for x in value) and len(value)==len(set(value)) and set(value)<=set(allowed)

def validate(value, job):
    if not isinstance(value,dict):return False
    payload=json.loads(job['request']['messages'][1]['content'])
    target=[u['unit_id'] for u in payload['target_semantics']]
    claims=[c['claim_id'] for c in payload['verified_claims']]
    if job['phase']=='auditor':
        return set(value)=={'uncovered_target_unit_ids'} and id_list(value['uncovered_target_unit_ids'],target)
    if set(value)!={'verdict','supporting_claim_ids','uncovered_target_unit_ids'}:return False
    if not id_list(value['supporting_claim_ids'],claims) or not id_list(value['uncovered_target_unit_ids'],target):return False
    if value['verdict']=='SUPPORTED':
        return bool(value['supporting_claim_ids']) and not value['uncovered_target_unit_ids']
    return value['verdict']=='OPEN' and bool(value['uncovered_target_unit_ids'])
