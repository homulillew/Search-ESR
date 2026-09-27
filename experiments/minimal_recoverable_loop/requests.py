"""Exact source-only Writer payloads and output-dependent Admission requests."""
from .common import *
from .contracts import excerpt_check, validate_writer, validate_admission

def request(prompt,payload):
    system=(P/'prompts'/f'{prompt}.txt').read_text()
    schema=P/'schemas'/f'{prompt}.json'
    if schema.exists():system+='\n\nOutput contract (format only; no additional keys):\n'+schema.read_text()
    return {'model':'deepseek-flash','messages':[{'role':'system','content':system},
            {'role':'user','content':json.dumps(payload,ensure_ascii=False)}],
            'temperature':0,'stream':False,'response_format':{'type':'json_object'}}

def writer_jobs():
    refs={r['source_id']:r for r in read(P/'e0_reference/ADMISSION_REFERENCE.json')}
    bank=read(P/'e0_reference/ADMISSION_BANK.json')
    rows=[]
    # Two complete, deterministically hash-ordered replicates; no best-of/vote.
    for rep in (1,2):
        for b in sorted(bank,key=lambda b:digest(['minimal-recoverable-writer-v1',rep,b['source_id']])):
            payload={'original_question':b['question'],'relevant_requirement':refs[b['source_id']]['relevant_requirement'],
                     'source_id':b['source_id'],'source_observation':b['source_observation']}
            req=request('writer',payload)
            rows.append({'id':f"W_{b['source_id']}_r{rep}",'phase':'writer','qid':b['qid'],
                         'source_id':b['source_id'],'replicate':rep,'request':req,'request_sha256':digest(req)})
    return rows

def compile_admissions(writer_rows):
    bank={r['source_id']:r for r in read(P/'e0_reference/ADMISSION_BANK.json')}
    jobs=[];ledger=[]
    for row in writer_rows:
        if not row['valid_output']:continue
        assert validate_writer(row['output'])
        src=bank[row['source_id']]
        for i,c in enumerate(row['output']['candidate_claims']):
            cid=f"{row['id']}_C{i+1}"
            valid=excerpt_check(c,src)
            ledger.append({'candidate_id':cid,'writer_id':row['id'],'source_id':row['source_id'],
                           'replicate':row['replicate'],'candidate':c,'exact_excerpt_valid':valid,
                           'mechanical_reject':None if valid else 'excerpt_mismatch_or_source_identity',
                           'atom_reference_ids':[r['atom_id'] for r in next(r for r in read(P/'e0_reference/ADMISSION_REFERENCE.json') if r['source_id']==row['source_id'])['acceptable_claim_atoms']]})
            if not valid:continue
            payload={'candidate_claim':c['statement'],'exact_supporting_excerpt':c['supporting_excerpt'],
                     'source_metadata':{'source_id':src['source_id'],'observed_title':src['source_observation']['title'],
                                        'observed_url':src['source_observation']['url'],'observation_sha256':src['observation_sha256']}}
            req=request('admission',payload)
            jobs.append({'id':f'A_{cid}','phase':'admission','writer_id':row['id'],'candidate_id':cid,
                         'source_id':src['source_id'],'qid':src['qid'],'replicate':row['replicate'],
                         'request':req,'request_sha256':digest(req)})
    return jobs,ledger

def valid_output(value,phase):
    try:return validate_writer(value) if phase=='writer' else validate_admission(value)
    except (TypeError,KeyError,ValueError):return False
