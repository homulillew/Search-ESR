"""Fixed-content state-view experiments: prepare, plan, execute, audit.

Only execute calls a model. No Search/Open executor, Reviewer, state writer,
JSON repair, retry-until-success, or automatic promotion to a later experiment.
"""
from __future__ import annotations
import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import random
import re
import shutil
import sys
import time
from urllib.parse import urlsplit

from ..need_review.checkpoint import digest, load_checkpoint
from ..need_review.node import classify_actor_response
from ..need_review.accounting import inspect_usage
from .packet import (COMPARISONS, build_packet, validate_packet, render,
                     proposed_repeats, text)
from .storage import read, write, loads, safe_path, sealed, verify_seal

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[2]
REVISION = 'investigation_view_v1'


def code_files() -> dict[str, Path]:
    paths = list(PACKAGE.glob('*.py'))
    paths += [PACKAGE.parent / 'need_review' / name for name in
              ('checkpoint.py', 'node.py', 'accounting.py')]
    return {str(p.relative_to(ROOT)): p for p in sorted(paths)}


def code_hashes() -> dict[str, str]:
    return {key: hashlib.sha256(p.read_bytes()).hexdigest() for key, p in code_files().items()}


def runtime_versions() -> dict:
    versions = {'python': sys.version}
    for package in ('openai', 'python-dotenv'):
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = None
    return versions


def blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def prepare(selection_path: Path, root: Path, output: Path, cases: list[str] | None = None) -> dict:
    selection = read(selection_path)
    if not isinstance(selection, dict) or selection.get('schema_version') != 'investigation_selection_v1':
        raise ValueError('Unsupported selection')
    if not re.fullmatch(r'[0-9a-f]{40}', selection.get('archive_commit', '')):
        raise ValueError('A full archive commit is required')
    selected = selection.get('cases')
    if not isinstance(selected, list) or not selected:
        raise ValueError('Empty case selection')
    all_ids = [row['case_id'] for row in selected]
    if len(set(all_ids)) != len(all_ids) or any(not re.fullmatch(r'[A-Za-z0-9_-]+', i) for i in all_ids):
        raise ValueError('Case identifiers must be unique and path-safe')
    if cases is not None:
        if not cases or len(cases) != len(set(cases)) or set(cases) - set(all_ids):
            raise ValueError('Unknown, empty, or duplicate case subset')
        selected = [row for row in selected if row['case_id'] in cases]
    packets = {}
    for row in selected:
        path = safe_path(root, row['checkpoint_path'])
        if blob_sha(path.read_bytes()) != row['checkpoint_blob_sha']:
            raise ValueError('Archived checkpoint bytes differ from pinned selection')
        cp = load_checkpoint(path)
        if cp['checkpoint_id'] != row['case_id']:
            raise ValueError('Selection/checkpoint ID mismatch')
        packets[row['case_id']] = build_packet(cp, row['fixture'])
    bundle = sealed({'schema_version': 'investigation_bundle_v1',
                     'selection': {**selection, 'cases': selected}, 'packets': packets}, 'bundle_sha256')
    output.mkdir(parents=True, exist_ok=False)
    write(output / 'bundle.json', bundle)
    write(output / 'fixture_review.template.json', {
        'bundle_sha256': bundle['bundle_sha256'], 'reviewer': None,
        'prefix_only': False, 'quotes_and_claim_scope_checked': False,
        'task_is_not_a_gold_answer_hint': False, 'prior_outputs_known': True,
        'notes': 'Fill after checking original visible sources; membership checks do not prove entailment.'})
    return {'cases': list(packets), 'bundle_sha256': bundle['bundle_sha256'], 'model_calls': 0}


def load_bundle(path: Path) -> dict:
    bundle = read(path)
    verify_seal(bundle, 'bundle_sha256')
    if bundle.get('schema_version') != 'investigation_bundle_v1' or not bundle.get('packets'):
        raise ValueError('Unsupported/empty bundle')
    selected = bundle['selection']['cases']
    if len(selected) != len(bundle['packets']) or set(bundle['packets']) != {r['case_id'] for r in selected}:
        raise ValueError('Bundle differs from selection')
    for row in selected:
        packet = validate_packet(bundle['packets'][row['case_id']])
        if packet['fixture'] != row['fixture'] or packet['checkpoint']['checkpoint_id'] != row['case_id']:
            raise ValueError('Fixture differs from selection')
    return bundle


