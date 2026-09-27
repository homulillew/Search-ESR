"""Offline agent, freeze, and evaluator preflight. No paid model calls."""
import json
from pathlib import Path
from types import SimpleNamespace
import unittest

from .native_agent import AgentSession
from .native_client import Config
from .evaluate import exact_score, primary_correct, wilson
from .runner import HERE, ROOT, read_json, sha


def call(name, args, call_id='c1'):
    return SimpleNamespace(id=call_id, type='function',
                           function=SimpleNamespace(name=name, arguments=json.dumps(args)))


class Message:
    def __init__(self, calls=None, content=None):
        self.tool_calls, self.content, self.refusal = calls, content, None

    def model_dump(self, exclude_none=True):
        value = {'role': 'assistant', 'content': self.content}
        if self.tool_calls:
            value['tool_calls'] = [{'id': c.id, 'type': c.type,
                                    'function': {'name': c.function.name, 'arguments': c.function.arguments}}
                                   for c in self.tool_calls]
        return {k: v for k, v in value.items() if v is not None}


class MockClient:
    def __init__(self, scripted):
        self.scripted = scripted
        self.requests = []
        self.chat = SimpleNamespace(completions=self)

    def create(self, **kwargs):
        self.requests.append(kwargs)
        return self.scripted(len(self.requests), kwargs)

    def close(self):
        pass


def response(calls=None, content=None, finish=None):
    return SimpleNamespace(choices=[SimpleNamespace(message=Message(calls, content),
                                                     finish_reason=finish or ('tool_calls' if calls else 'stop'))])


class MockTools:
    def __init__(self):
        self.calls = []

    def execute(self, name, arguments):
        self.calls.append((name, arguments))
        if name == 'search' and not arguments.get('query'):
            raise ValueError('query must be nonempty')
        return {'docid': 'd1', 'text': 'sample', 'truncated': False} if name == 'get_document' else [
            {'docid': 'd1', 'text': 'sample', 'truncated': False}]

    def close(self):
        pass


class Preflight(unittest.TestCase):
    def setUp(self):
        self.config = Config('mock-secret', 'https://api.deepseek.com', 'deepseek-flash')

    def test_search_get_document_multi_tool_and_final(self):
        tools = MockTools()
        mock = MockClient(lambda n, _: response([call('search', {'query': 'x'}, 's'),
                                                 call('get_document', {'docid': 'd1'}, 'd')], finish='stop')
                          if n == 1 else response(content='Answer [d1]'))
        agent = AgentSession(self.config, client=mock, tools=tools, max_rounds=200)
        self.assertEqual(agent.ask('question'), 'Answer [d1]')
        self.assertEqual([n for n, _ in tools.calls], ['search', 'get_document'])
        self.assertEqual(len(mock.requests), 2)
        agent.close()

    def test_invalid_arguments_are_recorded_as_tool_error(self):
        tools = MockTools()
        mock = MockClient(lambda n, _: response([call('search', {'query': '', 'k': 0})])
                          if n == 1 else response(content='No evidence'))
        agent = AgentSession(self.config, client=mock, tools=tools, max_rounds=200)
        self.assertEqual(agent.ask('question'), 'No evidence')
        self.assertEqual(tools.calls[0][0], 'search')
        self.assertIn('error', mock.requests[1]['messages'][-1]['content'])
        agent.close()

    def test_emergency_cap_only_after_200_tool_rounds(self):
        tools = MockTools()
        mock = MockClient(lambda n, req: response(content='Forced final') if req['tool_choice'] == 'none'
                          else response([call('search', {'query': 'x'}, f'c{n}')]))
        agent = AgentSession(self.config, client=mock, tools=tools, max_rounds=200)
        self.assertEqual(agent.ask('question'), 'Forced final')
        self.assertEqual(len(mock.requests), 201)
        self.assertTrue(all(req['tool_choice'] == 'auto' for req in mock.requests[:200]))
        self.assertEqual(mock.requests[200]['tool_choice'], 'none')
        agent.close()

    def test_evaluation_examples(self):
        self.assertTrue(exact_score('Queen Arwa University.', 'Queen Arwa University'))
        self.assertTrue(exact_score('queen arwa university', 'Queen Arwa University'))
        self.assertFalse(exact_score('Wrong University', 'Queen Arwa University'))
        self.assertFalse(exact_score('', 'Queen Arwa University'))
        self.assertFalse(exact_score('QAU', 'Queen Arwa University'))  # alias queue
        self.assertFalse(primary_correct('RUN_FAILED', 'Queen Arwa University', 'Queen Arwa University'))
        self.assertEqual(wilson(0, 50)[0], 0)

    def test_freeze_integrity(self):
        selection = read_json('SELECTION_FREEZE.json')
        online = read_json('ONLINE_INPUTS.json')
        model = read_json('MODEL_FREEZE.json')
        run = read_json('RUN_CONFIG.json')
        restart = read_json('RESTART_FREEZE.json')
        self.assertEqual(sha(HERE / 'ONLINE_INPUTS.json'), selection['selected_questions_sha256'])
        self.assertEqual(sha(ROOT / 'BCPlus/data/bcplus/qa.jsonl'), selection['dataset_sha256'])
        self.assertEqual([x['qid'] for x in online], selection['selected_qids'])
        self.assertEqual(len(online), 50)
        self.assertTrue(all(x['question'].strip() and set(x) == {'qid', 'question'} for x in online))
        self.assertTrue(model['thinking'])
        self.assertEqual(model['thinking_extra_body'], {'thinking': {'type': 'enabled'}})
        self.assertEqual(self.config.request_options()['extra_body'], model['thinking_extra_body'])
        self.assertEqual(run['workers'], 50)
        self.assertEqual(run['initial_api_concurrency'], 50)
        self.assertEqual(run['retrieval_worker_count'], 1)
        self.assertEqual(sha(HERE / 'RESTART_FREEZE.json'), run['restart_freeze_sha256'])
        self.assertEqual(restart['selected_qids'], selection['selected_qids'])


if __name__ == '__main__':
    unittest.main()
