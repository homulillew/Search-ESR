"""Offline regression tests on the 859e0f1 harness; no API or retrieval calls."""
from contextlib import redirect_stdout
from copy import deepcopy
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

from experiments.research_state.need_review import run
from experiments.research_state.need_review.accounting import inspect_usage
from experiments.research_state.need_review.node import validate_review


def fixture(root, count=3, n=1):
    root = Path(root)
    tools = [{'type': 'function', 'function': {'name': 'search', 'parameters': {
        'type': 'object', 'properties': {'query': {'type': 'string'}}, 'required': ['query']}}}]
    cases = []
    for i in range(count):
        result = [{'docid': str(i), 'text': 'A source establishes only one local relation.'}]
        request = {'model': 'synthetic-model', 'stream': False,
                   'extra_body': {'enable_thinking': False}, 'tools': tools,
                   'messages': [
                       {'role': 'system', 'content': 'Research the original question.'},
                       {'role': 'user', 'content': 'Identify an entity satisfying two dated relations.'},
                       {'role': 'assistant', 'content': 'Candidate and intermediary are guesses.',
                        'tool_calls': [{'id': 'old', 'type': 'function', 'function': {
                            'name': 'search', 'arguments': '{"query":"local relation"}'}}]},
                       {'role': 'tool', 'tool_call_id': 'old', 'content': json.dumps(result)}]}
        if n != 1:
            request['n'] = n
        path = root / f'source{i}.jsonl'
        path.write_text('\n'.join(json.dumps(event) for event in [
            {'seq': 1, 'kind': 'tool_result', 'name': 'search', 'result': result},
            {'seq': 2, 'kind': 'api_request', 'request': request}]) + '\n', encoding='utf-8')
        cases.append({'checkpoint_id': f'synthetic{i}', 'events_path': path.name,
                      'events_blob_sha': run.git_blob_sha(path), 'request_seq': 2,
                      'tool_version': 'synthetic_not_BCPlus'})
    selection = {'schema_version': 'need_review_selection_v1',
                 'source_commit': '8' * 40, 'checkpoints': cases}
    run.write_json(root / 'selection.json', selection)
    run.prepare(root / 'selection.json', root, root / 'prepared')
    return root / 'prepared'


class FakeClient:
    def __init__(self, *, invalid_review=False, error_review=False,
                 interrupt_actor=False, missing_usage=False, mutate=False):
        self.chat = SimpleNamespace(completions=self)
        self.requests = []
        self.invalid_review, self.error_review = invalid_review, error_review
        self.interrupt_actor, self.missing_usage = interrupt_actor, missing_usage
        self.mutate = mutate

    def create(self, **request):
        self.requests.append(deepcopy(request))
        is_actor = 'tools' in request
        if not is_actor and self.error_review:
            self.error_review = False
            raise RuntimeError('NEVER_LOG_THIS_FAKE_SECRET')
        if is_actor and self.interrupt_actor:
            raise KeyboardInterrupt()
        if self.mutate:
            request['messages'].append({'role': 'user', 'content': 'SDK mutation'})
        if is_actor:
            message = {'role': 'assistant', 'content': 'Investigate a local uncertainty.',
                       'tool_calls': [{'id': f'new{k}', 'type': 'function', 'function': {
                           'name': 'search', 'arguments': json.dumps({'query': f'probe{k}'})}}
                                      for k in range(2)]}
            finish = 'tool_calls'
        else:
            text = json.dumps({'current_assumption': 'The intermediary remains unverified.',
                               'next_need': 'Which dated relation is documented?',
                               'decision_effect': 'Revise the local binding, not the task.',
                               'basis_refs': ['question']})
            finish = 'length' if self.invalid_review else 'stop'
            message = {'role': 'assistant', 'content': text}
        return {'model': 'synthetic-model', 'choices': [{'index': 0, 'finish_reason': finish,
                                                        'message': message}],
                'usage': {} if self.missing_usage else {
                    'prompt_tokens': 2, 'completion_tokens': 1, 'total_tokens': 3}}


class SummaryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.item = {'sample_id': 'sample', 'checkpoint_id': 'synthetic', 'arm': 'C', 'repeat_id': 1}

    def recorded(self, usage, *, stage='actor', suffix=''):
        branch = self.root / 'branches' / self.item['sample_id']
        branch.mkdir(parents=True)
        events = [{'seq': 1, 'kind': 'request', 'stage': stage, 'request': {}},
                  {'seq': 2, 'kind': 'response', 'stage': stage, 'response': {'usage': usage}}]
        (branch / 'events.jsonl').write_text(
            '\n'.join(json.dumps(row) for row in events) + '\n' + suffix)
        return run.summarize(self.root, [self.item], write_output=False)

    def test_inconsistent_total_is_not_complete_cost(self):
        result = self.recorded({'prompt_tokens': 2, 'completion_tokens': 1, 'total_tokens': 99})
        self.assertEqual(result['responses_inconsistent_usage'], 1)
        self.assertEqual(result['responses_missing_usage'], 0)
        self.assertFalse(result['cost_accounting_complete'])
        self.assertEqual(result['reported_usage_by_stage']['actor']['total_tokens'], 99)
        self.assertEqual(result['semantic_evaluation'], 'not_evaluated')

    def test_partial_counts_preserved_without_invented_total(self):
        result = self.recorded({'prompt_tokens': 5})
        self.assertEqual(result['reported_usage_by_stage']['actor'], {'prompt_tokens': 5})
        self.assertEqual(result['responses_missing_usage'], 1)
        self.assertEqual(result['missing_usage_fields_by_stage']['actor'],
                         {'completion_tokens': 1, 'total_tokens': 1})
        self.assertFalse(result['cost_accounting_complete'])

    def test_empty_counts_are_unknown(self):
        result = self.recorded({})
        self.assertEqual(result['responses_missing_usage'], 1)
        self.assertFalse(result['cost_accounting_complete'])

    def test_invalid_numbers_do_not_enter_totals(self):
        result = self.recorded({'prompt_tokens': -1, 'completion_tokens': True, 'total_tokens': 2})
        self.assertEqual(result['reported_usage_by_stage']['actor'], {'total_tokens': 2})
        self.assertFalse(result['cost_accounting_complete'])

    def test_zero_counts_valid(self):
        result = self.recorded({'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0})
        self.assertTrue(result['cost_accounting_complete'])

    def test_unknown_stage_recorded(self):
        result = self.recorded({'prompt_tokens': 2, 'completion_tokens': 1, 'total_tokens': 3}, stage='bogus')
        self.assertFalse(result['cost_accounting_complete'])
        self.assertIn('unknown_usage_stage', [row['error'] for row in result['record_errors']])

    def test_corrupt_tail_still_preserves_paid_prefix(self):
        result = self.recorded({'prompt_tokens': 2, 'completion_tokens': 1, 'total_tokens': 3}, suffix='{"seq":')
        self.assertEqual(result['responses_received'], 1)
        self.assertEqual(result['reported_usage_by_stage']['actor']['total_tokens'], 3)
        self.assertFalse(result['cost_accounting_complete'])
        self.assertTrue(result['record_errors'])

    def test_read_only_summary(self):
        self.recorded({'prompt_tokens': 2, 'completion_tokens': 1, 'total_tokens': 3})
        self.assertFalse((self.root / 'summary.json').exists())


class IntegratedPairTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.prepared = fixture(self.root)
        self.settings = run.settings_dict(comparison='source_contract_pair', repeats=2, seed=20260920)
        self.plan = run.build_plan(self.prepared, self.settings)

    def execute(self, client=None, *, settings=None, transport=None):
        with redirect_stdout(io.StringIO()):
            return run.execute(self.prepared, self.root / 'output', client=client or FakeClient(),
                               settings=settings or self.settings, approved_plan=self.plan, transport=transport)

    def test_shared_pair_keeps_twelve_branches_twenty_four_calls(self):
        self.assertEqual(self.plan['scheduled_logical_requests'], 24)
        self.assertEqual(len(self.plan['schedule']), 12)
        for a, b in zip(self.plan['schedule'][::2], self.plan['schedule'][1::2]):
            self.assertEqual(a['checkpoint_id'], b['checkpoint_id'])
            self.assertEqual(a['repeat_id'], b['repeat_id'])
            self.assertEqual({a['review_contract'], b['review_contract']}, {'baseline', 'source_grounded_v1'})

    def test_only_review_system_differs_with_identical_mock_reviews(self):
        client = FakeClient()
        self.execute(client)
        for i in range(0, 24, 4):
            a, b = deepcopy(client.requests[i]), deepcopy(client.requests[i + 2])
            self.assertNotEqual(a['messages'][0], b['messages'][0])
            a['messages'][0] = b['messages'][0]
            self.assertEqual(a, b)
            self.assertEqual(client.requests[i + 1], client.requests[i + 3])
        self.assertTrue(all('seed' not in request for request in client.requests))

    def test_pipeline_retains_batches_and_contract_costs(self):
        client = FakeClient(mutate=True)
        result = self.execute(client)
        self.assertEqual(len(client.requests), 24)
        self.assertEqual(result['branch_statuses'], {'completed': 12})
        self.assertTrue(result['cost_accounting_complete'])
        for contract in ('baseline', 'source_grounded_v1'):
            group = result['by_contract'][contract]
            self.assertEqual(group['scheduled_branches'], 6)
            self.assertEqual(group['reported_usage_by_stage']['review']['total_tokens'], 18)
            self.assertEqual(group['reported_usage_by_stage']['actor']['total_tokens'], 18)
        for path in (self.root / 'output' / 'branches').glob('*/result.json'):
            value = run.read_json(path)
            self.assertEqual(len(value['actor']['response']['choices'][0]['message']['tool_calls']), 2)
            self.assertNotIn('SDK mutation', json.dumps(value))

    def test_length_failure_keeps_original_actor_request(self):
        client = FakeClient(invalid_review=True)
        result = self.execute(client)
        self.assertEqual(result['review_statuses'], {'node_invalid': 12})
        _, cps = run.load_prepared(self.prepared)
        for i, item in enumerate(self.plan['schedule']):
            self.assertEqual(client.requests[2 * i + 1], cps[item['checkpoint_id']]['request'])
        self.assertEqual(result['by_arm']['C']['fallbacks'], 12)

    def test_api_error_cost_remains_unknown(self):
        result = self.execute(FakeClient(error_review=True))
        self.assertEqual(result['failed_requests_with_unknown_cost'], 1)
        self.assertFalse(result['cost_accounting_complete'])
        self.assertEqual(result['scheduled_branches'], 12)
        logs = '\n'.join(p.read_text() for p in (self.root / 'output').rglob('events.jsonl'))
        self.assertNotIn('NEVER_LOG_THIS_FAKE_SECRET', logs)

    def test_interrupt_keeps_unrun_denominator(self):
        with self.assertRaises(KeyboardInterrupt):
            self.execute(FakeClient(interrupt_actor=True))
        result = run.read_json(self.root / 'output' / 'summary.json')
        self.assertEqual(result['scheduled_branches'], 12)
        self.assertEqual(result['branch_statuses'], {'interrupted': 1, 'not_run': 11})
        self.assertFalse(result['cost_accounting_complete'])

    def test_plan_drift_rejected_before_client(self):
        client = FakeClient()
        changed = dict(self.settings, review_max_tokens=1024)
        with self.assertRaisesRegex(ValueError, 'Frozen plan'):
            self.execute(client, settings=changed)
        self.assertEqual(client.requests, [])
        self.assertFalse((self.root / 'output').exists())

    def test_pair_disallows_simultaneous_indexed_handoff(self):
        with self.assertRaises(ValueError):
            run.settings_dict(comparison='source_contract_pair', memo_mode='indexed_json_v1')

    def test_partial_usage_reported_in_both_conditions(self):
        result = self.execute(FakeClient(missing_usage=True))
        self.assertEqual(result['responses_missing_usage'], 24)
        self.assertFalse(result['cost_accounting_complete'])
        self.assertTrue(all(group['responses_missing_usage'] == 12 for group in result['by_contract'].values()))

    def test_complete_but_inconsistent_usage_in_both_conditions(self):
        class BadTotalClient(FakeClient):
            def create(self, **request):
                result = super().create(**request)
                result['usage']['total_tokens'] = 99
                return result
        result = self.execute(BadTotalClient())
        self.assertEqual(result['responses_inconsistent_usage'], 24)
        self.assertFalse(result['cost_accounting_complete'])
        self.assertEqual(result['branch_statuses'], {'completed': 12})
        self.assertTrue(all(group['responses_inconsistent_usage'] == 12 for group in result['by_contract'].values()))


class AccountingTests(unittest.TestCase):
    def test_empty_or_partial_usage_is_unknown(self):
        for value in (None, {}, {'prompt_tokens': 4}, {'total_tokens': 7}):
            with self.subTest(value=value):
                self.assertFalse(inspect_usage(value)['complete'])

    def test_invalid_counts_rejected(self):
        for value in (True, -1, 1.5, '1'):
            with self.subTest(value=value):
                self.assertIn('total_tokens', inspect_usage({'total_tokens': value})['missing'])

    def test_no_imputed_total(self):
        self.assertNotIn('total_tokens', inspect_usage({'prompt_tokens': 2, 'completion_tokens': 1})['known'])

    def test_inconsistent_counts_flagged(self):
        value = inspect_usage({'prompt_tokens': 2, 'completion_tokens': 1, 'total_tokens': 99})
        self.assertTrue(value['inconsistent'])
        self.assertFalse(value['complete'])

    def test_zero_counts_valid(self):
        self.assertTrue(inspect_usage({'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0})['complete'])

    def test_structural_validation_cannot_prove_relationship(self):
        content = json.dumps({'current_assumption': 'Candidate X in assumed event Y.',
                              'next_need': 'Check X in Y.',
                              'decision_effect': 'If no match in Y, X must be rejected.',
                              'basis_refs': ['question']})
        response = {'choices': [{'finish_reason': 'stop', 'message': {'role': 'assistant', 'content': content}}]}
        self.assertTrue(validate_review(response, 'C', {'question'})['valid'])


if __name__ == '__main__':
    unittest.main()
