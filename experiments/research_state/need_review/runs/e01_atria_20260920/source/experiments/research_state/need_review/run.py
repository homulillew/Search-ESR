"""Prepare, plan, execute, or review E0. Only the execute command calls an API."""
import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import random
import re
import shutil
import subprocess
import sys
import time

from .accounting import inspect_usage
from .checkpoint import canonical_json, digest, extract_checkpoint, load_checkpoint
from .node import build_actor_request, build_review_request, classify_actor_response, validate_review
from .integrity import (
    HARNESS_REVISION, MEMO_MODES, atomic_json, branch_exit_code, normalize_base_url,
    read_events, seal_plan, source_hashes, strict_json, validate_actor_shape,
    verify_plan, visible_reference_index,
)

from .integrity import REVIEW_CONTRACTS, review_prompt_key, branch_settings

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[2]
ARMS = ('A', 'B', 'C')
TOKEN_KEYS = ('prompt_tokens', 'completion_tokens', 'total_tokens')


def now():
    return datetime.now(timezone.utc).isoformat()


def read_json(path):
    return strict_json(Path(path).read_text(encoding='utf-8'))


def write_json(path, value):
    atomic_json(path, value)


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


def settings_dict(*, repeats=2, seed=20260919, review_max_tokens=512, model=None,
                  sdk_max_retries=0, memo_mode='legacy_text', expected_base_url=None,
                  review_contract='baseline', comparison='abc'):
    if type(repeats) is not int or repeats < 1 or type(seed) is not int:
        raise ValueError('Positive integer repeats and integer schedule seed required')
    if memo_mode not in MEMO_MODES:
        raise ValueError('Unknown memo handoff mode')
    if comparison not in ('abc', 'source_contract_pair'):
        raise ValueError('Unknown comparison')
    if comparison == 'source_contract_pair' and (memo_mode != 'legacy_text' or review_contract != 'baseline'):
        raise ValueError('Paired source-contract comparison fixes legacy handoff and assigns both contracts')
    if review_contract not in REVIEW_CONTRACTS:
        raise ValueError('Unknown review contract')
    if review_contract != 'baseline' and memo_mode != 'legacy_text':
        raise ValueError('Source-contract and indexed-handoff changes require separate experiments')
    if expected_base_url is not None:
        expected_base_url = normalize_base_url(expected_base_url)
    if type(review_max_tokens) is not int or review_max_tokens < 1:
        raise ValueError('review-max-tokens must be positive')
    if type(sdk_max_retries) is not int or sdk_max_retries < 0:
        raise ValueError('sdk-max-retries cannot be negative')
    if model is not None and (not isinstance(model, str) or not model.strip()):
        raise ValueError('model override cannot be blank')
    return {'repeats': repeats, 'seed': seed, 'review_max_tokens': review_max_tokens,
            'model_override': model, 'sdk_max_retries': sdk_max_retries,
            'memo_mode': memo_mode, 'expected_base_url': expected_base_url,
            'review_contract': review_contract, 'comparison': comparison,
            'execute_tools': False, 'actor_decisions_per_branch': 1}


def load_prompts():
    return {name: (PACKAGE / 'prompts' / f'{name}.txt').read_text(encoding='utf-8')
            for name in ('generic_review', 'need_review', 'memo', 'memo_indexed', 'need_review_source_grounded')}


def memo_prompt(settings, prompts):
    return prompts['memo_indexed' if settings.get('memo_mode') == 'indexed_json_v1' else 'memo']


