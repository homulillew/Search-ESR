"""Staged raw-question search -> source notes -> frozen-observation A/B decisions.

select/plan/audit are offline. collect executes only the FIRST real Search.
execute calls only a model, never any proposed tool. No rewrite, initial goal,
manual replacement note, automatic semantic judge, repair, or implicit retry.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import os
from pathlib import Path
import random
import shutil
import time

from . import artifacts as io
from .contracts import (VERSION, canonical, digest, seal, verify, nonempty, positive,
                        profile, windows, note_result, actor_result, usage)

PACKAGE = Path(__file__).parent


def _stage_package(plan):
    """The package whose source files a plan's fingerprint commits to."""
    if plan.get('stage') == 'evidence_pointer':
        from experiments.research_state.evidence_pointer import run as ep_run
        return Path(ep_run.__file__).parent
    return PACKAGE

ROOT = Path(__file__).resolve().parents[3]


def select(dataset, qids):
    """Project only IDs and original questions from BC+; never persist gold fields."""
    qids = [str(x) for x in qids]
    if not qids or len(set(qids)) != len(qids) or any(not x.isdecimal() for x in qids):
        raise ValueError('Choose distinct numeric qids before retrieval')
    found = {}
    before = io.file_hash(dataset)
    with Path(dataset).open(encoding='utf-8') as stream:
        for line in stream:
            row = io.loads(line)
            qid = str(row['query_id'])
            if qid in qids:
                if qid in found:
                    raise ValueError('Duplicate dataset ID')
                found[qid] = {'id': qid, 'question': nonempty(row['query'], 1000000)}
    if set(found) != set(qids) or io.file_hash(dataset) != before:
        raise ValueError('Missing selected question or dataset changed')
    return seal({'version': VERSION, 'kind': 'selection', 'dataset_sha256': before,
                 'cases': [found[x] for x in qids]})


def check_selection(value):
    verify(value)
    if set(value) != {'version', 'kind', 'dataset_sha256', 'cases', 'sha256'} or value['version'] != VERSION or value['kind'] != 'selection':
        raise ValueError('Invalid selection schema')
    rows = value['cases']
    if not isinstance(rows, list) or not rows:
        raise ValueError('Empty selection')
    seen = set()
    for row in rows:
        if not isinstance(row, dict) or set(row) != {'id', 'question'}:
            raise ValueError('Selection contains undeclared fields')
        if not isinstance(row['id'], str) or not row['id'].isdecimal() or row['id'] in seen:
            raise ValueError('Invalid case ID')
        seen.add(row['id'])
        nonempty(row['question'], 1000000)
    return value


def collect(selection, backend, output, *, k=5, max_query_tokens=1024):
    """One exact raw-question search per eligible selected question, no LLM call."""
    check_selection(selection)
    positive(k, 10)
    positive(max_query_tokens, 1024)  # Existing dense-retriever guard, includes prefix/special tokens.
    if backend.mode not in ('live', 'mock'):
        raise ValueError('Explicit retrieval mode required')
    tool_names = [x['function']['name'] for x in backend.tools]
    if tool_names != ['search', 'open']:
        raise ValueError('Capture the current search/open definitions, not legacy get_document')
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    base = {'version': VERSION, 'kind': 'collection', 'mode': backend.mode,
            'selection': deepcopy(selection), 'retrieval': backend.passport(),
            'k': k, 'max_query_tokens': max_query_tokens, 'tools': deepcopy(backend.tools),
            'fingerprint': io.fingerprint(), 'initial_model_calls': 0,
            'cases': [{**deepcopy(row), 'query': row['question'], 'status': 'not_run',
                       'query_tokens': None, 'observation': None} for row in selection['cases']]}
    io.exclusive(output / 'collect_plan.json', seal({k: v for k, v in base.items() if k != 'cases'}))
    io.write(output / 'collection.json', seal(base))
    try:
        for row in base['cases']:
            folder = output / row['id']
            folder.mkdir()
            journal = io.Journal(folder / 'events.jsonl')
            start = time.monotonic()
            row['status'] = 'interrupted'
            try:
                count = backend.count_query(row['question'])
                if type(count) is not int or count < 0:
                    raise ValueError('Invalid tokenizer count')
                row['query_tokens'] = count
                if count > max_query_tokens or len(row['question']) > 16000:
                    row['status'] = 'query_over_budget'
                    journal.emit('query_rejected', query=row['question'], tokens=count)
                    continue
                arguments = {'query': row['question'], 'k': k}
                journal.emit('search_request', arguments=arguments)
                try:
                    observation = backend.search(row['question'], k, folder)
                except Exception as exc:
                    row.update(status='search_error', error_type=type(exc).__name__)
                    journal.emit('search_error', error_type=type(exc).__name__)
                    continue
                row['observation'] = deepcopy(observation)
                journal.emit('search_response', observation=observation)
                windows(observation)
                if len(observation) > k:
                    raise ValueError('Search returned more windows than requested')
                row['status'] = 'ok'
            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception as exc:
                row.update(status='harness_error', error_type=type(exc).__name__)
                raise
            finally:
                row['elapsed_seconds'] = time.monotonic() - start
                io.write(output / 'collection.json', seal(base))
        backend.check_unchanged()
    except BaseException:
        base['capture_complete'] = False
        raise
    else:
        base['capture_complete'] = True
    finally:
        io.write(output / 'collection.json', seal(base))
    return seal(base)


