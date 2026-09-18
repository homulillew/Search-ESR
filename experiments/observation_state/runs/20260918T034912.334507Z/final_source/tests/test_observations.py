import copy
import json
import random
import httpx
import pytest
from test_snippets import tokenizer
from test_chat import config,client,reply
from llm_chat.raw_windows import RawWindowBuilder
from llm_chat.observations import ObservationStore,merge_ranges,subtract_ranges
from llm_chat.observed_agent import ObservedTools,ObservedAgentSession


def source(builder):
    text='title: Sample\n'+''.join(f'Sentence {i} about a distinct event.\n' for i in range(150))
    return text,builder.search('d',text,'https://example.test/source','distinct event 73')


def test_interval_accounting_against_character_sets():
    rng=random.Random(919)
    for _ in range(100):
        spans=[sorted(rng.sample(range(100),2)) for _ in range(8)]
        a,z=sorted(rng.sample(range(100),2))
        covered={i for x,y in spans for i in range(x,y)}
        actual={i for x,y in subtract_ranges(a,z,spans) for i in range(x,y)}
        assert actual==set(range(a,z))-covered
        assert {i for x,y in merge_ranges(spans) for i in range(x,y)}==covered


def test_duplicate_overlap_title_and_version_accounting(tokenizer):
    b=RawWindowBuilder(tokenizer);text,v=source(b);store=ObservationStore()
    original=copy.deepcopy(v)
    first=store.record('search',{'query':'x'},[v],b)
    again=store.record('search',{'query':'x'},[v],b)
    assert v==original
    assert first['observations'][0]['new_chars']>0
    assert again['observations'][0]['new_chars']==0
    assert again['observations'][0]['repeated_window']
    expanded=b.open(v['window_ref'],'around');store.record('open',{},expanded,b)
    assert store.summary()['new_source_chars']==store.summary()['covered_source_chars']
    new=b.search('d','title: New\nDifferent source text.','u','source');store.record('search',{},[new],b)
    assert store.summary()['source_versions']==2
    store.close()


def test_restart_open_uses_pinned_source_not_current_corpus(tokenizer,tmp_path):
    path=tmp_path/'observations.sqlite';b=RawWindowBuilder(tokenizer);text,v=source(b)
    store=ObservationStore(path);store.record('search',{},[v],b);expected=b.open(v['window_ref'],'after');store.close()
    resumed=ObservationStore(path);fresh=RawWindowBuilder(tokenizer)
    fresh.search('d','title: Changed\nReplaced corpus text.','new','changed')
    resumed.restore_window(fresh,v['window_ref'])
    actual=fresh.open(v['window_ref'],'after')
    assert actual==expected
    resumed.record('open',{'window_ref':v['window_ref'],'direction':'after'},actual,fresh)
    assert resumed.summary()['new_source_chars']==resumed.summary()['covered_source_chars']
    resumed.close()


def test_invalid_batch_is_atomic_and_unknown_session_ref_rejected(tokenizer):
    b=RawWindowBuilder(tokenizer);text,v=source(b);store=ObservationStore();bad=copy.deepcopy(v);bad['text']='corrupted'
    with pytest.raises(ValueError):store.record('search',{},[v,bad],b)
    assert store.sequence==0 and store.summary()['returned_windows']==0
    tools=ObservedTools(store);tools.window_builder=b
    with pytest.raises(ValueError):tools.execute('open',{'window_ref':v['window_ref'],'direction':'after'})
    store.close()


def test_failed_turn_rollback_audit_and_reset(tokenizer,tmp_path):
    count=0
    def handler(request):
        nonlocal count
        count+=1
        if count==1:return httpx.Response(200,json=reply(None,[{'id':'c','type':'function','function':{'name':'search','arguments':'{"query":"event"}'}}]))
        return httpx.Response(401,json={'error':{'message':'bad key','type':'authentication_error'}})
    session=ObservedAgentSession(config(),state_path=tmp_path/'state.sqlite',client=client(handler))
    session.tools.window_builder=RawWindowBuilder(tokenizer)
    class Searcher:
        def search(self,q,k):return [dict(docid='d',text='title: Test\nAn event occurred.',url='u',score=1)]
    session.tools.searcher=Searcher()
    with pytest.raises(Exception):session.ask('question')
    assert len(session.messages)==1 and session.observations.summary()['returned_windows']==0
    assert len(session.observations.events())==1 and not session.observations.events()[0]['active']
    session.reset();session.close()


