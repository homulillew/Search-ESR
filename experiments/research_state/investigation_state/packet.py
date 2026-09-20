"""Lossless source views plus explicitly curated notebook/task fixtures.

The compiler does not summarize, discover candidates, judge entailment, or call
any tools. Attempt linkage describes exact recorded inputs/observations, never
information gain. A statement's quote membership is not a truth certificate.
"""
from __future__ import annotations
from copy import deepcopy
import re
from ..need_review.checkpoint import digest, validate_checkpoint
from .storage import loads, sealed, verify_seal

NOTE_KINDS = ('given_constraint', 'observed_finding', 'hypothesis', 'unresolved')
ROLE_KINDS = {'system': 'historical_instructions', 'developer': 'historical_instructions',
              'user': 'original_question', 'assistant': 'past_analysis', 'tool': 'raw_observations'}
GROUP_ORDER = ('original_question', 'given_constraint', 'observed_finding', 'hypothesis',
               'unresolved', 'current_task', 'attempts', 'raw_observations',
               'past_analysis', 'historical_instructions')
COMPARISONS = {'layout': ('flat', 'typed'), 'attempt_linkage': ('typed', 'linked')}


def text(value: object, label: str, limit: int = 4000) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ValueError(f'{label} must be nonempty text within {limit} characters')
    return value


def resolve(cp: dict, ref: str) -> object:
    matches = [r for r in cp['references'] if r['ref'] == ref]
    if not matches:
        raise ValueError('Unknown visible reference')
    resolved = []
    for loc in matches:
        message = cp['request']['messages'][loc['message_index']]
        value = message['content'] if ref == 'question' else loads(message['content'])
        pointer = loc['path']
        if pointer and not pointer.startswith('/'):
            raise ValueError('Invalid reference pointer')
        for token in pointer.split('/')[1:]:
            if re.search(r'~(?![01])', token):
                raise ValueError('Invalid reference escape')
            token = token.replace('~1', '/').replace('~0', '~')
            if isinstance(value, list):
                if not re.fullmatch(r'0|[1-9][0-9]*', token):
                    raise ValueError('Invalid array reference')
                value = value[int(token)]
            else:
                value = value[token]
        resolved.append(value)
    if any(value != resolved[0] for value in resolved):
        # The same immutable window can carry different search scores. Compare
        # source identity and text, not retrieval-only ranking metadata.
        def identity(v):
            return {k: v.get(k) for k in ('docid', 'url', 'text', 'title', 'offset',
                    'end_char', 'document_sha256')} if isinstance(v, dict) else v
        if any(identity(v) != identity(resolved[0]) for v in resolved):
            raise ValueError('Conflicting content behind a visible reference')
    return deepcopy(resolved[0])


def validate_basis(cp: dict, basis: object, kind: str) -> list[dict]:
    if not isinstance(basis, list) or not basis or len(basis) > 12:
        raise ValueError('Each curated entry requires 1-12 visible bases')
    for item in basis:
        if not isinstance(item, dict):
            raise ValueError('Basis must be an object')
        quote = text(item.get('quote'), 'quote')
        if set(item) == {'ref', 'quote'}:
            ref = text(item['ref'], 'ref', 300)
            value = resolve(cp, ref)
            content = value if isinstance(value, str) else value['text']
            if kind == 'given_constraint' and ref != 'question':
                raise ValueError('A given constraint requires question provenance')
            if kind == 'observed_finding' and ref == 'question':
                raise ValueError('A question clue is not an observed candidate fact')
        elif set(item) == {'message_index', 'quote'}:
            index = item['message_index']
            messages = cp['request']['messages']
            if type(index) is not int or not 0 <= index < len(messages):
                raise ValueError('Basis index outside prefix')
            message = messages[index]
            if kind not in {'hypothesis', 'unresolved', 'current_task'} or message['role'] != 'assistant':
                raise ValueError('Assistant prose cannot ground an observed finding')
            content = message.get('content') or ''
        else:
            raise ValueError('Basis requires ref+quote or assistant message_index+quote')
        if quote not in content:
            raise ValueError('Basis quote is not a contiguous substring of its visible source')
    return deepcopy(basis)


def validate_notebook(cp: dict, fixture: dict) -> dict:
    if not isinstance(fixture, dict) or set(fixture) != {'notebook', 'task'}:
        raise ValueError('Fixture has only notebook and task')
    notes = fixture['notebook']
    if not isinstance(notes, list) or len(notes) > 12:
        raise ValueError('Notebook must contain at most 12 entries')
    for entry in notes:
        if not isinstance(entry, dict) or set(entry) != {'kind', 'text', 'basis'} or entry.get('kind') not in NOTE_KINDS:
            raise ValueError('Invalid notebook entry schema')
        text(entry['text'], 'notebook text', 1600)
        validate_basis(cp, entry['basis'], entry['kind'])
    task = fixture['task']
    if task is not None:
        if not isinstance(task, dict) or set(task) != {'intent', 'question', 'decision_effect', 'basis'}:
            raise ValueError('Task must be null or one fixed investigation question')
        if task['intent'] not in {'discover', 'verify', 'clarify'}:
            raise ValueError('Unknown investigation intent')
        text(task['question'], 'task question', 1000)
        text(task['decision_effect'], 'decision effect', 1600)
        validate_basis(cp, task['basis'], 'current_task')
    return deepcopy(fixture)


