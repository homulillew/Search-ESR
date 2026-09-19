"""Prepare, plan, execute, or review E0. Only the execute command calls an API."""
import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import random
import re
import shutil
import subprocess
import sys
import time

from .checkpoint import canonical_json, digest, extract_checkpoint, load_checkpoint
from .node import build_actor_request, build_review_request, classify_actor_response, validate_review

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[2]
ARMS = ('A', 'B', 'C')
TOKEN_KEYS = ('prompt_tokens', 'completion_tokens', 'total_tokens')


def now():
    return datetime.now(timezone.utc).isoformat()


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write_json(path, value):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    temporary.replace(path)


def relative_file(root, relative):
    if not isinstance(relative, str) or Path(relative).is_absolute() or '..' in Path(relative).parts:
        raise ValueError('Expected a repository-relative file path')
    path = (Path(root) / relative).resolve()
    if not path.is_relative_to(Path(root).resolve()):
        raise ValueError('File escapes its input directory')
    return path


def git_blob_sha(path):
    """Hash bytes for provenance, without interpreting any future log records."""
    sha = hashlib.sha1(b'blob ' + str(path.stat().st_size).encode('ascii') + b'\0')
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            sha.update(chunk)
    return sha.hexdigest()


def prepare(selection_path, repo_root, output):
    selection = read_json(selection_path)
    if selection.get('schema_version') != 'need_review_selection_v1':
        raise ValueError('Unsupported checkpoint selection schema')
    commit = selection.get('source_commit', '')
    if not re.fullmatch(r'[0-9a-f]{40}', commit):
        raise ValueError('Selection must pin a full source commit SHA')
    cases = selection.get('checkpoints')
    if not isinstance(cases, list) or not cases:
        raise ValueError('Selection must contain checkpoints')
    prepared, seen = [], set()
    for case in cases:
        identifier = case.get('checkpoint_id', '')
        if not re.fullmatch(r'[A-Za-z0-9_-]+', identifier) or identifier in seen:
            raise ValueError('Checkpoint IDs must be unique path-safe identifiers')
        seen.add(identifier)
        path = relative_file(repo_root, case['events_path'])
        expected_blob = case.get('events_blob_sha', '')
        if not re.fullmatch(r'[0-9a-f]{40}', expected_blob) or git_blob_sha(path) != expected_blob:
            raise ValueError(f'Source blob differs from selection: {identifier}')
        checkpoint = extract_checkpoint(path, case['request_seq'], checkpoint_id=identifier,
                                        source_commit=commit, tool_version=case['tool_version'],
                                        parent_run=str(Path(case['events_path']).parent))
        checkpoint['source']['events_path'] = case['events_path']
        checkpoint['source']['events_blob_sha'] = expected_blob
        checkpoint['checkpoint_sha256'] = digest({k: v for k, v in checkpoint.items() if k != 'checkpoint_sha256'})
        prepared.append(checkpoint)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    (output / 'checkpoints').mkdir()
    entries = []
    for checkpoint in prepared:
        relative = f"checkpoints/{checkpoint['checkpoint_id']}.json"
        write_json(output / relative, checkpoint)
        entries.append({'checkpoint_id': checkpoint['checkpoint_id'], 'file': relative,
                        'checkpoint_sha256': checkpoint['checkpoint_sha256']})
    manifest = {'schema_version': 'need_review_prepared_v1', 'created_at': now(),
                'selection': selection, 'selection_sha256': digest(selection), 'checkpoints': entries}
    write_json(output / 'manifest.json', manifest)
    return manifest


def load_prepared(directory):
    directory = Path(directory)
    manifest = read_json(directory / 'manifest.json')
    if manifest.get('schema_version') != 'need_review_prepared_v1':
        raise ValueError('Unsupported prepared schema')
    if digest(manifest['selection']) != manifest['selection_sha256']:
        raise ValueError('Selection hash mismatch')
    checkpoints = {}
    for item in manifest['checkpoints']:
        checkpoint = load_checkpoint(relative_file(directory, item['file']))
        identifier = item['checkpoint_id']
        if identifier in checkpoints or checkpoint['checkpoint_id'] != identifier:
            raise ValueError('Duplicate or inconsistent prepared checkpoint')
        if checkpoint['checkpoint_sha256'] != item['checkpoint_sha256']:
            raise ValueError('Prepared checkpoint differs from manifest')
        checkpoints[identifier] = checkpoint
    selected = [case['checkpoint_id'] for case in manifest['selection']['checkpoints']]
    if list(checkpoints) != selected or not checkpoints:
        raise ValueError('Prepared checkpoints differ from frozen selection')
    for case in manifest['selection']['checkpoints']:
        source = checkpoints[case['checkpoint_id']]['source']
        expected = {key: case[key] for key in ('events_path', 'events_blob_sha', 'request_seq', 'tool_version')}
        expected['source_commit'] = manifest['selection']['source_commit']
        if any(source.get(key) != value for key, value in expected.items()):
            raise ValueError('Checkpoint provenance differs from frozen selection')
    return manifest, checkpoints


