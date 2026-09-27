from copy import deepcopy
from dataclasses import replace
import hashlib
import pytest
from conftest import bridge, action
from llm_chat.recoverable_loop.contracts import action_schema, validate_action, parse_json
from llm_chat.search_find_agent import SEARCH_FIND_TOOLS


def test_schema_is_actual_executor_schema():
    for variant, real in zip(action_schema()['oneOf'], SEARCH_FIND_TOOLS):
        assert variant['properties']['arguments'] == real['function']['parameters']


@pytest.mark.parametrize('orthogonal', [False, True])
def test_search_find_miss_and_empty_search(orthogonal):
    b = bridge(orthogonal=orthogonal)
    first = b.execute(action())
    assert first['new_document_refs'] == ['D1']
    found = b.execute(action('find', doc_ref='D1', query='Alice'))
    assert found['windows'][0] == first['windows'][0]
    missed = b.execute(action('find', doc_ref='D1', query='zzzzunknown'))
    assert missed['result']['status'] == 'no_match' and not missed['windows']
    assert missed['inspected_sources'] == ['D1']
    assert not bridge(hits=[], orthogonal=orthogonal).execute(action())['windows']
    if orthogonal:
        again = b.execute(action())
        assert not again['windows']
        assert again['result']['results'][0]['existing_preview_ref'] == 'W1'


@pytest.mark.parametrize('direction', ['before', 'after', 'around'])
def test_all_open_directions_real_dispatch_and_preserved_spans(direction, monkeypatch):
    text = 'title: Long source\n' + ''.join(f'Paragraph {i} '+('alpha ' * 80)+'\n\n' for i in range(60))
    b = bridge(text)
    b.execute(action(query='Paragraph 30'))
    # Deterministically seed a middle observed span; bypass only retrieval ranking.
    builder = b.tools.window_builder
    key = b.tools.handles.resolve_document('D1')
    start = text.index('Paragraph 30'); end = text.index('Paragraph 31')
    raw = builder._emit(key, start, end)
    wr, _ = b.tools.handles.window(raw['window_ref'])
    b.evidence.add(b._normalize({'tool': 'open', 'raw_result': raw, 'handles': b.tools.handles.snapshot()}))
    old = b.evidence.get(wr)
    calls = []; original = b.tools.execute
    def execute(name, arguments):
        calls.append((name, deepcopy(arguments))); return original(name, arguments)
    monkeypatch.setattr(b.tools, 'execute', execute)
    act = action('open', window_ref=wr, direction=direction)
    out = b.execute(act)['windows'][0]
    assert calls == [('open', act['arguments'])]
    assert out.text == text[out.offset:out.end_char]
    assert b.evidence.get(wr) == old
    if direction == 'before': assert out.end_char == old.offset
    elif direction == 'after': assert out.offset == old.end_char
    else: assert out.offset <= old.offset and out.end_char >= old.end_char
    assert (out.offset, out.end_char) != (old.offset, old.end_char)


@pytest.mark.parametrize('invalid', [
    action('find', doc_ref='D999', query='Alice'), action('open', window_ref='W999', direction='around'),
    action('find', doc_ref='W1', query='Alice'), action('open', window_ref='D1', direction='after'),
    action('open', window_ref='W1', direction='Alice'), action('open', source_ref='W1', pattern='Alice'),
    {'tool': 'find', 'doc_ref': 'D1', 'query': 'Alice'}, action(query=''), action(query='x'*16001),
    action(query='Alice', k=0), action(query='Alice', k=11), action(query='Alice', k=True),
    action(query='Alice', k=2.0), action(query='Alice', pattern='oops'), action('STOP', answer='Alice'),
])
def test_invalid_action_never_repaired_or_executed(invalid):
    b = bridge(); b.execute(action()); count = len(b.tools.searcher.calls)
    with pytest.raises(ValueError): b.execute(invalid)
    assert len(b.tools.searcher.calls) == count


def test_new_document_bytes_get_new_handle_and_old_text_stays_pinned():
    b = bridge(); first = b.execute(action())['windows'][0]
    b.tools.searcher.hits[0]['text'] += '\nNew document revision.'
    second = b.execute(action())['windows'][0]
    assert second.doc_ref != first.doc_ref
    assert second.document_sha256 != first.document_sha256
    assert b.execute(action('open', window_ref=first.window_ref, direction='around'))['windows'][0] == first
    with pytest.raises(ValueError): b.evidence.add([replace(first, text='tampered')])
    bad = replace(first, text='X'*len(first.text), text_sha256=hashlib.sha256(('X'*len(first.text)).encode()).hexdigest())
    with pytest.raises(ValueError): b.evidence.add([bad])


@pytest.mark.parametrize('raw', ['{"decision":"acquire","decision":"request_closure"}', '{"k":NaN}'])
def test_duplicate_or_nonfinite_json_rejected(raw):
    with pytest.raises(ValueError): parse_json(raw)


def test_raw_canonical_identity_cannot_be_rebound_to_another_span():
    b = bridge(); batch = b.execute(action()); audit = deepcopy(batch['audit'])
    raw = audit['raw_result'][0]
    raw['offset'] += 1; raw['text'] = raw['text'][1:]
    with pytest.raises(ValueError, match='identity'): b._normalize(audit)