def check_collection(value):
    verify(value)
    if value.get('version') != VERSION or value.get('kind') != 'collection' or value.get('capture_complete') is not True:
        raise ValueError('Collection is incomplete or incompatible')
    selected = check_selection(value['selection'])['cases']
    if len(selected) != len(value['cases']) or value.get('initial_model_calls') != 0:
        raise ValueError('Invalid capture denominator')
    for original, row in zip(selected, value['cases']):
        if any(row.get(k) != v for k, v in original.items()) or row.get('query') != original['question']:
            raise ValueError('Original question was rewritten, normalized, or replaced')
        if row['status'] == 'ok':
            windows(row['observation'])
        elif row['status'] not in ('query_over_budget', 'search_error'):
            raise ValueError('Interrupted/harness-error capture must be investigated')
    return value


def audit_capture(folder):
    folder = Path(folder)
    data = check_collection(io.read(folder / 'collection.json'))
    frozen = verify(io.read(folder / 'collect_plan.json'))
    if {k: data[k] for k in frozen if k != 'sha256'} != {k: v for k, v in frozen.items() if k != 'sha256'}:
        raise ValueError('Capture settings changed after the plan')
    for row in data['cases']:
        events, errors = io.journal_prefix(folder / row['id'] / 'events.jsonl')
        if errors:
            raise ValueError('Capture journal is damaged')
        kinds = [e['kind'] for e in events]
        expected = {'ok': ['search_request', 'search_response'],
                    'search_error': ['search_request', 'search_error'],
                    'query_over_budget': ['query_rejected']}[row['status']]
        if kinds != expected:
            raise ValueError('Capture events do not match status')
        if row['status'] != 'query_over_budget':
            if events[0]['arguments'] != {'query': row['question'], 'k': data['k']}:
                raise ValueError('Actual first query differs from original question')
        if row['status'] == 'ok' and events[1]['observation'] != row['observation']:
            raise ValueError('Captured observation differs from original tool return')
    return data


def _request(row, stage, arm, config, prompt, tools, note):
    payload = {'question': row['question'], 'first_query': row['query'],
               'observation': deepcopy(row['observation'])}
    request = {'model': config['model'], 'stream': False, 'n': 1,
               'messages': [{'role': 'system', 'content': prompt},
                            {'role': 'user', 'content': canonical(payload)}],
               **deepcopy(config['request_options'])}
    injected = stage == 'actors' and arm == 'B' and note is not None and note['status'] == 'ok'
    if injected:
        request['messages'].append({'role': 'user', 'content': canonical({
            'kind': 'fallible_model_generated_source_notes', 'notes': note['notes']})})
    if stage == 'actors':
        request.update(tools=deepcopy(tools), tool_choice='auto')
    if len(canonical(request).encode('utf-8')) > config['max_request_utf8_bytes']:
        raise ValueError('Full request exceeds byte guard; do not trim source content')
    return request, bool(injected)