def attempts(cp: dict) -> list[dict]:
    """Record all completed calls; neither completion nor novelty means success."""
    messages = cp['request']['messages']
    call_map = {call['id']: (index, call['function'])
                for index, message in enumerate(messages)
                for call in (message.get('tool_calls') or [])}
    rows = []
    for event in cp['source']['tool_events']:
        index = event['message_index']
        message = messages[index]
        call_index, function = call_map[message['tool_call_id']]
        refs = [r['ref'] for r in cp['references'] if r['message_index'] == index]
        arguments = loads(function['arguments'])
        if not isinstance(arguments, dict):
            raise ValueError('Captured tool arguments must decode to an object')
        rows.append({'attempt_id': f'a{len(rows)}', 'call_message_index': call_index,
                     'result_message_index': index, 'tool_call_id': message['tool_call_id'],
                     'tool': function['name'], 'arguments': arguments, 'source_refs': refs,
                     'delivery': 'recorded_tool_response', 'information_gain': 'not_evaluated'})
    return rows


def attempt_index(cp: dict, rows: list[dict]) -> dict:
    by_request, by_observation = {}, {}
    for row in rows:
        request_key = digest({'tool': row['tool'], 'arguments': row['arguments']})
        # No score or event-specific ref in content identity. Different windows
        # in the same document remain distinct. Errors/empty results are retained.
        sources = [resolve(cp, ref) for ref in row['source_refs']]
        identity = [{k: v.get(k) for k in ('docid', 'url', 'text', 'title', 'offset',
                     'end_char', 'document_sha256')} for v in sources]
        if not sources:
            identity = loads(cp['request']['messages'][row['result_message_index']]['content'])
        observation_key = digest(identity)
        by_request.setdefault(request_key, []).append(row['attempt_id'])
        by_observation.setdefault(observation_key, []).append(row['attempt_id'])
    return {'same_exact_arguments': list(by_request.values()),
            'same_ordered_visible_source_content': list(by_observation.values()),
            'meaning': 'Mechanical equality only; not task failure, novelty, or independent support.'}


def build_packet(cp: dict, fixture: dict) -> dict:
    cp = validate_checkpoint(cp)
    if sum(m['role'] == 'user' for m in cp['request']['messages']) != 1:
        raise ValueError('This pilot supports single-question prefixes, not follow-up conversations')
    fixture = validate_notebook(cp, fixture)
    for ref in cp['references']:
        resolve(cp, ref['ref'])
    items = []
    for index, message in enumerate(cp['request']['messages']):
        items.append({'id': f'm{index}', 'kind': ROLE_KINDS[message['role']],
                      'message_index': index, 'value': deepcopy(message)})
    for index, entry in enumerate(fixture['notebook']):
        items.append({'id': f'n{index}', 'kind': entry['kind'], 'value': deepcopy(entry)})
    items.append({'id': 'task', 'kind': 'current_task', 'value': deepcopy(fixture['task'])})
    rows = attempts(cp)
    items.extend({'id': row['attempt_id'], 'kind': 'attempts', 'value': row} for row in rows)
    return sealed({'schema_version': 'investigation_packet_v1',
                   'checkpoint': cp, 'fixture': fixture, 'items': items,
                   'references': deepcopy(cp['references']), 'attempt_index': attempt_index(cp, rows)},
                  'packet_sha256')


def validate_packet(packet: dict) -> dict:
    verify_seal(packet, 'packet_sha256')
    expected = build_packet(packet['checkpoint'], packet['fixture'])
    if packet != expected:
        raise ValueError('Packet differs from deterministic compilation')
    return deepcopy(packet)


def render(packet: dict, mode: str) -> dict:
    """No gold, case IDs, annotation metadata, or hidden source text is rendered."""
    if mode not in {'flat', 'typed', 'linked'}:
        raise ValueError('Unknown view')
    items = deepcopy(packet['items'])
    view = {'reference_index': deepcopy(packet['references'])}
    if mode == 'flat':
        view['items'] = items
    else:
        view['groups'] = {kind: [item for item in items if item['kind'] == kind]
                          for kind in GROUP_ORDER}
        if mode == 'linked':
            view['attempt_index'] = deepcopy(packet['attempt_index'])
    if unpack(view) != sorted(items, key=lambda row: row['id']):
        raise ValueError('View changed the canonical item inventory')
    return view


def unpack(view: dict) -> list[dict]:
    rows = view.get('items')
    if rows is None:
        rows = [row for group in view['groups'].values() for row in group]
    if len({row['id'] for row in rows}) != len(rows):
        raise ValueError('Duplicate view item')
    return sorted(deepcopy(rows), key=lambda row: row['id'])


def proposed_repeats(packet: dict, calls: object) -> list[dict]:
    """Offline lexical/equality diagnostic; never blocks a model action."""
    history = [item['value'] for item in packet['items'] if item['kind'] == 'attempts']
    out = []
    for index, call in enumerate(calls if isinstance(calls, list) else []):
        try:
            function = call['function']
            arguments = loads(function['arguments'])
            matched = [row['attempt_id'] for row in history
                       if row['tool'] == function['name'] and row['arguments'] == arguments]
        except (KeyError, TypeError, ValueError):
            matched = None
        out.append({'call_index': index, 'exact_previous_attempts': matched,
                    'semantic_quality': 'not_evaluated'})
    return out
