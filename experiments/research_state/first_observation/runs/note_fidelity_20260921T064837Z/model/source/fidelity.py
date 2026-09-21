"""P0/P1 note-only comparison over the immutable 3d5fc3d observations.

Plan/prepare-review/export are offline. Execution delegates to run.execute;
there is no second API loop, retrieval adapter, semantic judge, or Actor here.
The old plan is an input passport, not a set of control responses to reuse.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import os
from pathlib import Path
import random

from . import artifacts as io
from . import run
from .contracts import VERSION, canonical, digest, seal, verify, profile

STAGE = 'note_fidelity'
SOURCE_COMMIT = '3d5fc3da2265e3ae17deecb7fe3841624617d61c'
ARCHIVE_PLAN_SHA = 'fd844132992e2e8b4166efe0fa4aab4b04787754e9cb434ce8e6d8084273c280'
COLLECTION_SHA = '7e43dad3176efc74c38eb4f0f6382f051912794563946a0a6edfe9ca8b9d9a2a'
P0_BLOB_SHA = '060e81d25a99e32ca66751702ca8ea24999c4ec7'
CASE_IDS = ('517', '546', '776', '519', '191', '71')
SEED = 20260922
PACKAGE = Path(__file__).parent
ARCHIVE = PACKAGE / 'runs' / 'notes_qwen_20260921'


def blob_sha(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def _parent(archive_plan: dict, origin: str) -> dict:
    """Verify the pinned historical input without revalidating its old runtime."""
    verify(archive_plan)
    if archive_plan.get('stage') != 'notes' or archive_plan.get('prior') is not None:
        raise ValueError('Expected the original single-arm notes plan')
    collection = run.check_collection(archive_plan['collection'])
    profile(archive_plan['profile'])
    if origin == 'archive':
        if (archive_plan['sha256'] != ARCHIVE_PLAN_SHA or collection['sha256'] != COLLECTION_SHA
                or collection['mode'] != 'live'
                or tuple(row['id'] for row in collection['cases']) != CASE_IDS):
            raise ValueError('Use the complete, unchanged 3d5fc3d archive; no subset or re-search')
    elif origin == 'synthetic_test':
        if collection['mode'] != 'mock':
            raise ValueError('Synthetic plans must use mock observations')
    else:
        raise ValueError('Unknown origin')
    return collection


def _prompts(archive_plan: dict) -> dict[str, str]:
    raw = (PACKAGE / 'prompts' / 'note.txt').read_bytes()
    if blob_sha(raw) != P0_BLOB_SHA:
        raise ValueError('P0 must remain byte-identical to the historical note.txt')
    base = raw.decode('utf-8')
    if archive_plan['prompt'] != base:
        raise ValueError('Archived and current P0 prompts differ')
    addendum = (PACKAGE / 'prompts' / 'note_fidelity_addendum.txt').read_text(encoding='utf-8')
    if not addendum.strip():
        raise ValueError('P1 addendum cannot be empty')
    return {'P0': base, 'P1': base + '\n' + addendum}


def make_fidelity_plan(archive_plan: dict, *, origin: str = 'archive') -> dict:
    """Freeze one call per case/arm. No repeat/arm/profile knobs in this protocol."""
    collection = _parent(archive_plan, origin)
    prompts = _prompts(archive_plan)
    config = deepcopy(archive_plan['profile'])
    rng = random.Random(SEED)
    cases = deepcopy(collection['cases'])
    rng.shuffle(cases)
    first = ['P0'] * (len(cases) // 2) + ['P1'] * (len(cases) - len(cases) // 2)
    rng.shuffle(first)  # In the real six-case batch: three P0-first, three P1-first.
    jobs = []
    for case, first_arm in zip(cases, first):
        order = (first_arm, 'P1' if first_arm == 'P0' else 'P0')
        pair = []
        for arm in order:
            request = None
            if case['status'] == 'ok':
                request, injected = run._request(case, 'notes', arm, config,
                                                prompts[arm], collection['tools'], None)
                if injected:
                    raise ValueError('Notes comparison may not inject semantic state')
            pair.append(request)
            jobs.append({'id': f"{case['id']}__{arm}__r1", 'case_id': case['id'],
                         'arm': arm, 'repeat': 1, 'request': request, 'memo_injected': False})
        # Check by exact object equality, not token counts or semantic similarity.
        if all(request is not None for request in pair):
            neutral = deepcopy(pair)
            for request in neutral:
                request['messages'][0]['content'] = '<SYSTEM_PROMPT>'
            if neutral[0] != neutral[1]:
                raise ValueError('P0/P1 differ beyond the system prompt')
    return seal({'version': VERSION, 'kind': 'model_plan', 'stage': STAGE,
                 'origin': origin, 'archive_plan': deepcopy(archive_plan),
                 'archive_commit': SOURCE_COMMIT if origin == 'archive' else None,
                 'collection': deepcopy(collection), 'profile': config, 'prior': None,
                 'prompts': prompts, 'repeats': 1, 'seed': SEED, 'jobs': jobs,
                 'fingerprint': io.fingerprint(), 'max_model_calls': len(jobs),
                 'planned_tool_executions': 0})


def validate_fidelity_plan(plan: dict) -> dict:
    verify(plan)
    if plan != make_fidelity_plan(plan['archive_plan'], origin=plan['origin']):
        raise ValueError('Fidelity plan drift: source, runtime, prompts, inputs, profile or schedule')
    return plan


def plan_from_archive(directory: Path = ARCHIVE) -> dict:
    """Read captured inputs and execution events only; never read old model outputs."""
    old = io.read(Path(directory) / 'notes-plan.json')
    _parent(old, 'archive')
    captured = run.audit_capture(Path(directory) / 'capture')
    if captured != old['collection']:
        raise ValueError('Historical plan and capture journal disagree')
    return make_fidelity_plan(old)


def _prefixes(plan: dict) -> list[dict]:
    return [{'case_id': case['id'], 'question': case['question'],
             'observation_sha256': digest(case['observation']),
             'core_relations': [],
             'no_clear_core': False, 'limits_and_alternatives': ''}
            for case in plan['collection']['cases']]


def review_template(plan: dict) -> dict:
    """An OFFLINE reviewer fills this from Q/O1 before any new P0/P1 response."""
    validate_fidelity_plan(plan)
    return {'plan_sha256': plan['sha256'], 'reviewer': '',
            'prior_cases_known': True, 'current_outputs_seen': False,
            'cases': _prefixes(plan)}


def check_review_basis(plan: dict, basis: dict) -> dict:
    """Mechanical attestation only; quote membership never proves entailment."""
    if (basis.get('plan_sha256') != plan['sha256'] or not isinstance(basis.get('reviewer'), str)
            or not basis['reviewer'].strip() or basis.get('current_outputs_seen') is not False
            or type(basis.get('prior_cases_known')) is not bool):
        raise ValueError('Complete the pre-output review attestation tied to this plan')
    cases = {case['id']: case for case in plan['collection']['cases']}
    rows = basis.get('cases')
    if (not isinstance(rows, list) or len(rows) != len(cases)
            or {row['case_id'] for row in rows} != set(cases)):
        raise ValueError('Review basis must cover every selected case exactly once')
    for row in rows:
        case = cases[row['case_id']]
        if (row.get('question') != case['question']
                or row.get('observation_sha256') != digest(case['observation'])
                or type(row.get('no_clear_core')) is not bool
                or not isinstance(row.get('limits_and_alternatives'), str)
                or not row['limits_and_alternatives'].strip()):
            raise ValueError('Review basis lost question, source version, or limitations')
        core = row.get('core_relations')
        if not isinstance(core, list) or len(core) > 6 or (not core) != row['no_clear_core']:
            raise ValueError('Declare up to six local core relations, or explicitly no clear core')
        refs = {window['window_ref']: window for window in case['observation'] or []}
        ids = set()
        for item in core:
            if set(item) != {'id', 'description', 'source_ref', 'quote'}:
                raise ValueError('Each core relation needs id/description/source_ref/quote')
            if any(not isinstance(v, str) or not v.strip() for v in item.values()):
                raise ValueError('Core relation fields cannot be empty')
            if item['id'] in ids or item['source_ref'] not in refs:
                raise ValueError('Duplicate target or unknown source')
            ids.add(item['id'])
            if item['quote'] not in refs[item['source_ref']]['text']:
                raise ValueError('Core relation quote is outside the actual window')
    return deepcopy(basis)


def authorize(plan: dict, basis: dict) -> dict:
    """Freeze review scope separately. It is NEVER passed into any model request."""
    validate_fidelity_plan(plan)
    return seal({'kind': 'note_fidelity_preoutput_review', 'plan_sha256': plan['sha256'],
                 'review_basis': check_review_basis(plan, basis)})


def export_review(directory: Path, output: Path) -> dict:
    """Export original sources, delivered text and per-note labels; no automatic judge."""
    plan = validate_fidelity_plan(io.read(Path(directory) / 'plan.json'))
    attestation = verify(io.read(Path(directory) / 'preoutput_review.json'))
    if attestation != authorize(plan, attestation['review_basis']):
        raise ValueError('Review basis differs from the pre-execution attestation')
    summary, rows = run.audit(directory)
    bases = {row['case_id']: row for row in attestation['review_basis']['cases']}
    cases = {case['id']: case for case in plan['collection']['cases']}
    cards, mapping = [], []
    diagnostic = {'by_arm': {}, 'semantic_evaluation': 'not_evaluated'}
    for row in sorted(rows, key=lambda r: digest([SEED, 'review', r['id']])):
        case, basis = cases[row['case_id']], bases[row['case_id']]
        raw = row['response']
        delivered = []
        if isinstance(raw, dict) and isinstance(raw.get('choices'), list):
            for choice in raw['choices']:
                if not isinstance(choice, dict):
                    continue
                msg = choice.get('message')
                delivered.append({'finish_reason': choice.get('finish_reason'),
                    'message': {k: deepcopy(msg[k]) for k in ('role', 'content', 'tool_calls', 'refusal')
                                if isinstance(msg, dict) and k in msg}})
        classification = row['classification'] or {}
        notes = classification.get('notes') or []
        card_id = f'card_{len(cards) + 1:02d}'
        cards.append({'card_id': card_id, 'question': case['question'],
            'first_query': case['query'], 'observation': deepcopy(case['observation']),
            'status': row['status'], 'semantic_eligible': row['semantic_eligible'],
            'delivered': delivered, 'mechanical_errors': row['errors'] + classification.get('errors', []),
            'notes': [{'index': i, 'note': deepcopy(note),
                       'labels': {key: None for key in ('source_support', 'attribution_scope',
                           'subject_time_scope', 'concrete_relevance')},
                       'label_evidence': [], 'interpretation_sensitivity': ''}
                      for i, note in enumerate(notes)],
            'core_coverage': [{'target': deepcopy(target), 'covered': None,
                              'supporting_note_indices': [], 'comment': ''}
                             for target in basis['core_relations']],
            'no_clear_core': basis['no_clear_core'],
            'limits_and_alternatives': basis['limits_and_alternatives'],
            'set_labels': {key: None for key in ('unsupported_expansion_present',
                'core_preserved', 'empty_appropriate', 'useful_set')},
            'set_reason': ''})
        mapping.append({'card_id': card_id, **{k: row[k] for k in
                        ('id', 'case_id', 'arm', 'repeat', 'status', 'usage', 'elapsed_seconds')}})
        totals = diagnostic['by_arm'].setdefault(row['arm'], Counter())
        totals['planned'] += 1
        totals['emitted_notes'] += len(notes)
        totals['valid_nonempty_sets'] += int(row['status'] == 'ok' and not row['errors'])
        totals['valid_empty_sets'] += int(row['status'] == 'empty' and not row['errors'])
        u = raw.get('usage') if isinstance(raw, dict) else None
        detail = u.get('completion_tokens_details') if isinstance(u, dict) else None
        reasoning = detail.get('reasoning_tokens') if isinstance(detail, dict) else None
        if type(reasoning) is int and reasoning >= 0:
            totals['reported_reasoning_tokens'] += reasoning
        else:
            totals['reasoning_usage_unknown_jobs'] += 1
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    for name, value in [('cards.json', cards), ('mapping.json', mapping),
                        ('summary.json', summary), ('diagnostics.json', diagnostic)]:
        io.exclusive(output / name, value)
    io.exclusive(output / 'rubric.json', {
        'allowed_labels': ['yes', 'no', 'unknown', 'not_applicable'],
        'source_unit': 'Entire displayed window, not quote alone; no unseen text or model reasoning.',
        'primary': ['unsupported_expansion_present', 'core_preserved'],
        'limits': ['No independence assumption across notes in one case; keep 6 cases per arm.',
                   'Empty is valid delivery, not automatic semantic success; check core coverage.',
                   'Unsupported by this observation is not the same as false in the world.',
                   'Relevance is separate from entailment. Preserve sensitivity of ambiguous cases.',
                   'No semantic object for API errors/truncation; retain all twelve scheduled rows.',
                   'Masking condition IDs is not blinded or independent human evaluation.',
                   'No Actor, retrieval gain, memory gain or answer accuracy is measured.']})
    return summary


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('plan')
    p.add_argument('--archive', type=Path, default=ARCHIVE)
    p.add_argument('--output', type=Path, required=True)
    p = sub.add_parser('review-template')
    p.add_argument('--plan', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p = sub.add_parser('execute')
    p.add_argument('--plan', type=Path, required=True)
    p.add_argument('--review-basis', type=Path, required=True)
    p.add_argument('--env-file', type=Path, default=run.ROOT / '.env')
    p.add_argument('--output', type=Path, required=True)
    p = sub.add_parser('audit')
    p.add_argument('--run', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    if args.cmd == 'plan':
        plan = plan_from_archive(args.archive)
        io.exclusive(args.output, plan)
        print(canonical({'sha256': plan['sha256'], 'model_calls': 12, 'tool_calls': 0}))
        return 0
    if args.cmd == 'audit':
        summary = export_review(args.run, args.output)
    else:
        plan = validate_fidelity_plan(io.read(args.plan))
        if args.cmd == 'review-template':
            io.exclusive(args.output, review_template(plan))
            return 0
        if plan['origin'] != 'archive':
            raise ValueError('CLI may not run synthetic plans against a real API')
        authorization = authorize(plan, io.read(args.review_basis))
        if args.output.exists():
            raise ValueError('Output exists; no overwrite or automatic resume')
        from dotenv import dotenv_values
        from openai import OpenAI, APIError
        values = {**dotenv_values(args.env_file), **os.environ}  # no credentials in plan
        key = values.get('OPENAI_API_KEY') or values.get('DASHSCOPE_API_KEY')
        if not key or not str(key).strip():
            raise ValueError('API key missing')
        config = plan['profile']
        with OpenAI(api_key=key, base_url=config['base_url'],
                    timeout=config['timeout_seconds'], max_retries=0) as client:
            summary = run.execute(plan, client, args.output, mode='live',
                                  api_error_types=(APIError,), preoutput_review=authorization)
    print(canonical(summary))
    return 0 if summary['all_model_jobs_delivered'] and summary['cost_accounting_complete'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