def build_plan(prepared, settings, prompts=None, *, loaded=None):
    manifest, checkpoints = loaded if loaded is not None else load_prepared(prepared)
    prompts = prompts or load_prompts()
    schedule = make_schedule(checkpoints, settings['repeats'], settings['seed'])
    if settings.get('comparison') == 'source_contract_pair':
        rng = random.Random(settings['seed'])
        paired = []
        for item in (x for x in schedule if x['arm'] == 'C'):
            contracts = list(REVIEW_CONTRACTS)
            rng.shuffle(contracts)
            for contract in contracts:
                paired.append(dict(item, review_contract=contract,
                                   sample_id=item['sample_id'] + '__' + contract))
        schedule = paired
    # Validate every request shape before the first paid request, including the
    # wrapper and reserved extra_body fields. No context truncation is applied.
    for checkpoint in checkpoints.values():
        validate_actor_shape(checkpoint['request'])
        visible_reference_index(checkpoint)
        build_actor_request(checkpoint, 'preflight note', memo_prompt(settings, prompts),
                            model=settings['model_override'], memo_mode=settings.get('memo_mode', 'legacy_text'))
        contracts = REVIEW_CONTRACTS if settings.get('comparison') == 'source_contract_pair' else (settings.get('review_contract', 'baseline'),)
        for contract in contracts:
            for arm in ('B', 'C'):
                key = review_prompt_key(arm, contract)
                build_review_request(checkpoint, arm, prompts[key], max_tokens=settings['review_max_tokens'],
                                     model=settings['model_override'])
    reviewers = sum(item['arm'] != 'A' for item in schedule)
    return seal_plan({'schema_version': 'need_review_plan_v1', 'harness_revision': HARNESS_REVISION,
            'implementation_sha256': source_hashes(PACKAGE),
            'settings': deepcopy(settings), 'schedule': schedule,
            'scheduled_actor_requests': len(schedule), 'scheduled_review_requests': reviewers,
            'scheduled_logical_requests': len(schedule) + reviewers,
            'tool_executions': 0, 'prepared_manifest_sha256': digest(manifest),
            'prompt_sha256': {key: hashlib.sha256(value.encode()).hexdigest() for key, value in prompts.items()},
            'checkpoints': [{'checkpoint_id': key, 'request_sha256': cp['request_sha256'],
                             'tool_version': cp['source']['tool_version'],
                             'captured_model': cp['request']['model'],
                             'effective_model': settings['model_override'] or cp['request']['model'],
                             'request_utf8_bytes': len(canonical_json(cp['request']).encode())}
                            for key, cp in checkpoints.items()]})


class CallLog:
    def __init__(self, path):
        self.path, self.seq, self.requests = Path(path), 0, 0

    def emit(self, kind, stage, **fields):
        self.seq += 1
        event = {'seq': self.seq, 'time': now(), 'kind': kind, 'stage': stage, **fields}
        with self.path.open('a', encoding='utf-8') as stream:
            stream.write(canonical_json(event) + '\n')
            stream.flush()
            os.fsync(stream.fileno())

    def call(self, client, stage, request):
        # A broken adapter is a harness defect, not a failed language-model judgment.
        try:
            create = client.chat.completions.create
        except (AttributeError, TypeError):
            raise TypeError('Client lacks the Chat Completions create contract') from None
        if not callable(create):
            raise TypeError('Client create is not callable')
        self.emit('request', stage, request=deepcopy(request))
        self.requests += 1
        start = time.monotonic()
        try:
            response = create(**deepcopy(request))
        except BaseException as exc:
            # Exception strings/HTTP bodies can contain credentials or headers.
            error = {'error_type': type(exc).__name__, 'elapsed_seconds': time.monotonic() - start}
            code = getattr(exc, 'status_code', None)
            if type(code) is int:
                error['status_code'] = code
            self.emit('error', stage, **error)
            if isinstance(exc, (KeyboardInterrupt, SystemExit, TypeError, AttributeError)):
                raise
            return {'status': 'api_error', 'request': request, 'response': None, 'usage': None, **error}
        try:
            raw = deepcopy(response) if isinstance(response, dict) else response.model_dump(mode='json')
        except (TypeError, AttributeError):
            self.emit('error', stage, error_type='AdapterResponseError',
                      elapsed_seconds=time.monotonic() - start)
            raise TypeError('Client response cannot be serialized as a completion') from None
        elapsed = time.monotonic() - start
        self.emit('response', stage, response=raw, elapsed_seconds=elapsed)
        return {'status': 'ok', 'request': request, 'response': raw,
                'elapsed_seconds': elapsed, 'usage': raw.get('usage') if isinstance(raw, dict) else None}


