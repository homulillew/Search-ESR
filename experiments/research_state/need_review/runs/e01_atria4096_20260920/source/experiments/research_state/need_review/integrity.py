"""Offline integrity checks, addressable memo data, and durable E0 records.

These checks establish data/transport contracts, never evidence entailment.
Hashes detect drift; they are not signatures or protection against an attacker
who can replace both a record and its approved hash.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import os
import re
from pathlib import Path
import tempfile
from urllib.parse import urlsplit

from .checkpoint import canonical_json, digest, validate_checkpoint

HARNESS_REVISION = 'e0_audit_v1'
MEMO_MODES = ('legacy_text', 'indexed_json_v1')
REVIEW_CONTRACTS = ('baseline', 'source_grounded_v1')

def review_prompt_key(arm, contract='baseline'):
    if contract not in REVIEW_CONTRACTS or arm not in ('B', 'C'):
        raise ValueError('Unknown review contract or arm')
    return ('generic_review' if arm == 'B' else
            'need_review_source_grounded' if contract == 'source_grounded_v1' else 'need_review')


def branch_settings(settings, sample):
    """Only a predeclared paired contract can override the global C prompt."""
    out = deepcopy(settings)
    if settings.get('comparison', 'abc') == 'source_contract_pair':
        contract = sample.get('review_contract')
        if sample.get('arm') != 'C' or contract not in REVIEW_CONTRACTS:
            raise ValueError('Invalid paired source-contract sample')
        out['review_contract'] = contract
    elif 'review_contract' in sample:
        raise ValueError('Undeclared per-sample prompt override')
    return out


def strict_json(text):
    def pairs(items):
        out = {}
        for key, value in items:
            if key in out:
                raise ValueError('Duplicate JSON key')
            out[key] = value
        return out
    def constant(_):
        raise ValueError('Non-finite JSON constant')
    value = json.loads(text, object_pairs_hook=pairs, parse_constant=constant)
    # Also rejects finite-looking numeric literals that overflow to infinity.
    canonical_json(value)
    return value


def atomic_json(path, value):
    """Atomic replacement plus fsync. Never leaves a partially replaced JSON."""
    path = Path(path)
    text = json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n'
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent,
                                         prefix=path.name + '.', delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(path)
        if hasattr(os, 'O_DIRECTORY'):
            fd = os.open(path.parent, os.O_DIRECTORY)
            try:
                os.fsync(fd)
            finally:
                os.close(fd)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def source_hashes(package):
    return {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(Path(package).glob('*.py'))}


def seal_plan(plan):
    out = deepcopy(plan)
    out.pop('plan_sha256', None)
    out['plan_sha256'] = digest(out)
    return out


def verify_plan(approved, actual):
    if not isinstance(approved, dict) or seal_plan(approved) != approved:
        raise ValueError('Approved plan integrity mismatch')
    if approved != actual:
        raise ValueError('Frozen plan differs from current inputs, settings, prompts or implementation')


def normalize_base_url(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError('Expected API base URL is required')
    value = value.strip().rstrip('/')
    try:
        parts = urlsplit(value)
        parts.port  # Validate malformed/out-of-range ports without echoing the URL.
    except ValueError:
        raise ValueError('Invalid API base URL') from None
    if (parts.scheme not in ('http', 'https') or not parts.hostname or not parts.netloc or parts.username
            or parts.password or parts.query or parts.fragment
            or parts.path.endswith('/chat/completions')):
        raise ValueError('Expected a credential-free HTTP(S) API base URL')
    return value


def validate_actor_shape(request):
    """Reject unsupported captured experiments instead of charging for them."""
    if type(request.get('n', 1)) is not int or request.get('n', 1) != 1:
        raise ValueError('E0 requires exactly one Actor choice; do not silently change n')
    if request.get('stream') is not False:
        raise ValueError('E0 requires a nonstreaming captured Actor request')
    tools = request.get('tools')
    if not isinstance(tools, list) or not tools:
        raise ValueError('E0 requires captured function tool definitions')
    names = set()
    for tool in tools:
        function = tool.get('function') if isinstance(tool, dict) else None
        if (not isinstance(function, dict) or tool.get('type') != 'function'
                or not isinstance(function.get('name'), str) or not function['name']):
            raise ValueError('Malformed captured function tool')
        if function['name'] in names:
            raise ValueError('Duplicate captured tool name')
        names.add(function['name'])
        schema = function.get('parameters', {})
        if (not isinstance(schema, dict) or not isinstance(schema.get('properties', {}), dict)
                or not isinstance(schema.get('required', []), list)):
            raise ValueError('Malformed captured tool parameter schema')


def resolve_reference(checkpoint, reference):
    """Resolve ONLY an index into already visible messages, never a document DB."""
    messages = checkpoint['request']['messages']
    index, pointer = reference['message_index'], reference['path']
    if type(index) is not int or not 0 <= index < len(messages) or not isinstance(pointer, str):
        raise ValueError('Invalid visible reference locator')
    message = messages[index]
    if reference['ref'] == 'question':
        first_user = next(i for i, row in enumerate(messages) if row.get('role') == 'user')
        if index != first_user or pointer != '':
            raise ValueError('Reserved question reference was rebound')
        return message['content']
    if message.get('role') != 'tool':
        raise ValueError('Source references must point to actual tool observations')
    value = strict_json(message['content'])
    if pointer and not pointer.startswith('/'):
        raise ValueError('Invalid JSON pointer')
    for token in pointer.split('/')[1:]:
        # RFC 6901 escaping; malformed escape sequences are not accepted.
        if re.search(r'~(?![01])', token):
            raise ValueError('Invalid JSON pointer escape')
        token = token.replace('~1', '/').replace('~0', '~')
        if isinstance(value, list):
            if not token.isdigit() or str(int(token)) != token:
                raise ValueError('Invalid JSON pointer array index')
            try:
                value = value[int(token)]
            except IndexError as exc:
                raise ValueError('Reference index outside visible observation') from exc
        elif isinstance(value, dict) and token in value:
            value = value[token]
        else:
            raise ValueError('Reference path not present in visible observation')
    if not isinstance(value, dict) or not isinstance(value.get('text'), str):
        raise ValueError('Reference must resolve to an actual returned text object')
    return value


def visible_reference_index(checkpoint):
    checkpoint = validate_checkpoint(checkpoint)
    identities = {}
    for reference in checkpoint['references']:
        value = resolve_reference(checkpoint, reference)
        identity = value if isinstance(value, str) else {
            key: value.get(key) for key in (
                'docid', 'document_sha256', 'offset', 'end_char', 'text', 'title', 'title_span')}
        key = reference['ref']
        if key in identities and identities[key] != identity:
            raise ValueError('One visible reference identifies conflicting source content')
        identities[key] = identity
    return deepcopy(checkpoint['references'])


def read_events(path):
    """Recover complete prefix records; do not silently skip corruption mid-log."""
    try:
        raw_lines = Path(path).read_bytes().splitlines()
    except FileNotFoundError:
        return [], []
    except OSError:
        return [], ['events_unreadable']
    events, errors = [], []
    for number, raw in enumerate(raw_lines, 1):
        if not raw.strip():
            continue
        try:
            event = strict_json(raw.decode('utf-8'))
        except (ValueError, UnicodeError):
            errors.append(f'invalid_event_line_{number}')
            break
        if not isinstance(event, dict):
            errors.append(f'non_object_event_line_{number}')
            break
        if not isinstance(event.get('kind'), str) or ('stage' in event and not isinstance(event['stage'], str)):
            errors.append(f'invalid_event_envelope_line_{number}')
            break
        if 'seq' in event and (type(event['seq']) is not int or event['seq'] != len(events) + 1):
            errors.append(f'noncontiguous_event_sequence_line_{number}')
            break
        events.append(event)
    return events, errors


def branch_exit_code(summary):
    """Zero means a mechanically clean batch, NOT semantically successful work."""
    if summary.get('record_errors'):
        return 2
    if summary.get('branch_statuses') != {'completed': summary['scheduled_branches']}:
        return 2
    if any(summary.get('review_statuses', {}).get(key, 0) for key in ('node_invalid', 'api_error')):
        return 2
    if summary.get('actor_protocol_statuses', {}).get('incompatible', 0):
        return 2
    return 0
