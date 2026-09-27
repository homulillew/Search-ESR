import asyncio
import copy
import json
from pathlib import Path
import httpx
import pytest
from experiments.claim_pipeline_root_cause import harness as h, metrics as m, transport as t, runner
from llm_chat.recoverable_loop.roles import PROMPTS,schemas

def config():return h.read(h.HERE/'CONFIG.json')
def packet(pid='P_TEST',split='D'):
    return {'packet_id':pid,'qid':pid,'split':split,'context_kind':'synthetic_contract_test_only',
        'OneGap':'GAP_CANARY','C':[{'statement':'C_CANARY'}],
        'Observation':[{'window_ref':'W1','doc_ref':'D1','text':'Natural test text.','title':'Title','url':'https://example.invalid'}],
        'Q':'Q_CANARY','H':'H_CANARY','Trace':'TRACE_CANARY','annotation':'LABEL_CANARY'}
def candidate(i=0):return {'statement':f'Fact {i}','evidence_refs':['W1']}

class Port:
    def __init__(self,fn=None):self.calls=[];self.fn=fn
    async def call(self,ident,role,payload,meta):
        self.calls.append((ident,role,payload,meta));await asyncio.sleep(0)
        value=self.fn(role,payload) if self.fn else (
            {'selections':[{'window_ref':'W1','reason':'REASON_CANARY'}]} if role=='a2_selector' else
            {'facts':[candidate()]} if role=='g1_evidence_inventory' else
            {'verdict':'supported','reason':'test'} if role in ['g0_current_grounding','g1_candidate_coverage'] else {'findings':[candidate()]})
        return h.validate(role,value,payload)

def test_baselines_byte_identical_and_wire_format():
    for stem,key in [('a0_current_reader','reader'),('a1_no_c_reader','reader'),('g0_current_grounding','grounding')]:
        assert (h.HERE/'prompts'/f'{stem}.txt').read_text()==PROMPTS[key]
        assert h.read(h.HERE/'schemas'/f'{stem}.json')==schemas()[key]
    a=h.request('a0_current_reader',h.inputs('a0_current_reader',packet()),config())
    b=h.request('a1_no_c_reader',h.inputs('a1_no_c_reader',packet()),config())
    assert a['messages'][0]==b['messages'][0]
    aa=json.loads(a['messages'][1]['content']);bb=json.loads(b['messages'][1]['content']);aa.pop('C');assert aa==bb

def test_information_domain_canaries_and_exact_evidence():
    p=packet();selector={'selections':[{'window_ref':'W1','reason':'REASON_CANARY'}]}
    v=h.inputs('a2_evidence_formulator',p,selected=selector)
    assert v=={'Evidence':p['Observation']}
    for word in ['GAP_CANARY','C_CANARY','Q_CANARY','H_CANARY','TRACE_CANARY','LABEL_CANARY','REASON_CANARY']:assert word not in h.canonical(v)
    inv=h.inputs('g1_evidence_inventory',windows=p['Observation']);assert set(inv)=={'Evidence'}
    cover=h.inputs('g1_candidate_coverage',candidate=candidate(),inventory={'facts':[candidate()]})
    assert set(cover)=={'candidate','SourceCommitmentInventory'} and 'Natural test text.' not in h.canonical(cover)
    v['Evidence'][0]['text']='mutated copy';assert p['Observation'][0]['text']=='Natural test text.'

def test_new_prompts_generic():
    for name in ['a2_selector','a2_evidence_formulator','g1_evidence_inventory','g1_candidate_coverage']:
        s=(h.HERE/'prompts'/f'{name}.txt').read_text().lower()
        for term in ['euler','memo','letter','q435','albums','sps','dlc','teammate','patient nationality']:assert term not in s

@pytest.mark.parametrize('value',[
    {'findings':[{'statement':'x','evidence_refs':['W999']}]},
    {'findings':[{'statement':' ','evidence_refs':['W1']}]},
    {'findings':[{'statement':'x','evidence_refs':[]}]},
    {'findings':[candidate(i) for i in range(4)]},
    {'findings':[],'repair':'silently ignored'},
])
def test_reader_contract_rejects(value):
    with pytest.raises(Exception):h.validate('a0_current_reader',value,h.inputs('a0_current_reader',packet()))

def test_selector_refs_unique_and_observed():
    for refs in [['W1','W1'],['W999']]:
        with pytest.raises(ValueError):h.validate('a2_selector',{'selections':[{'window_ref':r,'reason':'x'} for r in refs]},h.inputs('a2_selector',packet()))

