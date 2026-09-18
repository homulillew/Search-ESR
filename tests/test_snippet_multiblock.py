from experiments.snippets.compare_multiblock import rank_chunks, choose_two
from experiments.snippets.selector import Selector
from test_snippets import tokenizer


def test_same_top_one_and_disjoint_second(tokenizer):
    s=Selector(tokenizer,budget=64,overlap=8)
    text=('Orion actor film role.\n'*35)+'\n'+('Orion played a constable.\n'*25)
    chunks=s.chunks('x',text)
    first,reason=s.select('Orion constable',chunks)
    ranked=rank_chunks('Orion constable',chunks)
    selected,_=choose_two(ranked)
    assert selected[0]['chunk_id']==first.chunk_id
    assert abs(selected[0]['score']-reason['score'])<1e-9
    assert len(selected)==2
    a,b=selected
    assert a['end_char']<=b['start_char'] or b['end_char']<=a['start_char']
    assert choose_two(rank_chunks('zzzzzz',chunks))[0]==[]


def test_skips_overlap_and_keeps_score_order():
    ranked=[{'start_char':0,'end_char':100,'score':4},
            {'start_char':80,'end_char':140,'score':3},
            {'start_char':100,'end_char':170,'score':2}]
    selected,skipped=choose_two(ranked)
    assert [c['bm25_rank'] for c in selected]==[1,3]
    assert skipped==[2]
