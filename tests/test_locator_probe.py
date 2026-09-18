from experiments.snippets.probe_locator import score_terms,rank
from llm_chat.window_locator import Chunk


def test_score_pair_keeps_order_and_normalizes_dash():
    assert score_terms('win 4-3 then 4–0')==score_terms('win 4–3 then 4-0')
    assert 'scorepair4x3' in score_terms('4-3')
    assert not {'4','3'} & set(score_terms('4-3'))
    assert score_terms('4-3')!=score_terms('3-4')
    assert '2023' in score_terms('in 2023 won 4-3')


def test_score_ranking_separates_numeric_overlap():
    chunks=[Chunk('a',0,10,'result 0–3',5,'line'),Chunk('b',10,20,'result 4–3',5,'line')]
    out=rank('4-3',chunks,score_terms)
    assert out[0][2].chunk_id=='b'
    assert out[1][0]==0