def run_branch(checkpoint, item, client, directory, settings, prompts):
    settings = branch_settings(settings, item)
    directory.mkdir(parents=True, exist_ok=False)
    log = CallLog(directory / 'events.jsonl')
    result = {**item, 'status': 'running', 'started_at': now(), 'review': None, 'actor': None,
              'request_sha256': checkpoint['request_sha256'], 'memo_injected': False}
    review_text = None
    try:
        if item['arm'] != 'A':
            key = review_prompt_key(item['arm'], settings.get('review_contract', 'baseline'))
            request = build_review_request(checkpoint, item['arm'], prompts[key],
                                           max_tokens=settings['review_max_tokens'], model=settings['model_override'])
            review = log.call(client, 'review', request)
            # Preserve the paid response even if local validation crashes.
            result['review'] = review
            if review['status'] == 'ok':
                validation = validate_review(review['response'], item['arm'], {ref['ref'] for ref in checkpoint['references']})
                review.update(validation)
                if validation['valid']:
                    review_text = validation['raw_text']
            else:
                review.update(valid=False, raw_text=None, parsed=None, errors=['review_api_error'])
            result['review'] = review
            log.emit('validation', 'review', status=review['status'], errors=review['errors'])
        request = build_actor_request(checkpoint, review_text, memo_prompt(settings, prompts),
                                      model=settings['model_override'],
                                      memo_mode=settings.get('memo_mode', 'legacy_text'))
        result['memo_injected'] = review_text is not None
        actor = log.call(client, 'actor', request)
        result['actor'] = actor
        if actor['status'] == 'ok':
            actor['classification'] = classify_actor_response(actor['response'], request)
            result['status'] = 'completed'
        else:
            result['status'] = 'actor_error'
    except (KeyboardInterrupt, SystemExit):
        result['status'] = 'interrupted'
        raise
    except Exception as exc:
        result['status'] = 'harness_error'
        result['harness_error_type'] = type(exc).__name__
        raise
    finally:
        result['logical_requests'] = log.requests
        result['finished_at'] = now()
        write_json(directory / 'result.json', result)
    return result