def make_schedule(checkpoint_ids, repeats=2, seed=20260919):
    if type(repeats) is not int or repeats < 1:
        raise ValueError('repeats must be a positive integer')
    rng = random.Random(seed)
    schedule = []
    for repeat in range(1, repeats + 1):
        cases = list(checkpoint_ids)
        rng.shuffle(cases)
        orders = {}
        for identifier in cases:
            orders[identifier] = list(ARMS)
            rng.shuffle(orders[identifier])
        for arm_slot in range(3):
            for identifier in cases:
                arm = orders[identifier][arm_slot]
                schedule.append({'sample_id': f'{identifier}__{arm}__r{repeat}',
                                 'checkpoint_id': identifier, 'arm': arm, 'repeat_id': repeat})
    return schedule


def settings_dict(*, repeats=2, seed=20260919, review_max_tokens=512, model=None, sdk_max_retries=0):
    if type(review_max_tokens) is not int or review_max_tokens < 1:
        raise ValueError('review-max-tokens must be positive')
    if type(sdk_max_retries) is not int or sdk_max_retries < 0:
        raise ValueError('sdk-max-retries cannot be negative')
    if model is not None and not model.strip():
        raise ValueError('model override cannot be blank')
    return {'repeats': repeats, 'seed': seed, 'review_max_tokens': review_max_tokens,
            'model_override': model, 'sdk_max_retries': sdk_max_retries,
            'execute_tools': False, 'actor_decisions_per_branch': 1}


def load_prompts():
    return {name: (PACKAGE / 'prompts' / f'{name}.txt').read_text(encoding='utf-8')
            for name in ('generic_review', 'need_review', 'memo')}


def build_plan(prepared, settings, prompts=None):
    manifest, checkpoints = load_prepared(prepared)
    prompts = prompts or load_prompts()
    schedule = make_schedule(checkpoints, settings['repeats'], settings['seed'])
    # Validate every request shape before the first paid request, including the
    # wrapper and reserved extra_body fields. No context truncation is applied.
    for checkpoint in checkpoints.values():
        build_actor_request(checkpoint, 'preflight note', prompts['memo'], model=settings['model_override'])
        for arm, key in (('B', 'generic_review'), ('C', 'need_review')):
            build_review_request(checkpoint, arm, prompts[key], max_tokens=settings['review_max_tokens'],
                                 model=settings['model_override'])
    reviewers = sum(item['arm'] != 'A' for item in schedule)
    return {'schema_version': 'need_review_plan_v1', 'settings': settings, 'schedule': schedule,
            'scheduled_actor_requests': len(schedule), 'scheduled_review_requests': reviewers,
            'scheduled_logical_requests': len(schedule) + reviewers,
            'tool_executions': 0, 'prepared_manifest_sha256': digest(manifest),
            'prompt_sha256': {key: hashlib.sha256(value.encode()).hexdigest() for key, value in prompts.items()},
            'checkpoints': [{'checkpoint_id': key, 'request_sha256': cp['request_sha256'],
                             'tool_version': cp['source']['tool_version'],
                             'captured_model': cp['request']['model'],
                             'effective_model': settings['model_override'] or cp['request']['model'],
                             'request_utf8_bytes': len(canonical_json(cp['request']).encode())}
                            for key, cp in checkpoints.items()]}


class CallLog:
    def __init__(self, path):
        self.path, self.seq, self.requests = Path(path), 0, 0

    def emit(self, kind, stage, **fields):
        self.seq += 1
        event = {'seq': self.seq, 'time': now(), 'kind': kind, 'stage': stage, **fields}
        with self.path.open('a', encoding='utf-8') as stream:
            stream.write(canonical_json(event) + '\n')
            stream.flush()

    def call(self, client, stage, request):
        self.emit('request', stage, request=deepcopy(request))
        self.requests += 1
        start = time.monotonic()
        try:
            response = client.chat.completions.create(**deepcopy(request))
            raw = deepcopy(response) if isinstance(response, dict) else response.model_dump(mode='json')
        except BaseException as exc:
            # Exception strings/HTTP bodies can contain credentials or headers.
            error = {'error_type': type(exc).__name__, 'elapsed_seconds': time.monotonic() - start}
            code = getattr(exc, 'status_code', None)
            if type(code) is int:
                error['status_code'] = code
            self.emit('error', stage, **error)
            if isinstance(exc, (KeyboardInterrupt, SystemExit)):
                raise
            return {'status': 'api_error', 'request': request, 'response': None, 'usage': None, **error}
        elapsed = time.monotonic() - start
        self.emit('response', stage, response=raw, elapsed_seconds=elapsed)
        return {'status': 'ok', 'request': request, 'response': raw,
                'elapsed_seconds': elapsed, 'usage': raw.get('usage') if isinstance(raw, dict) else None}


