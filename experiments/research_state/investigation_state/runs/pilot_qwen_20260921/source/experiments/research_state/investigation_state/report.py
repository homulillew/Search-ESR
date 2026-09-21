"""Read-only run audit and fresh human-review exports; never invokes a model."""
from __future__ import annotations
from collections import Counter
from copy import deepcopy
import hashlib
from pathlib import Path
from ..need_review.checkpoint import digest, canonical_json
from ..need_review.accounting import inspect_usage
from .packet import proposed_repeats
from .storage import read, write, read_journal, safe_path, verify_seal

LABELS = {
    'complete_response_acceptable': 'Whole delivered content and every proposed call; not eventual answer accuracy.',
    'source_attribution_correct': 'Were original clues, source text, and earlier assistant hypotheses distinguished?',
    'relation_scope_preserved': 'Were subject, time, polarity, and upstream-binding scope preserved?',
    'task_used_in_decision': 'Was the specific uncertainty/decision purpose used, not merely the same topic?',
    'tool_direction_reasonable': 'Is the proposed action reasonable? Do not infer retrieval outcome before tools execute.',
    'repetition_has_new_purpose': 'For a repeated/nearby route, is a substantive new purpose present? Equality is not a veto.',
    'body_assertions_supported': 'Evaluate visible content, not private reasoning. Tentative exploration is not a confirmed fact.',
    'final_answer_supported': 'Only for a final answer: do actual visible sources support its necessary claims?',
    'new_error_introduced': 'A new unsupported binding or relaxed original condition; distinguish inherited errors.',
    'regression': 'Fill only after separate judgments; compare matched runs, allowing unknown for mixed changes.'}


def _object_or_none(path):
    try:
        value = read(path)
    except FileNotFoundError:
        return None, []
    except (ValueError, OSError, UnicodeError):
        return None, ['invalid_result_file']
    return (value, []) if isinstance(value, dict) else (None, ['result_is_not_object'])


