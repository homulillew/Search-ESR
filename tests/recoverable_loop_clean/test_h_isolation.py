"""Offline failure injection: verifies authority, not model semantic accuracy."""
from dataclasses import asdict, replace
import hashlib
import json
import pytest
from conftest import bridge, state, action, acquire, Script, EMPTY_READER, EMPTY_H, SUPPORTED, CONTINUE
from llm_chat.recoverable_loop.engine import RecoverableLoop
from llm_chat.recoverable_loop.integrity import IntegrityError
from llm_chat.recoverable_loop.replay import replay_log
from llm_chat.recoverable_loop.state import Claim, Hypothesis, append_event, trace_view
from llm_chat.recoverable_loop.roles import schemas
from llm_chat.recoverable_loop.contracts import check


def proposal(*updates, sources=()):
    return {'updates': list(updates), 'useful_source_refs': list(sources)}


def add(refs=(), statement='Alice may satisfy the question.'):
    return {'operation': 'ADD', 'statement': statement, 'basis_refs': list(refs)}


def finding():
    return {'findings': [{'statement': 'Alice was born in 1900.', 'evidence_refs': ['W1']}]}


@pytest.mark.parametrize('refs', [[], ['W1']])
def test_valid_add_keeps_low_authority(refs, tmp_path):
    p = Script(('actor', acquire()), ('reader', EMPTY_READER), ('hypotheses', proposal(add(refs))))
    loop = RecoverableLoop(state(), bridge(), p, tmp_path/'trace.jsonl')
    result = loop.step(); p.done(); loop.close()
    assert result['feedback'] == 'Gain' and result['auxiliary_failures'] == []
    assert loop.state.H[0].basis_refs == tuple(refs) and loop.state.C == ()
    with pytest.raises(PermissionError): loop.finalize()
    assert replay_log(tmp_path/'trace.jsonl')[0] == loop.state


BAD_PROPOSALS = [
    proposal(add(['C3'])), proposal(add(['D4'])), proposal(add(['R1'])), proposal(add(['H1'])),
    proposal(add(['W999'])), proposal(add(['W0'])), proposal(add(['W01'])),
    proposal(add(), {'operation': 'KEEP', 'hypothesis_id': 'H99'}),
    proposal(add(), {'operation': 'KEEP', 'hypothesis_id': 'H1'}, {'operation': 'KEEP', 'hypothesis_id': 'H1'}),
    proposal(*(add(['W1'], f'Distinct candidate {i}') for i in range(7))),
    proposal(add(), sources=['D999']), proposal(add(), sources=['W1']),
    {'updates': [], 'useful_source_refs': [], 'C': []},
    '{"updates":[],"updates":[],"useful_source_refs":[]}',
    'not JSON', None,
]


@pytest.mark.parametrize('bad', BAD_PROPOSALS)
def test_whole_h_transaction_rejected_preserves_claim_gain_and_next_actor(bad, tmp_path):
    s = replace(state(), H=(Hypothesis('H1', 'Alice may be born in 2000.', 'active', ()),))
    def next_actor(req):
        x = json.loads(req.input_json)
        assert x['C'][-1]['claim_id'] == 'C1'
        assert x['TraceView']['recent_attempts'][-1]['auxiliary_failures']
        assert x['H'] == json.loads(json.dumps([asdict(h) for h in s.H]))
        return {'decision': 'request_closure'}
    p = Script(('actor', acquire()), ('reader', finding()), ('grounding', SUPPORTED),
               ('hypotheses', bad), ('actor', next_actor), ('closure', CONTINUE))
    loop = RecoverableLoop(s, bridge(), p, tmp_path/'trace.jsonl')
    out = loop.step()
    assert 'failure' not in out and out['feedback'] == 'Gain' and out['claim_delta'] == ['C1']
    assert out['claim_outcome'] == 'completed' and out['hypothesis_outcome'] == 'failed'
    assert loop.state.H == s.H and len(loop.state.C) == 1
    event = next(e.payload() for e in loop.state.T if e.kind == 'hypothesis_update_failed')
    raw = next(e.payload()['output'] for e in loop.state.T if e.kind == 'role_response' and e.payload()['role'] == 'hypotheses')
    from llm_chat.recoverable_loop.state import canonical
    assert raw == bad and event['raw_output_hash'] == hashlib.sha256((raw if isinstance(raw, str) else canonical(raw)).encode()).hexdigest()
    assert event['H_unchanged'] and event['attempt_id'] == 1
    assert not any(e.kind == 'step_failure' for e in loop.state.T)
    assert loop.step()['closure']['status'] == 'CONTINUE'; p.done(); loop.close()
    assert replay_log(tmp_path/'trace.jsonl')[0] == loop.state


