"""Evidence Pointer A/B plan: equality, leakage, execution and failure denominators.

No test here calls a real model, performs a search, or opens a window. The mock
client records requests; proposed tools are classified but never executed.
"""
from __future__ import annotations
from copy import deepcopy
from collections import Counter
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

from experiments.research_state.evidence_pointer import contracts as ec
from experiments.research_state.evidence_pointer import run as ep
from experiments.research_state.first_observation import artifacts as io
from experiments.research_state.first_observation import contracts as fc
from experiments.research_state.first_observation import run as fo_run

CONFIG = {'model': 'mock-only', 'base_url': 'https://example.invalid/v1',
          'timeout_seconds': 180, 'request_options': {'max_tokens': 8192},
          'max_request_utf8_bytes': 1000000, 'allow_tool_calls_with_stop': False}
TOOLS = [{'type': 'function', 'function': {'name': name, 'parameters': {}}}
         for name in ('search', 'open')]
BODY = ('Heading text.\n\nThe hotel was constructed in 1905 on an artificial island '
        'built from ballast, and £8\xa0million was never mentioned again.\n\nTail.')


def window(text=BODY, ref='w_one', offset=0):
    return {'window_ref': ref, 'docid': 'doc-' + ref, 'document_sha256': 'a' * 64,
            'url': 'https://example.invalid/' + ref, 'title': '', 'text': text,
            'offset': offset, 'end_char': offset + len(text),
            'text_tokens': 60, 'title_tokens': 0}


def collection(n=6):
    cases = [{'id': str(i), 'question': f'Which building is on the island {i}?  \n'}
             for i in range(n)]
    selection = fc.seal({'version': fc.VERSION, 'kind': 'selection',
                         'dataset_sha256': 'b' * 64, 'cases': cases})
    return fc.seal({'version': fc.VERSION, 'kind': 'collection', 'mode': 'mock',
        'selection': selection, 'retrieval': {'adapter': 'mock'}, 'k': 5,
        'max_query_tokens': 1024, 'tools': TOOLS, 'fingerprint': io.fingerprint(),
        'initial_model_calls': 0, 'capture_complete': True,
        'cases': [{**case, 'query': case['question'], 'status': 'ok', 'query_tokens': 8,
                   'observation': [window()]} for case in cases]})


def reviewer_selection(col, *, empty_case=None, rationale=True):
    cases = {}
    for case in col['cases']:
        cid = case['id']
        if empty_case is not None and cid == empty_case:
            cases[cid] = ec.seal({'pointers': [], 'rationale': 'no load-bearing span'})
            continue
        body = case['observation'][0]['text']
        cases[cid] = ec.seal({'pointers': [
            {'window_ref': 'w_one', 'start': body.index('constructed in 1905'),
             'end': body.index('constructed in 1905') + 20},
            {'window_ref': 'w_one', 'start': body.index('£8'),
             'end': body.index('£8') + 10}],
            'rationale': 'reviewer note for audit only'}) if rationale else ec.seal(
            {'pointers': [{'window_ref': 'w_one', 'start': 0, 'end': 5}]})
    return ec.seal({'version': ec.VERSION, 'kind': 'pointer_selection',
                    'collection_sha256': col['sha256'], 'cases': cases})


def tool_response(name='search', finish='tool_calls'):
    args = {'query': 'a follow-up query'} if name == 'search' else {
        'window_ref': 'w_one', 'direction': 'after'}
    return {'choices': [{'finish_reason': finish, 'message': {'role': 'assistant',
        'content': None, 'tool_calls': [{'id': 'call_1', 'type': 'function',
        'function': {'name': name, 'arguments': json.dumps(args)}}]}}],
        'usage': {'prompt_tokens': 40, 'completion_tokens': 5, 'total_tokens': 45}}


def batch_response():
    return {'choices': [{'finish_reason': 'tool_calls', 'message': {'role': 'assistant',
        'content': None, 'tool_calls': [
            {'id': 'call_1', 'type': 'function', 'function': {
                'name': 'search', 'arguments': json.dumps({'query': 'first follow-up'})}},
            {'id': 'call_2', 'type': 'function', 'function': {
                'name': 'open', 'arguments': json.dumps(
                    {'window_ref': 'w_one', 'direction': 'after'})}}]}}],
        'usage': {'prompt_tokens': 40, 'completion_tokens': 5, 'total_tokens': 45}}


class FakeAPIError(Exception):
    pass


class AuthRejected(FakeAPIError):
    """Stands in for openai.AuthenticationError: a rejected credential."""


class Client:
    def __init__(self, effect=None):
        self.chat = SimpleNamespace(completions=self)
        self.requests = []
        self.effect = effect if effect is not None else tool_response()
        self.base_url = CONFIG['base_url']
        self.timeout = CONFIG['timeout_seconds']
        self.max_retries = 0

    def create(self, **request):
        self.requests.append(deepcopy(request))
        if isinstance(self.effect, BaseException):
            raise self.effect
        return deepcopy(self.effect)


class ABPlanTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.col = collection()
        self.state = ep.bind_state(self.col, reviewer_selection(self.col))
        self.plan = ep.make_ab_plan(self.col, self.state, CONFIG)

    def tearDown(self):
        self.tmp.cleanup()

    def test_balanced_pairs_and_order(self):
        self.assertEqual(len(self.plan['jobs']), 12)
        self.assertEqual(Counter(j['arm'] for j in self.plan['jobs']), {'A': 6, 'B': 6})
        for case in self.col['cases']:
            pair = [j for j in self.plan['jobs'] if j['case_id'] == case['id']]
            self.assertEqual({j['arm'] for j in pair}, {'A', 'B'})

    def test_ab_differ_by_treatment_only(self):
        for job in self.plan['jobs']:
            if job['arm'] != 'B':
                continue
            sibling = next(j for j in self.plan['jobs']
                           if j['case_id'] == job['case_id'] and j['arm'] == 'A')
            neutral = deepcopy(job['request'])
            neutral['messages'] = neutral['messages'][:-1]
            self.assertEqual(neutral, sibling['request'])
            treatment = job['request']['messages'][-1]
            self.assertEqual(treatment['role'], 'user')
            parsed = fc.loads(treatment['content'])
            self.assertEqual(parsed['kind'], 'evidence_pointer_state')

    def test_validator_proves_equality_object_wise(self):
        # Rebuilds the whole plan and compares; also proves the treatment pairing.
        ep.validate_ab_plan(self.plan)

    def test_plan_drift_is_rejected(self):
        bad = deepcopy(self.plan)
        bad['jobs'][0]['request']['messages'][0]['content'] = 'tampered'
        with self.assertRaises(ValueError):
            ep.validate_ab_plan(bad)

    def treatment_messages(self):
        out = []
        for job in self.plan['jobs']:
            if job['arm'] != 'B':
                continue
            payload = job['request']['messages'][1]['content']
            treatment = job['request']['messages'][-1]['content']
            out.append((payload, treatment))
        return out

    def test_treatment_leaks_no_reviewer_artifact(self):
        for payload, treatment in self.treatment_messages():
            # The reviewer's rationale string must never reach a model.
            self.assertNotIn('reviewer note for audit only', treatment)
            self.assertNotIn('no load-bearing span', treatment)
            self.assertNotIn('rationale', treatment)
            # Selection is the only reviewer content: addresses, nothing else.
            parsed = fc.loads(treatment)
            self.assertEqual(set(parsed), {'kind', 'evidence'})
            for ev in parsed['evidence']:
                self.assertEqual(set(ev), set(ec._STATE_FIELDS))
            # The raw observation is still delivered untouched in both arms.
            self.assertNotIn('evidence_pointer_state', payload)

    def test_no_gold_pairwise_or_labels_in_treatment(self):
        for payload, treatment in self.treatment_messages():
            for banned in ('gold', 'pairwise', 'outcome', 'label', 'coverage',
                           'better', 'score'):
                self.assertNotIn(banned, treatment.lower())

    def test_empty_case_is_a_legal_state(self):
        state = ep.bind_state(self.col, reviewer_selection(self.col, empty_case='2'))
        plan = ep.make_ab_plan(self.col, state, CONFIG)
        b = next(j for j in plan['jobs'] if j['case_id'] == '2' and j['arm'] == 'B')
        parsed = fc.loads(b['request']['messages'][-1]['content'])
        self.assertEqual(parsed['evidence'], [])
        ep.validate_ab_plan(plan)

    def test_selection_from_another_collection_rejected(self):
        other = collection()
        other = deepcopy(other)
        other['cases'][0]['question'] = 'rewritten question?'
        other['sha256'] = ec.digest({k: v for k, v in other.items() if k != 'sha256'})
        with self.assertRaises(ValueError):
            ep.bind_state(other, reviewer_selection(self.col))

    def test_request_byte_guard(self):
        tight = dict(CONFIG, max_request_utf8_bytes=1000)
        with self.assertRaises(ValueError):
            ep.make_ab_plan(self.col, self.state, tight)

    def test_plan_carries_no_executed_tools(self):
        self.assertEqual(self.plan['planned_tool_executions'], 0)
        self.assertEqual(self.plan['max_model_calls'], 12)


class ExecutionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.col = collection(n=4)
        self.state = ep.bind_state(self.col, reviewer_selection(self.col))
        self.plan = ep.make_ab_plan(self.col, self.state, CONFIG)

    def tearDown(self):
        self.tmp.cleanup()

    def run_batch(self, effect=None):
        client = Client(effect)
        fo_run.execute(self.plan, client, self.root / 'run', mode='mock',
                       api_error_types=(FakeAPIError,), auth_error_types=(AuthRejected,))
        return ep.audit(self.root / 'run')[0], client

    def test_shared_loop_executes_and_classifies(self):
        summary, client = self.run_batch()
        self.assertEqual(len(client.requests), 8)
        self.assertEqual(summary['scheduled'], 8)
        self.assertEqual(summary['tool_executions'], 0)
        self.assertEqual(summary['proposed_tools'], 8)
        # proposed tools are recorded but nothing was opened or searched
        self.assertEqual(summary['by_arm']['B']['memo_injected'], 4)
        self.assertTrue(summary['all_model_jobs_delivered'])
        self.assertTrue(summary['cost_accounting_complete'])

    def test_full_tool_batch_kept_not_truncated(self):
        summary, client = self.run_batch(batch_response())
        self.assertEqual(summary['proposed_tools'], 16)
        row = ep.audit(self.root / 'run')[1][0]
        self.assertEqual(row['proposed_tools'], 2)
        names = [c['function']['name'] for c in row['classification']['calls']]
        self.assertEqual(names, ['search', 'open'])

    def test_b_request_actually_carries_evidence(self):
        _, client = self.run_batch()
        for request in client.requests:
            if request['messages'][-1]['role'] == 'user' and 'evidence_pointer_state' in \
                    request['messages'][-1]['content']:
                break
        else:
            self.fail('no treatment message observed')
        parsed = fc.loads(request['messages'][-1]['content'])
        self.assertEqual(len(parsed['evidence']), 2)
        ev = parsed['evidence'][0]
        self.assertEqual(ev['text'], BODY[29:49])
        self.assertEqual(ev['text'], 'constructed in 1905 ')
        # NBSP survives untouched end to end: no normalisation in this path.
        self.assertEqual(parsed['evidence'][1]['text'], '£8\xa0million')
        self.assertIn('£8\xa0million', ec.canonical(parsed))

    def test_source_snapshot_matches_fingerprint(self):
        self.run_batch()
        ep.audit(self.root / 'run')

    def test_auth_failure_blocks_remaining_jobs(self):
        """A rejected credential is not retried 11 more times against the same endpoint."""
        summary, client = self.run_batch(AuthRejected('401 invalid key'))
        self.assertEqual(len(client.requests), 1)
        self.assertEqual(summary['statuses'], {'api_error': 1, 'blocked_by_auth': 7})
        self.assertFalse(summary['all_model_jobs_delivered'])
        # blocked jobs are not counted as API attempts
        self.assertEqual(summary['attempts'], 1)
        self.assertEqual(summary['responses'], 0)
        # The one request that left the wire has genuinely unknown cost, and the
        # blocked majority contributes no phantom attempts or phantom usage.
        self.assertEqual(summary['unknown_usage_requests'], 1)
        self.assertFalse(summary['cost_accounting_complete'])

    def test_non_auth_api_error_keeps_trying(self):
        summary, client = self.run_batch(FakeAPIError('TimeoutError'))
        self.assertEqual(len(client.requests), 8)
        self.assertEqual(summary['statuses'], {'api_error': 8})
        self.assertEqual(summary['attempts'], 8)
        self.assertNotIn('blocked_by_auth', summary['statuses'])

    def test_blocked_jobs_stay_unsent_and_unbilled(self):
        """The unsent majority stays in the denominator without becoming attempts."""
        summary, client = self.run_batch(AuthRejected('401 invalid key'))
        # A job that executed after the blocked point, in execution order.
        third = self.plan['jobs'][1]['id']
        events = io.journal_prefix(self.root / 'run' / third / 'events.jsonl')[0]
        self.assertEqual([e['kind'] for e in events], ['blocked_by_auth'])
        self.assertEqual(summary['attempts'], 1)
        self.assertEqual(summary['responses'], 0)
        # The one request that did leave the wire has genuinely unknown cost.
        self.assertEqual(summary['unknown_usage_requests'], 1)
        self.assertFalse(summary['all_model_jobs_delivered'])
        self.assertFalse(summary['cost_accounting_complete'])

    def test_programming_bug_stops_the_batch(self):
        """A non-API exception is a harness fault: must not be recorded as a model
        failure or silently swallowed."""
        class Boom(Exception):
            pass
        with self.assertRaises(Boom):
            fo_run.execute(self.plan, Client(Boom('harness bug')), self.root / 'bad',
                           mode='mock', api_error_types=(FakeAPIError,))

    def test_export_review_emits_unlabelled_cards(self):
        self.run_batch()
        summary = ep.export_review(self.root / 'run', self.root / 'review')
        cards = io.read(self.root / 'review' / 'cards.json')
        self.assertEqual(len(cards), 8)
        for card in cards:
            self.assertEqual(Counter(k is None for k in card['labels'].values()),
                             Counter({True: 8}))
            self.assertIsNone(card['pairwise'])
            self.assertIn('limitations', card)


if __name__ == '__main__':
    unittest.main()