def test_selector_failure_does_not_formulate_and_empty_is_valid():
    async def go():
        port=Port(lambda role,payload:{'selections':[{'window_ref':'W404','reason':'x'}]})
        r=await h.construct(port,packet(),'A2');assert r['status']=='failed' and len(port.calls)==1
        port=Port(lambda role,payload:{'selections':[]});r=await h.construct(port,packet(),'A2')
        assert r['status']=='ok' and r['findings']==[] and len(port.calls)==1
    asyncio.run(go())

def test_full_e1_dag_call_ceiling_and_reserved_holdout():
    async def go():
        port=Port();rows=await h.run_e1(port,h.bank(['D','H_diagnostic']))
        # Frozen refs differ; a generic synthetic port selects the actual first W.
        assert len(rows)==72
        with pytest.raises(ValueError):await h.run_e1(port,h.bank(['H_confirmation']))
        port=Port(lambda role,p: {'selections':[{'window_ref':p['Observation'][0]['window_ref'],'reason':'x'}]} if role=='a2_selector' else
            {'findings':[{'statement':'Test fact','evidence_refs':[(p.get('Observation') or p['Evidence'])[0]['window_ref']]}]})
        rows=await h.run_e1(port,h.bank(['D','H_diagnostic']))
        assert len(port.calls)==96 and all(r['status']=='ok' for r in rows)
    asyncio.run(go())

def test_e2_inventory_shared_and_candidate_blind():
    async def go():
        port=Port();p=packet()
        pairs=[{'pair_id':str(i),'candidate':candidate(i),'Evidence':p['Observation'],'qid':'1','split':'D','origins':[{'packet_id':'p'}]} for i in range(2)]
        rows=await h.run_e2(port,pairs)
        assert len(rows)==4 and len(port.calls)==5
        calls=[c for c in port.calls if c[1]=='g1_evidence_inventory'];assert len(calls)==1
        assert set(calls[0][2])=={'Evidence'}
        for c in port.calls:
            if c[1]=='g1_candidate_coverage':assert 'Evidence' not in c[2]
    asyncio.run(go())

def test_e3_conditional_components_and_maximum_budget():
    async def go():
        def f(role,payload):
            if role=='a2_selector':return {'selections':[{'window_ref':'W1','reason':'x'}]}
            if role=='g1_evidence_inventory':return {'facts':[candidate(i) for i in range(3)]}
            if role in ['g0_current_grounding','g1_candidate_coverage']:return {'verdict':'supported','reason':'test'}
            return {'findings':[candidate(i) for i in range(3)]}
        packets=[packet(str(i),'H_confirmation') for i in range(12)];port=Port(f)
        decision={'eligible':True,'supported':{'H1':False,'H2':True,'H3':True},'construction':'A2','grounding':'G1'}
        rows=await h.run_e3(port,packets,decision)
        assert len(port.calls)==120 and all(r['status']=='ok' for r in rows)
        assert all(len(r['candidate_C'])==3 for r in rows)
        with pytest.raises(ValueError):await h.run_e3(port,packets,{**decision,'eligible':False})
        with pytest.raises(ValueError):await h.run_e3(port,packets,{**decision,'grounding':'G0'})
    asyncio.run(go())

def test_blind_packets_exclude_arm_goal_on_support_pass(tmp_path):
    p=packet();r={'packet_id':p['packet_id'],'arm':'A0','status':'ok','findings':[candidate()]}
    mapping=h.export_review([p],[r],tmp_path);rid=mapping[0]['review_id']
    source=h.read(tmp_path/'source'/f'{rid}.json');assert set(source)=={'review_id','Candidate','Observation'}
    assert 'A0' not in h.canonical(source) and 'GAP_CANARY' not in h.canonical(source)
    assert h.read(tmp_path/'relevance'/f'{rid}.json')['OneGap']=='GAP_CANARY'

def test_e2_requires_both_labels_on_holdout_and_does_not_backfill():
    rows=[]
    for split in ['D','H_diagnostic']:
        for supported in [True,False]:
            for i in range(18):
                rows.append({'packet_id':split+str(i),'qid':split,'split':split,'candidate':{'statement':f'{split}-{supported}-{i}','evidence_refs':['W1']},
                    'Evidence':packet()['Observation'],'source_supported':supported,'semantic_strengthening':not supported,'ambiguous_relation':False,'reason':'test'})
    b=h.freeze_e2_candidates(rows,[]);assert len(b['pairs'])==60 and b['calls']==121
    assert b==h.freeze_e2_candidates(list(reversed(rows)),[])
    with pytest.raises(ValueError):h.freeze_e2_candidates([r for r in rows if r['split']=='D' or r['source_supported']],[])

def test_usage_cache_only_complete_consistent_records():
    good={'prompt_tokens':10,'completion_tokens':2,'total_tokens':12,'prompt_cache_hit_tokens':8,'prompt_cache_miss_tokens':2}
    assert t.accounting(good)['complete']
    bad={**good,'prompt_cache_miss_tokens':3};assert not t.accounting(bad)['complete']
    summary=t.usage_summary([{'accounting':t.accounting(v)} for v in [good,bad,None]])
    assert summary['cache_hit_rate']==.8 and summary['missing_or_inconsistent_records']==2

