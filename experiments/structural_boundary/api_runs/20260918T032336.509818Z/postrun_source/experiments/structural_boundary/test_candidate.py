import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tests'))
from test_snippets import tokenizer
from experiments.structural_boundary.candidate import TableEntryWindowBuilder

def document(b):
    text='title: Example\n\n'+'Earlier background sentence. '*12+'\nAnchor sentence.\n\n| Film | Role |\n|---|---|\n| Example | Officer |\n| Other | Guest |\n'
    key=b.register('doc',text,'');return text,key

def test_complete_first_row_preserves_anchor_under_budget(tokenizer):
    b=TableEntryWindowBuilder(tokenizer);text,key=document(b)
    anchor=(text.index('Anchor sentence.'),text.index('| Film'))
    start=text.index('Earlier');end=text.index('|---')
    row_end=text.index('| Other')
    cap=b.count(text[anchor[0]:row_end])
    a,z=b._repair_table_entry(key,start,end,anchor,cap)
    assert a<=anchor[0] and z>=anchor[1]
    assert a>start and z==row_end
    assert b.count(text[a:z])<=cap
    assert '| Film | Role |\n|---|---|\n| Example | Officer |\n' in text[a:z]

def test_budget_failure_keeps_original_span(tokenizer):
    b=TableEntryWindowBuilder(tokenizer);text,key=document(b)
    start=text.index('Earlier');end=text.index('|---')
    cap=b.count(text[start:end])
    assert b.count(text[start:text.index('| Other')])>cap
    assert b._repair_table_entry(key,start,end,(start,end),cap)==(start,end)

def test_complete_table_entry_is_unchanged(tokenizer):
    b=TableEntryWindowBuilder(tokenizer);text,key=document(b)
    start=text.index('Earlier');end=len(text)
    assert b._repair_table_entry(key,start,end,(start,start+10),400)==(start,end)

def test_open_does_not_apply_search_repair(tokenizer):
    b=TableEntryWindowBuilder(tokenizer);text,key=document(b)
    v=b._emit(key,0,text.index('|---'))
    result=b.open(v['window_ref'],'after')
    assert result['offset']==v['end_char']
    assert result['text']==text[result['offset']:result['end_char']]
    assert b.last_repair is None


def test_no_data_row_does_not_expand_table_header(tokenizer):
    b=TableEntryWindowBuilder(tokenizer)
    text='title: Empty table\nAnchor sentence.\n| Film | Role |\n|---|---|\n'
    key=b.register('d',text,'');start=text.index('Anchor');end=text.index('|---')
    assert b._repair_table_entry(key,start,end,(start,start+16),400)==(start,end)


def test_unfinished_first_row_completes_without_losing_anchor(tokenizer):
    b=TableEntryWindowBuilder(tokenizer);text,key=document(b)
    start=text.index('Anchor');end=text.index('Officer')+3
    a,z=b._repair_table_entry(key,start,end,(start,text.index('| Film')),400)
    assert a==start and z==text.index('| Other')
    assert text[a:z].endswith('| Example | Officer |\n')