def test_completed_session_resume_open_and_configuration(tokenizer,tmp_path):
    state=tmp_path/'state.sqlite';count=0
    def handler(request):
        nonlocal count
        count+=1
        if count==1:return httpx.Response(200,json=reply(None,[{'id':'c','type':'function','function':{'name':'search','arguments':'{"query":"event 73"}'}}]))
        return httpx.Response(200,json=reply('answer'))
    session=ObservedAgentSession(config(),state_path=state,client=client(handler));session.tools.window_builder=RawWindowBuilder(tokenizer)
    text,_=source(session.tools.window_builder)
    class Searcher:
        def search(self,q,k):return [dict(docid='d',text=text,url='u',score=1)]
    session.tools.searcher=Searcher();session.ask('question');messages=copy.deepcopy(session.messages);ref=next(iter(session.observations.seen));session.close()
    resumed=ObservedAgentSession(config(),state_path=state,client=client(lambda r:httpx.Response(200,json=reply('ok'))))
    assert resumed.messages==messages
    resumed.tools.window_builder=RawWindowBuilder(tokenizer)
    v=resumed.tools.execute('open',{'window_ref':ref,'direction':'after'})
    assert v['parent_window_ref']==ref
    # Simulate interruption before this extra observation reaches a completed turn.
    resumed.close()
    recovered=ObservedAgentSession(config(),state_path=state,client=client(lambda r:httpx.Response(200,json=reply('ok'))))
    assert recovered.observations.summary()['events']==1
    recovered.reset()
    with pytest.raises(ValueError):recovered.tools.execute('open',{'window_ref':ref,'direction':'after'})
    recovered.close()
    other=config();other.model='different'
    with pytest.raises(ValueError):ObservedAgentSession(other,state_path=state)


def test_persisted_source_corruption_fails_closed(tokenizer,tmp_path):
    b=RawWindowBuilder(tokenizer);text,v=source(b);store=ObservationStore(tmp_path/'state.sqlite');store.record('search',{},[v],b)
    with store.db:store.db.execute('UPDATE documents SET text=?',('changed',))
    with pytest.raises(ValueError):store.restore_window(RawWindowBuilder(tokenizer),v['window_ref'])
    store.close()


def test_safe_table_repair_keeps_existing_records(tokenizer):
    from llm_chat.structural_windows import TableEntryWindowBuilder,SafeTableEntryWindowBuilder
    text='title: Tables\n| Name | Detail |\n|---|---|\n| First | '+('long context '*40)+'|\n| Anchor | value |\n\nNext section\n| Name | Detail |\n|---|---|\n| Next | entry |\n'
    start=text.index('| First');end=text.index('|---',text.index('Next section'))
    anchor_start=text.index('| Anchor');anchor_end=text.index('\n',anchor_start)+1
    legacy=TableEntryWindowBuilder(tokenizer);safe=SafeTableEntryWindowBuilder(tokenizer)
    k1=legacy.register('d',text,'u');k2=safe.register('d',text,'u');budget=legacy.count(text[start:end])
    assert legacy._repair_table_entry(k1,start,end,(anchor_start,anchor_end),budget)!=(start,end)
    assert safe._repair_table_entry(k2,start,end,(anchor_start,anchor_end),budget)==(start,end)
    assert safe.last_repair['status']=='unchanged_existing_table_rows'


def test_safe_table_repair_still_allows_trimming_prose(tokenizer):
    from llm_chat.structural_windows import SafeTableEntryWindowBuilder
    b=SafeTableEntryWindowBuilder(tokenizer)
    text='title: Text\n'+('Earlier prose. '*40)+'\nAnchor sentence.\n\n| Name | Detail |\n|---|---|\n| First | value |\n'
    key=b.register('d',text,'u');start=text.index('Earlier');end=text.index('|---');a=text.index('Anchor');z=text.index('| Name');budget=b.count(text[start:end])
    new_start,new_end=b._repair_table_entry(key,start,end,(a,z),budget)
    assert new_start>start and new_start<=a and new_end==len(text)
    assert b.last_repair['status']=='repaired'


def test_state_file_has_single_writer(tmp_path):
    path=tmp_path/'state.sqlite';first=ObservationStore(path)
    with pytest.raises(ValueError,match='already in use'):ObservationStore(path)
    first.close()
    second=ObservationStore(path);second.close()
