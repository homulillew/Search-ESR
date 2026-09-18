import json
from pathlib import Path
import pytest
from experiments.query_initialization.single_entry.test_single_entry import Client, CONFIG
from .generate import generate, payload, parse

CASES = json.loads(Path(__file__).with_name('cases.json').read_text())


def test_manual_deletion_changes_only_the_predeclared_span():
    for c in CASES:
        a, b = c['removed_span']
        assert c['full_query'][a:b] == c['removed_text']
        assert c['full_query'][:a] + c['full_query'][b:] == c['delete_query']
        assert len(c['full_query']) <= 512


def test_model_never_receives_controls_or_answers():
    for c in CASES:
        data = payload(c)
        assert set(data) == {'question', 'fixed_target', 'selected_clues'}
        assert [u['ref'] for u in data['selected_clues']] == c['basis_refs']
        for u in data['selected_clues']:
            assert u['text'] in data['question']
    client = Client(['{"query":"A person"}'])
    generate(client, CONFIG, CASES[0])
    user = json.loads(client.requests[0]['messages'][1]['content'])
    assert user == payload(CASES[0])
    assert 'tools' not in client.requests[0]


def test_parse_does_not_claim_semantic_validation():
    assert parse('{"query":"sibling of Major"}')[1] == []
    assert parse('{"query":"x", "goal":"extra"}')[1]
    assert parse('{"query":""}')[1]
    assert parse(json.dumps({'query': 'x' * 513}))[1]


def test_one_format_repair_no_feedback_and_no_truncated_salvage():
    client = Client(['{', '{"query":"literary reviewer"}'])
    result = generate(client, CONFIG, CASES[0])
    assert result['status'] == 'valid' and result['repairs'] == 1
    assert client.requests[0]['messages'][1] == client.requests[1]['messages'][1]
    client = Client(['{', '{'])
    assert generate(client, CONFIG, CASES[0])['status'] == 'invalid'
    client = Client([('{"query":"x"}', 'length')])
    with pytest.raises(ValueError, match='Incomplete'):
        generate(client, CONFIG, CASES[0])
    assert len(client.requests) == 1
