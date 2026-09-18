import pytest
from transformers import AutoTokenizer
from experiments.snippets.selector import Selector


@pytest.fixture(scope='module')
def tokenizer():
    return AutoTokenizer.from_pretrained('/data/model/Qwen3-Embedding-8B',local_files_only=True,use_fast=True)


def test_chunks_cover_original_with_stable_ids_and_token_bound(tokenizer):
    s=Selector(tokenizer,budget=64,overlap=8)
    text=('Heading\n\n普通说明 café 🙂. '+ 'filler '*70+'\n\n')*5
    chunks=s.chunks('d',text)
    assert [c.chunk_id for c in chunks]==[c.chunk_id for c in s.chunks('d',text)]
    covered=0
    for c in chunks:
        assert c.start_char<=covered
        assert c.text==text[c.start_char:c.end_char]
        assert c.tokens<=64
        covered=max(covered,c.end_char)
    assert covered==len(text)
    assert s.count(s.prefix(text))<=64
    assert s.chunks('other',text)[0].chunk_id!=chunks[0].chunk_id


def test_query_finds_later_relation_without_gold(tokenizer):
    s=Selector(tokenizer,budget=64,overlap=8)
    text=('The weather is mild and trees are green.\n\n'*40)+ 'Match record\n\nOrion defeated Vega 4-0 in the semifinal.\n\n'+('The flowers are yellow.\n\n'*20)
    chunk,reason=s.select('Orion Vega semifinal',s.chunks('x',text))
    assert chunk.start_char>0
    assert 'Orion defeated Vega 4-0' in chunk.text
    assert reason['fallback'] is None
    chunk,reason=s.select('zzzznotpresent',s.chunks('x',text))
    assert chunk is None and reason['fallback']=='no_lexical_match_use_prefix'


def test_table_rows_not_cut_when_line_fits(tokenizer):
    s=Selector(tokenizer,budget=64,overlap=8)
    text='| Player | Opponent | Score |\n|---|---|---|\n'+''.join(f'| Player{i} | Other{i} | 4-0 |\n' for i in range(30))
    for c in s.chunks('table',text):
        assert c.start_char==0 or text[c.start_char-1]=='\n'
        assert c.end_char==len(text) or text[c.end_char-1]=='\n'