def response(value,code=200):
    return httpx.Response(code,json={'id':'mock','model':'deepseek-flash','choices':[{'finish_reason':'stop','message':{'content':json.dumps(value),'reasoning_content':'MOCK_REASONING'}}],
        'usage':{'prompt_tokens':10,'completion_tokens':2,'total_tokens':12,'prompt_cache_hit_tokens':8,'prompt_cache_miss_tokens':2}})

def test_mock_transport_concurrency_archive_hash_and_reasoning(tmp_path):
    async def go():
        active=0;peak=0
        async def handler(req):
            nonlocal active,peak
            active+=1;peak=max(peak,active);await asyncio.sleep(.01);active-=1
            return response({'findings':[]})
        port=t.Transport(config(),tmp_path/'mock','E1',mock_transport=httpx.MockTransport(handler),account_available=4)
        await asyncio.gather(*(port.call(str(i),'a0_current_reader',h.inputs('a0_current_reader',packet()),{'packet_id':str(i),'arm':'A0'}) for i in range(10)))
        result=await port.close();assert result['attempted']==10 and peak==4 and result['peak_concurrency']==4
        c=h.read(tmp_path/'mock/calls/0.content.json');assert c['reasoning_content']=='MOCK_REASONING'
        r=h.read(tmp_path/'mock/calls/0.request.json');assert r['request_hash']==h.digest(r['request'])
        assert 'OFFLINE_TEST_ONLY' not in json.dumps(r)
        with pytest.raises(ValueError):await port.call('0','a0_current_reader',{}, {})
    asyncio.run(go())

@pytest.mark.parametrize('bad',[response({'findings':[]},429),response({'findings':[{'statement':'x','evidence_refs':['W999']}]})])
def test_failure_halts_unsent_and_never_retries(tmp_path,bad):
    async def go():
        count=0
        async def handler(req):
            nonlocal count
            count+=1;await asyncio.sleep(.005);return bad
        port=t.Transport(config(),tmp_path/'mock','E1',mock_transport=httpx.MockTransport(handler),account_available=1)
        values=await asyncio.gather(*(port.call(str(i),'a0_current_reader',h.inputs('a0_current_reader',packet()),{}) for i in range(4)),return_exceptions=True)
        summary=await port.close();assert all(isinstance(v,Exception) for v in values)
        assert count==1 and summary['attempted']==1 and summary['unsent']==3
        assert len(list((tmp_path/'mock/calls').glob('*.result.json')))==4
    asyncio.run(go())

def test_authorization_checked_before_credentials_or_client(monkeypatch,tmp_path):
    def blocked(*args):raise PermissionError('section50 new authorization required')
    monkeypatch.setattr(t,'authorize',blocked)
    monkeypatch.setattr(t.os,'getenv',lambda *a:pytest.fail('credential access before authorization'))
    monkeypatch.setattr(t.httpx,'AsyncClient',lambda *a,**k:pytest.fail('network client before authorization'))
    with pytest.raises(PermissionError):t.Transport(config(),tmp_path/'not_created','E1',authorization_path=tmp_path/'missing')
    assert not (tmp_path/'not_created').exists()

def test_append_only(tmp_path):
    p=tmp_path/'immutable.json';h.save(p,{'first':1})
    with pytest.raises(FileExistsError):h.save(p,{'second':2})
    assert h.read(p)=={'first':1}

def simple_metric_case():
    packets=[packet('D1','D'),packet('H1','H_diagnostic')];results=[];reviews=[];annotations=[]
    for p in packets:
        atom=p['packet_id']+'_a';annotations.append({'packet_id':p['packet_id'],'families':['role'],
            'required_atoms':[{'atom_id':atom}],'correct_silence_primary_eligible':False})
        for arm in ['A0','A1','A2']:
            good=arm!='A0';c=candidate();results.append({'packet_id':p['packet_id'],'arm':arm,'status':'ok','findings':[c]})
            reviews.append({'packet_id':p['packet_id'],'arm':arm,'index':0,'candidate':c,'source_supported':good,
                'semantic_strengthening':not good,'gap_relevant':True,'duplicate_with_C':False,'covered_atom_ids':[atom] if good else []})
    return packets,results,reviews,annotations

def test_metrics_gate_needs_errors_heldout_and_recall():
    p,r,c,a=simple_metric_case();report=m.e1(p,r,c,a)
    assert report['hypotheses']['H1']['supported'] and not report['hypotheses']['H2']['supported']
    for x in c:
        if x['packet_id']=='H1' and x['arm']=='A1':x.update(source_supported=False,semantic_strengthening=True,covered_atom_ids=[])
    assert not m.e1(p,r,c,a)['hypotheses']['H1']['supported']