def make_plan(collection, config, stage, *, prior=None, repeats=1, seed=20260921):
    check_collection(collection)
    config = profile(config)
    if stage not in ('notes', 'actors'):
        raise ValueError('Unknown stage')
    positive(repeats, 100)
    if stage == 'notes' and repeats != 1:
        raise ValueError('First experiment writes one note set per observation')
    if type(seed) is not int:
        raise ValueError('Schedule seed must be integer')
    if stage == 'actors':
        verify(prior)
        if prior.get('collection_sha256') != collection['sha256'] or prior.get('kind') != 'note_outputs':
            raise ValueError('Notes came from different observations')
        if set(prior['cases']) != {r['id'] for r in collection['cases']}:
            raise ValueError('Notes must retain the full selection denominator')
        for row in collection['cases']:
            raw = prior['responses'][row['id']]
            if digest(raw) != prior['source_response_sha256'][row['id']]:
                raise ValueError('Original note response hash mismatch')
            classified = prior['cases'][row['id']]
            if raw is not None:
                if row['status'] != 'ok' or note_result(raw, row['observation']) != classified:
                    raise ValueError('Notes were edited instead of reusing actual model output')
            elif classified != {'status': 'api_error' if row['status'] == 'ok' else 'skipped_first_search', 'notes': None}:
                raise ValueError('Missing note response has inconsistent status')
    elif prior is not None:
        raise ValueError('No previous semantic state at the note stage')
    prompt = (PACKAGE / 'prompts' / ('note.txt' if stage == 'notes' else 'actor.txt')).read_text(encoding='utf-8')
    jobs, rng = [], random.Random(seed)
    for repeat in range(1, repeats + 1):
        cases = deepcopy(collection['cases'])
        rng.shuffle(cases)
        for row in cases:
            arms = ['N'] if stage == 'notes' else ['A', 'B']
            rng.shuffle(arms)
            for arm in arms:
                note = prior['cases'][row['id']] if prior else None
                request, injected = (None, False) if row['status'] != 'ok' else _request(
                    row, stage, arm, config, prompt, collection['tools'], note)
                jobs.append({'id': f"{row['id']}__{arm}__r{repeat}", 'case_id': row['id'],
                             'arm': arm, 'repeat': repeat, 'request': request, 'memo_injected': injected})
    return seal({'version': VERSION, 'kind': 'model_plan', 'stage': stage,
                 'collection': deepcopy(collection), 'prior': deepcopy(prior), 'profile': config,
                 'prompt': prompt, 'repeats': repeats, 'seed': seed, 'jobs': jobs,
                 'fingerprint': io.fingerprint(), 'max_model_calls': len(jobs),
                 'planned_tool_executions': 0})


def validate_plan(plan):
    verify(plan)
    if plan.get('stage') == 'note_fidelity':
        from .fidelity import validate_fidelity_plan
        return validate_fidelity_plan(plan)
    if plan.get('stage') == 'evidence_pointer':
        # Sibling package; lazy import keeps one shared execution loop.
        from experiments.research_state.evidence_pointer.run import validate_ab_plan
        return validate_ab_plan(plan)
    if plan.get('version') != VERSION or plan.get('kind') != 'model_plan':
        raise ValueError('Invalid model plan')
    rebuilt = make_plan(plan['collection'], plan['profile'], plan['stage'], prior=plan['prior'],
                        repeats=plan['repeats'], seed=plan['seed'])
    if rebuilt != plan:
        raise ValueError('Frozen plan differs from source, prompts, runtime, inputs or requests')
    return plan


def _classify(plan, job, response):
    observation = next(r['observation'] for r in plan['collection']['cases'] if r['id'] == job['case_id'])
    if plan['stage'] in ('notes', 'note_fidelity'):
        return note_result(response, observation)
    return actor_result(response, observation, plan['profile']['allow_tool_calls_with_stop'])


