"""Offline integrity/failure regressions, not scientific effect measurements."""
import copy
import json
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import patch
import httpx
from .prepare import P, read
from .run import Batch, DIMENSIONS, accounting_summary, execute, load_rows, parse_response, usage_audit, validate_need
from .score import counts, fresh_gate, summarize, validate_review

def response(content=None, finish='stop', usage=None, model='deepseek-flash'):
    return json.dumps({'model': model, 'choices': [{'finish_reason': finish, 'message': {'content': content if content is not None else '{"decision":"research","need":"Which source establishes X?"}'}}], 'usage': usage})

class Contracts(unittest.TestCase):
    def setUp(self):
        self.network = patch.object(socket.socket, 'connect', side_effect=AssertionError('NETWORK FORBIDDEN IN OFFLINE TESTS'))
        self.network.start()
        self.addCleanup(self.network.stop)
        self.cfg = read(P / 'CONFIG.json')
        self.jobs = read(P / 'e1_need/SCHEDULE.json')[:8]

    def test_paid_guard_precedes_credentials_and_network(self):
        with patch('experiments.minimal_need_multiquery.run.audit_prepared', side_effect=AssertionError('must not reach')):
            with self.assertRaises(PermissionError):
                execute(False, '')
            with self.assertRaises(PermissionError):
                execute(True, ' ')

    def test_minimal_schema_rejects_new_semantic_fields(self):
        self.assertTrue(validate_need({'decision': 'research', 'need': 'Which author?'}))
        for obj in ({'decision': 'stop', 'need': 'X'}, {'decision': 'research', 'need': ' '},
                    {'decision': 'research', 'need': 'X', 'confidence': 1}, {'need': 'X'}, []):
            self.assertFalse(validate_need(obj))

    def test_failure_classes_are_retained(self):
        for body, expected in [(response(finish='length'), 'length'), (response(content=''), 'empty_output'),
                               (response(content='{'), 'invalid_json'), (response(content='{"need":"X"}'), 'schema_error'),
                               ('{}', 'response_schema_error'), (response(model='other'), 'model_mismatch')]:
            result = parse_response(200, body, 'deepseek-flash')
            self.assertFalse(result['valid_output'])
            self.assertEqual(result['failure'], expected)

    def test_usage_never_invents_missing_or_double_counts_reasoning(self):
        u = {'prompt_tokens': 10, 'completion_tokens': 20, 'total_tokens': 30,
             'completion_tokens_details': {'reasoning_tokens': 15}, 'prompt_cache_hit_tokens': 8, 'prompt_cache_miss_tokens': 2}
        self.assertTrue(usage_audit(u)['complete'])
        rows = [{'attempted': True, 'usage': u}, {'attempted': True, 'usage': None}, {'attempted': False, 'usage': None}]
        report = accounting_summary(rows)
        self.assertFalse(report['accounting_complete'])
        self.assertEqual(report['reported_partial_totals']['total'], 30)
        self.assertEqual(report['cache_weighted_rate'], .8)
        for key in ('prompt_tokens', 'completion_tokens', 'total_tokens'):
            bad = copy.deepcopy(u); bad[key] = True
            self.assertFalse(usage_audit(bad)['complete'])
        bad = copy.deepcopy(u); bad['total_tokens'] = 99
        self.assertIn('input+output!=total', usage_audit(bad)['inconsistent'])

    def test_auth_formal_canary_short_circuits_all_remaining(self):
        for code in (401, 403):
            seen = []
            def handler(request):
                seen.append(request)
                return httpx.Response(code, json={'error': {'message': 'rejected'}})
            with tempfile.TemporaryDirectory() as d, httpx.Client(transport=httpx.MockTransport(handler)) as client:
                b = Batch(client, 'fake-secret', self.cfg, d, 'mock-head')
                b.run(self.jobs)
                rows = load_rows(d, self.jobs)
                self.assertEqual(len(seen), 1)
                self.assertEqual(len(rows), 8)
                self.assertEqual(sum(r.get('failure') == 'blocked_by_auth' for r in rows), 7)
                self.assertEqual(accounting_summary(rows)['attempted_or_send_intent'], 1)
                self.assertFalse(accounting_summary(rows)['accounting_complete'])
                self.assertNotIn('fake-secret', ''.join(p.read_text() for p in Path(d).rglob('*.json')))

    def test_timeout_no_retry_and_attempt_is_durable(self):
        seen = []
        def handler(request):
            seen.append(request)
            raise httpx.ReadTimeout('mock', request=request)
        with tempfile.TemporaryDirectory() as d, httpx.Client(transport=httpx.MockTransport(handler)) as client:
            b = Batch(client, 'fake', self.cfg, d, 'mock')
            b.one(self.jobs[0])
            rows = load_rows(d, self.jobs[:1])
            self.assertEqual(len(seen), 1)
            self.assertEqual(rows[0]['failure'], 'timeout')
            self.assertTrue(rows[0]['attempted'])
            with self.assertRaises(FileExistsError):
                b.one(self.jobs[0])
            self.assertEqual(len(seen), 1)

    def test_mock_success_uses_frozen_payload(self):
        seen = []
        def handler(request):
            seen.append(json.loads(request.content))
            return httpx.Response(200, text=response())
        with tempfile.TemporaryDirectory() as d, httpx.Client(transport=httpx.MockTransport(handler)) as client:
            Batch(client, 'fake', self.cfg, d, 'mock').run(self.jobs)
            rows = load_rows(d, self.jobs)
            self.assertEqual(len(seen), len(self.jobs))
            self.assertTrue(all(r['valid_output'] for r in rows))
            self.assertEqual(sorted(map(json.dumps, seen)), sorted(json.dumps(j['request']) for j in self.jobs))
            self.assertTrue(all('max_tokens' not in p and 'tools' not in p for p in seen))

    def test_incomplete_attempt_not_resampled_or_removed(self):
        with tempfile.TemporaryDirectory() as d:
            prefix = Path(d) / 'calls' / self.jobs[0]['id']; prefix.parent.mkdir()
            prefix.with_suffix('.attempt.json').write_text('{}')
            rows = load_rows(d, self.jobs)
            self.assertEqual(len(rows), 8)
            self.assertEqual(rows[0]['failure'], 'incomplete_attempt')
            self.assertEqual(rows[1]['failure'], 'not_started')
            self.assertFalse(accounting_summary(rows)['accounting_complete'])

    def test_execution_failure_cannot_count_as_semantic_success(self):
        row = {'valid_output': False}
        label = {'dimensions': {k: None for k in DIMENSIONS}, 'codes': ['X'], 'reason': 'timeout'}
        self.assertFalse(validate_review(row, label))
        label['dimensions']['Coherent'] = True
        with self.assertRaises(ValueError):
            validate_review(row, label)

    def test_coherent_multifacet_can_be_strict_valid(self):
        label = {'dimensions': {k: True for k in DIMENSIONS}, 'codes': [], 'reason': 'One education equality judgment.',
                 'ambiguity': 'low', 'premise_anchors': ['Q names X and Y'], 'objective_decomposition': ['EducationCondition(X,Y)']}
        self.assertTrue(validate_review({'valid_output': True}, label))
        label['codes'] = ['W']
        with self.assertRaises(ValueError):
            validate_review({'valid_output': True}, label)

    def test_fresh_gate_requires_all_conditions_and_integer_boundaries(self):
        b0 = {'n': 40, 'strict_valid': 26, 'p_plus_a_sum': 3, 'codes': {'W': 6}}
        b3 = {'n': 40, 'strict_valid': 32, 'p_plus_a_sum': 2, 'codes': {'W': 4}}
        self.assertEqual(fresh_gate(b0, b3, 14, True)['status'], 'PASS')
        self.assertEqual(fresh_gate(b0, b3, 14, False)['status'], 'FAIL')
        self.assertEqual(fresh_gate(b0, b3, 9, True)['status'], 'FAIL')
        b3['p_plus_a_sum'] = 3
        self.assertEqual(fresh_gate(b0, b3, 14, True)['status'], 'FAIL')

    def test_p_plus_a_sum_and_itt_are_not_silently_relaxed(self):
        rows = [{'valid_output': True, 'strict_valid': False, 'codes': ['P', 'A']},
                {'valid_output': False, 'strict_valid': False, 'codes': ['X']},
                {'valid_output': True, 'strict_valid': True, 'codes': []}]
        result = counts(rows)
        self.assertEqual(result['n'], 3)
        self.assertEqual(result['p_plus_a_sum'], 2)
        self.assertEqual(result['pa_union'], 1)
        self.assertEqual(result['strict_rate'], 1/3)

    def test_full_schedule_aggregation_keeps_pairing_and_no_h(self):
        bank = {s['state_id']: s for s in read(P / 'e1_need/BANK.json')}
        jobs = read(P / 'e1_need/SCHEDULE.json')
        rows, labels = [], {}
        for j in jobs:
            r = {k: j[k] for k in ('id', 'state_id', 'qid', 'arm')}
            r.update(valid_output=True, attempted=True, usage=None)
            rows.append(r)
            labels[j['id']] = {'dimensions': {d: True for d in DIMENSIONS}, 'codes': [],
                              'reason': 'Synthetic scoring fixture, not a model result.', 'ambiguity': 'low',
                              'premise_anchors': [], 'objective_decomposition': ['fixture']}
        lost = next(r for r in rows if r['arm'] == 'B3')
        lost['valid_output'] = False
        labels[lost['id']] = {'dimensions': {d: None for d in DIMENSIONS}, 'codes': ['X'], 'reason': 'mock timeout'}
        result = summarize(rows, labels, bank)
        self.assertEqual(result['by_arm']['B3']['n'], 18)
        self.assertEqual(result['by_arm']['B3']['strict_valid'], 17)
        self.assertEqual(result['no_h']['B0']['n'], 8)
        self.assertEqual(result['paired']['B3']['strict_loss_ids'], [lost['state_id']])
        self.assertFalse(result['mechanism_gate']['opens_E2'])
        self.assertEqual(len(result['by_qid']), 9)

if __name__ == '__main__':
    unittest.main()