def test_old_pending_d17_rejected_without_partial_h_or_opportunity_loss():
    hits = [dict(docid=str(i), text=f'title: {i}\nAlice record {i}', url=f'local:{i}', score=1) for i in range(17)]
    b = bridge(hits=hits[:10]); b.execute(action(query='records', k=10))
    b.tools.searcher.hits = hits[10:]; b.execute(action(query='more records', k=10))
    b.tools.searcher.hits = hits
    s = replace(state(), H=(Hypothesis('H1', 'Candidate', 'active', ()),))
    pending = {'doc_ref': 'D17', 'window_ref': 'W17', 'title': '16', 'preview': 'Alice record', 'uninspected': True}
    s = append_event(s, 'step_outcome', {'new_source_opportunities': [pending], 'inspected_sources': []})
    def h(req):
        assert json.loads(req.input_json)['eligible_source_refs'] == []
        return proposal(add(), sources=['D17'])
    p = Script(('actor', acquire()), ('reader', EMPTY_READER), ('hypotheses', h))
    loop = RecoverableLoop(s, b, p); out = loop.step(); p.done()
    assert out['feedback'] == 'NoGain' and 'failure' not in out
    assert out['auxiliary_failures'][0]['error_type'] == 'invalid_source_nomination'
    assert loop.state.H == s.H and trace_view(loop.state)['pending_source_opportunities'] == [pending]


@pytest.mark.parametrize('force_invalid', [False, True])
def test_r1_repeated_search_nogain_reaches_materially_different_route(force_invalid, tmp_path):
    b = bridge(orthogonal=True); b.execute(action())  # Search preview already observed.
    def changed(req):
        x = json.loads(req.input_json)
        assert x['TraceView']['recent_attempts'][-1]['feedback'] == 'NoGain'
        return acquire('Inspect birth record.', action('find', doc_ref='D1', query='born'), strategy='LOCALIZE_IN_SOURCE')
    outputs = [('actor', acquire())]
    if force_invalid: outputs.append(('hypotheses', proposal(add(['R1']))))
    outputs += [('actor', changed), ('reader', finding()), ('grounding', SUPPORTED), ('hypotheses', EMPTY_H)]
    p = Script(*outputs); loop = RecoverableLoop(state(), b, p, tmp_path/'trace.jsonl')
    if force_invalid:
        # Fault injection only: production's new skip would avoid this old H call.
        loop._should_update_hypotheses = lambda *args: True
    first = loop.step()
    assert first['feedback'] == 'NoGain' and 'failure' not in first
    assert first['hypothesis_outcome'] == ('failed' if force_invalid else 'skipped')
    assert loop.state.C == () and loop.state.H == ()
    assert loop.step()['feedback'] == 'Gain'; p.done(); loop.close()
    attempts = trace_view(loop.state)['recent_attempts']
    assert attempts[-1]['decision']['action']['tool'] == 'find'
    assert attempts[-1]['family'] != attempts[-2]['family']
    assert replay_log(tmp_path/'trace.jsonl')[0] == loop.state


def test_active_h_allows_nogain_deprioritization_without_new_evidence():
    s = replace(state(), H=(Hypothesis('H1', 'Unproductive route candidate', 'active', ()),))
    p = Script(('actor', acquire(hids=['H1'])), ('hypotheses', proposal(
        {'operation': 'DEPRIORITIZE', 'hypothesis_id': 'H1', 'basis_refs': []})))
    loop = RecoverableLoop(s, bridge(hits=[]), p); out = loop.step(); p.done()
    assert out['feedback'] == 'Gain' and not loop.state.C
    assert loop.state.H[0].status == 'deprioritized'


def test_closure_veto_acquisition_claim_invalid_h_next_actor(tmp_path):
    def closure(req):
        assert set(json.loads(req.input_json)) == {'Q', 'R', 'C', 'Evidence'}
        return CONTINUE
    def actor(req):
        assert json.loads(req.input_json)['TraceView']['latest_closure_feedback'] == CONTINUE
        return acquire('Resolve the missing birth-year evidence.')
    p = Script(('actor', {'decision': 'request_closure'}), ('closure', closure), ('actor', actor),
               ('reader', finding()), ('grounding', SUPPORTED), ('hypotheses', proposal(add(['C1']))),
               ('actor', {'decision': 'request_closure'}), ('closure', closure))
    loop = RecoverableLoop(state(), bridge(), p, tmp_path/'trace.jsonl')
    assert loop.step()['closure']['status'] == 'CONTINUE'
    second = loop.step(); assert second['feedback'] == 'Gain' and 'failure' not in second
    assert loop.step()['closure']['status'] == 'CONTINUE'
    p.done(); loop.close(); assert len(loop.state.C) == 1
    assert replay_log(tmp_path/'trace.jsonl')[0] == loop.state