def summarize(directory, schedule, *, include_conditions=True, write_output=True):
    statuses, review_statuses, actor_kinds = Counter(), Counter(), Counter()
    actor_protocol = Counter()
    usage = {stage: Counter() for stage in ('review', 'actor')}
    requests = responses = api_errors = missing_usage = inconsistent_usage = 0
    missing_fields = {stage: Counter() for stage in usage}
    record_errors = []
    by_arm = {arm: {'scheduled': 0, 'branch_statuses': Counter(), 'logical_requests': 0,
                    'reported_usage': Counter(), 'fallbacks': 0,
                    'review_statuses': Counter(), 'actor_protocol_statuses': Counter(),
                    'elapsed_seconds_by_stage': Counter()} for arm in ARMS}
    for item in schedule:
        branch = directory / 'branches' / item['sample_id']
        try:
            result = read_json(branch / 'result.json') if (branch / 'result.json').exists() else None
            if result is not None and (
                    not isinstance(result, dict) or not isinstance(result.get('status'), str)
                    or any(result.get(k) != item[k] for k in ('sample_id', 'checkpoint_id', 'arm', 'repeat_id'))
                    or any(result.get(k) is not None and not isinstance(result[k], dict) for k in ('review', 'actor'))):
                raise ValueError('Malformed or mismatched branch result')
        except (ValueError, OSError, UnicodeError):
            result = None
            record_errors.append({'sample_id': item['sample_id'], 'error': 'invalid_result_json'})
        arm_stats = by_arm[item['arm']]
        arm_stats['scheduled'] += 1
        arm_stats['branch_statuses'][result['status'] if result else (
            'uncompleted' if (branch / 'events.jsonl').exists() else 'not_run')] += 1
        if result and item['arm'] != 'A' and (result.get('actor') or {}).get('request') is not None:
            arm_stats['fallbacks'] += result.get('memo_injected') is False
        statuses[result['status'] if result else ('uncompleted' if (branch / 'events.jsonl').exists() else 'not_run')] += 1
        if result:
            review_status = (result.get('review') or {}).get('status', 'not_applicable' if item['arm'] == 'A' else 'not_observed')
            if not isinstance(review_status, str):
                record_errors.append({'sample_id': item['sample_id'], 'error': 'invalid_review_status'})
                review_status = 'invalid_record'
            review_statuses[review_status] += 1
            arm_stats['review_statuses'][review_status] += 1
            classification = ((result.get('actor') or {}).get('classification') or {})
            if not isinstance(classification, dict):
                record_errors.append({'sample_id': item['sample_id'], 'error': 'invalid_actor_classification'})
                classification = {}
            response_kind = classification.get('response_kind', 'not_observed')
            if not isinstance(response_kind, str):
                record_errors.append({'sample_id': item['sample_id'], 'error': 'invalid_actor_kind'})
                response_kind = 'invalid_record'
            actor_kinds[response_kind] += 1
            compatible = classification.get('protocol_compatible')
            protocol_status = 'compatible' if compatible is True else 'incompatible' if compatible is False else 'not_observed'
            actor_protocol[protocol_status] += 1
            arm_stats['actor_protocol_statuses'][protocol_status] += 1
        events, issues = read_events(branch / 'events.jsonl')
        record_errors.extend({'sample_id': item['sample_id'], 'error': issue} for issue in issues)
        for event in events:
            requests += event.get('kind') == 'request'
            arm_stats['logical_requests'] += event.get('kind') == 'request'
            api_errors += event.get('kind') == 'error'
            elapsed = event.get('elapsed_seconds')
            if event.get('kind') in ('response', 'error') and type(elapsed) in (float, int) and elapsed >= 0:
                arm_stats['elapsed_seconds_by_stage'][event.get('stage', 'unknown')] += elapsed
            if event.get('kind') == 'response':
                responses += 1
                raw = event.get('response')
                reported = raw.get('usage') if isinstance(raw, dict) else None
                stage = event.get('stage')
                inspected = inspect_usage(reported)
                if stage not in usage:
                    missing_usage += 1
                    record_errors.append({'sample_id': item['sample_id'], 'error': 'unknown_usage_stage'})
                    continue
                missing_usage += bool(inspected['missing'])
                inconsistent_usage += inspected['inconsistent']
                missing_fields[stage].update(inspected['missing'])
                # Keep valid partial counts as reported, without inventing totals.
                # A complete-looking but inconsistent report is still not a bill.
                usage[stage].update(inspected['known'])
                arm_stats['reported_usage'].update(inspected['known'])
    summary = {'scheduled_branches': len(schedule), 'branch_statuses': dict(statuses),
               'review_statuses': dict(review_statuses), 'actor_response_kinds': dict(actor_kinds),
               'actor_protocol_statuses': dict(actor_protocol),
               'logical_requests_attempted': requests, 'responses_received': responses,
               'failed_requests_with_unknown_cost': api_errors, 'responses_missing_usage': missing_usage,
               'responses_inconsistent_usage': inconsistent_usage,
               'missing_usage_fields_by_stage': {key: dict(value) for key, value in missing_fields.items()},
               'reported_usage_by_stage': {key: dict(value) for key, value in usage.items()},
               'tool_executions': 0, 'semantic_evaluation': 'not_evaluated',
               'record_errors': record_errors, 'by_arm': by_arm}
    summary['mechanically_clean'] = branch_exit_code(summary) == 0
    summary['cost_accounting_complete'] = not (api_errors or missing_usage or inconsistent_usage
                                                or record_errors or requests != responses)
    if include_conditions and any('review_contract' in item for item in schedule):
        summary['by_contract'] = {
            contract: summarize(directory, [item for item in schedule if item.get('review_contract') == contract],
                                include_conditions=False, write_output=False)
            for contract in REVIEW_CONTRACTS}
    if write_output:
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