def test_failed_results_are_not_silence_or_refusal():
    p,r,c,a=simple_metric_case();r[0]={'packet_id':'D1','arm':'A0','status':'failed'};c=[x for x in c if not (x['packet_id']=='D1' and x['arm']=='A0')]
    report=m.e1(p,r,c,a);assert not report['complete'] and report['tables']['pooled']['A0']['FSSR']['rate'] is None
    assert not report['packet_rows'][0]['raw_silent']
    pair={'pair_id':'p','qid':'q','split':'D','label':{'semantic_strengthening':True,'source_supported':False,'ambiguous_relation':True}}
    report=m.e2([pair],[{'pair_id':'p','arm':'G0','status':'failed'},{'pair_id':'p','arm':'G1','status':'ok','verdict':'insufficient'}])
    assert report['tables']['pooled']['G0']['FAR']['rate'] is None and not report['supported']

def test_empty_system_does_not_pass_e3():
    p=packet('p','H_confirmation');a={'packet_id':'p','families':['role'],'required_atoms':[{'atom_id':'a'}],'correct_silence_primary_eligible':False}
    rs=[{'packet_id':'p','pipeline':arm,'status':'ok','findings':[],'candidate_C':[]} for arm in ['current','repaired']]
    report=m.e3([p],rs,[],[a]);assert not report['pass'] and report['tables']['repaired']['SSP']['rate'] is None

def test_bank_frozen_atom_anchors_qid_partition_and_sources():
    packets=h.bank();anns=h.read(h.HERE/'bank/annotations.json')['packets'];by={p['packet_id']:p for p in packets}
    assert len(packets)==36 and len({p['qid'] for p in packets})==20
    partitions=[{p['qid'] for p in packets if p['split']==s} for s in ['D','H_diagnostic','H_confirmation']]
    assert all(not partitions[i]&partitions[j] for i in range(3) for j in range(i+1,3))
    for a in anns:
        ws={w['window_ref']:w for w in by[a['packet_id']]['Observation']}
        for atom in a['required_atoms']:
            for ref in atom['support']:assert ws[ref['window_ref']]['text'][ref['start']:ref['end']]==ref['anchor']
    for path,sha in h.read(h.HERE/'bank/provenance.json')['source_file_hashes'].items():assert h.file_hash(h.ROOT/path)==sha

def test_e3_duplicate_proposals_align_once_and_false_admission_is_never_repaired():
    positive=packet('positive','H_confirmation');silent=packet('silent','H_confirmation')
    annotations=[{'packet_id':p['packet_id'],'families':['role'],'required_atoms':[{'atom_id':'atom'}] if p==positive else [],
        'correct_silence_primary_eligible':p==silent} for p in [positive,silent]]
    results=[];reviews=[]
    for pipeline in ['current','repaired']:
        for p in [positive,silent]:
            cs=[candidate(),candidate()] if p==positive else []
            results.append({'packet_id':p['packet_id'],'pipeline':pipeline,'status':'ok','findings':cs,'candidate_C':cs[:1]})
            for i,c in enumerate(cs):reviews.append({'packet_id':p['packet_id'],'arm':pipeline,'index':i,'candidate':c,
                'source_supported':True,'semantic_strengthening':False,'gap_relevant':True,'duplicate_with_C':False,'covered_atom_ids':['atom']})
    report=m.e3([positive,silent],results,reviews,annotations);assert report['pass']
    for r in reviews:
        if r['arm']=='repaired':r.update(source_supported=False,semantic_strengthening=True,duplicate_with_C=True,covered_atom_ids=[])
    report=m.e3([positive,silent],results,reviews,annotations)
    assert not report['pass'] and report['false_authoritative_C']['repaired']==1

def test_partial_keepalive_timeout_is_archived_without_retry(tmp_path):
    class Partial(httpx.AsyncByteStream):
        async def __aiter__(self):
            yield b'\n\n'
            raise httpx.ReadTimeout('offline simulated timeout')
    async def go():
        count=0
        async def handler(req):
            nonlocal count
            count+=1;return httpx.Response(200,stream=Partial())
        port=t.Transport(config(),tmp_path/'mock','E1',mock_transport=httpx.MockTransport(handler),account_available=1)
        with pytest.raises(httpx.ReadTimeout):await port.call('partial','a0_current_reader',h.inputs('a0_current_reader',packet()),{})
        summary=await port.close()
        assert count==1 and summary['attempted_failures']==1
        assert (tmp_path/'mock/calls/partial.response.body').read_bytes()==b'\n\n'
        assert summary['cache_hit_rate'] is None and summary['missing_or_inconsistent_records']==1
