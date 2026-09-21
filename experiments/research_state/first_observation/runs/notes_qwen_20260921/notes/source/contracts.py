"""Contracts for raw-question first search and a minimal, fallible source note.

No SDK, environment access, retrieval, semantic judge, or JSON repair lives here.
Quote membership proves visibility, not entailment. A proposed tool is not an
executed tool. We deliberately support only the frozen search/open interface.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import math
from urllib.parse import urlsplit

VERSION = 'first_observation_v1'


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':'), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode('utf-8')).hexdigest()


def _pairs(pairs):
    value = {}
    for key, child in pairs:
        if key in value:
            raise ValueError('Duplicate JSON key')
        value[key] = child
    return value


def _constant(value):
    raise ValueError('Non-finite JSON number')


def loads(text):
    return json.loads(text, object_pairs_hook=_pairs, parse_constant=_constant)


def seal(value):
    value = deepcopy(value)
    if 'sha256' in value:
        raise ValueError('Already sealed')
    return {**value, 'sha256': digest(value)}


def verify(value):
    if not isinstance(value, dict) or value.get('sha256') != digest(
            {k: v for k, v in value.items() if k != 'sha256'}):
        raise ValueError('Artifact hash mismatch')
    return value


def nonempty(value, maximum=16000):
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise ValueError('Expected bounded nonempty text')
    return value


def positive(value, maximum):
    if type(value) is not int or not 1 <= value <= maximum:
        raise ValueError('Invalid positive integer')
    return value


def profile(value):
    required = {'model', 'base_url', 'timeout_seconds', 'request_options',
                'max_request_utf8_bytes', 'allow_tool_calls_with_stop'}
    if not isinstance(value, dict) or set(value) != required:
        raise ValueError('Use exactly the documented profile keys')
    nonempty(value['model'], 200)
    url = nonempty(value['base_url'], 2000)
    parts = urlsplit(url)
    parts.port
    if (parts.scheme not in ('https', 'http') or not parts.hostname
            or parts.username is not None or parts.password is not None
            or parts.query or parts.fragment or url != url.strip().rstrip('/')
            or parts.path.endswith(('/chat/completions', '/responses'))):
        raise ValueError('Use a normalized credential-free API base')
    seconds = value['timeout_seconds']
    if type(seconds) not in (int, float) or not math.isfinite(seconds) or seconds <= 0:
        raise ValueError('Invalid timeout')
    positive(value['max_request_utf8_bytes'], 10000000)
    if type(value['allow_tool_calls_with_stop']) is not bool:
        raise ValueError('Tool stop compatibility must be explicit')
    options = value['request_options']
    allowed = {'max_tokens', 'max_completion_tokens', 'temperature', 'top_p',
               'seed', 'reasoning_effort'}
    if not isinstance(options, dict) or set(options) - allowed:
        raise ValueError('Unsupported request option; no implicit provider extensions')
    caps = set(options) & {'max_tokens', 'max_completion_tokens'}
    if len(caps) != 1:
        raise ValueError('Specify one completion cap')
    positive(options[next(iter(caps))], 1000000)
    for key, lower, upper in [('temperature', 0, 2), ('top_p', 0, 1)]:
        if key in options and (type(options[key]) not in (int, float)
                or not math.isfinite(options[key]) or not lower <= options[key] <= upper):
            raise ValueError('Invalid sampling parameter')
    if 'seed' in options and type(options['seed']) is not int:
        raise ValueError('Sampling seed must be an integer')
    if 'reasoning_effort' in options:
        nonempty(options['reasoning_effort'], 40)
    canonical(value)
    return deepcopy(value)


def windows(observation):
    """Validate actual search window identities; do not reconstruct hidden pages."""
    if not isinstance(observation, list) or len(observation) > 10:
        raise ValueError('Search must return a list of at most ten windows')
    refs = {}
    for item in observation:
        if not isinstance(item, dict):
            raise ValueError('Invalid window')
        for key in ('window_ref', 'docid', 'document_sha256'):
            nonempty(item.get(key), 4000)
        if not isinstance(item.get('url'), str):
            raise ValueError('Source URL must remain text, possibly empty')
        body = item.get('text')
        start, end = item.get('offset'), item.get('end_char')
        if (not isinstance(body, str) or type(start) is not int or type(end) is not int
                or start < 0 or end < start or end - start != len(body)):
            raise ValueError('Window body and character range differ')
        if len(item['document_sha256']) != 64 or any(
                c not in '0123456789abcdef' for c in item['document_sha256']):
            raise ValueError('Invalid document version')
        for key in ('text_tokens', 'title_tokens'):
            if type(item.get(key)) is not int or item[key] < 0:
                raise ValueError('Window token counts missing')
        if item['text_tokens'] + item['title_tokens'] > 400:
            raise ValueError('Frozen search window exceeds 400-token budget')
        if item['window_ref'] in refs:
            raise ValueError('Duplicate window in a single search result')
        refs[item['window_ref']] = item
    return refs


def message(response):
    if not isinstance(response, dict) or not isinstance(response.get('choices'), list) or len(response['choices']) != 1:
        raise ValueError('Expected exactly one completion choice')
    choice = response['choices'][0]
    if not isinstance(choice, dict) or not isinstance(choice.get('message'), dict):
        raise ValueError('Missing response message')
    msg = choice['message']
    if msg.get('role') != 'assistant':
        raise ValueError('Unexpected message role')
    if any(msg.get(k) is not None and not isinstance(msg[k], str) for k in ('content', 'refusal')):
        raise ValueError('Only text/null content and refusal are supported')
    return msg, choice.get('finish_reason')


def note_result(response, observation):
    """Strict all-or-nothing validation. Empty notes are a valid semantic output."""
    refs = windows(observation)
    result = {'status': 'invalid', 'notes': None, 'errors': [], 'quote_locations': []}
    try:
        msg, finish = message(response)
        if finish != 'stop' or msg.get('tool_calls') or msg.get('function_call') or msg.get('refusal'):
            raise ValueError('Note must complete normally without tools or refusal')
        body = msg.get('content')
        if not isinstance(body, str) or not body.strip():
            raise ValueError('No delivered note text; reasoning is not a substitute')
        parsed = loads(body)
        if not isinstance(parsed, dict) or set(parsed) != {'notes'}:
            raise ValueError('Return only notes')
        notes = parsed['notes']
        if not isinstance(notes, list) or len(notes) > 3:
            raise ValueError('Return zero to three notes')
        seen = set()
        locations = []
        for note in notes:
            if not isinstance(note, dict) or set(note) != {'statement', 'source_ref', 'quote'}:
                raise ValueError('Invalid note keys')
            nonempty(note['statement'], 1200)
            quote = nonempty(note['quote'], 4000)
            ref = nonempty(note['source_ref'], 1000)
            if ref not in refs or quote not in refs[ref]['text']:
                raise ValueError('Quote is not in this visible window body')
            identity = digest(note)
            if identity in seen:
                raise ValueError('Duplicate note')
            seen.add(identity)
            text = refs[ref]['text']
            starts = [i for i in range(len(text)) if text.startswith(quote, i)]
            locations.append({'source_ref': ref, 'relative_starts': starts,
                              'absolute_starts': [refs[ref]['offset'] + i for i in starts]})
        result.update(status='ok' if notes else 'empty', notes=deepcopy(notes), quote_locations=locations)
    except (ValueError, TypeError, KeyError, RecursionError) as exc:
        result['errors'] = [str(exc)]
    return result


def actor_result(response, observation, allow_stop=False):
    """Validate the current search/open batch, never execute or judge its utility."""
    refs = windows(observation)
    result = {'status': 'invalid', 'kind': None, 'errors': [], 'calls': []}
    try:
        msg, finish = message(response)
        if msg.get('function_call') is not None:
            raise ValueError('Legacy function_call unsupported')
        calls = msg.get('tool_calls')
        if calls is not None and not isinstance(calls, list):
            raise ValueError('tool_calls must be a list')
        if calls:
            if finish != 'tool_calls' and not (allow_stop and finish == 'stop'):
                raise ValueError('Incomplete or unsupported tool finish reason')
            if len(calls) > 8 or msg.get('refusal'):
                raise ValueError('Invalid tool batch')
            ids = set()
            for call in calls:
                if not isinstance(call, dict) or call.get('type') != 'function':
                    raise ValueError('Malformed tool call')
                call_id = nonempty(call.get('id'), 1000)
                if call_id in ids:
                    raise ValueError('Duplicate tool call ID')
                ids.add(call_id)
                fn = call.get('function')
                if not isinstance(fn, dict) or not isinstance(fn.get('arguments'), str):
                    raise ValueError('Malformed tool function')
                args = loads(fn['arguments'])
                if not isinstance(args, dict):
                    raise ValueError('Arguments must be an object')
                if fn.get('name') == 'search':
                    if 'query' not in args or set(args) - {'query', 'k'}:
                        raise ValueError('Invalid search arguments')
                    nonempty(args['query'])
                    positive(args.get('k', 5), 10)
                elif fn.get('name') == 'open':
                    if set(args) != {'window_ref', 'direction'}:
                        raise ValueError('Invalid open arguments')
                    if args['window_ref'] not in refs or args['direction'] not in ('before', 'after', 'around'):
                        raise ValueError('Open requires a window already visible at this checkpoint')
                else:
                    raise ValueError('Unknown tool')
            result.update(status='ok', kind='tools', calls=deepcopy(calls))
        else:
            if finish != 'stop':
                raise ValueError('Incomplete final response')
            nonempty(msg.get('refusal') or msg.get('content'), 1000000)
            result.update(status='ok', kind='refusal' if msg.get('refusal') else 'final_text')
    except (ValueError, TypeError, KeyError, RecursionError) as exc:
        result['errors'] = [str(exc)]
    return result


def usage(response):
    """Return reported counts, missing fields and inconsistency; never impute costs."""
    raw = response.get('usage') if isinstance(response, dict) else None
    raw = raw if isinstance(raw, dict) else {}
    keys = ('prompt_tokens', 'completion_tokens', 'total_tokens')
    known = {k: raw[k] for k in keys if type(raw.get(k)) is int and raw[k] >= 0}
    missing = [k for k in keys if k not in known]
    inconsistent = not missing and known['prompt_tokens'] + known['completion_tokens'] != known['total_tokens']
    return {'known': known, 'missing': missing, 'inconsistent': inconsistent,
            'complete': not missing and not inconsistent}
