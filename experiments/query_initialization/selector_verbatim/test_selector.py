import copy
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from experiments.query_initialization.single_entry.source_units import build_question
from experiments.query_initialization.basis_packet.packet import check_packet
from experiments.query_initialization.selector_verbatim.selector import build_messages, generate, parse


class Tokenizer:
    def __call__(self, text, **kwargs):
        assert kwargs == dict(add_special_tokens=True, truncation=False)
        return {'input_ids': [0] + list(text) + [1]}


class Client:
    def __init__(self, contents, finish='stop'):
        self.contents = iter(contents)
        self.finish = finish
        self.calls = []
        self.chat = SimpleNamespace(completions=self)

    def create(self, **kwargs):
        # Keep originals too: subsequent repair must not mutate a recorded request.
        self.calls.append(kwargs)
        content = next(self.contents)
        if isinstance(content, Exception):
            raise content
        return SimpleNamespace(choices=[SimpleNamespace(
            finish_reason=self.finish,
            message=SimpleNamespace(content=content, tool_calls=None))])


class Config:
    model = 'test-model'

    def request_options(self):
        return {'extra_body': {'enable_thinking': False}}


@pytest.fixture
def question():
    return build_question('Which journal?\nMajor eloped with a person whose sibling earned degrees.\nThat sibling reviewed the journal from 1824 to 1832.')


def test_prompt_is_frozen_source_and_model_only_sees_original_material(question):
    here = Path(__file__).parent
    assert (here / 'SELECTOR_PROMPT.txt').read_bytes() == (here.parent / 'basis_packet/SELECTOR_PROMPT.txt').read_bytes()
    enriched = dict(question, gold_answer='DO NOT LEAK', evidence=['hidden'])
    messages = build_messages(enriched)
    payload = json.loads(messages[1]['content'])
    assert set(payload) == {'question', 'question_units'}
    assert payload['question'] == question['text']
    assert payload['question_units'] == [dict(ref=u['ref'], text=u['text']) for u in question['units']]
    assert 'DO NOT LEAK' not in json.dumps(messages)


def test_reverse_selection_preserves_raw_order_but_search_keeps_original_relations(question):
    client = Client(['{"selected_units":["q3","q2"]}'])
    result = generate(client, Config(), question, Tokenizer(), 'Query:')
    assert result['selected_units'] == ['q3', 'q2']
    assert result['input_refs'] == ['q2', 'q3']
    assert result['selector_input_refs'] == ['q1', 'q2', 'q3']
    assert result['query'] == ('Major eloped with a person whose sibling earned degrees.\n\n'
                               'That sibling reviewed the journal from 1824 to 1832.')
    assert result['status'] == 'valid' and result['initial_valid'] and result['repairs'] == 0
    check_packet(result['packet'], question)


@pytest.mark.parametrize('content', ['{}', '{"selected_units":["q99"]}',
    '{"selected_units":["q1","q1"]}', '{"selected_units":[1]}',
    '{"selected_units":["q1"],"query":"invented"}', '```json\n{}\n```'])
def test_invalid_contract_gets_exactly_one_repair(question, content):
    client = Client([content, '{"selected_units":["q2"]}'])
    result = generate(client, Config(), question, Tokenizer(), '')
    assert result['status'] == 'valid' and not result['initial_valid']
    assert result['repairs'] == 1 and result['initial_errors'] and not result['errors']
    assert len(client.calls) == 2
    assert len(client.calls[0]['messages']) == 2
    assert len(client.calls[1]['messages']) == 4
    assert client.calls[1]['messages'][:2] == build_messages(question)
    assert client.calls[0]['max_tokens'] == 1536
    assert client.calls[0]['extra_body'] == {'enable_thinking': False}


def test_repair_exhaustion_does_not_fallback(question):
    client = Client(['{}', '{"selected_units":["q99"]}'])
    result = generate(client, Config(), question, Tokenizer(), '')
    assert result['status'] == 'invalid' and result['repairs'] == 1
    assert result['packet'] is None and result['query'] is None
    assert result['selected_units'] is None and len(client.calls) == 2


def test_empty_is_no_basis_not_format_error(question):
    client = Client(['{"selected_units":[]}'])
    result = generate(client, Config(), question, Tokenizer(), '')
    assert result['status'] == 'no_basis' and result['initial_valid']
    assert result['selected_units'] == [] and result['repairs'] == 0
    assert result['query'] is None and result['packet'] is None
    assert len(client.calls) == 1


def test_budget_includes_prefix_and_specials_never_reselects_or_clips():
    question = build_question('Hello.')
    for limit, expected in [(10, 'valid'), (9, 'packet_over_budget')]:
        client = Client(['{"selected_units":["q1"]}'])
        result = generate(client, Config(), question, Tokenizer(), 'xy', limit)
        assert result['query_tokens'] == 10 and result['status'] == expected
        assert result['query'] == 'Hello.' and result['packet'] is not None
        assert result['repairs'] == 0 and result['initial_valid'] and len(client.calls) == 1


def test_whitespace_only_normalization_preserves_dates_and_negation():
    question = build_question('Not\tretired by 2020.\nReleased between 2008 and 2011, inclusive.')
    result = generate(Client(['{"selected_units":["q1","q2"]}']), Config(), question, Tokenizer(), '')
    assert result['query'] == 'Not retired by 2020.\n\nReleased between 2008 and 2011, inclusive.'
    assert result['packet']['segments'][0]['text'] == question['units'][0]['text']


def test_source_version_and_mapping_checked_before_api(question):
    changed = copy.deepcopy(question)
    changed['text'] = 'Different source'
    client = Client([])
    with pytest.raises(ValueError, match='version'):
        generate(client, Config(), changed, Tokenizer(), '')
    assert not client.calls
    changed = copy.deepcopy(question)
    changed['units'][0]['ref'] = 'q99'
    with pytest.raises(ValueError, match='mapping'):
        build_messages(changed)


def test_nonstop_and_api_failure_do_not_trigger_repair(question):
    client = Client(['{"selected_units":["q1"]}'], finish='length')
    with pytest.raises(ValueError, match='Incomplete'):
        generate(client, Config(), question, Tokenizer(), '')
    assert len(client.calls) == 1
    client = Client([RuntimeError('transport failure')])
    with pytest.raises(RuntimeError, match='transport'):
        generate(client, Config(), question, Tokenizer(), '')
    assert len(client.calls) == 1


def test_parse_rejects_null_selection(question):
    value, errors = parse('{"selected_units":null}', question)
    assert value == {'selected_units': None} and errors
