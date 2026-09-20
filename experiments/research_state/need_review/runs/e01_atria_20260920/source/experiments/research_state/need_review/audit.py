"""Compare executed E0 requests with the approved visible prefix and prompts.

An integrity error is a harness/data error, not a semantic model failure.
This module does not load credentials, source corpora or reference answers.
"""
from __future__ import annotations
from copy import deepcopy

from .integrity import review_prompt_key, branch_settings
from .node import build_actor_request, build_review_request, classify_actor_response, validate_review


def recover_record(result, events):
    """Recover paid responses from the journal without inventing node validation."""
    result = deepcopy(result)
    recovered = []
    for stage, target in (('review', 'review'), ('actor', 'actor')):
        request_events = [e for e in events if e.get('kind') == 'request' and e.get('stage') == stage]
        response_events = [e for e in events if e.get('kind') == 'response' and e.get('stage') == stage]
        if len(response_events) != 1:
            continue
        value = result.get(target)
        if not isinstance(value, dict):
            value = {'status': 'unvalidated_partial'}
            result[target] = value
        if value.get('response') is None:
            value['response'] = deepcopy(response_events[0].get('response'))
            recovered.append(stage)
        if value.get('request') is None and len(request_events) == 1:
            value['request'] = deepcopy(request_events[0].get('request'))
        raw = value.get('response')
        if isinstance(raw, dict):
            value.setdefault('usage', deepcopy(raw.get('usage')))
        if stage == 'review' and 'valid' not in value:
            value['status'] = 'unvalidated_partial'
    return result, recovered


def verify_branch_requests(checkpoint, result, sample, settings, prompts, events):
    """Verify actual request and response linkage, not just branch labels."""
    settings = branch_settings(settings, sample)
    errors = []
    if result.get('review_contract') != sample.get('review_contract'):
        errors.append('branch_review_contract_mismatch')
    if result.get('request_sha256') != checkpoint['request_sha256']:
        errors.append('branch_checkpoint_request_hash_mismatch')
    records = {}
    for stage in ('review', 'actor'):
        requests = [e.get('request') for e in events
                    if e.get('kind') == 'request' and e.get('stage') == stage]
        responses = [e.get('response') for e in events
                     if e.get('kind') == 'response' and e.get('stage') == stage]
        if len(requests) > 1 or len(responses) > 1:
            errors.append(f'{stage}_multiple_logical_calls_in_single_decision')
        record = result.get(stage)
        record = record if isinstance(record, dict) else {}
        if record.get('request') is not None and requests != [record['request']]:
            errors.append(f'{stage}_request_journal_mismatch')
        if record.get('response') is not None and responses != [record['response']]:
            errors.append(f'{stage}_response_journal_mismatch')
        records[stage] = {
            'request': requests[0] if len(requests) == 1 else None,
            'response': responses[0] if len(responses) == 1 else None,
            'stored': record,
        }
    if any(e.get('kind') in {'tool_start', 'tool_result'} for e in events):
        errors.append('unexpected_tool_execution_in_e0')
    arm = sample['arm']
    memo_text = None
    review = records['review']
    if arm == 'A':
        if review['request'] is not None or review['response'] is not None:
            errors.append('baseline_contains_reviewer_call')
    else:
        if review['request'] is not None:
            expected = build_review_request(
                checkpoint, arm, prompts[review_prompt_key(arm, settings.get('review_contract', 'baseline'))],
                max_tokens=settings['review_max_tokens'], model=settings.get('model_override'))
            if review['request'] != expected:
                errors.append('review_request_differs_from_frozen_prefix_or_contract')
        if review['response'] is not None:
            valid = validate_review(review['response'], arm, {r['ref'] for r in checkpoint['references']})
            if valid['valid']:
                memo_text = valid['raw_text']
            if 'valid' in review['stored'] and review['stored']['valid'] != valid['valid']:
                errors.append('review_validation_record_mismatch')
    actor = records['actor']
    if actor['request'] is not None:
        mode = settings.get('memo_mode', 'legacy_text')
        template = prompts['memo_indexed' if mode == 'indexed_json_v1' else 'memo']
        expected = build_actor_request(checkpoint, memo_text, template,
                                       model=settings.get('model_override'), memo_mode=mode)
        if actor['request'] != expected:
            errors.append('actor_request_differs_from_frozen_prefix_or_handoff')
        if result.get('memo_injected') is not (memo_text is not None):
            errors.append('memo_injected_record_mismatch')
        if actor['response'] is not None:
            actual = classify_actor_response(actor['response'], actor['request'])
            stored = actor['stored'].get('classification')
            if stored is not None and stored != actual:
                errors.append('actor_classification_record_mismatch')
    if result.get('status') == 'completed' and (actor['request'] is None or actor['response'] is None):
        errors.append('completed_branch_missing_actor_journal')
    return errors
