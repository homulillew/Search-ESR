"""Initialization handoff: original question, attempted intent, and unmodified observations."""
from .initializer import generate
from .source_units import check_question


def initialize(client, config, question, tools, *, attempt_id, arm='minimal', emit=None):
    check_question(question)
    emit = emit or (lambda *args, **kwargs: None)
    handoff = dict(schema_version='single_entry_handoff_v1', attempt_id=attempt_id, arm=arm,
                   question=question, status='pending', plan=None, search_attempts=[],
                   observation_store='observations.sqlite')
    try:
        plan = generate(client, config, question, arm)
    except Exception as exc:
        handoff.update(status='generation_error', error_type=type(exc).__name__,
                       error_detail=str(exc).replace(config.api_key, '[redacted]') if getattr(config, 'api_key', '') else str(exc))
        emit('generation_error', error_type=type(exc).__name__)
        return handoff
    handoff['plan'] = plan
    if plan['question_sha256'] != question['sha256']:
        raise ValueError('Plan and question versions differ')
    emit('plan_finalized', plan=plan)
    if plan['status'] != 'valid':
        handoff['status'] = plan['status']
        return handoff
    intent = plan['intents'][0]
    attempt = dict(attempt_id=attempt_id + '/search_1', intent=intent,
                   question_sha256=question['sha256'], basis_origin=plan['basis_origin'],
                   arguments=dict(query=intent['query'], k=6), status='pending', result=[], window_refs=[])
    handoff['search_attempts'].append(attempt)
    emit('search_start', attempt_id=attempt['attempt_id'], arguments=attempt['arguments'])
    try:
        result = tools.execute('search', attempt['arguments'])
        attempt.update(status='complete', result=result, window_refs=[w['window_ref'] for w in result])
        handoff['status'] = 'complete'  # Execution completed; does not assert relevance.
        emit('search_result', attempt_id=attempt['attempt_id'], arguments=attempt['arguments'], result=result)
    except Exception as exc:
        detail = str(exc).replace(config.api_key, '[redacted]') if getattr(config, 'api_key', '') else str(exc)
        attempt.update(status='search_error', error_type=type(exc).__name__, error_detail=detail)
        handoff['status'] = 'search_error'
        emit('search_error', attempt_id=attempt['attempt_id'], error_type=type(exc).__name__)
    return handoff