def audit(directory: Path) -> tuple[dict, list[dict]]:
    from .run import load_bundle, validate_plan, request_for, compact_classification
    directory = Path(directory)
    bundle = load_bundle(directory / 'bundle.json')
    plan = validate_plan(read(directory / 'plan.json'), bundle)
    execution = read(directory / 'execution.json')
    verify_seal(execution, 'execution_sha256')
    global_errors = []
    if execution.get('plan_sha256') != plan['plan_sha256'] or execution.get('runtime_versions') != plan['runtime_versions']:
        global_errors.append('execution_manifest_mismatch')
    for relative, expected_hash in plan['code_sha256'].items():
        path = safe_path(directory / 'source', relative)
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected_hash:
            global_errors.append('source_snapshot_mismatch:' + relative)
    rows, totals = [], Counter()
    statuses, by_view = Counter(), {}
    all_usage_complete = True
    for item in plan['schedule']:
        branch = safe_path(directory / 'branches', item['sample_id'])
        events, errors = read_journal(branch / 'events.jsonl')
        record, record_errors = _object_or_none(branch / 'result.json')
        errors.extend(record_errors)
        packet = bundle['packets'][item['case_id']]
        expected = request_for(packet, item['view'], plan['profile'], plan['prompt'])
        if digest(expected) != item['request_sha256']:
            errors.append('planned_request_hash_mismatch')
        requests = [e for e in events if e['kind'] == 'request']
        responses = [e for e in events if e['kind'] == 'response']
        api_errors = [e for e in events if e['kind'] == 'api_error']
        harness_errors = [e for e in events if e['kind'] == 'harness_error']
        if len(requests) > 1 or len(responses) > 1 or len(api_errors) > 1:
            errors.append('multiple_calls_in_single_actor_decision')
        if responses and api_errors:
            errors.append('response_and_api_error_for_same_call')
        if (responses or api_errors) and (not requests or (responses or api_errors)[0]['seq'] <= requests[0]['seq']):
            errors.append('response_precedes_request')
        if requests and requests[0].get('request') != expected:
            errors.append('actual_request_differs_from_frozen_view')
        response = responses[0].get('response') if len(responses) == 1 else None
        status = record.get('status') if record else ('uncompleted' if events else 'not_run')
        if status not in {'completed', 'api_error', 'harness_error', 'interrupted', 'uncompleted', 'not_run'}:
            status = 'invalid_record'
            errors.append('invalid_branch_status')
        if record:
            if any(record.get(k) != v for k, v in item.items()):
                errors.append('result_metadata_mismatch')
            if record.get('request') != expected:
                errors.append('stored_request_differs_from_plan')
            if record.get('response') is not None and record['response'] != response:
                errors.append('result_response_differs_from_journal')
            if status == 'completed' and [e['kind'] for e in events] != ['request', 'response']:
                errors.append('completed_event_sequence_mismatch')
            if status == 'completed' and (len(requests) != 1 or response is None):
                errors.append('completed_without_complete_journal')
            if status == 'api_error' and len(api_errors) != 1:
                errors.append('api_error_missing_from_journal')
        classification = compact_classification(response, expected) if response is not None else None
        if classification and record and record.get('classification') not in (None, classification):
            errors.append('classification_mismatch')
        reported = inspect_usage(response.get('usage') if isinstance(response, dict) else None)
        attempts_count = len(requests)
        unknown_usage = max(0, attempts_count - len(responses)) + (1 if response is not None and not reported['complete'] else 0)
        if unknown_usage or errors:
            all_usage_complete = False
        totals.update(reported['known'])
        totals['requests'] += attempts_count
        totals['responses'] += len(responses)
        totals['unknown_usage_calls'] += unknown_usage
        totals['responses_inconsistent_usage'] += int(response is not None and reported['inconsistent'])
        detail = response.get('usage', {}).get('completion_tokens_details') if isinstance(response, dict) and isinstance(response.get('usage'), dict) else None
        reasoning = detail.get('reasoning_tokens') if isinstance(detail, dict) else None
        if type(reasoning) is int and reasoning >= 0:
            totals['reported_reasoning_tokens'] += reasoning
        statuses[status] += 1
        condition = by_view.setdefault(item['view'], {'planned': 0, 'protocol_valid': 0, 'unknown_usage_calls': 0,
                                                     'reported_tokens': Counter(), 'statuses': Counter()})
        condition['planned'] += 1
        condition['statuses'][status] += 1
        condition['unknown_usage_calls'] += unknown_usage
        condition['reported_tokens'].update(reported['known'])
        valid = bool(classification and classification['protocol_compatible'])
        condition['protocol_valid'] += int(valid)
        elapsed = sum(e.get('elapsed_seconds', 0) for e in events
                      if type(e.get('elapsed_seconds')) in (int, float) and e['elapsed_seconds'] >= 0)
        rows.append({**item, 'status': status, 'errors': errors, 'classification': classification,
                     'response': response, 'response_recovered_from_journal': bool(response is not None and (not record or record.get('response') is None)),
                     'semantic_eligible': valid and not errors and status == 'completed',
                     'unknown_usage_calls': unknown_usage, 'reported_usage': reported,
                     'elapsed_seconds': elapsed,
                     'exact_repeat_diagnostic': proposed_repeats(packet, classification['tool_calls'] if classification else None)})
    summary = {'schema_version': 'investigation_audit_v1', 'purpose': plan['purpose'],
               'mode': execution.get('mode'), 'plan_sha256': plan['plan_sha256'],
               'scheduled_branches': len(plan['schedule']), 'statuses': dict(statuses),
               'logical_requests_attempted': totals['requests'], 'responses_received': totals['responses'],
               'unknown_usage_calls': totals['unknown_usage_calls'],
               'responses_inconsistent_usage': totals['responses_inconsistent_usage'],
               'reported_token_lower_bounds': {k: totals[k] for k in ('prompt_tokens', 'completion_tokens', 'total_tokens', 'reported_reasoning_tokens')},
               'cost_accounting_complete': all_usage_complete,
               'global_errors': global_errors,
               'branches_with_audit_errors': sum(bool(r['errors']) for r in rows),
               'by_view': by_view, 'tool_executions': 0, 'reviewer_calls': 0,
               'semantic_evaluation': 'not_evaluated'}
    summary['mechanically_clean'] = (not global_errors and not summary['branches_with_audit_errors']
        and len(rows) == totals['requests'] == totals['responses'] and all(r['semantic_eligible'] for r in rows))
    if global_errors:
        summary['cost_accounting_complete'] = False
    return summary, rows