def execute(plan, client, output, *, mode='mock', api_error_types=(),
         auth_error_types=(), preoutput_review=None):
    """auth_error_types marks rejections that void the whole credential: every
    remaining request in this batch is left unsent rather than counted as an
    API attempt."""
    plan = deepcopy(validate_plan(plan))
    if plan['stage'] == 'note_fidelity':
        from .fidelity import authorize
        verify(preoutput_review)
        if preoutput_review != authorize(plan, preoutput_review['review_basis']):
            raise ValueError('Invalid pre-output review attestation')
    elif preoutput_review is not None:
        raise ValueError('Pre-output review belongs only to the fidelity protocol')
    if mode not in ('mock', 'live'):
        raise ValueError('Explicit execution mode required')
    if mode == 'live':
        if plan['collection']['mode'] != 'live' or (plan['prior'] and plan['prior']['mode'] != 'live'):
            raise ValueError('A mock collection cannot be reported as a live study')
        if str(client.base_url).rstrip('/') != plan['profile']['base_url'] or client.max_retries != 0:
            raise ValueError('Actual client endpoint/retries differ from frozen profile')
        actual = client.timeout
        expected = plan['profile']['timeout_seconds']
        if not (actual == expected if type(actual) in (int, float) else
                all(getattr(actual, k, None) == expected for k in ('connect', 'read', 'write', 'pool'))):
            raise ValueError('Client timeout differs from frozen profile')
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    io.exclusive(output / 'plan.json', plan)
    execution = {'mode': mode, 'plan_sha256': plan['sha256']}
    if preoutput_review is not None:
        io.exclusive(output / 'preoutput_review.json', preoutput_review)
        execution['preoutput_review_sha256'] = preoutput_review['sha256']
        from datetime import datetime, timezone
        execution['preoutput_review_recorded_at'] = datetime.now(timezone.utc).isoformat()
    io.exclusive(output / 'execution.json', seal(execution))
    # Snapshot only the plan's own package; sibling packages share flat filenames.
    stage_package = _stage_package(plan)
    for source in io.source_files(stage_package):
        target = output / 'source' / source.relative_to(stage_package)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    auth_failure = None
    try:
        for job in plan['jobs']:
            folder = output / job['id']
            folder.mkdir()
            journal = io.Journal(folder / 'events.jsonl')
            if job['request'] is None:
                journal.emit('skipped', reason='first_search_failed')
                continue
            # A rejected credential applies to every remaining request in this batch:
            # the endpoint, key and profile are fixed for the whole execute() call.
            # Remaining jobs stay unsent rather than being counted as API attempts.
            # (Failure denominator is preserved: they are audited as blocked_by_auth.)
            if auth_failure is not None:
                journal.emit('blocked_by_auth', error_type=auth_failure)
                continue
            start = time.monotonic()
            journal.emit('request', request=deepcopy(job['request']))
            try:
                response = client.chat.completions.create(**deepcopy(job['request']))
            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception as exc:
                # Only actual SDK exceptions count as API failures; programming bugs stop the batch.
                if not isinstance(exc, api_error_types):
                    journal.emit('harness_error', error_type=type(exc).__name__)
                    raise
                if auth_error_types and isinstance(exc, auth_error_types):
                    auth_failure = type(exc).__name__
                journal.emit('api_error', error_type=type(exc).__name__,
                             elapsed_seconds=time.monotonic() - start)
            else:
                try:
                    raw = deepcopy(response) if isinstance(response, dict) else response.model_dump(mode='json')
                    canonical(raw)
                    journal.emit('response', response=raw, elapsed_seconds=time.monotonic() - start)
                except Exception as exc:
                    journal.emit('harness_error', error_type=type(exc).__name__)
                    raise
    finally:
        summary, _ = audit(output)
        io.write(output / 'summary.json', summary)
    return summary