def validate_profile(profile: dict) -> dict:
    required = {'model', 'base_url', 'timeout_seconds', 'request_options', 'max_request_utf8_bytes'}
    if not isinstance(profile, dict) or set(profile) != required:
        raise ValueError('Profile must use the documented exact keys')
    text(profile['model'], 'model', 200)
    url = text(profile['base_url'], 'base_url', 1000)
    try:
        parts = urlsplit(url)
        parts.port
    except ValueError:
        raise ValueError('Invalid API base') from None
    if (parts.scheme not in {'http', 'https'} or not parts.hostname or parts.username is not None or parts.password is not None
            or parts.query or parts.fragment or url != url.strip().rstrip('/')
            or parts.path.endswith(('/chat/completions', '/responses'))):
        raise ValueError('Profile requires a normalized credential-free API base')
    timeout = profile['timeout_seconds']
    if type(timeout) not in (int, float) or not math.isfinite(timeout) or timeout <= 0:
        raise ValueError('Timeout must be finite and positive')
    size = profile['max_request_utf8_bytes']
    if type(size) is not int or size < 1:
        raise ValueError('Request byte guard must be positive; no silent truncation')
    options = profile['request_options']
    allowed = {'max_tokens', 'max_completion_tokens', 'temperature', 'top_p', 'seed', 'reasoning_effort'}
    if not isinstance(options, dict) or set(options) - allowed:
        raise ValueError('Unsupported request option; no silent provider-specific extra_body')
    caps = set(options) & {'max_tokens', 'max_completion_tokens'}
    if len(caps) != 1 or type(options[next(iter(caps))]) is not int or options[next(iter(caps))] < 1:
        raise ValueError('Specify exactly one positive completion cap')
    for key, low, high in (('temperature', 0, 2), ('top_p', 0, 1)):
        if key in options and (type(options[key]) not in (int, float)
                or not math.isfinite(options[key]) or not low <= options[key] <= high):
            raise ValueError('Invalid sampling option')
    if 'seed' in options and type(options['seed']) is not int:
        raise ValueError('Sampling seed must be an integer')
    if 'reasoning_effort' in options:
        text(options['reasoning_effort'], 'reasoning_effort', 40)
    digest(profile)  # Reject nested nonfinite values.
    return deepcopy(profile)


def request_for(packet: dict, view: str, profile: dict, prompt: str) -> dict:
    profile = validate_profile(profile)
    text(prompt, 'actor prompt', 12000)
    original = packet['checkpoint']['request']
    tools = original.get('tools')
    if not isinstance(tools, list) or not tools:
        raise ValueError('Function definitions are required in the checkpoint')
    names = []
    for tool in tools:
        if (not isinstance(tool, dict) or tool.get('type') != 'function'
                or not isinstance(tool.get('function'), dict)
                or not isinstance(tool['function'].get('parameters'), dict)):
            raise ValueError('Unsupported captured tool definition')
        names.append(text(tool['function'].get('name'), 'tool name', 100))
    if len(names) != len(set(names)):
        raise ValueError('Duplicate tool definitions')
    from ..need_review.checkpoint import canonical_json
    request = {'model': profile['model'], 'stream': False, 'n': 1,
               'tools': deepcopy(tools), 'tool_choice': 'auto',
               'messages': [{'role': 'system', 'content': prompt},
                            {'role': 'user', 'content': json.dumps(render(packet, view), ensure_ascii=False, allow_nan=False, separators=(',', ':'))}],
               **deepcopy(profile['request_options'])}
    if len(canonical_json(request).encode()) > profile['max_request_utf8_bytes']:
        raise ValueError('Request exceeds byte guard; do not trim the evidence inventory')
    return request


def build_plan(bundle: dict, profile: dict, prompt: str, *, comparison: str = 'layout',
               repeats: int = 2, seed: int = 20260921, purpose: str = 'pilot',
               fixture_review: dict | None = None, acceptance: dict | None = None) -> dict:
    if comparison not in COMPARISONS or purpose not in {'pilot', 'formal'}:
        raise ValueError('Unknown comparison or purpose')
    if type(repeats) is not int or repeats < 1 or type(seed) is not int:
        raise ValueError('Positive repetitions and integer schedule seed required')
    verify_seal(bundle, 'bundle_sha256')
    if purpose == 'formal':
        if (not isinstance(fixture_review, dict)
                or fixture_review.get('bundle_sha256') != bundle['bundle_sha256']
                or not isinstance(fixture_review.get('reviewer'), str) or not fixture_review['reviewer'].strip()
                or any(fixture_review.get(k) is not True for k in
                       ('prefix_only', 'quotes_and_claim_scope_checked', 'task_is_not_a_gold_answer_hint'))):
            raise ValueError('Formal plan requires a reviewed fixture attestation tied to this bundle')
        if (not isinstance(acceptance, dict) or acceptance.get('bundle_sha256') != bundle['bundle_sha256']
                or acceptance.get('profile_sha256') != digest(profile)
                or acceptance.get('comparison') != comparison
                or acceptance.get('code_sha256') != code_hashes()
                or acceptance.get('runtime_versions') != runtime_versions()
                or acceptance.get('prompt_sha256') != digest(prompt)
                or acceptance.get('mechanically_clean') is not True):
            raise ValueError('Formal plan requires a clean same-profile/materials pilot audit')
    rng = random.Random(seed)
    schedule = []
    for repeat in range(1, repeats + 1):
        case_ids = sorted(bundle['packets'])
        rng.shuffle(case_ids)
        for case_id in case_ids:
            packet = validate_packet(bundle['packets'][case_id])
            views = list(COMPARISONS[comparison])
            rng.shuffle(views)
            for view in views:
                request = request_for(packet, view, profile, prompt)
                schedule.append({'sample_id': f'{case_id}__{view}__r{repeat}', 'case_id': case_id,
                                 'view': view, 'repeat': repeat, 'request_sha256': digest(request)})
    return sealed({'schema_version': REVISION, 'bundle_sha256': bundle['bundle_sha256'],
                   'profile': validate_profile(profile), 'prompt': prompt, 'comparison': comparison,
                   'purpose': purpose, 'repeats': repeats, 'schedule_seed': seed,
                   'fixture_review': deepcopy(fixture_review), 'acceptance': deepcopy(acceptance),
                   'code_sha256': code_hashes(), 'runtime_versions': runtime_versions(), 'schedule': schedule,
                   'planned_model_calls': len(schedule), 'planned_tool_executions': 0,
                   'sdk_max_retries': 0}, 'plan_sha256')


