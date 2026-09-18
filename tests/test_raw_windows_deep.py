"""Boundary and continuation regression checks, without external API calls."""
import pytest
from test_snippets import tokenizer
from llm_chat.raw_windows import RawWindowBuilder

@pytest.mark.parametrize('text',[
    '   \n\n',
    'title: '+('Long title '*100)+'\n'+'正文🙂 café. '*300,
    'title:\n\nBody without a title.\n'+('Orion sentence. '*300),
    '# Heading\n'+('| Alice | Orion | 2005 |\n'*200),
    'title: Unicode\n'+('很长的句子没有换行🙂'*400),
    'title: Test\n'+('Before.\n'*100)+'Orion marker.\n'+('After.\n'*700)+'\n\n',
])
def test_roundtrip_paging_and_around_saturation(tokenizer,text):
    b=RawWindowBuilder(tokenizer)
    hit=b.search('test',text,'u','Orion')
    assert hit['text_tokens']+hit['title_tokens']<=400
    if hit['title_span']:
        a,z=hit['title_span'];assert text[a:z]==hit['title']
    original=b.windows[hit['window_ref']]
    for direction in ('before','after'):
        cursor=hit
        for _ in range(100):
            if not cursor['has_more_'+direction]:break
            new=b.open(cursor['window_ref'],direction)
            assert new['text']==text[new['offset']:new['end_char']]
            assert new['text_tokens']+new['title_tokens']<=1200
            if direction=='after':
                assert new['offset']==cursor['end_char'] and new['end_char']>cursor['end_char']
            else:
                assert new['end_char']==cursor['offset'] and new['offset']<cursor['offset']
            cursor=new
        assert not cursor['has_more_'+direction]
    cursor=hit
    for _ in range(20):
        new=b.open(cursor['window_ref'],'around')
        assert new['offset']<=cursor['offset'] and new['end_char']>=cursor['end_char']
        assert new['text_tokens']+new['title_tokens']<=2400
        if new['window_ref']==cursor['window_ref']:
            assert new['status']==('document_complete' if new['offset']==0 and new['end_char']==len(text) else 'no_expansion_within_budget');break
        cursor=new
    else:pytest.fail('around failed to converge')
    assert b.windows[hit['window_ref']]==original
