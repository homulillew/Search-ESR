"""Backward-compatibility and shared-runner regressions.

Proves the evidence_pointer integration did not change the existing stages, and
that the authentication short-circuit is an execution-layer reliability fix that
applies to every stage rather than to one experiment.

No model, search or open call is made anywhere in this module.
"""
from __future__ import annotations
from copy import deepcopy
from collections import Counter
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

from experiments.research_state.first_observation import artifacts as io
from experiments.research_state.first_observation import contracts as c
from experiments.research_state.first_observation import fidelity as f
from experiments.research_state.first_observation import run as r
from experiments.research_state.evidence_pointer import contracts as ec
from experiments.research_state.evidence_pointer import run as ep

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


def collection(n=6):
    cases = [{'id': str(i), 'question': f'Who wrote book {i}?  \n'} for i in range(n)]
    selection = c.seal({'version': c.VERSION, 'kind': 'selection',
                        'dataset_sha256': 'b' * 64, 'cases': cases})
    return c.seal({'version': c.VERSION, 'kind': 'collection', 'mode': 'mock',
        'selection': selection, 'retrieval': {'adapter': 'mock'}, 'k': 5,
        'max_query_tokens': 1024, 'tools': TOOLS, 'fingerprint': io.fingerprint(),
        'initial_model_calls': 0, 'capture_complete': True,
        'cases': [{**case, 'query': case['question'], 'status': 'ok', 'query_tokens': 8,
                   'observation': [window()]} for case in cases]})


def note_response(finish='stop'):
    return {'choices': [{'finish_reason': finish, 'message': {'role': 'assistant',
        'content': c.canonical({'notes': [{'statement': 'The book quotes a later tea visit.',
            'source_ref': 'w_mock',
            'quote': 'The book quotes a later tea visit.'}]})}}],
        'usage': {'prompt_tokens': 50, 'completion_tokens': 10, 'total_tokens': 60}}


class FakeAPIError(Exception):
    pass


class AuthRejected(FakeAPIError):
    """Stands in for openai.AuthenticationError: a voided credential."""


class Client:
    def __init__(self, effect=None):
        self.chat = SimpleNamespace(completions=self)
        self.requests = []
        self.effect = note_response() if effect is None else effect
        self.base_url = CONFIG['base_url']
        self.timeout = CONFIG['timeout_seconds']
        self.max_retries = 0

    def create(self, **request):
        self.requests.append(deepcopy(request))
        if isinstance(self.effect, BaseException):
            raise self.effect
        return deepcopy(self.effect)