def audit(folder):
    folder = Path(folder)
    plan = validate_plan(io.read(folder / 'plan.json'))
    execution = verify(io.read(folder / 'execution.json'))
    if execution['plan_sha256'] != plan['sha256']:
        raise ValueError('Execution manifest mismatch')
    if plan['stage'] == 'note_fidelity':
        from .fidelity import authorize
        attestation = verify(io.read(folder / 'preoutput_review.json'))
        if (execution.get('preoutput_review_sha256') != attestation['sha256']
                or attestation != authorize(plan, attestation['review_basis'])):
            raise ValueError('Pre-output review snapshot mismatch')
    for name, h in plan['fingerprint']['source_sha256'].items():
        if io.file_hash(folder / 'source' / name) != h:
            raise ValueError('Source snapshot mismatch')
    rows, totals, counts, by_arm = [], Counter(), Counter(), {}
    for job in plan['jobs']:
        events, errors = io.journal_prefix(folder / job['id'] / 'events.jsonl')
        kinds = [e['kind'] for e in events]
        requests = [e for e in events if e['kind'] == 'request']
        responses = [e for e in events if e['kind'] == 'response']
        if len(requests) > 1 or len(responses) > 1:
            errors.append('multiple_calls_in_single_job')
        if requests and requests[0].get('request') != job['request']:
            errors.append('actual_request_differs_from_frozen_plan')
        classification, response = None, None
        status = 'not_run'
        if kinds == ['skipped'] and job['request'] is None:
            status = 'skipped_first_search'
        elif kinds == ['blocked_by_auth'] and job['request'] is not None:
            status = 'blocked_by_auth'
        elif kinds == ['request', 'response']:
            response = responses[0]['response']
            classification = _classify(plan, job, response)
            status = classification['status']
        elif kinds == ['request', 'api_error']:
            status = 'api_error'
        elif kinds:
            status = 'incomplete'
            if kinds != ['request']:
                errors.append('unexpected_or_damaged_event_sequence')
        reported = usage(response)
        unknown = len(requests) > 0 and (response is None or not reported['complete'])
        counts[status] += 1
        arm = by_arm.setdefault(job['arm'], {'planned': 0, 'attempts': 0, 'responses': 0,
            'memo_injected': 0, 'statuses': Counter(), 'reported_tokens': Counter(), 'unknown_usage_requests': 0})
        arm['planned'] += 1
        arm['attempts'] += len(requests)
        arm['responses'] += len(responses)
        arm['memo_injected'] += int(job['memo_injected'] and bool(requests))
        arm['statuses'][status] += 1
        arm['reported_tokens'].update(reported['known'])
        arm['unknown_usage_requests'] += int(unknown)
        totals.update(reported['known'])
        totals['attempts'] += len(requests)
        totals['responses'] += len(responses)
        totals['unknown_usage_requests'] += int(unknown)
        totals['audit_errors'] += len(errors)
        totals['responses_inconsistent_usage'] += int(response is not None and reported['inconsistent'])
        rows.append({**{k: v for k, v in job.items() if k != 'request'}, 'status': status,
                     'classification': classification, 'response': response, 'usage': reported,
                     'memo_planned': job['memo_injected'],
                     'memo_injected': job['memo_injected'] and bool(requests),
                     'errors': errors, 'semantic_eligible': status in ('ok', 'empty') and not errors,
                     'elapsed_seconds': sum(e.get('elapsed_seconds', 0) for e in events)})
    summary = {'version': VERSION, 'stage': plan['stage'], 'mode': execution['mode'],
               'plan_sha256': plan['sha256'], 'scheduled': len(plan['jobs']), 'statuses': dict(counts), 'by_arm': by_arm,
               **dict(totals), 'reported_token_lower_bounds': {k: totals[k] for k in
                   ('prompt_tokens', 'completion_tokens', 'total_tokens')},
               'initial_model_calls': 0, 'tool_executions': 0, 'semantic_evaluation': 'not_evaluated',
               'cost_accounting_complete': not totals['unknown_usage_requests'] and not totals['audit_errors'],
               'all_model_jobs_delivered': all(r['status'] in ('ok', 'empty') and not r['errors'] for r in rows)}
    return summary, rows


def note_outputs(folder):
    summary, rows = audit(folder)
    plan = io.read(Path(folder) / 'plan.json')
    if plan['stage'] != 'notes' or summary.get('audit_errors', 0):
        raise ValueError('Expected an intact note-stage archive')
    if any(r['status'] not in ('ok', 'empty', 'invalid', 'api_error', 'skipped_first_search') for r in rows):
        raise ValueError('Do not hide interrupted/missing note attempts')
    return seal({'kind': 'note_outputs', 'collection_sha256': plan['collection']['sha256'],
                 'note_plan_sha256': plan['sha256'], 'mode': summary['mode'],
                 'source_response_sha256': {r['case_id']: digest(r['response']) for r in rows},
                 'responses': {r['case_id']: deepcopy(r['response']) for r in rows},
                 'cases': {r['case_id']: r['classification'] or {'status': r['status'], 'notes': None}
                           for r in rows},
                 'note_stage_cost': summary})


