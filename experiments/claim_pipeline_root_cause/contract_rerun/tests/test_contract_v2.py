import asyncio,copy,json,subprocess
from pathlib import Path
import httpx,jsonschema,pytest
from experiments.claim_pipeline_root_cause import harness as old
from experiments.claim_pipeline_root_cause.contract_rerun import contracts as c
from experiments.claim_pipeline_root_cause.contract_rerun.transport import Transport

BASE_HEAD='99fbe47b9a6fa1bcfe628cb801cbd8e1ebcb29c5'
def window(ref='W1'):
    return {'window_ref':ref,'doc_ref':'D1','title':'Title','url':'https://example.invalid','text':'Unmodified observed content.',
        'date':'2000-01-01','source_window_ref':'w_CANARY','docid':'PRIVATE_DOCID','document_sha256':'PRIVATE_SHA','text_sha256':'PRIVATE_TEXT_SHA','offset':42,'end_char':88}
def packet():return {'packet_id':'TEST','qid':'TEST','split':'D','OneGap':'GAP_CANARY','C':[{'statement':'C_CANARY'}],'Observation':[window()],'Q':'Q_CANARY'}
def output(ref='W1'):return {'findings':[{'statement':'Test statement','evidence_refs':[ref]}]}
def config():return old.read(c.HERE/'CONFIG_V2.json')

@pytest.mark.parametrize('field',['window_ref','doc_ref','title','url','text'])
def test_public_fields_exact(field):assert c.semantic_evidence_view(window())[field]==window()[field]

@pytest.mark.parametrize('field',['source_window_ref','docid','document_sha256','text_sha256','offset','end_char'])
def test_private_fields_absent(field):assert field not in c.semantic_evidence_view(window())

def test_optional_semantic_date_not_enriched_or_mutated():
    w=window();before=copy.deepcopy(w);v=c.semantic_evidence_view(w);assert w==before and v['date']==w['date']
    del w['date'];assert 'date' not in c.semantic_evidence_view(w)

@pytest.mark.parametrize('role',sorted(c.CLAIM_ROLES))
@pytest.mark.parametrize('ref,valid',[('W1',True),('W12',True),('w_abc',False),('D1',False),('C3',False),('R1',False),('W0',False),('W01',False)])
def test_static_ref_schema(role,ref,valid):
    schema=c.ref_array(c.schema_for(role),role);validator=jsonschema.Draft202012Validator(schema)
    assert validator.is_valid([ref])==valid

def test_dynamic_enum_and_independent_membership_reject_unseen():
    payload={'Evidence':[c.semantic_evidence_view(window('W3'))]}
    role='a2_evidence_formulator';refs=c.ref_array(c.schema_for(role,payload),role)
    assert refs['items']['enum']==['W3']
    with pytest.raises(jsonschema.ValidationError):c.validate(role,output('W999'),payload)
    with pytest.raises(ValueError):c.validate_membership(role,output('W999'),payload)
    with pytest.raises(jsonschema.ValidationError):c.validate(role,{'findings':[{'statement':'x','evidence_refs':['W3','W3']}]},payload)

def test_schema_only_reference_contract_changes():
    for role in c.CLAIM_ROLES:
        previous=old.read(c.BASE/'schemas'/f'{role}.json');new=c.schema_for(role)
        oldrefs=copy.deepcopy(c.ref_array(previous,role));r=c.ref_array(new,role);r.clear();r.update(oldrefs)
        assert new==previous
    assert (c.HERE/'schemas/a2_selector.json').read_bytes()==(c.BASE/'schemas/a2_selector.json').read_bytes()

def test_all_arm_information_domains_and_full_evidence_agree():
    p=packet();pub=c.semantic_evidence_view(p['Observation'][0]);roles=['a0_current_reader','a1_no_c_reader','a2_selector']
    payloads={r:c.project_payload(r,old.inputs(r,p)) for r in roles}
    assert 'C' in payloads[roles[0]] and 'C' not in payloads[roles[1]] and {'C','OneGap'}<=payloads[roles[2]].keys()
    for v in payloads.values():assert v['Observation']==[pub]
    selected={'selections':[{'window_ref':'W1','reason':'REASON_CANARY'}]}
    f=c.project_payload('a2_evidence_formulator',old.inputs('a2_evidence_formulator',p,selected=selected))
    assert f=={'Evidence':[pub]}
    for secret in ['GAP_CANARY','C_CANARY','Q_CANARY','REASON_CANARY','PRIVATE_DOCID','PRIVATE_SHA','w_CANARY']:assert secret not in old.canonical(f)

