"""Offline checks for the bounded prompt ablation; no API or retrieval calls."""
import copy
import json

import pytest

from llm_chat.agent import AGENT_PROMPT, TOOLS
from experiments.query_initialization.exploratory_policy.policy import (
    GUIDANCE, PROBE, action, request, schemas, system_prompt,
)


class Config:
    model = 'fake-model'
    system_prompt = 'Fake common system instruction.'

    def request_options(self):
        return {'extra_body': {'enable_thinking': False}}


def call(name='search', arguments=None, call_id='call_1'):
    if arguments is None:
        arguments = {'query': 'some exact source query'}
    return {'id': call_id, 'type': 'function', 'function': {
        'name': name, 'arguments': json.dumps(arguments, ensure_ascii=False)}}


def message(*calls, content=None):
    value = {'role': 'assistant'}
    if calls:
        value['tool_calls'] = list(calls)
    if content is not None:
        value['content'] = content
    return value


def test_b_only_appends_guidance_to_same_control_prompt():
    a = system_prompt(Config(), 'current')
    b = system_prompt(Config(), 'exploratory')
    assert a == Config.system_prompt + '\n\n' + AGENT_PROMPT + '\n\n' + PROBE
    assert b == a + '\n\n' + GUIDANCE
    assert GUIDANCE not in a
    with pytest.raises(ValueError):
        system_prompt(Config(), 'other')


def test_schema_isolated_from_default_tools_and_each_request():
    original = copy.deepcopy(TOOLS)
    first = schemas()
    second = schemas()
    assert TOOLS == original
    assert first == second and first is not second
    assert first[0]['function']['parameters']['properties']['k']['enum'] == [6]
    assert first[1] == original[1]
    first[0]['function']['name'] = 'mutated'
    first[1]['function']['parameters']['required'].append('unexpected')
    assert TOOLS == original and schemas() == second


def test_request_forces_first_search_only_then_auto_and_preserves_history():
    history = [{'role': 'system', 'content': 'system'}, {'role': 'user', 'content': 'question'}]
    first = request(Config(), history, 1)
    second = request(Config(), history, 2)
    assert first['tool_choice'] == {'type': 'function', 'function': {'name': 'search'}}
    assert second['tool_choice'] == 'auto'
    common_first = {k: v for k, v in first.items() if k != 'tool_choice'}
    common_second = {k: v for k, v in second.items() if k != 'tool_choice'}
    assert common_first == common_second
    assert first['parallel_tool_calls'] is False
    assert first['stream'] is False and first['max_tokens'] == 1536
    assert first['extra_body'] == {'enable_thinking': False}
    first['messages'][0]['content'] = 'mutated'
    assert history[0]['content'] == 'system'
    assert second['messages'][0]['content'] == 'system'


@pytest.mark.parametrize('step', [1, 2])
@pytest.mark.parametrize('with_k', [False, True])
def test_search_preserves_exact_query_with_optional_fixed_k(step, with_k):
    query = '  person whose sister retired by 2020\n原始关系  '
    arguments = {'query': query}
    if with_k:
        arguments['k'] = 6
    raw = message(call(arguments=arguments), content='Optional visible commentary.')
    original = copy.deepcopy(raw)
    result = action(raw, 'tool_calls', step)
    assert result['name'] == 'search'
    assert result['arguments'] == {'query': query, 'k': 6}
    assert result['requested_arguments'] == arguments
    assert result['tool_call_id'] == 'call_1'
    assert raw == original


@pytest.mark.parametrize('k', [5, 7, True, 6.0, '6', None])
def test_search_rejects_wrong_k_without_overriding(k):
    with pytest.raises(ValueError):
        action(message(call(arguments={'query': 'query', 'k': k})), 'tool_calls', 1)


@pytest.mark.parametrize('arguments', [[], {}, {'query': ''}, {'query': '  '},
                                       {'query': None}, {'query': 'x', 'extra': 1}])
def test_search_rejects_invalid_arguments(arguments):
    with pytest.raises(ValueError):
        action(message(call(arguments=arguments)), 'tool_calls', 1)


def test_invalid_json_rejected_without_repair():
    raw_call = call()
    raw_call['function']['arguments'] = '{"query":'
    with pytest.raises(json.JSONDecodeError):
        action(message(raw_call), 'tool_calls', 1)


@pytest.mark.parametrize('step', [1, 2])
def test_multiple_calls_rejected_instead_of_taking_first(step):
    raw = message(call(call_id='first'), call(call_id='second'))
    with pytest.raises(ValueError, match='Exactly one'):
        action(raw, 'tool_calls', step)


@pytest.mark.parametrize('finish', ['stop', 'length', 'content_filter', None])
def test_tool_call_requires_complete_tool_finish(finish):
    with pytest.raises(ValueError):
        action(message(call()), finish, 1)


@pytest.mark.parametrize('direction', ['before', 'after', 'around'])
def test_open_only_allowed_as_second_action(direction):
    arguments = {'window_ref': 'visible_window', 'direction': direction}
    raw = message(call('open', arguments))
    with pytest.raises(ValueError):
        action(raw, 'tool_calls', 1)
    assert action(raw, 'tool_calls', 2)['arguments'] == arguments


@pytest.mark.parametrize('arguments', [
    {'window_ref': 'w', 'direction': 'focus'},
    {'window_ref': 'w', 'direction': 'after', 'query': 'x'},
    {'window_ref': 3, 'direction': 'after'},
    {'window_ref': 'w'},
])
def test_open_rejects_invalid_direction_shape(arguments):
    with pytest.raises(ValueError):
        action(message(call('open', arguments)), 'tool_calls', 2)


def test_unknown_tool_rejected():
    with pytest.raises(ValueError):
        action(message(call('get_document', {'docid': '1'})), 'tool_calls', 2)


def test_complete_second_answer_allowed_first_answer_rejected():
    raw = message(content='Evidence is insufficient for a full answer.')
    assert action(raw, 'stop', 2) is None
    with pytest.raises(ValueError):
        action(raw, 'stop', 1)


def test_second_refusal_is_recordable_stop():
    raw = {'role': 'assistant', 'refusal': 'I cannot answer.'}
    assert action(raw, 'stop', 2) is None
    with pytest.raises(ValueError):
        action(raw, 'stop', 1)


@pytest.mark.parametrize('finish', ['length', 'tool_calls', 'content_filter', None])
def test_incomplete_second_answer_rejected(finish):
    with pytest.raises(ValueError):
        action(message(content='Partial answer'), finish, 2)


def test_empty_second_response_rejected():
    with pytest.raises(ValueError):
        action(message(), 'stop', 2)
