from dataclasses import asdict, FrozenInstanceError, replace
import json
import pytest
from conftest import bridge, state, action, acquire, Script, EMPTY_READER, EMPTY_H, SUPPORTED, CONTINUE
from llm_chat.recoverable_loop.engine import RecoverableLoop
from llm_chat.recoverable_loop.state import Claim, Hypothesis, State, trace_view, skeleton
from llm_chat.recoverable_loop.replay import replay_log


def finding(statement='Alice was born in 1900.', ref='W1'):
    return {'findings': [{'statement': statement, 'evidence_refs': [ref]}]}


def test_state_is_only_qrcht_and_immutable():
    s = state()
    assert set(asdict(s)) == {'Q','R','C','H','T'}
    with pytest.raises(FrozenInstanceError): s.Q = 'changed'
    with pytest.raises(TypeError): State(s.Q, list(s.R))
    with pytest.raises(TypeError): Claim('C1','fact',['W1'])
    with pytest.raises(ValueError): State('different Q', s.R)
    with pytest.raises(ValueError): State(s.Q, skeleton(s.Q,[{'source_spans':[{'text':'absent span'}]}]))
    with pytest.raises(ValueError): replace(s,H=tuple(Hypothesis(f'H{i}',str(i),'active',()) for i in range(7)))


@pytest.mark.parametrize('output', [
    {**acquire(), 'C': [{'statement':'Actor wrote fact'}]},
    {'decision':'STOP'}, {'decision':'final','answer':'Alice'},
    {'decision':'request_closure','one_gap':'forced'},
    {**acquire(),'focus_requirement_id':'R99'}, {**acquire(),'hypothesis_ids_under_test':['H99']},
    {**acquire(),'one_gap':'   '},
    '{"decision":"request_closure","decision":"acquire"}',
])
def test_actor_has_no_state_or_completion_authority_and_failure_retained(output):
    b=bridge(); s=state(); p=Script(('actor',output)); loop=RecoverableLoop(s,b,p)
    result=loop.step(); p.done()
    assert result['failure'] and result['feedback']=='NoGain'
    assert loop.state.Q==s.Q and loop.state.R==s.R and loop.state.C==()
    assert b.tools.searcher.calls==[]
    assert any(e.kind=='role_response' for e in loop.state.T)
    assert any(e.kind=='step_failure' for e in loop.state.T)
    with pytest.raises(PermissionError): loop.finalize()


def test_role_input_copies_prevent_state_mutation():
    def actor(req):
        view=json.loads(req.input_json); view['Q']='mutated'; view['R'].clear(); view['C'].append({'lie':True})
        return acquire()
    s=state(); p=Script(('actor',actor),('reader',EMPTY_READER),('hypotheses',EMPTY_H))
    loop=RecoverableLoop(s,bridge(),p); loop.step(); p.done()
    assert loop.state.Q==s.Q and loop.state.R==s.R and not loop.state.C


def test_selective_claim_grounding_full_raw_window_and_replay(tmp_path):
    text='title: Registry\nName | Birth year\n---- | ----\nAlice | 1900\nContext retained exactly.'
    def reader(req):
        x=json.loads(req.input_json)
        assert set(x)=={'OneGap','C','Observation'}
        assert x['Observation'][0]['text']==text
        return finding()
    def ground(req):
        x=json.loads(req.input_json)
        assert set(x)=={'candidate','Evidence'}
        assert x['Evidence'][0]['text']==text and x['Evidence'][0]['title']=='Registry'
        assert 'H' not in x and 'Q' not in x and 'OneGap' not in x
        return SUPPORTED
    p=Script(('actor',acquire()),('reader',reader),('grounding',ground),('hypotheses',EMPTY_H))
    path=tmp_path/'trace.jsonl'; loop=RecoverableLoop(state(),bridge(text),p,path)
    assert loop.step()['feedback']=='Gain'; loop.close(); p.done()
    assert loop.state.C==(Claim('C1','Alice was born in 1900.',('W1',)),)
    restored,evidence=replay_log(path)
    assert restored==loop.state and evidence.get('W1').text==text
    lines=path.read_text().splitlines(); row=json.loads(lines[-1]); row['payload_json']='{}'; lines[-1]=json.dumps(row)
    bad=tmp_path/'tampered.jsonl';bad.write_text('\n'.join(lines)+'\n')
    with pytest.raises(ValueError): replay_log(bad)
    with pytest.raises(FileExistsError): RecoverableLoop(state(),bridge(),Script(),path)