def execute(prepared, output, *, client, settings, transport=None, approved_plan=None):
    prompts = load_prompts()
    # One validated input snapshot supplies both the plan and actual calls.
    prepared_manifest, checkpoints = load_prepared(prepared)
    plan = build_plan(prepared, settings, prompts, loaded=(prepared_manifest, checkpoints))
    if approved_plan is not None:
        verify_plan(approved_plan, plan)
    expected_base = settings.get('expected_base_url')
    if expected_base and normalize_base_url((transport or {}).get('base_url')) != expected_base:
        raise ValueError('Actual API base differs from the approved experiment endpoint')
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    (output / 'checkpoints').mkdir()
    (output / 'prompts').mkdir()
    for key, value in checkpoints.items():
        write_json(output / 'checkpoints' / f'{key}.json', value)
    for key, value in prompts.items():
        (output / 'prompts' / f'{key}.txt').write_text(value, encoding='utf-8')
    manifest = {**plan, 'schema_version': 'need_review_run_v1', 'created_at': now(),
                'prepared_manifest': prepared_manifest, 'transport': transport or {},
                'plan_approved': approved_plan is not None, 'approved_plan': approved_plan,
                **code_snapshot(output)}
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
    parser.add_argument('--memo-mode', choices=MEMO_MODES, default='legacy_text')
    parser.add_argument('--review-contract', choices=REVIEW_CONTRACTS, default='baseline')
    parser.add_argument('--comparison', choices=('abc', 'source_contract_pair'), default='abc')
    parser.add_argument('--expected-base-url', help='Pin a credential-free provider API base; required for paid CLI execution')


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
            p.add_argument('--plan-file', type=Path, help='Previously saved and reviewed plan; required before paid calls')
        else:
            p.add_argument('--output', type=Path, help='New file for the sealed plan (never overwritten)')
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
        result = export_review(args.run_dir, args.output)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2 if result['cards_with_export_errors'] else 0
    settings = settings_dict(repeats=args.repeats, seed=args.seed, review_max_tokens=args.review_max_tokens,
                             model=args.model, sdk_max_retries=args.sdk_max_retries,
                             memo_mode=args.memo_mode, expected_base_url=args.expected_base_url,
                             review_contract=args.review_contract, comparison=args.comparison)
    plan = build_plan(args.prepared, settings)
    if args.command == 'plan':
        if args.output:
            with args.output.open('x', encoding='utf-8') as stream:
                stream.write(canonical_json(plan) + '\n')
                stream.flush()
                os.fsync(stream.fileno())
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        return
    if args.output.exists():
        parser.error('Output exists; use a new run directory. Resume is intentionally not implemented.')
    if args.plan_file is None or settings['expected_base_url'] is None:
        parser.error('Paid execute requires --plan-file and --expected-base-url; review a sealed plan first')
    approved_plan = read_json(args.plan_file)
    verify_plan(approved_plan, plan)
    # These imports and credential loading are reachable only via execute.
    from llm_chat.client import Config
    from openai import OpenAI
    config = Config.load(args.env_file, model=args.model or plan['checkpoints'][0]['captured_model'])
    if normalize_base_url(config.base_url) != settings['expected_base_url']:
        parser.error('Configured API base differs from the approved --expected-base-url')
    with OpenAI(api_key=config.api_key, base_url=config.base_url, timeout=config.timeout,
                max_retries=settings['sdk_max_retries']) as client:
        result = execute(args.prepared, args.output, client=client, settings=settings,
                         approved_plan=approved_plan,
                         transport={'base_url': config.base_url, 'timeout_seconds': config.timeout,
                                    'sdk_max_retries': settings['sdk_max_retries'],
                                    'openai_version': importlib.metadata.version('openai')})
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return branch_exit_code(result)


if __name__ == '__main__':
    raise SystemExit(main())