def validate_plan(plan: dict, bundle: dict) -> dict:
    verify_seal(plan, 'plan_sha256')
    rebuilt = build_plan(bundle, plan['profile'], plan['prompt'], comparison=plan['comparison'],
                         repeats=plan['repeats'], seed=plan['schedule_seed'], purpose=plan['purpose'],
                         fixture_review=plan['fixture_review'], acceptance=plan['acceptance'])
    if plan != rebuilt:
        raise ValueError('Frozen plan differs from material, code, profile, or schedule')
    return rebuilt


class Journal:
    def __init__(self, path: Path):
        self.path, self.seq = path, 0

    def emit(self, kind: str, **payload) -> None:
        from ..need_review.checkpoint import canonical_json
        self.seq += 1
        row = {'seq': self.seq, 'time': datetime.now(timezone.utc).isoformat(), 'kind': kind, **payload}
        with self.path.open('a', encoding='utf-8') as stream:
            stream.write(canonical_json(row) + '\n')
            stream.flush()
            os.fsync(stream.fileno())


def compact_classification(response: dict, request: dict) -> dict:
    return {k: v for k, v in classify_actor_response(response, request).items() if k != 'raw_response'}


def execute(plan: dict, bundle: dict, output: Path, client: object, *, mode: str = 'mock') -> dict:
    # Validate and copy once before any paid call. SDK mutation cannot drift later arms.
    plan, bundle = deepcopy(plan), deepcopy(bundle)
    validate_plan(plan, bundle)
    if mode not in {'mock', 'live'}:
        raise ValueError('Unknown execution mode')
    if mode == 'live':
        if str(getattr(client, 'base_url', '')).rstrip('/') != plan['profile']['base_url']:
            raise ValueError('Actual client endpoint differs from frozen profile')
        if getattr(client, 'max_retries', None) != 0:
            raise ValueError('Actual client retry policy differs from frozen profile')
        actual_timeout = getattr(client, 'timeout', None)
        expected_timeout = plan['profile']['timeout_seconds']
        if type(actual_timeout) in (int, float):
            matches = actual_timeout == expected_timeout
        else:
            matches = all(getattr(actual_timeout, k, None) == expected_timeout
                          for k in ('connect', 'read', 'write', 'pool'))
        if not matches:
            raise ValueError('Actual client timeout differs from frozen profile')
    create = client.chat.completions.create
    if not callable(create):
        raise TypeError('Client adapter is not callable')
    requests = {row['sample_id']: request_for(bundle['packets'][row['case_id']], row['view'],
                plan['profile'], plan['prompt']) for row in plan['schedule']}
    output.mkdir(parents=True, exist_ok=False)
    write(output / 'plan.json', plan)
    write(output / 'bundle.json', bundle)
    write(output / 'execution.json', sealed({'mode': mode, 'runtime_versions': runtime_versions(),
          'plan_sha256': plan['plan_sha256']}, 'execution_sha256'))
    for relative, path in code_files().items():
        destination = output / 'source' / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, destination)
    try:
        for row in plan['schedule']:
            directory = output / 'branches' / row['sample_id']
            directory.mkdir(parents=True)
            journal = Journal(directory / 'events.jsonl')
            request = requests[row['sample_id']]
            record = {**row, 'status': 'interrupted', 'request': deepcopy(request), 'response': None}
            start = time.monotonic()
            try:
                journal.emit('request', request=deepcopy(request))
                try:
                    response = create(**deepcopy(request))
                except Exception as exc:
                    code = getattr(exc, 'status_code', None)
                    is_api = (type(code) is int and 100 <= code <= 599) or type(exc).__name__ in {
                        'APITimeoutError', 'APIConnectionError', 'APIError', 'RateLimitError'}
                    if not is_api:
                        raise
                    record.update(status='api_error', error_type=type(exc).__name__)
                    journal.emit('api_error', error_type=type(exc).__name__,
                                 status_code=code if type(code) is int else None,
                                 elapsed_seconds=time.monotonic() - start)
                else:
                    raw = deepcopy(response) if isinstance(response, dict) else response.model_dump(mode='json')
                    digest(raw)  # Must be a serializable raw response, not a repaired response.
                    record['response'] = raw
                    journal.emit('response', response=raw, elapsed_seconds=time.monotonic() - start)
                    record['classification'] = compact_classification(raw, request)
                    record['status'] = 'completed'
            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception as exc:
                record.update(status='harness_error', error_type=type(exc).__name__)
                journal.emit('harness_error', error_type=type(exc).__name__, elapsed_seconds=time.monotonic() - start)
                raise
            finally:
                write(directory / 'result.json', record)
    finally:
        from .report import audit
        summary, _ = audit(output)
        write(output / 'summary.json', summary)
    return summary


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('prepare')
    p.add_argument('--selection', type=Path, default=PACKAGE / 'fixtures.json')
    p.add_argument('--repo-root', type=Path, default=ROOT)
    p.add_argument('--cases', nargs='+')
    p.add_argument('--output', type=Path, required=True)
    p = sub.add_parser('plan')
    p.add_argument('--prepared', type=Path, required=True)
    p.add_argument('--profile', type=Path, required=True)
    p.add_argument('--comparison', choices=COMPARISONS, default='layout')
    p.add_argument('--purpose', choices=('pilot', 'formal'), default='pilot')
    p.add_argument('--repeats', type=int, default=2)
    p.add_argument('--seed', type=int, default=20260921)
    p.add_argument('--fixture-review', type=Path)
    p.add_argument('--accepted-pilot', type=Path)
    p.add_argument('--output', type=Path, required=True)
    p = sub.add_parser('execute')
    p.add_argument('--prepared', type=Path, required=True)
    p.add_argument('--plan', type=Path, required=True)
    p.add_argument('--env-file', type=Path, default=ROOT / '.env')
    p.add_argument('--output', type=Path, required=True)
    p = sub.add_parser('audit')
    p.add_argument('--run-dir', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    from ..need_review.checkpoint import canonical_json
    if args.command == 'prepare':
        print(canonical_json(prepare(args.selection, args.repo_root, args.output, args.cases)))
        return 0
    if args.command == 'audit':
        from .report import export
        summary = export(args.run_dir, args.output)
        print(canonical_json(summary))
        return 0 if summary['mechanically_clean'] else 2
    bundle = load_bundle(args.prepared / 'bundle.json')
    if args.command == 'plan':
        acceptance = None
        if args.accepted_pilot:
            from .report import pilot_acceptance
            acceptance = pilot_acceptance(args.accepted_pilot)
        plan = build_plan(bundle, read(args.profile), (PACKAGE / 'prompts' / 'actor.txt').read_text(),
                          comparison=args.comparison, purpose=args.purpose, repeats=args.repeats, seed=args.seed,
                          fixture_review=read(args.fixture_review) if args.fixture_review else None,
                          acceptance=acceptance)
        with args.output.open('x', encoding='utf-8') as stream:
            stream.write(canonical_json(plan) + '\n')
            stream.flush()
            os.fsync(stream.fileno())
        print(canonical_json({'plan_sha256': plan['plan_sha256'],
                              'planned_model_calls': plan['planned_model_calls'], 'tool_executions': 0}))
        return 0
    plan = validate_plan(read(args.plan), bundle)
    if args.output.exists():
        raise ValueError('Output exists; no implicit resume or overwrite')
    # Credentials enter only here and never enter a profile, request, or artifact.
    from dotenv import dotenv_values
    from openai import OpenAI
    values = {**dotenv_values(args.env_file), **os.environ}
    key = values.get('OPENAI_API_KEY') or values.get('DASHSCOPE_API_KEY')
    if not key or not str(key).strip():
        raise ValueError('Missing API key')
    profile = plan['profile']
    with OpenAI(api_key=key, base_url=profile['base_url'], timeout=profile['timeout_seconds'], max_retries=0) as client:
        summary = execute(plan, bundle, args.output, client, mode='live')
    print(canonical_json(summary))
    return 0 if summary['mechanically_clean'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
