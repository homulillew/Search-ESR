"""Inspect reported token counts without turning missing costs into zero."""
from typing import Any

TOKEN_KEYS = ('prompt_tokens', 'completion_tokens', 'total_tokens')


def inspect_usage(value: Any) -> dict:
    """Return known nonnegative counts, missing fields and arithmetic validity.

    Known partial counts may be summed as *reported* counts, but are not a full
    cost estimate. Booleans and negative counts are invalid. Never impute a
    missing total or unknown API-error cost. Cached tokens remain a separate
    provider detail; these counters are not a bill in currency.
    """
    usage = value if isinstance(value, dict) else {}
    known = {key: usage[key] for key in TOKEN_KEYS
             if type(usage.get(key)) is int and usage[key] >= 0}
    missing = [key for key in TOKEN_KEYS if key not in known]
    inconsistent = not missing and (
        known['prompt_tokens'] + known['completion_tokens'] != known['total_tokens'])
    return {'known': known, 'missing': missing, 'inconsistent': bool(inconsistent),
            'complete': not missing and not inconsistent}