def run_branch(checkpoint, item, client, directory, settings, prompts):
    directory.mkdir(parents=True, exist_ok=False)
    log = CallLog(directory / 'events.jsonl')
    result = {**item, 'status': 'interrupted', 'started_at': now(), 'review': None, 'actor': None,
              'request_sha256': checkpoint['request_sha256'], 'memo_injected': False}
    review_text = None
    try:
        if item['arm'] != 'A':
            key = 'generic_review' if item['arm'] == 'B' else 'need_review'
            request = build_review_request(checkpoint, item['arm'], prompts[key],
                                           max_tokens=settings['review_max_tokens'], model=settings['model_override'])
            review = log.call(client, 'review', request)
            if review['status'] == 'ok':
                validation = validate_review(review['response'], item['arm'], {ref['ref'] for ref in checkpoint['references']})
                review.update(validation)
                if validation['valid']:
                    review_text = validation['raw_text']
            else:
                review.update(valid=False, raw_text=None, parsed=None, errors=['review_api_error'])
            result['review'] = review
            log.emit('validation', 'review', status=review['status'], errors=review['errors'])
        request = build_actor_request(checkpoint, review_text, prompts['memo'], model=settings['model_override'])
        result['memo_injected'] = review_text is not None
        actor = log.call(client, 'actor', request)
        result['actor'] = actor
        if actor['status'] == 'ok':
            actor['classification'] = classify_actor_response(actor['response'], request)
            result['status'] = 'completed'
        else:
            result['status'] = 'actor_error'
    finally:
        result['logical_requests'] = log.requests
        result['finished_at'] = now()
        write_json(directory / 'result.json', result)
    return result


def summarize(directory, schedule):
    statuses, review_statuses, actor_kinds = Counter(), Counter(), Counter()
    actor_protocol = Counter()
    usage = {stage: Counter() for stage in ('review', 'actor')}
    requests = responses = api_errors = missing_usage = 0
    for item in schedule:
        branch = directory / 'branches' / item['sample_id']
        result = read_json(branch / 'result.json') if (branch / 'result.json').exists() else None
        statuses[result['status'] if result else ('uncompleted' if (branch / 'events.jsonl').exists() else 'not_run')] += 1
        if result:
            review_statuses[(result.get('review') or {}).get('status', 'not_applicable' if item['arm'] == 'A' else 'not_observed')] += 1
            classification = ((result.get('actor') or {}).get('classification') or {})
            actor_kinds[classification.get('response_kind', 'not_observed')] += 1
            compatible = classification.get('protocol_compatible')
            actor_protocol['compatible' if compatible is True else 'incompatible' if compatible is False else 'not_observed'] += 1
        if (branch / 'events.jsonl').exists():
            for line in (branch / 'events.jsonl').read_text(encoding='utf-8').splitlines():
                event = json.loads(line)
                requests += event['kind'] == 'request'
                api_errors += event['kind'] == 'error'
                if event['kind'] == 'response':
                    responses += 1
                    raw = event['response']
                    reported = raw.get('usage') if isinstance(raw, dict) else None
                    if not isinstance(reported, dict):
                        missing_usage += 1
                    else:
                        for key in TOKEN_KEYS:
                            if type(reported.get(key)) is int:
                                usage[event['stage']][key] += reported[key]
    summary = {'scheduled_branches': len(schedule), 'branch_statuses': dict(statuses),
               'review_statuses': dict(review_statuses), 'actor_response_kinds': dict(actor_kinds),
               'actor_protocol_statuses': dict(actor_protocol),
               'logical_requests_attempted': requests, 'responses_received': responses,
               'failed_requests_with_unknown_cost': api_errors, 'responses_missing_usage': missing_usage,
               'reported_usage_by_stage': {key: dict(value) for key, value in usage.items()},
               'tool_executions': 0, 'semantic_evaluation': 'not_evaluated'}
    write_json(directory / 'summary.json', summary)
    return summary


