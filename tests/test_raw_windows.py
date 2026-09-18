import json
import pytest
from test_snippets import tokenizer
from llm_chat.raw_windows import RawWindowBuilder
from llm_chat.agent import BCPlusTools,TOOLS


def test_immutable_reference_and_continuation(tokenizer):
    b=RawWindowBuilder(tokenizer)
    text='title: Actor Biography\n'+('Introductory material.\n'*100)+'Orion played the constable.\n'+('Later material.\n'*700)
    hit=b.search('d',text,'url','Orion constable')
    assert 'Orion played the constable.' in hit['text']
    assert hit['text_tokens']+hit['title_tokens']<=400
    saved=b.windows[hit['window_ref']]
    expanded=b.open(hit['window_ref'],'around')
    assert expanded['offset']<=hit['offset'] and expanded['end_char']>=hit['end_char']
    assert hit['text'] in expanded['text']
    assert b.windows[hit['window_ref']]==saved
    following=b.open(hit['window_ref'],'after')
    assert following['offset']==hit['end_char']
    assert following['end_char']>following['offset']
    previous=b.open(hit['window_ref'],'before')
    assert previous['end_char']==hit['offset']
    for v in [hit,expanded,following,previous]:
        assert v['text']==text[v['offset']:v['end_char']]
    with pytest.raises(ValueError):b.open('unknown','after')
    with pytest.raises(ValueError):b.open(hit['window_ref'],'focus')
    # Document updates cannot change the old window or its continuation.
    b.search('d','title: Changed\nDifferent body.','url','body')
    assert b.open(hit['window_ref'],'around')['text']==expanded['text']


def test_tool_contract_empty_and_boundaries(tokenizer):
    b=RawWindowBuilder(tokenizer)
    empty=b.search('e','','','x')
    assert empty['text']==''
    assert b.open(empty['window_ref'],'after')['status']=='document_boundary'
    assert b.open(empty['window_ref'],'around')['status']=='document_complete'
    t=BCPlusTools();t.window_builder=b
    class FakeSearcher:
        def search(self,query,k):return [{'docid':'d','text':'title: Alice\nAlice played Orion.','url':'u','score':1}]
    t.searcher=FakeSearcher()
    hit=t.execute('search',{'query':'Orion'})[0]
    assert t.execute('open',{'window_ref':hit['window_ref'],'direction':'around'})['text']==hit['text']
    assert {x['function']['name'] for x in TOOLS}=={'search','open'}
    json.dumps(hit)
    t.close()
