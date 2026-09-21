"""Offline P0/P1 contracts and fault injection, not model-quality measurements."""
from __future__ import annotations
from copy import deepcopy
from collections import Counter
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from experiments.research_state.first_observation import fidelity as f
from experiments.research_state.first_observation import run as r
from experiments.research_state.first_observation import artifacts as io
from experiments.research_state.first_observation import contracts as c


CONFIG = {'model': 'mock-only', 'base_url': 'https://example.invalid/v1',
          'timeout_seconds': 180, 'request_options': {'max_tokens': 8192},
          'max_request_utf8_bytes': 1000000, 'allow_tool_calls_with_stop': False}
TOOLS = [{'type': 'function', 'function': {'name': name, 'parameters': {}}}
         for name in ('search', 'open')]
TEXT = 'The article describes a meeting. The book quotes a later tea visit.\n'


def window():
    return {'window_ref': 'w_mock', 'docid': 'synthetic', 'document_sha256': 'a' * 64,
            'url': 'https://example.invalid/source', 'title': '', 'text': TEXT,
            'offset': 0, 'end_char': len(TEXT), 'text_tokens': 20, 'title_tokens': 0}


def collection():
    cases = [{'id': str(i), 'question': f'Who wrote book {i}?  \n'} for i in range(6)]
    selection = c.seal({'version': c.VERSION, 'kind': 'selection',
                        'dataset_sha256': 'b' * 64, 'cases': cases})
    return c.seal({'version': c.VERSION, 'kind': 'collection', 'mode': 'mock',
        'selection': selection, 'retrieval': {'adapter': 'mock'}, 'k': 5,
        'max_query_tokens': 1024, 'tools': TOOLS, 'fingerprint': io.fingerprint(),
        'initial_model_calls': 0, 'capture_complete': True,
        'cases': [{**case, 'query': case['question'], 'status': 'ok', 'query_tokens': 8,
                   'observation': [window()]} for case in cases]})


def note_response(text='The book quotes a later tea visit.', finish='stop', note_text=None):
    notes = [{'statement': text, 'source_ref': 'w_mock', 'quote': 'The book quotes a later tea visit.'}]
    return {'choices': [{'finish_reason': finish, 'message': {'role': 'assistant',
        'content': c.canonical({'notes': notes}) if note_text is None else note_text,
        'reasoning_content': 'PRIVATE_MOCK_REASONING'}}],
        'usage': {'prompt_tokens': 50, 'completion_tokens': 10, 'total_tokens': 60,
                  'completion_tokens_details': {'reasoning_tokens': 8}}}


class FakeAPIError(Exception):
    pass


class Client:
    def __init__(self, effects=None, mutate=False):
        self.chat = SimpleNamespace(completions=self)
        self.requests = []
        self.effects = effects or {}
        self.mutate = mutate
        self.base_url = CONFIG['base_url']
        self.timeout = CONFIG['timeout_seconds']
        self.max_retries = 0

    def create(self, **request):
        self.requests.append(deepcopy(request))
        effect = self.effects.get(len(self.requests), note_response())
        if self.mutate:
            request['messages'].clear()
        if isinstance(effect, BaseException):
            raise effect
        return deepcopy(effect)


class FidelityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.col = collection()
        self.parent = r.make_plan(self.col, CONFIG, 'notes')
        self.plan = f.make_fidelity_plan(self.parent, origin='synthetic_test')
        self.basis = f.review_template(self.plan)
        self.basis['reviewer'] = 'offline-test'
        for row in self.basis['cases']:
            row['core_relations'] = [{'id': 'tea', 'description': 'Keep the book/tea relation',
                                     'source_ref': 'w_mock', 'quote': 'The book quotes a later tea visit.'}]
            row['limits_and_alternatives'] = 'Do not extend the book attribution to the meeting.'
        self.auth = f.authorize(self.plan, self.basis)

    def tearDown(self):
        self.tmp.cleanup()

    def execute(self, client=None):
        return r.execute(self.plan, client or Client(), self.root / 'run',
                         api_error_types=(FakeAPIError,), preoutput_review=self.auth)

    def test_twelve_jobs_balanced_pair_order(self):
        self.assertEqual(len(self.plan['jobs']), 12)
        self.assertEqual(Counter(j['arm'] for j in self.plan['jobs'][::2]), {'P0': 3, 'P1': 3})
        for i in range(0, 12, 2):
            a, b = self.plan['jobs'][i:i+2]
            self.assertEqual(a['case_id'], b['case_id'])
            self.assertEqual({a['arm'], b['arm']}, {'P0', 'P1'})

    def test_only_system_prompt_differs(self):
        for i in range(0, 12, 2):
            a, b = [deepcopy(j['request']) for j in self.plan['jobs'][i:i+2]]
            self.assertNotEqual(a['messages'][0], b['messages'][0])
            a['messages'][0] = b['messages'][0]
            self.assertEqual(a, b)
            self.assertNotIn('tools', a)
            self.assertNotIn('tool_choice', a)

    def test_p0_identical_to_old_request(self):
        old = {j['case_id']: j['request'] for j in self.parent['jobs']}
        for job in self.plan['jobs']:
            if job['arm'] == 'P0':
                self.assertEqual(job['request'], old[job['case_id']])

    def test_no_gold_or_review_basis_in_payload(self):
        for job in self.plan['jobs']:
            payload = c.loads(job['request']['messages'][1]['content'])
            self.assertEqual(set(payload), {'question', 'first_query', 'observation'})
            self.assertEqual(payload['question'], payload['first_query'])
            self.assertTrue(payload['question'].endswith('  \n'))
            self.assertNotIn('Keep the book/tea relation', c.canonical(job['request']))

    def test_p1_extends_original_without_replacing_it(self):
        self.assertTrue(self.plan['prompts']['P1'].startswith(self.plan['prompts']['P0'] + '\n'))
        self.assertEqual(self.plan['profile'], self.parent['profile'])
        self.assertEqual(self.plan['planned_tool_executions'], 0)

    def test_synthetic_cannot_use_archive_origin(self):
        with self.assertRaises(ValueError):
            f.make_fidelity_plan(self.parent)

    def test_synthetic_cannot_be_marked_live(self):
        bad = deepcopy(self.parent)
        bad['collection']['mode'] = 'live'
        bad['collection'] = c.seal({k: v for k, v in bad['collection'].items() if k != 'sha256'})
        bad = c.seal({k: v for k, v in bad.items() if k != 'sha256'})
        with self.assertRaises(ValueError):
            f.make_fidelity_plan(bad, origin='synthetic_test')

    def test_plan_tampered_and_resealed_request_rejected(self):
        bad = deepcopy(self.plan)
        bad['jobs'][0]['request']['messages'][1]['content'] += 'hint'
        bad = c.seal({k: v for k, v in bad.items() if k != 'sha256'})
        with self.assertRaises(ValueError):
            r.validate_plan(bad)

    def test_runtime_drift_rejected(self):
        with patch.object(io, 'fingerprint', return_value={'runtime': 'changed'}):
            with self.assertRaises(ValueError):
                r.validate_plan(self.plan)

    def test_prompt_drift_rejected(self):
        with patch.object(f, '_prompts', return_value={'P0': 'changed', 'P1': 'changed too'}):
            with self.assertRaises(ValueError):
                r.validate_plan(self.plan)

    def test_incomplete_review_rejected_before_calls(self):
        client = Client()
        with self.assertRaises(ValueError):
            r.execute(self.plan, client, self.root / 'run')
        self.assertEqual(client.requests, [])
        self.assertFalse((self.root / 'run').exists())

    def test_review_bad_quote_rejected(self):
        self.basis['cases'][0]['core_relations'][0]['quote'] = 'not visible'
        with self.assertRaises(ValueError):
            f.authorize(self.plan, self.basis)

    def test_review_requires_explicit_no_core(self):
        self.basis['cases'][0]['core_relations'] = []
        with self.assertRaises(ValueError):
            f.authorize(self.plan, self.basis)
        self.basis['cases'][0]['no_clear_core'] = True
        f.authorize(self.plan, self.basis)

    def test_review_cannot_be_after_outputs(self):
        self.basis['current_outputs_seen'] = True
        with self.assertRaises(ValueError):
            f.authorize(self.plan, self.basis)

    def test_review_missing_case_rejected(self):
        self.basis['cases'].pop()
        with self.assertRaises(ValueError):
            f.authorize(self.plan, self.basis)

    def test_twelve_calls_source_snapshots_and_cards(self):
        client = Client(mutate=True)
        summary = self.execute(client)
        self.assertEqual(len(client.requests), 12)
        self.assertTrue(summary['all_model_jobs_delivered'])
        self.assertEqual(summary['statuses'], {'ok': 12})
        self.assertEqual(summary['tool_executions'], 0)
        self.assertEqual(summary['by_arm']['P0']['attempts'], 6)
        self.assertEqual(summary['by_arm']['P1']['attempts'], 6)
        self.assertEqual(client.requests, [j['request'] for j in self.plan['jobs']])
        f.export_review(self.root / 'run', self.root / 'review')
        cards = io.read(self.root / 'review/cards.json')
        self.assertEqual(len(cards), 12)
        self.assertTrue(all(len(card['notes']) == 1 for card in cards))
        self.assertTrue(all(card['notes'][0]['labels']['source_support'] is None for card in cards))
        self.assertNotIn('PRIVATE_MOCK_REASONING', c.canonical(cards))
        self.assertTrue(all('arm' not in card for card in cards))
        self.assertEqual(len(io.read(self.root / 'review/mapping.json')), 12)

    def test_valid_empty_is_not_failed_or_semantic_success(self):
        self.execute(Client({1: note_response(note_text='{"notes":[]}')}))
        f.export_review(self.root / 'run', self.root / 'review')
        cards = io.read(self.root / 'review/cards.json')
        empty = next(card for card in cards if card['status'] == 'empty')
        self.assertEqual(empty['notes'], [])
        self.assertIsNone(empty['set_labels']['core_preserved'])
        self.assertEqual(len(empty['core_coverage']), 1)

    def test_invalid_ref_retained_no_repair(self):
        raw = note_response()
        raw['choices'][0]['message']['content'] = raw['choices'][0]['message']['content'].replace('w_mock', 'w_bad')
        client = Client({1: raw})
        summary = self.execute(client)
        self.assertEqual(summary['statuses'], {'invalid': 1, 'ok': 11})
        self.assertEqual(len(client.requests), 12)
        self.assertEqual(r.audit(self.root / 'run')[1][0]['response'], raw)

    def test_length_reasoning_only_not_salvaged(self):
        raw = note_response(finish='length')
        raw['choices'][0]['message']['content'] = None
        raw['choices'][0]['message']['reasoning_content'] = '{"notes":[]}'
        summary = self.execute(Client({1: raw}))
        self.assertEqual(summary['statuses'].get('invalid'), 1)
        row = r.audit(self.root / 'run')[1][0]
        self.assertIsNone(row['classification']['notes'])

    def test_api_timeout_kept_unknown_no_retry(self):
        client = Client({2: FakeAPIError('do not log secret text')})
        summary = self.execute(client)
        self.assertEqual(len(client.requests), 12)
        self.assertEqual(summary['statuses']['api_error'], 1)
        self.assertEqual(summary['unknown_usage_requests'], 1)
        self.assertFalse(summary['cost_accounting_complete'])
        self.assertNotIn('do not log secret', ''.join(p.read_text() for p in (self.root / 'run').glob('*/events.jsonl')))

    def test_usage_inconsistency_kept(self):
        raw = note_response(); raw['usage']['total_tokens'] = 999
        summary = self.execute(Client({1: raw}))
        self.assertEqual(summary['responses_inconsistent_usage'], 1)
        self.assertFalse(summary['cost_accounting_complete'])

    def test_missing_usage_not_zero(self):
        raw = note_response(); del raw['usage']
        summary = self.execute(Client({1: raw}))
        self.assertEqual(summary['unknown_usage_requests'], 1)
        self.assertEqual(summary['reported_token_lower_bounds']['total_tokens'], 11 * 60)

    def test_interrupt_retains_full_denominator(self):
        client = Client({2: KeyboardInterrupt()})
        with self.assertRaises(KeyboardInterrupt):
            self.execute(client)
        summary, rows = r.audit(self.root / 'run')
        self.assertEqual(len(rows), 12)
        self.assertEqual(summary['statuses'], {'ok': 1, 'incomplete': 1, 'not_run': 10})
        f.export_review(self.root / 'run', self.root / 'review')
        self.assertEqual(len(io.read(self.root / 'review/cards.json')), 12)

    def test_programming_error_stops_not_api_error(self):
        client = Client({1: RuntimeError('local bug')})
        with self.assertRaises(RuntimeError):
            self.execute(client)
        self.assertEqual(len(client.requests), 1)
        summary = io.read(self.root / 'run/summary.json')
        self.assertNotIn('api_error', summary['statuses'])
        self.assertGreater(summary['audit_errors'], 0)

    def test_no_overwrite_or_implicit_resume(self):
        self.execute()
        client = Client()
        with self.assertRaises(FileExistsError):
            self.execute(client)
        self.assertEqual(client.requests, [])

    def test_corrupt_journal_suffix_preserves_responses_and_flags_error(self):
        self.execute()
        path = self.root / 'run' / self.plan['jobs'][0]['id'] / 'events.jsonl'
        with path.open('a') as stream:
            stream.write('{broken')
        summary, rows = r.audit(self.root / 'run')
        self.assertGreater(summary['audit_errors'], 0)
        self.assertFalse(rows[0]['semantic_eligible'])

    def test_snapshot_mutation_blocks_audit(self):
        self.execute()
        path = self.root / 'run/source/prompts/note_fidelity_addendum.txt'
        path.write_text('changed')
        with self.assertRaises(ValueError):
            r.audit(self.root / 'run')

    def test_review_mutation_blocks_audit_even_resealed(self):
        self.execute()
        path = self.root / 'run/preoutput_review.json'
        modified = io.read(path)
        modified['review_basis']['reviewer'] = 'someone else'
        io.write(path, c.seal({k: v for k, v in modified.items() if k != 'sha256'}))
        with self.assertRaises(ValueError):
            r.audit(self.root / 'run')

    def test_comparison_cannot_be_exported_as_one_note_per_case(self):
        self.execute()
        with self.assertRaises(ValueError):
            r.note_outputs(self.root / 'run')

    def test_ordinary_note_stage_still_works(self):
        client = Client()
        summary = r.execute(self.parent, client, self.root / 'ordinary')
        self.assertEqual(len(client.requests), 6)
        self.assertEqual(summary['statuses'], {'ok': 6})
        outputs = r.note_outputs(self.root / 'ordinary')
        self.assertEqual(len(outputs['cases']), 6)

    def test_ordinary_stage_rejects_unrelated_attestation(self):
        with self.assertRaises(ValueError):
            r.execute(self.parent, Client(), self.root / 'ordinary', preoutput_review=self.auth)

    def test_syntactic_validity_is_not_semantic_entailment(self):
        raw = note_response(text='The book contains both the meeting and the tea event.')
        # Deliberately unsupported broadening; the mechanical validator must NOT be
        # advertised as an entailment judge. Human evaluation is separate.
        self.assertEqual(c.note_result(raw, [window()])['status'], 'ok')

    def test_no_live_from_mock_collection(self):
        with self.assertRaises(ValueError):
            r.execute(self.plan, Client(), self.root / 'live', mode='live', preoutput_review=self.auth)

    def test_parent_bad_seal_rejected(self):
        self.parent['profile']['request_options']['max_tokens'] = 16384
        with self.assertRaises(ValueError):
            f.make_fidelity_plan(self.parent, origin='synthetic_test')


    def test_existing_actor_ab_stage_is_unchanged(self):
        r.execute(self.parent, Client(), self.root / 'ordinary')
        prior = r.note_outputs(self.root / 'ordinary')
        plan = r.make_plan(self.col, CONFIG, 'actors', prior=prior)
        raw = {'choices': [{'finish_reason': 'tool_calls', 'message': {'role': 'assistant',
            'content': None, 'tool_calls': [{'id': 'x', 'type': 'function', 'function': {
                'name': 'search', 'arguments': '{"query":"test"}'}}]}}],
            'usage': {'prompt_tokens': 50, 'completion_tokens': 10, 'total_tokens': 60}}
        client = Client({i: raw for i in range(1, 13)})
        summary = r.execute(plan, client, self.root / 'actors')
        self.assertEqual(summary['statuses'], {'ok': 12})
        self.assertEqual(summary['by_arm']['B']['memo_injected'], 6)
        self.assertEqual(summary['by_arm']['A']['memo_injected'], 0)
        self.assertEqual(summary['tool_executions'], 0)

    def test_archive_loader_checks_inputs_without_reading_model_outputs(self):
        # Synthetic archive exercises the complete loader, not the real corpus.
        col = deepcopy(self.col); col['mode'] = 'live'
        col = c.seal({k: v for k, v in col.items() if k != 'sha256'})
        old = r.make_plan(col, CONFIG, 'notes')
        archive = self.root / 'archive'; archive.mkdir()
        cap = archive / 'capture'; cap.mkdir()
        io.write(archive / 'notes-plan.json', old)
        io.write(cap / 'collection.json', col)
        io.write(cap / 'collect_plan.json', c.seal({k: v for k, v in col.items()
                   if k not in {'cases', 'capture_complete', 'sha256'}}))
        for case in col['cases']:
            folder = cap / case['id']; folder.mkdir()
            journal = io.Journal(folder / 'events.jsonl')
            journal.emit('search_request', arguments={'query': case['question'], 'k': 5})
            journal.emit('search_response', observation=case['observation'])
        (archive / 'note_outputs.json').write_text('DO NOT READ: invalid old output')
        with patch.object(f, 'ARCHIVE_PLAN_SHA', old['sha256']), \
             patch.object(f, 'COLLECTION_SHA', col['sha256']), \
             patch.object(f, 'CASE_IDS', tuple(x['id'] for x in col['cases'])):
            plan = f.plan_from_archive(archive)
            self.assertEqual(plan['profile'], CONFIG)
            self.assertEqual(len(plan['jobs']), 12)
            self.assertEqual(plan['collection'], col)

    def test_p0_byte_change_is_rejected(self):
        package = self.root / 'p0changed'; (package / 'prompts').mkdir(parents=True)
        (package / 'prompts/note.txt').write_text('slightly different prompt')
        with patch.object(f, 'PACKAGE', package):
            with self.assertRaises(ValueError):
                f.make_fidelity_plan(self.parent, origin='synthetic_test')

    def test_review_is_recorded_before_first_request(self):
        from datetime import datetime
        self.execute()
        execution = io.read(self.root / 'run/execution.json')
        events, _ = io.journal_prefix(self.root / 'run' / self.plan['jobs'][0]['id'] / 'events.jsonl')
        self.assertLessEqual(datetime.fromisoformat(execution['preoutput_review_recorded_at']),
                             datetime.fromisoformat(events[0]['time']))


class ActualArchiveTests(unittest.TestCase):
    @unittest.skipUnless((f.ARCHIVE / 'notes-plan.json').is_file(), 'Complete 3d5fc3d archive not mounted')
    def test_pinned_archive_prepares_offline(self):
        plan = f.plan_from_archive()
        self.assertEqual(len(plan['jobs']), 12)
        self.assertEqual(plan['collection']['sha256'], f.COLLECTION_SHA)
        self.assertEqual([c['id'] for c in plan['collection']['cases']], list(f.CASE_IDS))
        self.assertEqual(plan['profile']['request_options'], {'max_tokens': 8192})
        self.assertEqual(plan['profile']['timeout_seconds'], 180)
        r.validate_plan(plan)


if __name__ == '__main__':
    unittest.main()