@pytest.mark.parametrize('candidate_response', [
    finding(ref='W999'), {'findings': finding()['findings']*4},
    {'findings':[{'statement':'made up','evidence_refs':['W1'],'document_sha256':'model hash'}]},
])
def test_reader_invalid_or_fabricated_metadata_never_commits(candidate_response):
    p=Script(('actor',acquire()),('reader',candidate_response));loop=RecoverableLoop(state(),bridge(),p)
    assert loop.step()['failure'];p.done();assert not loop.state.C


def test_unsupported_fact_rejected_without_destroying_observation():
    p=Script(('actor',acquire()),('reader',finding('Alice was born in 2000.')),
             ('grounding',{'verdict':'insufficient','reason':'Different year.'}),('hypotheses',EMPTY_H))
    loop=RecoverableLoop(state(),bridge(),p)
    assert loop.step()['feedback']=='NoGain';p.done();assert not loop.state.C
    assert loop.bridge.evidence.get('W1').text


def test_timeout_no_retry_and_partial_verified_claim_survives_later_failure():
    p=Script(('actor',acquire()),('reader',finding()),('grounding',SUPPORTED),('hypotheses',TimeoutError('offline injected timeout')))
    loop=RecoverableLoop(state(),bridge(),p);out=loop.step();p.done()
    assert out['failure']['type']=='TimeoutError' and out['feedback']=='Gain'
    assert len(loop.state.C)==1 and not loop.state.H
    assert len([r for r in p.requests if r.role=='hypotheses'])==1


def test_duplicate_c_and_h_do_not_mask_nogain():
    b=bridge();b.execute(action())
    s=replace(state(),C=(Claim('C1','Alice was born in 1900.',('W1',)),),H=(Hypothesis('H1','Alice may fit.','active',('W1',)),))
    p=Script(('actor',acquire()),('reader',finding(' Alice WAS born in 1900. ')),
             ('hypotheses',{'updates':[{'operation':'ADD','statement':'  ALICE may fit.','basis_refs':['W1']}],'useful_source_refs':[]}))
    loop=RecoverableLoop(s,b,p); assert loop.step()['feedback']=='NoGain';p.done()
    assert loop.state.C==s.C and loop.state.H==s.H


@pytest.mark.parametrize('updates', [
    [{'operation':'ADD','statement':str(i),'basis_refs':['W1']} for i in range(7)],
    [{'operation':'REJECT','hypothesis_id':'H1','basis_refs':[]}],
    [{'operation':'REJECT','hypothesis_id':'H1','basis_refs':['W999']}],
    [{'operation':'KEEP','hypothesis_id':'H1','C':[{'statement':'leak'}]}],
    [{'operation':'REJECT','hypothesis_id':'H99','basis_refs':['W1']}],
])
def test_h_updates_are_atomic_bounded_and_low_authority(updates):
    s=replace(state(),H=(Hypothesis('H1','Alice might be born in 2000.','active',()),))
    p=Script(('actor',acquire()),('reader',EMPTY_READER),('hypotheses',{'updates':updates,'useful_source_refs':[]}))
    loop=RecoverableLoop(s,bridge(),p);assert loop.step()['failure'];p.done()
    assert loop.state.H==s.H and loop.state.C==()


def test_wrong_h_recovery_with_real_mock_acquisition():
    s=replace(state(),H=(Hypothesis('H1','Alice might be born in 2000.','active',()),))
    p=Script(('actor',acquire(hids=['H1'])),('reader',finding()),('grounding',SUPPORTED),
             ('hypotheses',{'updates':[{'operation':'REJECT','hypothesis_id':'H1','basis_refs':['W1']}],'useful_source_refs':[]}))
    loop=RecoverableLoop(s,bridge(),p);assert loop.step()['feedback']=='Gain';p.done()
    assert loop.state.H[0].status=='rejected'
    assert '2000' not in loop.state.C[0].statement
    assert trace_view(loop.state)['recent_attempts'][0]['hypothesis_delta']==['H1']


def test_two_nogain_attempts_feed_a_third_changed_route():
    def third(req):
        tv=json.loads(req.input_json)['TraceView']
        assert tv['same_family_consecutive_nogain']==2
        return acquire('Inspect the existing source for a different relation.', action('find',doc_ref='D1',query='Alice'),strategy='VERIFY_RELATION')
    p=Script(('actor',acquire('Check premise one.')),('reader',EMPTY_READER),('hypotheses',EMPTY_H),
             ('actor',acquire('Reword premise one.')),('reader',EMPTY_READER),('hypotheses',EMPTY_H),
             ('actor',third),('reader',EMPTY_READER),('hypotheses',EMPTY_H))
    loop=RecoverableLoop(state(),bridge(),p)
    assert [loop.step()['feedback'] for _ in range(3)]==['NoGain']*3;p.done()
    assert trace_view(loop.state)['same_family_consecutive_nogain']==1
    assert trace_view(loop.state)['recent_attempts'][-1]['decision']['action']['tool']=='find'


