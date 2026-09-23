"""Strict, atomic validation of provider-returned tool batches.

Raw provider responses are recorded by the caller.  This module never repairs
tool names or arguments and never changes the provider's finish reason.
"""

import json

from jsonschema import Draft7Validator


def validate_batch(choice, tool_schema, *, allow_stop_with_calls):
    """Return (parsed calls, error code). No tool may run unless error is None."""
    finish = choice.get('finish_reason')
    message = choice.get('message') or {}
    calls = message.get('tool_calls') or []
    if not calls:
        return [], None if finish == 'stop' else 'finish_without_calls'
    if finish not in ({'tool_calls', 'stop'} if allow_stop_with_calls else {'tool_calls'}):
        return [], 'finish_with_calls'
    if not 1 <= len(calls) <= 8:
        return [], 'tool_batch_size'
    declared = {item['function']['name']: item['function']['parameters'] for item in tool_schema}
    seen = set()
    parsed = []
    for call in calls:
        call_id = call.get('id')
        if not isinstance(call_id, str) or not call_id or call_id in seen:
            return [], 'tool_call_id'
        seen.add(call_id)
        if call.get('type') != 'function' or not isinstance(call.get('function'), dict):
            return [], 'tool_call_type'
        function = call['function']
        name = function.get('name')
        if name not in declared:
            return [], 'undeclared_tool'
        try:
            args = json.loads(function.get('arguments'))
        except (ValueError, TypeError):
            return [], 'malformed_json'
        if not isinstance(args, dict):
            return [], 'arguments_not_object'
        if not Draft7Validator(declared[name]).is_valid(args):
            return [], 'schema_invalid'
        parsed.append({'id': call_id, 'name': name, 'arguments': args})
    return parsed, None


def validate_then_execute(choice, tool_schema, execute, *, allow_stop_with_calls):
    """Used in synthetic tests; an invalid later call leaves execution empty."""
    parsed, error = validate_batch(choice, tool_schema,
                                   allow_stop_with_calls=allow_stop_with_calls)
    if error:
        return {'validation': error, 'executed': []}
    results = [execute(call['name'], call['arguments']) for call in parsed]
    return {'validation': 'valid', 'executed': results}