class OldPathRegressionTests(unittest.TestCase):
    """The note and actor stages must behave exactly as before the integration."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.col = collection()
        self.notes = r.make_plan(self.col, CONFIG, 'notes')

    def tearDown(self):
        self.tmp.cleanup()

    def test_note_stage_plan_and_execute_unchanged(self):
        summary = r.execute(self.notes, Client(), self.root / 'notes',
                            mode='mock', api_error_types=(FakeAPIError,))
        self.assertEqual(len(summary['jobs']) if 'jobs' in summary else 0, 0)
        self.assertEqual(summary['scheduled'], 6)
        self.assertEqual(summary['statuses'], {'ok': 6})
        self.assertTrue(summary['all_model_jobs_delivered'])
        self.assertEqual(summary['initial_model_calls'], 0)
        self.assertEqual(summary['tool_executions'], 0)

    def test_source_files_default_root_is_first_observation(self):
        files = io.source_files()
        self.assertEqual(files, io.source_files(Path(__file__).resolve().parents[1]
                            / 'experiments/research_state/first_observation'))
        self.assertIn('contracts.py', [p.name for p in files])

    def test_source_files_explicit_root(self):
        root = Path(ep.__file__).parent
        names = {p.name for p in io.source_files(root)}
        self.assertEqual(names, {'__init__.py', 'contracts.py', 'run.py', 'actor.txt'})
        self.assertIn('prompts/actor.txt',
                      {p.relative_to(root).as_posix() for p in io.source_files(root)})
        self.assertEqual(io.sources(root), io.fingerprint(root)['source_sha256'])

    def test_unknown_stage_still_rejected(self):
        bad = deepcopy(self.notes)
        bad['stage'] = 'something_new'
        with self.assertRaises(ValueError):
            r.validate_plan(bad)

    def test_actor_stage_still_builds_and_validates(self):
        r.execute(self.notes, Client(), self.root / 'notes',
                  mode='mock', api_error_types=(FakeAPIError,))
        actor = r.make_plan(self.col, CONFIG, 'actors',
                            prior=r.note_outputs(self.root / 'notes'))
        self.assertEqual(Counter(j['arm'] for j in actor['jobs']), {'A': 6, 'B': 6})
        r.validate_plan(actor)


class AuthShortCircuitTests(unittest.TestCase):
    """The historical 12/12 AuthenticationError batches must not be reproducible."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.col = collection(n=4)
        self.notes = r.make_plan(self.col, CONFIG, 'notes')

    def tearDown(self):
        self.tmp.cleanup()

    def test_auth_failure_stops_a_notes_batch(self):
        client = Client(AuthRejected('401'))
        summary = r.execute(self.notes, client, self.root / 'notes', mode='mock',
                            api_error_types=(FakeAPIError,),
                            auth_error_types=(AuthRejected,))
        self.assertEqual(len(client.requests), 1)
        self.assertEqual(summary['statuses'], {'api_error': 1, 'blocked_by_auth': 3})
        self.assertEqual(summary['attempts'], 1)
        self.assertFalse(summary['all_model_jobs_delivered'])

    def test_without_auth_types_the_old_behaviour_is_preserved(self):
        """Default (no auth_error_types) keeps sending, matching the archived batches."""
        client = Client(AuthRejected('401'))
        summary = r.execute(self.notes, client, self.root / 'notes', mode='mock',
                            api_error_types=(FakeAPIError,))
        self.assertEqual(len(client.requests), 4)
        self.assertEqual(summary['statuses'], {'api_error': 4})
        self.assertNotIn('blocked_by_auth', summary['statuses'])

    def test_blocked_by_auth_journal_sequence(self):
        client = Client(AuthRejected('401'))
        r.execute(self.notes, client, self.root / 'notes', mode='mock',
                  api_error_types=(FakeAPIError,), auth_error_types=(AuthRejected,))
        kinds = {}
        for job in self.notes['jobs']:
            events = io.journal_prefix(self.root / 'notes' / job['id'] / 'events.jsonl')[0]
            kinds[job['id']] = [e['kind'] for e in events]
        self.assertEqual(Counter(tuple(v) for v in kinds.values()),
                         Counter({('request', 'api_error'): 1, ('blocked_by_auth',): 3}))

    def test_export_review_still_accounts_blocked_jobs(self):
        client = Client(AuthRejected('401'))
        r.execute(self.notes, client, self.root / 'notes', mode='mock',
                  api_error_types=(FakeAPIError,), auth_error_types=(AuthRejected,))
        summary = r.export_review(self.root / 'notes', self.root / 'review')
        self.assertEqual(summary['scheduled'], 4)
        self.assertEqual(Counter(x['status'] for x in io.read(
            self.root / 'review' / 'mapping.json')),
            Counter({'api_error': 1, 'blocked_by_auth': 3}))

    def test_blocked_jobs_are_never_resumed_silently(self):
        """No implicit resume: a partially failed batch cannot be re-run in place."""
        client = Client(AuthRejected('401'))
        r.execute(self.notes, client, self.root / 'notes', mode='mock',
                  api_error_types=(FakeAPIError,), auth_error_types=(AuthRejected,))
        with self.assertRaises(FileExistsError):
            r.execute(self.notes, Client(note_response()), self.root / 'notes',
                      mode='mock', api_error_types=(FakeAPIError,))


if __name__ == '__main__':
    unittest.main()
