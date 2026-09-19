"""Offline contracts for frozen-prefix extraction; no SDK or retrieval imports."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from experiments.research_state.need_review.checkpoint import (
    CheckpointError,
    canonical_json,
    digest,
    extract_checkpoint,
    load_checkpoint,
    validate_checkpoint,
)


COMMIT = "6d1be8d9b04972d8a55752449294abf12383f554"


def trajectory(batches=None):
    """Build recorder events with API snapshots and complete multi-call batches."""
    if batches is None:
        batches = [[[{'docid': '17', 'text': 'Visible relation.', 'url': 'https://source.test/17'}]]]
    messages = [
        {'role': 'system', 'content': 'Research the user question.'},
        {'role': 'user', 'content': 'Which person satisfies the dated relationship?'},
    ]
    options = {
        'model': 'captured-model', 'messages': messages,
        'tools': [{'type': 'function', 'function': {
            'name': 'search', 'parameters': {'type': 'object'}}}],
        'tool_choice': 'auto', 'stream': False,
        'temperature': 0.2, 'extra_body': {'enable_thinking': False},
    }
    events = []

    def emit(kind, **payload):
        events.append({'seq': len(events) + 1, 'kind': kind, **deepcopy(payload)})

    for batch_index, results in enumerate(batches):
        emit('api_request', request=options)
        calls = [{'id': f'call_{batch_index}_{index}', 'type': 'function',
                  'function': {'name': 'search', 'arguments': '{"query":"clue"}'}}
                 for index in range(len(results))]
        assistant = {'role': 'assistant', 'content': 'A hypothesis, not source evidence.',
                     'tool_calls': calls}
        emit('api_response', response={'choices': [
            {'finish_reason': 'tool_calls', 'message': assistant}]})
        messages.append(deepcopy(assistant))
        for call, result in zip(calls, results):
            emit('tool_start', name='search', arguments={'query': 'clue'})
            emit('tool_result', name='search', result=result,
                 views=[{'docid': 'hidden-full-document', 'window_ref': 'hidden-window'}])
            messages.append({'role': 'tool', 'tool_call_id': call['id'],
                             'content': json.dumps(result, ensure_ascii=False)})
    emit('api_request', request=options)
    return events


class CheckpointTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.events_path = self.directory / 'events.jsonl'

    def write_events(self, events, future=b''):
        prefix = ''.join(json.dumps(event, ensure_ascii=False) + '\n' for event in events).encode('utf-8')
        self.events_path.write_bytes(prefix + future)
        return prefix

    def extract(self, events=None, future=b''):
        events = trajectory() if events is None else events
        self.write_events(events, future)
        return extract_checkpoint(self.events_path, events[-1]['seq'],
                                  checkpoint_id='development-checkpoint',
                                  source_commit=COMMIT, tool_version='v000_baseline',
                                  parent_run='experiments/runs/development')

    @staticmethod
    def resign(checkpoint):
        checkpoint['checkpoint_sha256'] = digest({
            key: value for key, value in checkpoint.items() if key != 'checkpoint_sha256'})

    def test_exact_request_and_hash_stop_before_malformed_future(self):
        events = trajectory()
        # The future is deliberately invalid UTF-8 and invalid JSON.
        prefix = self.write_events(events, b'\xff future gold and unseen-window\n')
        cp = extract_checkpoint(self.events_path, events[-1]['seq'],
                                checkpoint_id='exact', source_commit=COMMIT,
                                tool_version='v000_baseline')
        self.assertEqual(cp['request'], events[-1]['request'])
        self.assertEqual(cp['request_sha256'], digest(events[-1]['request']))
        self.assertEqual(cp['source']['prefix_sha256'], hashlib.sha256(prefix).hexdigest())
        self.assertEqual(cp['references'], [
            {'ref': 'question', 'message_index': 1, 'path': ''},
            {'ref': 'event:4:doc:17', 'message_index': 3, 'path': '/0'},
        ])
        self.assertNotIn('hidden-full-document', canonical_json(cp))
        self.assertNotIn('unseen-window', canonical_json(cp))

    def test_unselected_event_metadata_is_not_exposed(self):
        events = trajectory()
        events[0]['evaluation_only'] = {'answer': 'HIDDEN_EVALUATION_VALUE'}
        events[-2]['cached_fulltext'] = 'UNSEEN_CACHED_FULLTEXT'
        cp = self.extract(events)
        self.assertNotIn('HIDDEN_EVALUATION_VALUE', canonical_json(cp))
        self.assertNotIn('UNSEEN_CACHED_FULLTEXT', canonical_json(cp))

    def test_complete_multi_call_batch_keeps_every_observation(self):
        events = trajectory([[
            [{'docid': 'first', 'text': 'First source'}],
            [{'docid': 'second', 'text': 'Second source'}],
        ]])
        cp = self.extract(events)
        self.assertEqual([event['event_seq'] for event in cp['source']['tool_events']], [4, 6])
        self.assertEqual([ref['ref'] for ref in cp['references']],
                         ['question', 'event:4:doc:first', 'event:6:doc:second'])
        self.assertEqual(len(cp['request']['messages'][-3]['tool_calls']), 2)

    def test_partial_tool_batch_is_rejected(self):
        events = trajectory([[[{'docid': 'one', 'text': 'One'}],
                              [{'docid': 'two', 'text': 'Two'}]]])
        events[-1]['request']['messages'].pop()
        with self.assertRaisesRegex(CheckpointError, 'incomplete tool batch'):
            self.extract(events)

    def test_no_intermediate_user_message_inside_tool_batch(self):
        events = trajectory()
        events[-1]['request']['messages'].insert(3, {'role': 'user', 'content': 'Interruption'})
        with self.assertRaisesRegex(CheckpointError, 'incomplete tool batch'):
            self.extract(events)

    def test_orphan_and_duplicate_ids_are_rejected(self):
        events = trajectory()
        events[-1]['request']['messages'][-1]['tool_call_id'] = 'not-issued'
        with self.assertRaisesRegex(CheckpointError, 'orphan'):
            self.extract(events)
        events = trajectory([[[{'docid': 'one', 'text': 'One'}]],
                             [[{'docid': 'two', 'text': 'Two'}]]])
        events[-1]['request']['messages'][4]['tool_calls'][0]['id'] = 'call_0_0'
        with self.assertRaisesRegex(CheckpointError, 'duplicate tool call id'):
            self.extract(events)

    def test_tool_result_name_content_and_order_must_match(self):
        for change in ('name', 'content', 'order'):
            with self.subTest(change=change):
                events = trajectory([[[{'docid': 'one', 'text': 'One'}],
                                      [{'docid': 'two', 'text': 'Two'}]]])
                if change == 'name':
                    events[3]['name'] = 'get_document'
                elif change == 'content':
                    events[3]['result'][0]['text'] = 'Unseen full text'
                else:
                    events[3]['result'], events[5]['result'] = events[5]['result'], events[3]['result']
                with self.assertRaisesRegex(CheckpointError, 'differs from recorded'):
                    self.extract(events)

    def test_unlogged_tool_observation_is_rejected(self):
        events = trajectory()
        events[3]['kind'] = 'tool_error'
        with self.assertRaisesRegex(CheckpointError, 'do not match recorded'):
            self.extract(events)

    def test_references_require_actual_visible_text_objects(self):
        results = {'items': [
            {'docid': 'visible', 'text': 'Text', 'window_ref': 'window:visible',
             'parent_window_ref': 'window:parent-unseen'},
            {'docid': 'metadata-only', 'window_ref': 'window:metadata-only'},
        ], 'a/b~': {'docid': 'escaped', 'text': 'Text'},
            'text_blob': '{"window_ref":"window:string-only","text":"Not a returned object"}'}
        events = trajectory([[results], [results]])
        events[-1]['request']['messages'][2]['content'] = 'Assistant claims window:invented'
        cp = self.extract(events)
        self.assertEqual(cp['references'], [
            {'ref': 'question', 'message_index': 1, 'path': ''},
            {'ref': 'window:visible', 'message_index': 3, 'path': '/items/0'},
            {'ref': 'event:4:doc:escaped', 'message_index': 3, 'path': '/a~1b~0'},
            {'ref': 'window:visible', 'message_index': 5, 'path': '/items/0'},
            {'ref': 'event:8:doc:escaped', 'message_index': 5, 'path': '/a~1b~0'},
        ])

    def test_source_sequence_and_selected_kind_are_checked(self):
        events = trajectory()
        self.write_events(events)
        with self.assertRaisesRegex(CheckpointError, 'not an api_request'):
            extract_checkpoint(self.events_path, 4, checkpoint_id='x', source_commit=COMMIT,
                               tool_version='v000_baseline')
        with self.assertRaisesRegex(CheckpointError, 'not found'):
            extract_checkpoint(self.events_path, 99, checkpoint_id='x', source_commit=COMMIT,
                               tool_version='v000_baseline')
        events[2]['seq'] = 100
        with self.assertRaisesRegex(CheckpointError, 'contiguous'):
            self.extract(events)

    def test_original_question_stream_and_model_are_required(self):
        for change in ('question', 'stream', 'model'):
            with self.subTest(change=change):
                events = trajectory()
                request = events[-1]['request']
                if change == 'question':
                    request['messages'][1]['content'] = ''
                else:
                    request.pop(change)
                with self.assertRaises(CheckpointError):
                    self.extract(events)

    def test_credentials_and_transport_fields_are_rejected_without_echoing_values(self):
        for field in ('api_key', 'extra_headers', 'nested_authorization'):
            with self.subTest(field=field):
                events = trajectory()
                request = events[-1]['request']
                if field == 'nested_authorization':
                    request['extra_body']['Authorization'] = 'DO_NOT_ECHO'
                else:
                    request[field] = 'DO_NOT_ECHO'
                with self.assertRaises(CheckpointError) as caught:
                    self.extract(events)
                self.assertNotIn('DO_NOT_ECHO', str(caught.exception))

    def test_load_never_needs_original_events_and_returns_independent_copy(self):
        cp = self.extract()
        prepared = self.directory / 'checkpoint.json'
        prepared.write_text(canonical_json(cp), encoding='utf-8')
        self.events_path.unlink()
        loaded = load_checkpoint(prepared)
        loaded['request']['messages'][1]['content'] = 'Changed externally'
        self.assertNotEqual(loaded['request'], cp['request'])
        copied = validate_checkpoint(cp)
        copied['source']['tool_events'].clear()
        self.assertEqual(len(cp['source']['tool_events']), 1)

    def test_outer_hash_request_hash_and_recomputed_reference_membership(self):
        cp = self.extract()
        changed = deepcopy(cp)
        changed['checkpoint_id'] = 'changed'
        with self.assertRaisesRegex(CheckpointError, 'checkpoint_sha256 mismatch'):
            validate_checkpoint(changed)
        changed = deepcopy(cp)
        changed['request']['messages'][1]['content'] = 'A different question'
        self.resign(changed)
        with self.assertRaisesRegex(CheckpointError, 'request_sha256 mismatch'):
            validate_checkpoint(changed)
        changed = deepcopy(cp)
        changed['references'].append({'ref': 'unseen', 'message_index': 3, 'path': '/0'})
        self.resign(changed)
        with self.assertRaisesRegex(CheckpointError, 'reference index differs'):
            validate_checkpoint(changed)

    def test_source_metadata_cannot_introduce_future_or_hidden_text(self):
        cp = self.extract()
        for change in ('future', 'hidden_text', 'wrong_content_hash'):
            with self.subTest(change=change):
                changed = deepcopy(cp)
                event = changed['source']['tool_events'][0]
                if change == 'future':
                    event['event_seq'] = 999
                elif change == 'hidden_text':
                    event['text'] = 'Not part of the visible request'
                else:
                    event['result_sha256'] = '0' * 64
                self.resign(changed)
                with self.assertRaises(CheckpointError):
                    validate_checkpoint(changed)

    def test_extra_source_provenance_is_hashed_and_paths_are_portable(self):
        cp = self.extract()
        cp['source']['events_path'] = 'experiments/runs/selected/events.jsonl'
        cp['source']['events_blob_sha'] = 'a' * 40
        self.resign(cp)
        self.assertEqual(validate_checkpoint(cp), cp)

    def test_duplicate_json_keys_and_nonfinite_numbers_are_rejected(self):
        self.events_path.write_text('{"seq":1,"seq":2,"kind":"api_request"}\n', encoding='utf-8')
        with self.assertRaisesRegex(CheckpointError, 'duplicate JSON'):
            extract_checkpoint(self.events_path, 1, checkpoint_id='x', source_commit=COMMIT,
                               tool_version='v000_baseline')
        with self.assertRaises(ValueError):
            canonical_json({'number': float('nan')})
        with self.assertRaises(ValueError):
            canonical_json({'number': float('inf')})
        self.assertEqual(canonical_json({'中文': '原题', 'a': 1}), '{"a":1,"中文":"原题"}')
        self.assertEqual(digest({'b': 2, 'a': 1}), digest({'a': 1, 'b': 2}))


if __name__ == '__main__':
    unittest.main()
