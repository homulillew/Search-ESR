from experiments.snippets.short_window import shorten
from experiments.snippets.selector import Selector
from test_snippets import tokenizer


def parent(text,tokenizer):
    return dict(chunk_id='p',start_char=100,end_char=100+len(text),text=text,tokens=Selector(tokenizer).count(text))


def test_late_match_and_global_offsets(tokenizer):
    text='The weather is mild. '*35+'Orion played the constable. His name is Alice.\n'
    p=parent(text,tokenizer);r=shorten('Orion constable',p,64,tokenizer)
    assert 'Orion played the constable.' in r['text']
    assert r['start_char']>100
    assert r['text']==text[r['start_char']-100:r['end_char']-100]
    assert r['tokens']<=64
    assert r['anchor']['start_char']>=100
    assert r['parent_chunk_id']=='p'


def test_table_row_intact_and_fitting_block_unchanged(tokenizer):
    text='| Film | Role |\n'+''.join(f'| Film{i} | Person{i} |\n' for i in range(20))+'| Orion | Constable |\n'
    r=shorten('Orion Constable',parent(text,tokenizer),64,tokenizer)
    assert '| Orion | Constable |\n' in r['text']
    assert r['text'].endswith('\n')
    p=parent('Short document.',tokenizer)
    r=shorten('zzzzz',p,64,tokenizer)
    assert r['text']==p['text'] and r['method']=='unchanged_fits'
