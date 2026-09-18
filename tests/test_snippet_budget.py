from experiments.snippets.compare_multiblock import choose_two
from experiments.snippets.compare_budget import fit_blocks
from experiments.snippets.selector import Selector
from test_snippets import tokenizer


def test_whitespace_only_overlap():
    ranked=[dict(start_char=0,end_char=4,score=3),dict(start_char=3,end_char=7,score=2)]
    assert len(choose_two(ranked)[0])==1
    assert len(choose_two(ranked,'abc\ndef')[0])==2
    assert len(choose_two(ranked,'abcdefg')[0])==1


def test_shared_budget_and_short_block_transfer(tokenizer):
    s=Selector(tokenizer)
    raw=['Short text.','Long text. '*180]
    blocks=[dict(chunk_id=str(i),start_char=0,end_char=len(t),text=t,tokens=s.count(t)) for i,t in enumerate(raw)]
    fitted=fit_blocks(blocks,tokenizer)
    assert sum(c['tokens'] for c in fitted)<=400
    assert fitted[1]['allocated_cap']>200
    assert fitted[0]['text']==raw[0]
    for c,t in zip(fitted,raw):
        assert c['text']==t[c['start_char']:c['end_char']]
        assert c['tokens']==s.count(c['text'])
