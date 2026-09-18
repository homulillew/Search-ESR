import copy
import json
from types import SimpleNamespace

import pytest

from experiments.query_initialization.single_entry.source_units import build_question
from experiments.query_initialization.basis_packet.packet import build_packet, check_packet, model_view, verbatim, query_token_count, validate_selection
from experiments.query_initialization.basis_packet.generate import build_messages, generate, parse


class Tokenizer:
    def __call__(self, text, **kwargs):
        assert kwargs == dict(add_special_tokens=True, truncation=False)
        return {'input_ids': [0] + list(text) + [1]}


class Client:
    def __init__(self, contents, finish='stop'):
        self.contents = iter(contents)
        self.calls = []
        self.finish = finish
        self.chat = SimpleNamespace(completions=self)

    def create(self, **kwargs):
        self.calls.append(copy.deepcopy(kwargs))
        return SimpleNamespace(choices=[SimpleNamespace(finish_reason=self.finish,
            message=SimpleNamespace(content=next(self.contents), tool_calls=None))])


class Config:
    model = 'test-model'

    def request_options(self):
        return {'extra_body': {'enable_thinking': False}}


@pytest.fixture
def source():
    return build_question('An author was born in 1964. Hidden unrelated clue. They published a paper before 2010.')


def test_packet_exact_order_and_no_model_ids(source):
    packet = build_packet(source, ['q3', 'q1'])
    assert packet['selected_refs'] == ['q1', 'q3']
    assert packet['input_refs'] == ['q1', 'q3']
    assert packet['segments'][0]['text'] == source['units'][0]['text']
    assert model_view(packet) == {'selected_texts': [source['units'][i]['text'] for i in [0, 2]], 'context_texts': []}
    assert verbatim(packet) == 'An author was born in 1964.\n\nThey published a paper before 2010.'
    check_packet(packet, source)


@pytest.mark.parametrize('refs', [['q99'], ['q1', 'q1'], [], [1]])
def test_invalid_selection_cannot_be_resolved(source, refs):
    with pytest.raises(ValueError):
        build_packet(source, refs)
    assert not validate_selection({'selected_units': []}, source)


def test_packet_scope_and_excerpt_integrity(source):
    packet = build_packet(source, ['q1'])
    changed = build_question('Different text. Hidden unrelated clue. They published a paper before 2010.')
    with pytest.raises(ValueError, match='version'):
        check_packet(packet, changed)
    packet['segments'][0]['text'] = 'Invented fact'
    with pytest.raises(ValueError, match='excerpts'):
        check_packet(packet, source)


def test_same_system_and_only_full_context_payload_differs(source):
    packet = build_packet(source, ['q1'])
    isolated = build_messages(packet, 'expression_packet', source)
    control = build_messages(packet, 'expression_full_context', source)
    assert isolated[0] == control[0]
    assert 'Hidden unrelated clue' not in isolated[1]['content']
    control_payload = json.loads(control[1]['content'])
    assert control_payload.pop('question_context') == source['text']
    assert control_payload == json.loads(isolated[1]['content'])
    assert 'q1' not in isolated[1]['content']


def test_budget_includes_prefix_and_special_tokens():
    assert query_token_count('abc', Tokenizer(), 'xy') == 7
    assert not parse('{"query":"abc"}', Tokenizer(), 'xy', 7)[1]
    assert parse('{"query":"abc"}', Tokenizer(), 'xy', 6)[1]
    assert not parse('{"query":null}', Tokenizer(), 'xy', 6)[1]
    assert parse('{"query":" "}', Tokenizer(), '', 6)[1]


def test_repair_keeps_isolation_and_records_original_call(source):
    packet = build_packet(source, ['q1'])
    client = Client(['not JSON', '{"query":"born in 1964 author"}'])
    result = generate(client, Config(), packet, 'conservative', Tokenizer(), '', question=source)
    assert result['status'] == 'valid' and result['repairs'] == 1
    assert result['input_refs'] == ['q1']
    assert len(client.calls[0]['messages']) == 2
    assert len(client.calls[1]['messages']) == 4
    assert 'Hidden unrelated clue' not in json.dumps(client.calls)
    assert client.calls[0]['max_tokens'] == 1536


def test_null_abstains_without_repair(source):
    client = Client(['{"query":null}'])
    result = generate(client, Config(), build_packet(source, ['q1']), 'conservative', Tokenizer(), '')
    assert result['status'] == 'abstained' and result['repairs'] == 0
    assert result['query_tokens'] is None and len(client.calls) == 1


def test_budget_rejected_before_api(source):
    client = Client([])
    with pytest.raises(ValueError, match='packet_over_budget'):
        generate(client, Config(), build_packet(source, ['q1']), 'conservative', Tokenizer(), '', max_query_tokens=5)
    assert not client.calls


def test_nonstop_has_no_repair_or_salvage(source):
    client = Client(['{"query":"valid JSON but truncated"}'], finish='length')
    with pytest.raises(ValueError, match='Incomplete'):
        generate(client, Config(), build_packet(source, ['q1']), 'conservative', Tokenizer(), '')
    assert len(client.calls) == 1


def test_full_context_records_actual_sources(source):
    client = Client(['{"query":"author born 1964"}'])
    result = generate(client, Config(), build_packet(source, ['q1']), 'expression_full_context', Tokenizer(), '', source)
    assert result['input_refs'] == ['q1', 'q2', 'q3']


def test_at_most_one_repair(source):
    client = Client(['{}', '{}'])
    result = generate(client, Config(), build_packet(source, ['q1']), 'conservative', Tokenizer(), '')
    assert result['status'] == 'invalid' and result['repairs'] == 1
    assert len(client.calls) == 2
