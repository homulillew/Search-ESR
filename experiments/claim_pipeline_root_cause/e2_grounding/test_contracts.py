import asyncio
import json
from pathlib import Path
import httpx
import pytest
from experiments.claim_pipeline_root_cause.harness import digest, inputs, file_hash, freeze_e2_candidates
from experiments.claim_pipeline_root_cause.contract_rerun.contracts import canonical, validate_membership
from experiments.claim_pipeline_root_cause.e2_grounding.contracts import HERE, BASE, read, request, project_payload, validate, schema_for
from experiments.claim_pipeline_root_cause.e2_grounding.runner import run_e2, make_plan
from experiments.claim_pipeline_root_cause.e2_grounding.transport import Transport, accounting

def bank():return read(HERE/'CANDIDATE_BANK.json')
def config():return read(HERE/'CONFIG.json')

def response(value,**kwargs):
    raw={'id':'mock','model':'deepseek-flash','choices':[{'finish_reason':'stop','message':{'content':json.dumps(value),'reasoning_content':'offline'}}],
         'usage':{'prompt_tokens':10,'completion_tokens':2,'total_tokens':12,'prompt_cache_hit_tokens':4,'prompt_cache_miss_tokens':6}}
    raw.update(kwargs);return httpx.Response(200,json=raw)

def test_bank_exact_and_no_confirmation():
    b=freeze_e2_candidates(read(BASE/'contract_rerun/review/REVIEWED.json'),read(BASE/'bank/historical_candidates.json'))
    assert b==bank() and b['calls']==85 and b['inventory_count']==15
    assert {p['split'] for p in b['pairs']}=={'D','H_diagnostic'}
    assert len(make_plan(b['pairs'],config()))==85

def test_actual_bank_information_isolation_and_prompt_identity():
    freeze=read(HERE/'BANK_FREEZE.json')
    for p in bank()['pairs']:
        for role in ('g0_current_grounding','g1_evidence_inventory'):
            payload=inputs(role,candidate=p['candidate'],windows=p['Evidence']);wire=request(role,payload,config())
            public=json.loads(wire['messages'][-1]['content'])
            assert set(public)==({'Evidence'} if role=='g1_evidence_inventory' else {'candidate','Evidence'})
            for private,visible in zip(p['Evidence'],public['Evidence']):
                assert visible=={k:v for k,v in private.items() if k in ('window_ref','doc_ref','title','url','text','date')}
                assert private['text']==visible['text']
                assert all(k not in visible for k in ('source_window_ref','docid','hash','offset','end_char'))
            if role=='g1_evidence_inventory':
                assert p['pair_id'] not in canonical(wire)
                assert schema_for(role,public)['properties']['facts']['items']['properties']['evidence_refs']['items']['enum']==sorted({w['window_ref'] for w in p['Evidence']})
            else:assert set(p['candidate']['evidence_refs']) <= {w['window_ref'] for w in p['Evidence']}
            assert wire['messages'][0]['content'].split('\nReturn one JSON object matching this schema:\n')[0].encode()==(BASE/'prompts'/f'{role}.txt').read_bytes()
    for role in freeze['prompts']:assert file_hash(BASE/'prompts'/f'{role}.txt')==freeze['prompts'][role]
    for role,payload in [('g1_evidence_inventory',{'Evidence':[],'candidate':{}}),('g1_candidate_coverage',{'candidate':{},'SourceCommitmentInventory':{},'Evidence':[]})]:
        with pytest.raises(ValueError):project_payload(role,payload)

@pytest.mark.parametrize('ref',['w_private','W999999'])
def test_inventory_ref_rejected_independently(ref):
    payload=project_payload('g1_evidence_inventory',inputs('g1_evidence_inventory',windows=bank()['pairs'][0]['Evidence']))
    val={'facts':[{'statement':'test','evidence_refs':[ref]}]}
    with pytest.raises(Exception):validate('g1_evidence_inventory',val,payload)
    with pytest.raises(ValueError):validate_membership('g1_evidence_inventory',val,payload)

