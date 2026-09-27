"""E1-only runner. Default is offline; explicit paid authorization is required."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import threading
import time

from .prepare import ARMS, COHERENCE, PREMISE, OLD, P, ROOT, digest, git, read, relative, sha, write

DIMENSIONS = ('Relevant', 'Unresolved', 'Grounded', 'PremiseClosed', 'Coherent', 'Actionable')

def now():
    return datetime.now(timezone.utc).isoformat()

def validate_need(value):
    return (isinstance(value, dict) and set(value) == {'decision', 'need'}
            and value['decision'] == 'research' and isinstance(value['need'], str) and bool(value['need'].strip()))

def audit_prepared(require_committed=True):
    manifest = read(P / 'FREEZE.json')
    head = git('rev-parse', 'HEAD')
    for name, expected in manifest['files'].items():
        if sha(ROOT / name) != expected:
            raise ValueError('Frozen file changed: ' + name)
        if require_committed:
            committed = subprocess.check_output(['git', 'show', head + ':' + name], cwd=ROOT)
            if committed != (ROOT / name).read_bytes():
                raise ValueError('Frozen file is not committed: ' + name)
    if require_committed:
        committed = subprocess.check_output(['git', 'show', head + ':' + relative(P / 'FREEZE.json')], cwd=ROOT)
        if committed != (P / 'FREEZE.json').read_bytes():
            raise ValueError('Manifest not committed')
    history = read(P / 'analysis/HISTORICAL_HASHES.json')
    for name, expected in history.items():
        if sha(ROOT / name) != expected:
            raise ValueError('Historical file changed: ' + name)
    bank = {s['state_id']: s for s in read(P / 'e1_need/BANK.json')}
    schedule = read(P / 'e1_need/SCHEDULE.json')
    old_jobs = {j['input_id']: j for j in read(OLD / 'need/confirmation/JOBS.json')}
    base = (OLD / 'need/prompts/B5.txt').read_text()
    expected_prompts = {'B0': base, 'B1': base + '\n' + PREMISE + '\n',
                        'B2': base + '\n' + COHERENCE + '\n', 'B3': base + '\n' + PREMISE + '\n\n' + COHERENCE + '\n'}
    ids = set()
    for job in schedule:
        sid, arm = job['state_id'], job['arm']
        if job['id'] in ids:
            raise ValueError('Duplicate scheduled cell')
        ids.add(job['id'])
        expected = json.loads(json.dumps(old_jobs[sid]['request']))
        expected['messages'][0]['content'] = expected_prompts[arm]
        if job['request'] != expected or digest(expected) != job['request_sha256']:
            raise ValueError('Payload mismatch: ' + job['id'])
        if (P / 'prompts' / ARMS[arm]).read_text() != expected_prompts[arm]:
            raise ValueError('Prompt delta mismatch')
        if digest(bank[sid]['belief']) != job['belief_sha256'] or job['qid'] != bank[sid]['qid']:
            raise ValueError('Belief mismatch')
        if any(k in expected for k in ('max_tokens', 'max_completion_tokens', 'tools', 'tool_choice')):
            raise ValueError('Unexpected tool/token restriction')
    if ids != {a + '__' + s for s in bank for a in ARMS} or len(schedule) != 72:
        raise ValueError('Schedule incomplete')
    return {'status': 'PASS', 'head': head, 'manifest_sha256': sha(P / 'FREEZE.json'),
            'historical_files_unchanged': len(history), 'frozen_files': len(manifest['files']),
            'states': len(bank), 'qids': len({s['qid'] for s in bank.values()}), 'scheduled_calls': len(schedule),
            'real_model_calls': 0, 'tool_calls': 0, 'credentials_loaded': False,
            'B0_payload_exact': True, 'only_system_additions': True, 'no_max_tokens': True}

def nonnegative_integer(v):
    return type(v) is int and v >= 0

def usage_audit(usage):
    u = usage if isinstance(usage, dict) else {}
    details = u.get('completion_tokens_details') or {}
    values = {'input': u.get('prompt_tokens'), 'output': u.get('completion_tokens'),
              'total': u.get('total_tokens'), 'reasoning': details.get('reasoning_tokens') if isinstance(details, dict) else None,
              'hit': u.get('prompt_cache_hit_tokens'), 'miss': u.get('prompt_cache_miss_tokens')}
    missing = [k for k, v in values.items() if not nonnegative_integer(v)]
    valid = {k: v if nonnegative_integer(v) else None for k, v in values.items()}
    inconsistent = []
    if all(valid[k] is not None for k in ('input', 'output', 'total')) and valid['input'] + valid['output'] != valid['total']:
        inconsistent.append('input+output!=total')
    if all(valid[k] is not None for k in ('hit', 'miss', 'input')) and valid['hit'] + valid['miss'] != valid['input']:
        inconsistent.append('hit+miss!=input')
    if valid['reasoning'] is not None and valid['output'] is not None and valid['reasoning'] > valid['output']:
        inconsistent.append('reasoning>output')
    return {'tokens': valid, 'missing': missing, 'inconsistent': inconsistent, 'complete': not missing and not inconsistent}

def parse_response(status, body, expected_model):
    result = {'valid_output': False, 'output': None, 'finish_reason': None, 'response_model': None, 'usage': None}
    try:
        raw = json.loads(body)
    except (ValueError, TypeError):
        raw = None
    if isinstance(raw, dict):
        result['usage'] = raw.get('usage')
        result['response_model'] = raw.get('model')
    if status != 200:
        result['failure'] = 'auth_error' if status in (401, 403) else 'http_error'
        return result
    try:
        choice = raw['choices'][0]
        content = choice['message'].get('content')
        finish = choice['finish_reason']
        result['finish_reason'] = finish
        if result['response_model'] != expected_model:
            result['failure'] = 'model_mismatch'
        elif finish != 'stop':
            result['failure'] = 'length' if finish == 'length' else 'incomplete_finish'
        elif not isinstance(content, str) or not content.strip():
            result['failure'] = 'empty_output'
        else:
            try:
                output = json.loads(content)
            except ValueError:
                result['failure'] = 'invalid_json'
            else:
                if validate_need(output):
                    result.update(valid_output=True, output=output, failure=None)
                else:
                    result['failure'] = 'schema_error'
    except (KeyError, IndexError, TypeError, AttributeError):
        result['failure'] = 'response_schema_error'
    return result

class Batch:
    """Injected client makes offline transport tests real network-free tests."""
    def __init__(self, client, key, config, out, run_head):
        self.client, self.key, self.config, self.out, self.head = client, key, config, Path(out), run_head
        self.auth = threading.Event()
        self.abort = threading.Event()
        self.lock = threading.Lock()
        self.active = self.peak = self.attempts = 0

    def one(self, job):
        path = self.out / 'calls' / job['id']
        with self.lock:
            blocked = self.auth.is_set() or self.abort.is_set()
            reason = 'blocked_by_auth' if self.auth.is_set() else 'blocked_by_harness'
            if not blocked:
                self.active += 1
                self.peak = max(self.peak, self.active)
        row = {'id': job['id'], 'arm': job['arm'], 'state_id': job['state_id'], 'qid': job['qid'],
               'head': self.head, 'request_sha256': job['request_sha256'], 'attempted': False,
               'valid_output': False, 'output': None, 'usage': None, 'finish_reason': None, 'started_utc': now()}
        if blocked:
            row.update(failure=reason, elapsed_seconds=0)
            write(path.with_suffix('.result.json'), row)
            return row
        start = time.monotonic()
        try:
            write(path.with_suffix('.request.json'), {'head': self.head, 'request': job['request'],
                  'request_sha256': job['request_sha256'], 'started_utc': row['started_utc']})
            # This durable marker precedes the network call. On a crash, outcome/cost is unknown;
            # it is never silently resubmitted.
            write(path.with_suffix('.attempt.json'), {'id': job['id'], 'send_intent_utc': now()})
            row['attempted'] = True
            with self.lock:
                self.attempts += 1
            try:
                response = self.client.post(self.config['base_url'] + '/chat/completions', json=job['request'],
                                            headers={'Authorization': 'Bearer ' + self.key})
            except Exception as exc:
                # Only known HTTP transport exceptions are data. Programming bugs abort the batch.
                import httpx
                if not isinstance(exc, httpx.RequestError):
                    self.abort.set()
                    raise
                row['failure'] = 'timeout' if isinstance(exc, httpx.TimeoutException) else 'transport_error'
                row['error_type'] = type(exc).__name__
            else:
                if response.status_code in self.config['auth_circuit_statuses']:
                    with self.lock:
                        self.auth.set()
                write(path.with_suffix('.response.json'), {'status': response.status_code, 'body': response.text, 'completed_utc': now()})
                row['http_status'] = response.status_code
                row.update(parse_response(response.status_code, response.text, self.config['model']))
            row.update(elapsed_seconds=time.monotonic() - start, completed_utc=now(), accounting=usage_audit(row['usage']))
            write(path.with_suffix('.result.json'), row)
            print(row['id'], 'valid-output' if row['valid_output'] else row['failure'], flush=True)
            return row
        except BaseException:
            self.abort.set()
            raise
        finally:
            with self.lock:
                self.active -= 1

    def run(self, jobs):
        # A formal scheduled cell doubles as auth preflight, so no extra billed canary.
        self.one(jobs[0])
        with ThreadPoolExecutor(max_workers=self.config['max_workers']) as pool:
            futures = [pool.submit(self.one, job) for job in jobs[1:]]
            for future in as_completed(futures):
                future.result()

def accounting_summary(rows):
    attempted = [r for r in rows if r.get('attempted')]
    audits = [usage_audit(r.get('usage')) for r in attempted]
    totals = {k: sum(a['tokens'][k] or 0 for a in audits) for k in ('input', 'output', 'reasoning', 'total', 'hit', 'miss')}
    cache_audits = [a for a in audits if all(a['tokens'][k] is not None for k in ('hit', 'miss'))]
    hit = sum(a['tokens']['hit'] for a in cache_audits)
    miss = sum(a['tokens']['miss'] for a in cache_audits)
    return {'planned': len(rows), 'attempted_or_send_intent': len(attempted),
            'reported_partial_totals': totals, 'usage_complete_calls': sum(a['complete'] for a in audits),
            'accounting_complete': all(a['complete'] for a in audits),
            'cache_reporting_calls': len(cache_audits), 'cache_weighted_rate': hit / (hit + miss) if hit + miss else None,
            'cache_consistent_with_input': all('hit+miss!=input' not in a['inconsistent'] for a in cache_audits),
            'zero_fill_means_only_reported_partial_sum': True, 'currency': None}

def load_rows(directory, jobs):
    rows = []
    for job in jobs:
        path = Path(directory) / 'calls' / job['id']
        if path.with_suffix('.result.json').exists():
            row = read(path.with_suffix('.result.json'))
            if row['id'] != job['id'] or row['request_sha256'] != job['request_sha256']:
                raise ValueError('Result/request identity mismatch')
        else:
            attempted = path.with_suffix('.attempt.json').exists()
            row = {k: job[k] for k in ('id', 'arm', 'state_id', 'qid', 'request_sha256')}
            row.update(attempted=attempted, valid_output=False, output=None, usage=None,
                       failure='incomplete_attempt' if attempted else 'not_started')
        rows.append(row)
    return rows

def execute(authorized, note):
    if not authorized or not note.strip():
        raise PermissionError('Task section35: explicit user paid-call authorization and its record are required. Use dry-run first.')
    audit = audit_prepared()
    config = read(P / 'CONFIG.json')
    jobs = read(P / 'e1_need/SCHEDULE.json')
    out = P / 'e1_need/development_run'
    if out.exists():
        raise FileExistsError('Run exists. No implicit resume, overwrite or resampling.')
    # Credentials are loaded only beyond all guards; never written to artifacts.
    from dotenv import dotenv_values
    import httpx
    key = os.environ.get(config['credential_field']) or dotenv_values(ROOT / config['credential_file']).get(config['credential_field'])
    if not key:
        raise RuntimeError('Credential missing; no call sent')
    out.mkdir()
    start = time.monotonic()
    write(out / 'RUN.json', {'head': audit['head'], 'manifest_sha256': audit['manifest_sha256'],
          'authorized_paid_calls': True, 'authorization_note': note, 'scheduled_calls': len(jobs), 'started_utc': now()})
    error_type = None
    with httpx.Client(timeout=config['timeout_seconds'], transport=httpx.HTTPTransport(retries=0), follow_redirects=False) as client:
        batch = Batch(client, key, config, out, audit['head'])
        try:
            batch.run(jobs)
        except BaseException as exc:
            error_type = type(exc).__name__
            raise
        finally:
            rows = load_rows(out, jobs)
            write(out / 'ACCOUNTING.json', {**accounting_summary(rows), 'wall_seconds': time.monotonic() - start,
                  'peak_concurrency': batch.peak, 'harness_error_type': error_type,
                  'valid_outputs': sum(r['valid_output'] for r in rows),
                  'status': 'AWAITING_SEMANTIC_REVIEW' if error_type is None else 'INTERRUPTED_RETAINED'})

def export_review():
    jobs = read(P / 'e1_need/SCHEDULE.json')
    out = P / 'e1_need/development_run'
    if not out.exists():
        raise ValueError('No real run. Do not create fake raw outputs or semantic review.')
    rows = load_rows(out, jobs)
    bank = {s['state_id']: s for s in read(P / 'e1_need/BANK.json')}
    ordered = sorted(rows, key=lambda r: digest(['review-mask-v1', r['id']]))
    packets, template, key = [], {}, {}
    for i, row in enumerate(ordered):
        mask = 'R%03d' % (i + 1)
        key[mask] = row['id']
        packets.append({'review_id': mask, 'belief': bank[row['state_id']]['belief'],
                        'valid_output': row['valid_output'], 'output': row['output'], 'execution_failure': row.get('failure')})
        template[mask] = {'dimensions': {d: None for d in DIMENSIONS}, 'codes': [] if row['valid_output'] else ['X'],
                          'reason': '', 'premise_anchors': [], 'objective_decomposition': [], 'ambiguity': ''}
    write(out / 'review/PACKETS.json', packets)
    write(out / 'review/TEMPLATE.json', template)
    write(out / 'review/SEALED_KEY.json', key)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['dry-run', 'execute', 'export-review'])
    parser.add_argument('--paid-calls-authorized', action='store_true')
    parser.add_argument('--authorization-note', default='')
    args = parser.parse_args()
    if args.mode == 'execute':
        execute(args.paid_calls_authorized, args.authorization_note)
    elif args.mode == 'export-review':
        export_review()
    else:
        result = audit_prepared()
        write(P / 'analysis/DRY_RUN.json', result)
        print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
