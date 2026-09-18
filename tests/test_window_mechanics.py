from test_snippets import tokenizer
from llm_chat.raw_windows import RawWindowBuilder


def test_empty_title_does_not_consume_body(tokenizer):
    b=RawWindowBuilder(tokenizer)
    v=b.search('d','title:\n\nActual body sentence.','','body')
    assert v['title']==''


def test_boundary_repair_uses_full_document_units(tokenizer):
    b=RawWindowBuilder(tokenizer)
    text='title: Example\nFirst sentence is complete. Second sentence contains Orion and details.\n'
    key=b.register('d',text,'')
    start=text.index('contains');end=text.index('details')+len('details')
    a,z=b._repair_anchor(key,start,end,100)
    assert text[a:z]=='Second sentence contains Orion and details.\n'


def test_table_header_included_when_contiguous_range_fits(tokenizer):
    b=RawWindowBuilder(tokenizer)
    text='title: Cast\n\n| Film | Role |\n|---|---|\n| Alpha | Actor |\n| Orion | Constable |\n'
    key=b.register('d',text,'');a=text.index('| Orion');z=len(text)
    a,z=b._repair_anchor(key,a,z,100)
    assert text[a:z].startswith('| Film | Role |')
    assert '| Orion | Constable |' in text[a:z]