def test_full_dag_freeze_and_parallelism(tmp_path):
    async def go():
        roles=[];started=0;barrier=asyncio.Event()
        async def handle(req):
            nonlocal started
            data=json.loads(req.content);payload=json.loads(data['messages'][-1]['content'])
            started+=1
            if started==50:barrier.set()
            if 'SourceCommitmentInventory' not in payload:
                await asyncio.wait_for(barrier.wait(),10)
            if set(payload)=={'Evidence'}:
                value={'facts':[{'statement':'observed fact','evidence_refs':[payload['Evidence'][0]['window_ref']]}]};roles.append('I')
            else:
                value={'verdict':'supported','reason':'offline test'}
                roles.append('G1' if 'SourceCommitmentInventory' in payload else 'G0')
                if 'SourceCommitmentInventory' in payload:
                    assert any(read(f)['inventory']==payload['SourceCommitmentInventory'] for f in (tmp_path/'run/inventories').glob('*.json'))
            return response(value)
        port=Transport(config(),tmp_path/'run','E2',mock_transport=httpx.MockTransport(handle),account_available=50)
        rows=await run_e2(port,bank()['pairs']);s=await port.close()
        assert len(rows)==70 and all(r['status']=='ok' for r in rows)
        assert s['attempted']==85 and s['peak_concurrency']==50 and s['halt'] is None
        assert roles.count('I')==15 and roles.count('G0')==roles.count('G1')==35
        assert len(list((tmp_path/'run/inventories').glob('*.json')))==15
        assert s['cache_hit_rate']==.4 and s['complete_consistent_records']==85
        with pytest.raises(FileExistsError):Transport(config(),tmp_path/'run','E2',mock_transport=httpx.MockTransport(handle))
    asyncio.run(go())

@pytest.mark.parametrize('failure',['http429','http503','parse','schema','ref','model','finish','timeout'])
def test_failures_halt_unsent_no_retry(tmp_path,failure):
    async def go():
        n=0
        async def handle(req):
            nonlocal n
            n+=1
            if failure.startswith('http'):return httpx.Response(int(failure[4:]),json={'error':'test'})
            if failure=='parse':return httpx.Response(200,content=b'broken JSON')
            if failure=='schema':return response({'facts':'not list'})
            if failure=='ref':return response({'facts':[{'statement':'test','evidence_refs':['W999999']}]})
            if failure=='model':return response({'facts':[]},model='wrong-model')
            if failure=='finish':return response({'facts':[]},choices=[{'finish_reason':'length','message':{'content':'{}'}}])
            raise httpx.ReadTimeout('offline timeout')
        port=Transport(config(),tmp_path/'run','E2',mock_transport=httpx.MockTransport(handle),account_available=1)
        rows=await run_e2(port,bank()['pairs']);s=await port.close()
        assert n==1 and s['attempted']==1 and s['attempted_failures']==1 and s['halt']
        assert all(r['status']=='failed' for r in rows)
        assert len(list((tmp_path/'run/calls').glob('*.attempt.json')))==1
    asyncio.run(go())

def test_coverage_cannot_precede_freeze(tmp_path):
    async def go():
        async def handle(req):raise AssertionError('network cannot be reached')
        port=Transport(config(),tmp_path/'run','E2',mock_transport=httpx.MockTransport(handle))
        with pytest.raises(FileNotFoundError):
            await port.call('early','g1_candidate_coverage',{'candidate':bank()['pairs'][0]['candidate'],'SourceCommitmentInventory':{'facts':[]}}, {'evidence_key':'missing'})
        s=await port.close();assert s['attempted']==0 and s['halt']
    asyncio.run(go())

def test_usage_inconsistency_is_not_counted_complete():
    assert not accounting(None)['complete']
    assert not accounting({'prompt_tokens':10,'completion_tokens':2,'total_tokens':12,'prompt_cache_hit_tokens':9,'prompt_cache_miss_tokens':6})['complete']

def test_inflight_completes_after_failure(tmp_path):
    async def go():
        barrier=asyncio.Event();seen=0
        async def handle(req):
            nonlocal seen
            seen+=1;n=seen
            if n==2:barrier.set()
            await barrier.wait()
            if n==1:return httpx.Response(503,json={'error':'offline'})
            await asyncio.sleep(.01)
            return response({'verdict':'supported','reason':'already inflight'})
        port=Transport(config(),tmp_path/'run','E2',mock_transport=httpx.MockTransport(handle),account_available=2)
        payload=inputs('g0_current_grounding',candidate=bank()['pairs'][0]['candidate'],windows=bank()['pairs'][0]['Evidence'])
        out=await asyncio.gather(*(port.call(str(i),'g0_current_grounding',payload,{}) for i in range(3)),return_exceptions=True)
        s=await port.close()
        assert s['attempted']==2 and s['attempted_failures']==1 and s['unsent']==1
        assert out[1]['verdict']=='supported'
    asyncio.run(go())

def test_only_e2_roles_allowed(tmp_path):
    async def go():
        port=Transport(config(),tmp_path/'run','E2',mock_transport=httpx.MockTransport(lambda req: response({})))
        with pytest.raises(PermissionError):await port.call('forbidden','a0_current_reader',{}, {})
        s=await port.close();assert s['attempted']==0
    asyncio.run(go())