@pytest.mark.parametrize('kind', ['missing_C_evidence', 'trace_hash', 'registry', 'unreplayable_C', 'evidence_bytes'])
def test_existing_state_corruption_is_fatal_before_next_actor(kind):
    b = bridge(); b.execute(action())
    s = replace(state(), C=(Claim('C1', 'Alice was born in 1900.', ('W1',)),))
    loop = RecoverableLoop(s, b, Script())
    if kind == 'missing_C_evidence': loop._state = replace(s, C=(replace(s.C[0], evidence_refs=('W999',)),))
    elif kind == 'trace_hash':
        loop._state = append_event(s, 'test', {})
        loop._state = replace(loop.state, T=(replace(loop.state.T[0], event_hash='broken'),))
    elif kind == 'registry': b.tools.handles._window_ref_to_source['W1'] = 'broken'
    elif kind == 'unreplayable_C': loop._state = replace(s, C=s.C+(Claim('C2', 'Unsupported mutation.', ('W1',)),))
    else: b.evidence._windows['W1'] = replace(b.evidence.get('W1'), text='tampered')
    with pytest.raises(IntegrityError): loop.step()
    assert not loop.semantics.requests


@pytest.mark.parametrize('output', [proposal(add(['R1'])), EMPTY_H, TimeoutError('port failure')])
def test_corruption_during_h_is_never_swallowed(output):
    b = bridge()
    def corrupt(req):
        b.tools.handles._doc_ref_to_key['D1'] = ('broken', 'broken')
        if isinstance(output, Exception): raise output
        return output
    p = Script(('actor', acquire()), ('reader', finding()), ('grounding', SUPPORTED), ('hypotheses', corrupt))
    loop = RecoverableLoop(state(), b, p)
    with pytest.raises(IntegrityError): loop.step()
    p.done(); assert not any(e.kind == 'hypothesis_update_failed' for e in loop.state.T)


@pytest.mark.parametrize('role', ['grounding', 'closure'])
def test_high_authority_role_provider_failure_stays_fatal(role):
    outputs = [('actor', acquire()), ('reader', finding()), ('grounding', TimeoutError('script'))] if role == 'grounding' else [
        ('actor', {'decision': 'request_closure'}), ('closure', TimeoutError('script'))]
    p = Script(*outputs); loop = RecoverableLoop(state(), bridge(), p)
    out = loop.step(); p.done()
    assert out['failure']['type'] == 'TimeoutError' and out['auxiliary_failures'] == []
    assert not loop.state.C
    with pytest.raises(PermissionError): loop.finalize()


def test_typed_contracts_are_distinct():
    schema = schemas()['hypotheses']
    check(proposal(add(['W1']), sources=['D1']), schema)
    for invalid in [proposal(add(['D1'])), proposal(add(['C1'])), proposal(add(), sources=['W1'])]:
        with pytest.raises(ValueError): check(invalid, schema)


def test_valid_hash_chain_does_not_legitimize_ungrounded_commit():
    from llm_chat.recoverable_loop.state import digest
    b = bridge(); b.execute(action()); loop = RecoverableLoop(state(), b, Script())
    c = Claim('C1', 'Alice was born in 1900.', ('W1',))
    evidence = b.evidence.select(c.evidence_refs)
    payload = {'candidate': {'statement': c.statement, 'evidence_refs': ['W1']}, 'Evidence': evidence}
    loop._state = replace(loop.state, C=(c,))
    loop._emit('claim_committed', claim=asdict(c), evidence_hash=digest(evidence), grounding_payload_hash=digest(payload))
    with pytest.raises(IntegrityError, match='no matching supported'): loop.step()


def test_provider_failure_without_progress_still_allows_next_actor():
    s = replace(state(), H=(Hypothesis('H1', 'Candidate', 'active', ()),))
    p = Script(('actor', acquire()), ('hypotheses', TimeoutError('offline provider outage')),
               ('actor', {'decision': 'request_closure'}), ('closure', CONTINUE))
    loop = RecoverableLoop(s, bridge(hits=[]), p); out = loop.step()
    assert 'failure' not in out and out['feedback'] == 'NoGain'
    assert out['auxiliary_failures'][0]['raw_output_hash'] is None
    assert loop.state.H == s.H
    assert loop.step()['closure']['status'] == 'CONTINUE'; p.done()


def test_inspected_current_source_cannot_be_nominated(monkeypatch):
    b = bridge(); original = b.execute
    # Model-output validator must exclude an inspected D even if current batch
    # also marks it newly discovered. This injected batch doesn't change tools.
    def execute(act):
        batch = original(act); batch['inspected_sources'] = ['D1']; return batch
    monkeypatch.setattr(b, 'execute', execute)
    p = Script(('actor', acquire()), ('reader', EMPTY_READER), ('hypotheses', proposal(add(), sources=['D1'])))
    loop = RecoverableLoop(state(), b, p); out = loop.step(); p.done()
    assert out['auxiliary_failures'][0]['error_type'] == 'invalid_source_nomination'
    assert loop.state.H == () and 'failure' not in out