def code_snapshot(output):
    paths = sorted(PACKAGE.glob('*.py')) + sorted(PACKAGE.glob('*.md')) + sorted(PACKAGE.glob('*.json'))
    paths += sorted((PACKAGE / 'prompts').glob('*.txt'))
    hashes = {}
    for path in paths:
        relative = path.relative_to(ROOT)
        dest = output / 'source' / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dest)
        hashes[str(relative)] = hashlib.sha256(path.read_bytes()).hexdigest()
    commit = subprocess.run(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], capture_output=True, text=True)
    return {'source_sha256': hashes, 'git_head': commit.stdout.strip() if commit.returncode == 0 else None,
            'python': sys.version}


def execute(prepared, output, *, client, settings, transport=None):
    prompts = load_prompts()
    plan = build_plan(prepared, settings, prompts)
    prepared_manifest, checkpoints = load_prepared(prepared)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    (output / 'checkpoints').mkdir()
    (output / 'prompts').mkdir()
    for key, value in checkpoints.items():
        write_json(output / 'checkpoints' / f'{key}.json', value)
    for key, value in prompts.items():
        (output / 'prompts' / f'{key}.txt').write_text(value, encoding='utf-8')
    manifest = {**plan, 'schema_version': 'need_review_run_v1', 'created_at': now(),
                'prepared_manifest': prepared_manifest, 'transport': transport or {}, **code_snapshot(output)}
    write_json(output / 'manifest.json', manifest)
    try:
        for item in plan['schedule']:
            print(f"E0 {item['sample_id']}", flush=True)
            run_branch(checkpoints[item['checkpoint_id']], item, client,
                       output / 'branches' / item['sample_id'], settings, prompts)
    finally:
        summary = summarize(output, plan['schedule'])
    return summary


def add_run_settings(parser):
    parser.add_argument('--prepared', type=Path, required=True)
    parser.add_argument('--repeats', type=int, default=2)
    parser.add_argument('--seed', type=int, default=20260919, help='Schedule seed only; does not override model sampling')
    parser.add_argument('--review-max-tokens', type=int, default=512)
    parser.add_argument('--model', help='Explicit, recorded override for both Actor and Reviewer')
    parser.add_argument('--sdk-max-retries', type=int, default=0)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('prepare', help='Offline: verify frozen log blobs and extract checkpoints')
    p.add_argument('--checkpoints', type=Path, default=PACKAGE / 'checkpoints.json')
    p.add_argument('--repo-root', type=Path, default=ROOT)
    p.add_argument('--output', type=Path, required=True)
    for name in ('plan', 'execute'):
        p = sub.add_parser(name, help='Offline request schedule' if name == 'plan' else 'Real model calls; zero tool executions')
        add_run_settings(p)
        if name == 'execute':
            p.add_argument('--output', type=Path, required=True)
            p.add_argument('--env-file', type=Path, default=ROOT / '.env')
    p = sub.add_parser('review', help='Offline: export review cards for every scheduled branch')
    p.add_argument('--run-dir', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == 'prepare':
        result = prepare(args.checkpoints, args.repo_root, args.output)
        print(json.dumps({'prepared': str(args.output), 'checkpoints': result['checkpoints']}, ensure_ascii=False, indent=2))
        return
    if args.command == 'review':
        from .report import export_review
        print(json.dumps(export_review(args.run_dir, args.output), ensure_ascii=False, indent=2))
        return
    settings = settings_dict(repeats=args.repeats, seed=args.seed, review_max_tokens=args.review_max_tokens,
                             model=args.model, sdk_max_retries=args.sdk_max_retries)
    plan = build_plan(args.prepared, settings)
    if args.command == 'plan':
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        return
    if args.output.exists():
        parser.error('Output exists; use a new run directory. Resume is intentionally not implemented.')
    # These imports and credential loading are reachable only via execute.
    from llm_chat.client import Config
    from openai import OpenAI
    config = Config.load(args.env_file, model=args.model or plan['checkpoints'][0]['captured_model'])
    with OpenAI(api_key=config.api_key, base_url=config.base_url, timeout=config.timeout,
                max_retries=settings['sdk_max_retries']) as client:
        result = execute(args.prepared, args.output, client=client, settings=settings,
                         transport={'base_url': config.base_url, 'timeout_seconds': config.timeout,
                                    'sdk_max_retries': settings['sdk_max_retries'],
                                    'openai_version': importlib.metadata.version('openai')})
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
