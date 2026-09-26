"""Proposed compatibility fix for a FUTURE frozen runner; not used in R1."""
import copy

def append_attempt(context, attempt):
    """Keep list histories and opaque historical provenance without losing either."""
    if isinstance(context, list):
        return copy.deepcopy(context) + [copy.deepcopy(attempt)]
    if isinstance(context, dict):
        updated = copy.deepcopy(context)
        log = updated.setdefault('current_run_attempts', [])
        if not isinstance(log, list):
            raise TypeError('current_run_attempts must be a list')
        log.append(copy.deepcopy(attempt))
        return updated
    raise TypeError('Expected a list history or dictionary historical context')
