import copy
import hashlib
import json
from types import SimpleNamespace
import pytest
from .source_units import build_question, check_question, model_input
from .initializer import generate, validate, system_prompt
from .pipeline import initialize


class Client:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.requests = []
        self.chat = SimpleNamespace(completions=self)

    def create(self, **kwargs):
        self.requests.append(copy.deepcopy(kwargs))
        item = next(self.responses)
        content, finish = item if isinstance(item, tuple) else (item, 'stop')
        return SimpleNamespace(choices=[SimpleNamespace(finish_reason=finish,
                               message=SimpleNamespace(content=content, tool_calls=None))])


CONFIG = SimpleNamespace(model='fake', api_key='fake-secret', request_options=lambda: {})


def output(query='person retired by 2020', refs=None, root='intents'):
    return {root: [dict(basis_refs=['q1'] if refs is None else refs, query=query)]}


@pytest.mark.parametrize('text', [
    '  Dr. Smith earned a Ph.D. in 1997. His mother was a poet.\r\n- He retired by 2020.  ',
    '名字 😀\u200b. An actor. Their nephew.\n\n',
    'A journal bought by a "Major," whose sibling earned a B.A. in 1821 and M.A. in 1824.',
    'A very long single description without punctuation ' * 40,
])
def test_lossless_versioned_units(text):
    question = build_question(text)
    assert ''.join(u['text'] for u in question['units']) == text
    assert question['sha256'] == hashlib.sha256(text.encode()).hexdigest()
    assert question == build_question(text)
    assert all(u['text'].strip() for u in question['units'])
    assert 'answer' not in model_input(question)
    damaged = copy.deepcopy(question)
    damaged['units'][0]['text'] += 'invented'
    with pytest.raises(ValueError):
        check_question(damaged)
    damaged = copy.deepcopy(question)
    damaged['text'] += '.'
    with pytest.raises(ValueError):
        check_question(damaged)


def test_abbreviations_and_cross_sentence_references():
    q = build_question('Dr. Smith earned a Ph.D. in 1997. His mother acted. He retired by 2020.')
    assert len(q['units']) == 3
    assert validate(output(refs=['q1', 'q3']), q, 'minimal') == []
    # Existence and structural checks intentionally do not infer relation fidelity.
    assert validate(output('His mother earned a Ph.D. in 1997'), q, 'minimal') == []


def test_flattened_list_keeps_context_and_numeric_range():
    text = 'Identify the person:  - An actor. - Worked with their nephew. - Active between 1990 - 2000.'
    q = build_question(text)
    assert len(q['units']) == 4
    assert ''.join(u['text'] for u in q['units']) == text
    assert q['units'][2]['text'] == '- Worked with their nephew. '
    assert '1990 - 2000' in q['units'][3]['text']


@pytest.mark.parametrize('refs', [[], ['q99'], ['q1', 'q1'], [1], 'q1'])
@pytest.mark.parametrize('arm', ['minimal', 'entry_v1'])
def test_bad_references_fail(refs, arm):
    assert validate(output(refs=refs), build_question('A person.'), arm)


@pytest.mark.parametrize('arm', ['minimal', 'entry_v1'])
def test_contract_and_prompt_ablation(arm):
    q = build_question('A person retired by 2020.')
    assert validate({'intents': []}, q, arm) == []
    assert validate({'intents': output()['intents'] * 2}, q, arm)
    assert validate(output(query='x' * 513), q, arm)
    assert validate({'intents': [{'query': 'person', 'basis_refs': ['q1'], 'goal': 'find'}]}, q, arm)
    assert 'source_clues' not in system_prompt('refs_goal')
    assert 'source_clues' not in system_prompt('refs')
    assert 'goal' not in system_prompt('refs')


@pytest.mark.parametrize('arm', ['minimal', 'entry_v1'])
def test_one_repair_no_retrieval_and_empty_is_not_forced(arm):
    q = build_question('A person retired by 2020.')
    client = Client([json.dumps(output(refs=['q99'])), json.dumps(output())])
    plan = generate(client, CONFIG, q, arm)
    assert plan['repairs'] == 1 and not plan['initial_valid'] and plan['status'] == 'valid'
    assert len(client.requests) == 2
    assert client.requests[0]['messages'][1]['content'] == client.requests[1]['messages'][1]['content']
    assert 'tools' not in client.requests[0]
    client = Client(['{"intents":[]}'])
    assert generate(client, CONFIG, q, arm)['status'] == 'no_direction'
    assert len(client.requests) == 1
    client = Client(['{', '{'])
    assert generate(client, CONFIG, q, arm)['status'] == 'invalid'
    assert len(client.requests) == 2


@pytest.mark.parametrize('arm', ['minimal', 'entry_v1'])
def test_truncation_is_not_salvaged_or_repaired(arm):
    client = Client([(json.dumps(output()), 'length')])
    with pytest.raises(ValueError, match='Incomplete'):
        generate(client, CONFIG, build_question('A person retired by 2020.'), arm)
    assert len(client.requests) == 1


class Tools:
    def __init__(self, error=False):
        self.calls = []
        self.error = error

    def execute(self, name, arguments):
        self.calls.append((name, arguments))
        if self.error:
            raise RuntimeError('fake-secret test failure')
        return [dict(window_ref='w_test', text='unchanged raw observation')]


@pytest.mark.parametrize('arm', ['minimal', 'entry_v1'])
def test_handoff_preserves_raw_observation_and_orders_search_after_plan(arm):
    q = build_question('A person retired by 2020. His mother acted.')
    tools = Tools()
    events = []
    handoff = initialize(Client([json.dumps(output())]), CONFIG, q, tools, attempt_id='test/1',
                         arm=arm, emit=lambda kind, **data: events.append(kind))
    assert events == ['plan_finalized', 'search_start', 'search_result']
    assert tools.calls == [('search', dict(query='person retired by 2020', k=6))]
    assert handoff['question'] == q and handoff['status'] == 'complete'
    assert handoff['search_attempts'][0]['window_refs'] == ['w_test']
    assert handoff['search_attempts'][0]['result'][0]['text'] == 'unchanged raw observation'
    assert not {'candidate', 'known_facts', 'gap', 'next_action'} & handoff.keys()


@pytest.mark.parametrize('arm', ['minimal', 'entry_v1'])
def test_failures_never_fallback_to_full_question_search(arm):
    q = build_question('A person retired by 2020.')
    for contents, status in [(['{', '{'], 'invalid'), (['{"intents":[]}'], 'no_direction'),
                             ([(json.dumps(output()), 'length')], 'generation_error')]:
        tools = Tools()
        handoff = initialize(Client(contents), CONFIG, q, tools, attempt_id='test/1', arm=arm)
        assert handoff['status'] == status and tools.calls == []
    tools = Tools(error=True)
    handoff = initialize(Client([json.dumps(output())]), CONFIG, q, tools, attempt_id='test/1', arm=arm)
    assert handoff['status'] == 'search_error' and len(tools.calls) == 1
    assert 'fake-secret' not in json.dumps(handoff)
