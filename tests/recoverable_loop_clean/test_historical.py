"""Human-reviewed fixtures + scripted semantic ports: no model accuracy claims."""
from dataclasses import asdict, replace
import hashlib
import json
from pathlib import Path
import pytest
from conftest import bridge, acquire, action, Script, EMPTY_READER, EMPTY_H
from llm_chat.recoverable_loop.state import State, Claim, Hypothesis, skeleton, trace_view, append_event
from llm_chat.recoverable_loop.engine import RecoverableLoop
from llm_chat.recoverable_loop.replay import replay_log

ROOT=Path(__file__).resolve().parents[2]
FIXTURES=ROOT/'experiments/recoverable_loop_clean/fixtures'
CASES=[p.stem for p in sorted(FIXTURES.glob('*.json')) if p.stem!='MANIFEST']


def restore(case):
    """Only archived observed bytes become the offline document corpus.

    New D/W identities are explicitly remapped. Full original documents are not
    restored and this does not measure original retrieval/window selection.
    """
    b=bridge(hits=[]); refs={}; docs={}
    for old in case['observations']:
        key=b.tools.window_builder.register('fixture:'+old['window_ref'],old['text'],old.get('url',''))
        raw=b.tools.window_builder._emit(key,0,len(old['text']))
        dr,_=b.tools.handles.document(key); wr,_=b.tools.handles.window(raw['window_ref'])
        b.evidence.add(b._normalize({'tool':'open','raw_result':raw,'handles':b.tools.handles.snapshot()}))
        refs[old['window_ref']]=wr;docs[old['doc_ref']]=dr
    claims=tuple(Claim(f'C{i}',c['statement'],tuple(refs[r] for r in c['evidence_refs'])) for i,c in enumerate(case['claims'],1))
    hs=(Hypothesis('H1',case['hypothesis'],'active',()),) if case['hypothesis'] else ()
    return State(case['question'],skeleton(case['question'],case['requirements']),claims,hs),b,refs,docs


def test_fixture_hashes_and_prefix_provenance():
    manifest=json.loads((FIXTURES/'MANIFEST.json').read_text())
    for path,sha in manifest['source_files_sha256'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==sha
    for name,sha in manifest['fixture_files_sha256'].items():
        assert hashlib.sha256((FIXTURES/name).read_bytes()).hexdigest()==sha
    assert len(CASES)==10


@pytest.mark.parametrize('ident',CASES)
def test_historical_closure_veto_roundtrip_and_no_h_to_c(ident,tmp_path):
    c=json.loads((FIXTURES/(ident+'.json')).read_text());s,b,refs,docs=restore(c)
    feedback={'status':'CONTINUE','missing':[{'requirement_id':'R1','summary':c['review']['reason']}]}
    def actor(req):
        x=json.loads(req.input_json)
        assert x['TraceView']['latest_closure_feedback']==feedback
        return acquire(c['review']['acceptable_one_gap'],action('open',window_ref=next(iter(refs.values())),direction='around'))
    def closure(req):
        x=json.loads(req.input_json)
        assert set(x)=={'Q','R','C','Evidence'}
        assert len(x['C'])==len(s.C)  # Local facts preserved, not denied by CONTINUE.
        return feedback  # Scripted human expectation, NOT a semantic classifier.
    p=Script(('actor',{'decision':'request_closure'}),('closure',closure),('actor',actor),
             ('reader',EMPTY_READER),*([('hypotheses',EMPTY_H)] if s.H else []))
    loop=RecoverableLoop(s,b,p,tmp_path/(ident+'.jsonl'))
    out=loop.step(); assert out['closure']['status']=='CONTINUE' and 'failure' not in out
    assert loop.state.Q==s.Q and loop.state.R==s.R and loop.state.C==s.C
    with pytest.raises(PermissionError): loop.finalize()
    assert 'failure' not in loop.step(); p.done();loop.close()
    assert loop.state.C==s.C and loop.state.H==s.H
    assert replay_log(tmp_path/(ident+'.jsonl'))[0]==loop.state


@pytest.mark.parametrize('ident',['euler','memo_letter','ding2019'])
def test_hardened_premise_is_control_error_without_direct_truth_authority(ident):
    c=json.loads((FIXTURES/(ident+'.json')).read_text());s,b,refs,_=restore(c)
    bad=c['review']['hardened_or_completion_error']; wr=next(iter(refs.values()))
    p=Script(('actor',acquire(bad,action('open',window_ref=wr,direction='around'))),
             ('reader',{'findings':[{'statement':bad,'evidence_refs':[wr]}]}),
             ('grounding',{'verdict':'insufficient','reason':c['review']['reason']}),('hypotheses',EMPTY_H))
    loop=RecoverableLoop(s,b,p);assert loop.step()['feedback']=='NoGain';p.done()
    assert loop.state.C==s.C
    # Structural validation intentionally does not pretend to verify English entailment.
    assert trace_view(loop.state)['recent_attempts'][0]['decision']['one_gap']==bad


def test_q546_pending_real_prefix_source_can_route_to_real_find():
    c=json.loads((FIXTURES/'q546.json').read_text());s,b,refs,docs=restore(c)
    dr=docs[c['pending_historical_source']]
    obs=next(o for o in c['observations'] if o['doc_ref']==c['pending_historical_source'])
    assert obs['observed_seq']<=33
    s=append_event(s,'step_outcome',{'family':['R1','LOCATE_SOURCE',[]],'feedback':'Gain',
        'inspected_sources':[], 'new_source_opportunities':[{'doc_ref':dr,'window_ref':refs[obs['window_ref']],
        'title':obs['title'],'preview':obs['text'],'uninspected':True}]})
    def actor(req):
        assert json.loads(req.input_json)['TraceView']['pending_source_opportunities'][0]['doc_ref']==dr
        return acquire(c['review']['acceptable_one_gap'],action('find',doc_ref=dr,query='Ding'))
    p=Script(('actor',actor),('reader',EMPTY_READER))
    loop=RecoverableLoop(s,b,p);assert 'failure' not in loop.step();p.done()
    assert not trace_view(loop.state)['pending_source_opportunities']


def test_q1094_repeated_search_no_gain_then_route_change():
    c=json.loads((FIXTURES/'q1094.json').read_text());s,b,refs,docs=restore(c)
    def third(req):
        assert json.loads(req.input_json)['TraceView']['same_family_consecutive_nogain']==2
        return acquire(c['review']['acceptable_one_gap'],action('find',doc_ref=next(iter(docs.values())),query='Messi'),strategy='VERIFY_RELATION')
    p=Script(('actor',acquire(act=action(query='club discord'))),
             ('actor',acquire(act=action(query='club disagreement'))),
             ('actor',third),('reader',EMPTY_READER))
    loop=RecoverableLoop(s,b,p)
    assert [loop.step()['feedback'] for _ in range(3)]==['NoGain']*3;p.done()
    assert loop.state.C==s.C


def test_patient_fixture_preserves_actual_clinic_evidence():
    c=json.loads((FIXTURES/'patient_country.json').read_text())
    assert 'clinic in Pakistan' in c['observations'][0]['text']
    assert 'ALSO' in c['review']['reason']  # Does not erase real context to manufacture a negative.