@pytest.mark.parametrize('group',['bank','prompts','rubric','thresholds','run001','historical_conclusion'])
def test_historical_inputs_byte_identical(group):
    groups={'bank':list((c.BASE/'bank').rglob('*')),'prompts':list((c.BASE/'prompts').glob('*.txt')),
        'rubric':[c.BASE/'REVIEW_RUBRIC.md'],'thresholds':[c.BASE/'HYPOTHESES.md',c.BASE/'PROTOCOL.md',c.BASE/'metrics.py'],
        'run001':list((c.BASE/'e1/run001').rglob('*')),'historical_conclusion':[c.BASE/'ROOT_CAUSE_CONCLUSION.md']}
    for p in groups[group]:
        if p.is_file() and '__pycache__' not in p.parts:
            assert p.read_bytes()==subprocess.check_output(['git','show',BASE_HEAD+':'+str(p.relative_to(c.ROOT))],cwd=c.ROOT)

def test_old_eight_failures_still_rejected_and_alias_removed():
    audit=old.read(c.BASE/'e1/CONTRACT_FAILURE_AUDIT.json');n=0
    for f in audit['failure_details']:
        if not f['attempted']:continue
        req=old.read(c.BASE/f['request_path']);private=json.loads(req['request']['messages'][-1]['content']);public=c.project_payload(f['role'],private)
        with pytest.raises(Exception):c.validate(f['role'],f['raw_output'],public)
        for alias in f['invalid_refs']:assert alias not in old.canonical(public)
        n+=1
    assert n==8

def test_fresh_full_dag_wire_surface_and_budget(tmp_path):
    async def go():
        calls=[]
        async def respond(req):
            data=json.loads(req.content);p=json.loads(data['messages'][-1]['content']);calls.append(p)
            for w in p.get('Observation',p.get('Evidence',[])):assert set(w)<=set(c.FIELDS)|{'date'}
            assert all(x not in p for x in ['annotations','split','qid','historical_candidates'])
            refs=[w['window_ref'] for w in p.get('Observation',p.get('Evidence',[]))]
            val={'selections':[{'window_ref':refs[0],'reason':'x'}]} if data['messages'][0]['content'].startswith('Select zero') else output(refs[0])
            return httpx.Response(200,json={'model':'deepseek-flash','choices':[{'finish_reason':'stop','message':{'content':json.dumps(val),'reasoning_content':'mock'}}]})
        port=Transport(config(),tmp_path/'run','E1',mock_transport=httpx.MockTransport(respond),account_available=72)
        results=await old.run_e1(port,old.bank(['D','H_diagnostic']));await port.close()
        assert len(calls)==96 and len(results)==72 and all(r['status']=='ok' for r in results)
        assert len(list((tmp_path/'run/calls').glob('*.private_payload.json')))==96
        with pytest.raises(ValueError):await old.run_e1(port,[{'split':'H_confirmation'}])
        with pytest.raises(PermissionError):await port.call('not_authorized','g1_evidence_inventory',{'Evidence':[window()]},{})
    asyncio.run(go())

def test_empty_selection_skips_formulation():
    class Empty:
        def __init__(self):self.count=0
        async def call(self,*args):self.count+=1;return {'selections':[]}
    async def go():
        p=Empty();r=await old.construct(p,packet(),'A2');assert r['status']=='ok' and r['findings']==[] and p.count==1
    asyncio.run(go())

def test_namespace_failure_halts_without_mapping_or_retry(tmp_path):
    async def go():
        calls=0
        async def bad(req):
            nonlocal calls
            calls+=1;return httpx.Response(200,json={'model':'deepseek-flash','choices':[{'finish_reason':'stop','message':{'content':json.dumps(output('w_CANARY'))}}]})
        port=Transport(config(),tmp_path/'run','E1',mock_transport=httpx.MockTransport(bad),account_available=1)
        payload=old.inputs('a0_current_reader',packet())
        responses=await asyncio.gather(*(port.call(str(i),'a0_current_reader',payload,{}) for i in range(3)),return_exceptions=True)
        stats=await port.close();assert calls==1 and stats['unsent']==2 and all(isinstance(x,Exception) for x in responses)
        assert 'w_CANARY' in (tmp_path/'run/calls/0.response.body').read_text()
        assert not (tmp_path/'run/calls/0.parsed.json').exists()
    asyncio.run(go())