def export_review(folder, output):
    summary, rows = audit(folder)
    plan = io.read(Path(folder) / 'plan.json')
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    cards, key = [], []
    for index, row in enumerate(sorted(rows, key=lambda r: digest([plan['seed'], r['id']]))):
        case = next(x for x in plan['collection']['cases'] if x['id'] == row['case_id'])
        response = row['response']
        delivered = []
        if isinstance(response, dict):
            for choice in response.get('choices', []):
                msg = choice.get('message') or {}
                delivered.append({'finish_reason': choice.get('finish_reason'),
                                  'message': {k: msg.get(k) for k in ('content', 'tool_calls', 'refusal')}})
        card = {'card_id': f'card_{index+1}', 'question': case['question'],
                'first_query': case['query'], 'observation': case['observation'],
                'delivered': delivered, 'status': row['status'], 'semantic_eligible': row['semantic_eligible'],
                'memo_injected': row['memo_injected'],
                'note_shown': plan['prior']['cases'][row['case_id']] if plan['prior'] and row['memo_injected'] else None,
                'labels': {k: None for k in ('source_support', 'subject_relation_scope',
                  'useful_information_coverage', 'next_action_uses_observation',
                  'new_unsupported_claim', 'whole_action_reasonable')},
                'evidence': [], 'limitations': 'Masking is not blinding; no proposed tool executed.'}
        cards.append(card)
        key.append({'card_id': card['card_id'], **row})
    io.exclusive(output / 'cards.json', cards)
    io.exclusive(output / 'mapping.json', key)
    io.exclusive(output / 'summary.json', summary)
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('select')
    p.add_argument('--dataset', type=Path, default=ROOT / 'BCPlus/data/bcplus/qa.jsonl')
    p.add_argument('--qids', nargs='+', required=True)
    p.add_argument('--output', type=Path, required=True)
    p = sub.add_parser('collect')
    p.add_argument('--selection', type=Path, required=True)
    p.add_argument('--k', type=int, default=5)
    p.add_argument('--output', type=Path, required=True)
    p = sub.add_parser('plan')
    p.add_argument('--collection', type=Path, required=True)
    p.add_argument('--profile', type=Path, required=True)
    p.add_argument('--stage', choices=('notes', 'actors'), required=True)
    p.add_argument('--notes-run', type=Path)
    p.add_argument('--repeats', type=int, default=1)
    p.add_argument('--seed', type=int, default=20260921)
    p.add_argument('--output', type=Path, required=True)
    p = sub.add_parser('execute')
    p.add_argument('--plan', type=Path, required=True)
    p.add_argument('--env-file', type=Path, default=ROOT / '.env')
    p.add_argument('--output', type=Path, required=True)
    p = sub.add_parser('audit')
    p.add_argument('--run', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    if args.cmd == 'select':
        io.exclusive(args.output, select(args.dataset, args.qids))
        return 0
    if args.cmd == 'collect':
        from .retrieval import LocalSearch
        backend = LocalSearch()
        try:
            data = collect(io.read(args.selection), backend, args.output, k=args.k)
        finally:
            backend.close()
        print(canonical({'cases': len(data['cases']), 'initial_model_calls': 0,
                         'statuses': dict(Counter(r['status'] for r in data['cases']))}))
        return 0 if all(r['status'] == 'ok' for r in data['cases']) else 2
    if args.cmd == 'plan':
        collection = audit_capture(args.collection)
        prior = note_outputs(args.notes_run) if args.notes_run else None
        plan = make_plan(collection, io.read(args.profile), args.stage, prior=prior,
                         repeats=args.repeats, seed=args.seed)
        io.exclusive(args.output, plan)
        print(canonical({'sha256': plan['sha256'], 'max_model_calls': plan['max_model_calls'],
                         'tool_executions': 0}))
        return 0
    if args.cmd == 'audit':
        summary = export_review(args.run, args.output)
    else:
        plan = validate_plan(io.read(args.plan))  # Validation precedes credentials and paid calls.
        from dotenv import dotenv_values
        from openai import OpenAI, APIError
        values = {**dotenv_values(args.env_file), **os.environ}
        api_key = values.get('OPENAI_API_KEY') or values.get('DASHSCOPE_API_KEY')
        if not api_key or not str(api_key).strip():
            raise ValueError('API key missing; never put secrets in profile/plan')
        p = plan['profile']
        with OpenAI(api_key=api_key, base_url=p['base_url'], timeout=p['timeout_seconds'], max_retries=0) as client:
            from openai import AuthenticationError
            summary = execute(plan, client, args.output, mode='live',
                              api_error_types=(APIError,), auth_error_types=(AuthenticationError,))
    print(canonical(summary))
    return 0 if summary['all_model_jobs_delivered'] and summary['cost_accounting_complete'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
