from experiments.snippets.window import WindowSelector
from test_snippets import tokenizer


def test_expands_whole_sentences_and_keeps_raw_span(tokenizer):
    s = WindowSelector(tokenizer,budget=64,overlap=8)
    text = '# Biography\nAlice works in cinema. She played the constable in Orion. Her father was a musician.\n# Other\nUnrelated story.'
    result = s.observe('constable Orion',text,s.units('d',text))
    assert 'Alice works' in result['text']
    assert 'Her father' in result['text']
    assert 'Unrelated' not in result['text']
    assert result['text']==text[result['start_char']:result['end_char']]
    assert result['tokens']<=64
    assert result['stop']['after']=='section_boundary'


def test_table_row_and_oversize_fallback(tokenizer):
    s = WindowSelector(tokenizer,budget=64,overlap=8)
    text = '| Name | Role |\n| Alice | Constable |\n| Bob | Doctor |\n'
    result = s.observe('Constable',text,s.units('table',text))
    assert result['anchor']['text']=='| Alice | Constable |\n'
    assert '| Name | Role |' in result['text']
    long = 'word '*250
    result = s.observe('word',long,s.units('long',long))
    assert result['anchor']['boundary']=='oversize_split'
    assert result['tokens']<=64
    result = s.observe('zzzz',text,s.units('table',text))
    assert result['selection']['fallback']=='no_lexical_match_use_prefix'