def pilot_acceptance(directory: Path) -> dict:
    summary, _ = audit(directory)
    plan = read(Path(directory) / 'plan.json')
    if summary['purpose'] != 'pilot' or summary['mode'] != 'live' or not summary['mechanically_clean'] or not summary['cost_accounting_complete']:
        raise ValueError('Pilot must be a live, complete, cost-accounted delivery check, not a semantic success filter')
    return {'pilot_plan_sha256': plan['plan_sha256'], 'pilot_summary_sha256': digest(summary),
            'bundle_sha256': plan['bundle_sha256'], 'comparison': plan['comparison'],
            'profile_sha256': digest(plan['profile']), 'code_sha256': plan['code_sha256'],
            'runtime_versions': plan['runtime_versions'],
            'prompt_sha256': digest(plan['prompt']), 'mechanically_clean': True,
            'semantic_quality_not_used': True}


def export(directory: Path, output: Path) -> dict:
    summary, rows = audit(directory)
    plan = read(Path(directory) / 'plan.json')
    bundle = read(Path(directory) / 'bundle.json')
    ordered = sorted(rows, key=lambda r: digest([plan['schedule_seed'], r['sample_id']]))
    output.mkdir(parents=True, exist_ok=False)
    cards, keys = [], []
    for index, row in enumerate(ordered):
        packet = bundle['packets'][row['case_id']]
        response = row['response']
        delivered = None
        if isinstance(response, dict):
            delivered = []
            for choice in response.get('choices', []) if isinstance(response.get('choices'), list) else []:
                if not isinstance(choice, dict):
                    continue
                message = choice.get('message')
                delivered.append({'finish_reason': choice.get('finish_reason'),
                    'message': {k: deepcopy(message[k]) for k in ('role', 'content', 'tool_calls', 'refusal') if k in message}
                    if isinstance(message, dict) else None})
        card_id = f'card_{index + 1:04d}'
        cards.append({'card_id': card_id, 'canonical_items': packet['items'],
                      'reference_index': packet['references'], 'delivered_response': delivered,
                      'execution': {k: row[k] for k in ('status', 'errors', 'semantic_eligible', 'response_recovered_from_journal')},
                      'permitted_next_actions_before_output': None,
                      'labels': {key: None for key in LABELS},
                      'label_evidence': {key: {'refs': [], 'notes': ''} for key in LABELS}})
        keys.append({'card_id': card_id, **{k: row[k] for k in ('sample_id', 'case_id', 'view', 'repeat', 'elapsed_seconds',
                     'reported_usage', 'unknown_usage_calls', 'exact_repeat_diagnostic')}})
    for filename, values in (('cards.jsonl', cards), ('prefix_cards.jsonl', [
            {k: row[k] for k in ('card_id', 'canonical_items', 'reference_index', 'permitted_next_actions_before_output')} for row in cards])):
        with (output / filename).open('x', encoding='utf-8') as stream:
            for value in values:
                stream.write(canonical_json(value) + '\n')
    write(output / 'private_key.json', keys)
    write(output / 'summary.json', summary)
    write(output / 'rubric.json', {'allowed': ['yes', 'no', 'unknown', 'not_applicable'], 'labels': LABELS,
        'limits': ['Metadata masking is not blinding; the fixture authors know earlier cases.',
                   'No tool has executed; direction judgments are not retrieval success.',
                   'Keep all scheduled rows; protocol failures have no attributable semantic success.',
                   'Curated notes/needs are fixed diagnostic inputs, not an automatic state updater.',
                   'Partial query constraints can be deliberate exploration; not all similar queries are bad.']})
    return summary
