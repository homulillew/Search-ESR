"""Evidence Pointer State v0: reference selection, materialization, A/B plan.

Offline stages: prepare_review / bind_state / make_ab_plan / audit / export.
The only network stage is execute, which delegates to the existing
first_observation runner so there is exactly one model-call loop in this repo.

A reference reviewer sees Q + q0 + O1 only: no gold answer, no later Search or
Open, no future trajectory, no Actor output. The reviewer writes addresses, the
harness writes the state. Rationale is sealed for audit and never enters a
model request.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from pathlib import Path
import random

from experiments.research_state.first_observation import artifacts as io
from experiments.research_state.first_observation import run as fo_run
from experiments.research_state.first_observation.contracts import (
    actor_result, canonical as fo_canonical, loads as fo_loads,
    seal as fo_seal, verify as fo_verify, usage, profile)
from . import contracts as ec

PACKAGE = Path(__file__).parent
ROOT = Path(__file__).resolve().parents[3]
PROMPT = PACKAGE / 'prompts' / 'actor.txt'


def load_collection(folder):
    """Reuse the frozen raw-question first-search collection verbatim."""
    return fo_run.audit_capture(Path(folder))


def check_reviewer_template(value):
    fo_verify(value)
    if value.get('version') != ec.VERSION or value.get('kind') != 'reviewer_template':
        raise ValueError('Not a reviewer template')
    for row in value['cases']:
        if set(row) != {'id', 'question', 'first_query', 'observation', 'annotated'}:
            raise ValueError('Reviewer template case has undeclared fields')
    return value


def prepare_review(collection, output):
    """Emit one review template per case: Q, q0, O1 and a char-offset view.

    `collection` is the sealed frozen collection from load_collection. The
    template deliberately contains no gold fields, no later attempts and no
    downstream outputs. Reviewers select spans from this artifact only.
    """
    rows = []
    for case in collection['cases']:
        annotated = {w['window_ref']: ec.show_window(w) for w in case['observation']}
        rows.append({'id': case['id'], 'question': case['question'],
                     'first_query': case['query'], 'observation': deepcopy(case['observation']),
                     'annotated': annotated})
    template = ec.seal({'version': ec.VERSION, 'kind': 'reviewer_template',
                        'collection_sha256': collection['sha256'],
                        'collection_folder': str(Path(collection['folder'])),
                        'cases': rows})
    check_reviewer_template(template)
    out = Path(output)
    out.mkdir(parents=True, exist_ok=False)
    io.exclusive(out / 'reviewer_template.json', template)
    return template


def check_selection_artifact(value):
    fo_verify(value)
    if value.get('version') != ec.VERSION or value.get('kind') != 'pointer_selection':
        raise ValueError('Not a pointer selection')
    if set(value) - {'version', 'kind', 'collection_sha256', 'cases', 'rationale', 'sha256'}:
        raise ValueError('Pointer selection has undeclared fields')
    return value


def bind_state(collection, selection, output=None):
    """Materialize the Evidence Pointer State from reviewer addresses.

    The reviewer artifact is consumed here and never forwarded: only the
    materialized state, whose every field is harness-derived, can reach a model.
    """
    check_selection_artifact(selection)
    if selection['collection_sha256'] != collection['sha256']:
        raise ValueError('Pointers were frozen against a different observation set')
    by_id = {c['id']: c for c in collection['cases']}
    if set(by_id) != set(selection['cases']):
        raise ValueError('Selection must retain the full case denominator')
    evidence, reviewed = {}, {}
    for case_id, row in selection['cases'].items():
        checked = ec.check_pointer_selection(by_id[case_id], row)
        items = []
        for index, pointer in enumerate(checked['pointers']):
            window = next(w for w in by_id[case_id]['observation']
                          if w['window_ref'] == pointer['window_ref'])
            items.append(ec.materialize(pointer, window, case_id, index))
        evidence[case_id] = ec.state_message(items, by_id[case_id]['observation'])
        reviewed[case_id] = {'pointers': checked['pointers'],
                             'rationale': checked['rationale']}
    state = ec.seal({'version': ec.VERSION, 'kind': 'evidence_state',
                     'collection_sha256': collection['sha256'],
                     'selection_sha256': selection['sha256'],
                     'evidence': evidence})
    if output is not None:
        out = Path(output)
        out.mkdir(parents=True, exist_ok=False)
        io.exclusive(out / 'evidence_state.json', state)
        # Reviewer rationale is archived for audit only.
        io.exclusive(out / 'reviewer_selection.json', ec.seal(
            {'version': ec.VERSION, 'kind': 'reviewer_selection_archived',
             'collection_sha256': collection['sha256'], 'cases': reviewed}))
    return state


def check_state(state, collection):
    fo_verify(state)
    if (state.get('version') != ec.VERSION or state.get('kind') != 'evidence_state'
            or state.get('collection_sha256') != collection['sha256']):
        raise ValueError('Evidence state does not bind to this collection')
    by_id = {c['id']: c for c in collection['cases']}
    if set(state['evidence']) != set(by_id):
        raise ValueError('Evidence state must retain the full case denominator')
    for case_id, message in state['evidence'].items():
        ec.state_message(message['evidence'], by_id[case_id]['observation'])
    return state


def _payload(case):
    return {'question': case['question'], 'first_query': case['query'],
            'observation': deepcopy(case['observation'])}


def _actor_request(payload, config, prompt):
    request = {'model': config['model'], 'stream': False, 'n': 1,
               'messages': [{'role': 'system', 'content': prompt},
                            {'role': 'user', 'content': fo_canonical(payload)}],
               **deepcopy(config['request_options'])}
    if len(fo_canonical(request).encode('utf-8')) > config['max_request_utf8_bytes']:
        raise ValueError('Full request exceeds byte guard; do not trim source content')
    return request


def make_ab_plan(collection, state, config, *, seed=20260922, repeats=1):
    """Freeze one A and one B actor call per case. A and B differ by treatment only."""
    check_state(state, collection)
    config = profile(config)
    if type(seed) is not int or repeats < 1 or repeats > 100:
        raise ValueError('Invalid schedule')
    prompt = PROMPT.read_text(encoding='utf-8')
    if not prompt.strip():
        raise ValueError('Shared actor prompt is empty')
    tools = deepcopy(collection['tools'])
    jobs, rng = [], random.Random(seed)
    for repeat in range(1, repeats + 1):
        cases = deepcopy(collection['cases'])
        rng.shuffle(cases)
        for case in cases:
            # Balanced pair order: the arm that is read first is randomised.
            arms = ['A', 'B']
            rng.shuffle(arms)
            for arm in arms:
                request = _actor_request(_payload(case), config, prompt)
                if arm == 'B':
                    request['messages'].append({'role': 'user', 'content': fo_canonical(
                        state['evidence'][case['id']])})
                    request['tools'] = tools
                    request['tool_choice'] = 'auto'
                else:
                    request['tools'] = tools
                    request['tool_choice'] = 'auto'
                jobs.append({'id': f"{case['id']}__{arm}__r{repeat}", 'case_id': case['id'],
                             'arm': arm, 'repeat': repeat, 'request': request,
                             'memo_injected': arm == 'B'})
    return ec.seal({'version': ec.VERSION, 'kind': 'model_plan', 'stage': ec.STAGE,
                    'collection': deepcopy(collection), 'state': deepcopy(state),
                    'profile': config, 'prompt': prompt, 'repeats': repeats, 'seed': seed,
                    'jobs': jobs, 'fingerprint': io.fingerprint(PACKAGE),
                    'max_model_calls': len(jobs), 'planned_tool_executions': 0})


def validate_ab_plan(plan):
    """Rebuild the whole plan and prove the arms differ by treatment only."""
    fo_verify(plan)
    if plan.get('stage') != ec.STAGE or plan.get('version') != ec.VERSION:
        raise ValueError('Not an evidence-pointer plan')
    rebuilt = make_ab_plan(plan['collection'], plan['state'], plan['profile'],
                           seed=plan['seed'], repeats=plan['repeats'])
    if rebuilt != plan:
        raise ValueError('Frozen plan differs from source, prompts, runtime, inputs or requests')
    # Object-equality proof, mirroring the fidelity protocol's masked comparison.
    for case in plan['collection']['cases']:
        pair = {j['arm']: j for j in plan['jobs'] if j['case_id'] == case['id']}
        neutral = deepcopy(pair['B']['request'])
        neutral['messages'] = neutral['messages'][:-1]
        if neutral != pair['A']['request']:
            raise ValueError('A and B differ beyond the evidence treatment')
        evidence_message = pair['B']['request']['messages'][-1]
        parsed = fo_loads(evidence_message['content'])
        if parsed['kind'] != 'evidence_pointer_state':
            raise ValueError('Treatment message is not an evidence pointer state')
    return plan


def _classify(plan, job, response):
    observation = next(r['observation'] for r in plan['collection']['cases']
                       if r['id'] == job['case_id'])
    return actor_result(response, observation,
                        plan['profile']['allow_tool_calls_with_stop'])


def audit(folder):
    folder = Path(folder)
    plan = validate_ab_plan(io.read(folder / 'plan.json'))
    execution = fo_verify(io.read(folder / 'execution.json'))
    if execution['plan_sha256'] != plan['sha256']:
        raise ValueError('Execution manifest mismatch')
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
            'memo_injected': 0, 'statuses': Counter(), 'reported_tokens': Counter(),
            'unknown_usage_requests': 0, 'proposed_tools': 0, 'tool_kinds': Counter()})
        arm['planned'] += 1
        arm['attempts'] += len(requests)
        arm['responses'] += len(responses)
        arm['memo_injected'] += int(job['memo_injected'] and bool(requests))
        arm['statuses'][status] += 1
        if classification and classification['kind'] == 'tools':
            arm['proposed_tools'] += len(classification['calls'])
            arm['tool_kinds'].update(c['function']['name'] for c in classification['calls'])
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
                     'errors': errors, 'proposed_tools': len(classification['calls'])
                     if classification and classification['kind'] == 'tools' else 0,
                     'elapsed_seconds': sum(e.get('elapsed_seconds', 0) for e in events)})
    summary = {'version': ec.VERSION, 'stage': plan['stage'], 'mode': execution['mode'],
               'plan_sha256': plan['sha256'], 'scheduled': len(plan['jobs']),
               'statuses': dict(counts), 'by_arm': by_arm, **dict(totals),
               'reported_token_lower_bounds': {k: totals[k] for k in
                   ('prompt_tokens', 'completion_tokens', 'total_tokens')},
               'initial_model_calls': 0, 'tool_executions': 0,
               'proposed_tools': sum(r['proposed_tools'] for r in rows),
               'semantic_evaluation': 'not_evaluated',
               'cost_accounting_complete': not totals['unknown_usage_requests'] and not totals['audit_errors'],
               'all_model_jobs_delivered': all(r['status'] in ('ok', 'empty') and not r['errors'] for r in rows)}
    return summary, rows


def export_review(folder, output):
    """Emit unlabelled review cards for offline pairwise judgement."""
    summary, rows = audit(folder)
    plan = io.read(Path(folder) / 'plan.json')
    out = Path(output)
    out.mkdir(parents=True, exist_ok=False)
    cards, key = [], []
    for index, row in enumerate(sorted(rows, key=lambda r: digest_pair(plan['seed'], r['id']))):
        case = next(x for x in plan['collection']['cases'] if x['id'] == row['case_id'])
        delivered = []
        if isinstance(row['response'], dict):
            for choice in row['response'].get('choices', []):
                msg = choice.get('message') or {}
                delivered.append({'finish_reason': choice.get('finish_reason'),
                                  'message': {k: msg.get(k) for k in ('content', 'tool_calls', 'refusal')}})
        treatment = (plan['state']['evidence'].get(row['case_id'], {}).get('evidence')
                     if row['arm'] == 'B' else None)
        card = {'card_id': f'card_{index + 1}', 'arm': row['arm'], 'case_id': row['case_id'],
                'question': case['question'], 'first_query': case['query'],
                'observation': case['observation'], 'evidence_shown': treatment,
                'delivered': delivered, 'status': row['status'],
                'proposed_tools': row['proposed_tools'],
                'labels': {k: None for k in ('uses_existing_observation',
                  'repeats_resolved_query', 'follows_intermediate_entity',
                  'upgrades_partial_support', 'chooses_open_when_needed',
                  'adds_unsupported_fact', 'premature_final_answer',
                  'whole_next_action_reasonable')},
                'pairwise': None,
                'limitations': 'Masking is not blinding; no proposed tool was executed.'}
        cards.append(card)
        key.append({'card_id': card['card_id'], **row})
    io.exclusive(out / 'cards.json', cards)
    io.exclusive(out / 'mapping.json', key)
    io.exclusive(out / 'summary.json', summary)
    return summary


def digest_pair(seed, job_id):
    from experiments.research_state.first_observation.contracts import digest
    return digest([seed, job_id])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('prepare-review')
    p.add_argument('--collection', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p = sub.add_parser('bind')
    p.add_argument('--collection', type=Path, required=True)
    p.add_argument('--selection', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p = sub.add_parser('plan')
    p.add_argument('--collection', type=Path, required=True)
    p.add_argument('--state', type=Path, required=True)
    p.add_argument('--profile', type=Path, required=True)
    p.add_argument('--repeats', type=int, default=1)
    p.add_argument('--seed', type=int, default=20260922)
    p.add_argument('--output', type=Path, required=True)
    p = sub.add_parser('audit')
    p.add_argument('--run', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    if args.cmd == 'prepare-review':
        collection = load_collection(args.collection)
        template = prepare_review(collection, args.output)
        print(fo_canonical({'collection_sha256': template['collection_sha256'],
                            'cases': len(template['cases'])}))
        return 0
    if args.cmd == 'bind':
        collection = load_collection(args.collection)
        state = bind_state(collection, io.read(args.selection), args.output)
        counts = {k: len(v['evidence']) for k, v in state['evidence'].items()}
        print(fo_canonical({'collection_sha256': state['collection_sha256'],
                            'pointers_per_case': counts,
                            'empty_cases': [k for k, v in counts.items() if not v]}))
        return 0
    if args.cmd == 'audit':
        summary = export_review(args.run, args.output)
    else:
        collection = load_collection(args.collection)
        state = check_state(io.read(args.state), collection)
        plan = make_ab_plan(collection, state, io.read(args.profile),
                            seed=args.seed, repeats=args.repeats)
        io.exclusive(args.output, plan)
        print(fo_canonical({'sha256': plan['sha256'], 'max_model_calls': plan['max_model_calls'],
                            'tool_executions': 0}))
        return 0
    print(fo_canonical(summary))
    return 0 if summary['all_model_jobs_delivered'] and summary['cost_accounting_complete'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