def test_new_handle_alone_not_gain_useful_opportunity_survives_until_inspection():
    p=Script(('actor',acquire()),('reader',EMPTY_READER),
             ('hypotheses',{'updates':[],'useful_source_refs':['D1']}),
             ('actor',acquire(act=action('find',doc_ref='D1',query='zzzznomatch'))),('hypotheses',EMPTY_H))
    loop=RecoverableLoop(state(),bridge(),p)
    assert loop.step()['feedback']=='Gain'
    assert trace_view(loop.state)['pending_source_opportunities'][0]['doc_ref']=='D1'
    assert loop.step()['feedback']=='NoGain';p.done()
    assert not trace_view(loop.state)['pending_source_opportunities']
    p=Script(('actor',acquire()),('reader',EMPTY_READER),('hypotheses',EMPTY_H))
    loop=RecoverableLoop(state(),bridge(),p);assert loop.step()['feedback']=='NoGain';p.done()


def test_closure_continue_is_feedback_and_next_actor_really_uses_it():
    s=replace(state(),H=(Hypothesis('H1','Provisional answer.','active',()),))
    def closure(req):
        x=json.loads(req.input_json);assert set(x)=={'Q','R','C','Evidence'}
        return CONTINUE
    def next_actor(req):
        x=json.loads(req.input_json)
        assert x['TraceView']['latest_closure_feedback']==CONTINUE
        assert x['C']==[]
        return acquire('Verify the relation identified by Closure feedback.')
    p=Script(('actor',{'decision':'request_closure'}),('closure',closure),('actor',next_actor),
             ('reader',EMPTY_READER),('hypotheses',EMPTY_H))
    loop=RecoverableLoop(s,bridge(),p);out=loop.step()
    assert out['closure']['status']=='CONTINUE' and 'failure' not in out
    assert loop.state.Q==s.Q and loop.state.R==s.R and loop.state.C==s.C
    with pytest.raises(PermissionError):loop.finalize()
    loop.step();p.done()
    assert len(loop.bridge.tools.searcher.calls)==1


def ready_loop(p, tmp_path=None):
    b=bridge();b.execute(action());s=replace(state(),C=(Claim('C1','Alice was born in 1900.',('W1',)),))
    return RecoverableLoop(s,b,p,tmp_path)


def test_only_current_ready_allows_final_and_final_input_excludes_h_r_trace(tmp_path):
    def final(req):
        x=json.loads(req.input_json); assert set(x)=={'Q','C','Evidence','Closure'}
        return {'answer':'1900.','claim_ids':['C1']}
    p=Script(('actor',{'decision':'request_closure'}),('closure',{'status':'READY','reason':'Explicit source.','claim_ids':['C1']}),('final',final))
    loop=ready_loop(p,tmp_path/'ready.jsonl')
    with pytest.raises(PermissionError):loop.finalize()
    assert loop.step()['closure']['status']=='READY'
    assert loop.finalize()['answer']=='1900.';p.done()
    with pytest.raises(PermissionError):loop.finalize()
    loop.close();assert replay_log(tmp_path/'ready.jsonl')[0]==loop.state


def test_invalid_ready_citations_do_not_authorize_final():
    p=Script(('actor',{'decision':'request_closure'}),('closure',{'status':'READY','reason':'fabricated','claim_ids':['C99']}))
    loop=ready_loop(p);assert loop.step()['failure'];p.done()
    with pytest.raises(PermissionError):loop.finalize()


def test_final_failure_consumes_permit_no_automatic_retry():
    p=Script(('actor',{'decision':'request_closure'}),('closure',{'status':'READY','reason':'Explicit source.','claim_ids':['C1']}),('final',TimeoutError('script')))
    loop=ready_loop(p);loop.step()
    with pytest.raises(TimeoutError):loop.finalize()
    with pytest.raises(PermissionError):loop.finalize()
    p.done()


def test_any_new_actor_attempt_invalidates_ready():
    p=Script(('actor',{'decision':'request_closure'}),('closure',{'status':'READY','reason':'Explicit source.','claim_ids':['C1']}),('actor',{'decision':'invalid'}))
    loop=ready_loop(p);loop.step();loop.step();p.done()
    with pytest.raises(PermissionError):loop.finalize()
