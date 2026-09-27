"""Frozen E1 checker execution: zero retries, exclusive outputs, strict ref schema."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
import subprocess
import threading
import time

from .common import P, ROOT, bank, digest, git, input_for, read, refs, rel, sha, write
from experiments.minimal_need_multiquery.run import accounting_summary, now, usage_audit

OUT = P / 'e1_checker'

def text_value(x):
    return isinstance(x, str) and bool(x.strip())

def validate_output(value, arm, candidate):
    allowed = refs(candidate)
    def valid_refs(v):
        return isinstance(v, list) and all(isinstance(x, str) and x in allowed for x in v)
    if not isinstance(value, dict):
        return False
    if arm == 'V0':
        return (set(value) == {'decision', 'issue', 'basis_refs'} and value['decision'] in ('keep', 'revise')
                and (value['issue'] is None or text_value(value['issue'])) and valid_refs(value['basis_refs']))
    if arm != 'V1' or set(value) != {'target', 'subject', 'required_background', 'decision'}:
        return False
    subject = value['subject']
    if not (text_value(value['target']) and isinstance(subject, dict)
            and set(subject) == {'description', 'status', 'basis_refs'} and text_value(subject['description'])
            and subject['status'] in ('grounded', 'unresolved_referent', 'invented') and valid_refs(subject['basis_refs'])
            and value['decision'] in ('keep', 'lift_premise', 'discover_subject')
            and isinstance(value['required_background'], list)):
        return False
    return all(isinstance(b, dict) and set(b) == {'statement', 'status', 'basis_refs'}
               and text_value(b['statement']) and b['status'] in ('supported', 'unsupported')
               and valid_refs(b['basis_refs']) for b in value['required_background'])

def parse_response(status, body, job, candidate):
    result = {'valid_json': False, 'valid_output': False, 'output': None, 'usage': None,
              'response_model': None, 'finish_reason': None, 'failure': None}
    try:
        raw = json.loads(body)
    except (ValueError, TypeError):
        raw = None
    if isinstance(raw, dict):
        result.update(usage=raw.get('usage'), response_model=raw.get('model'))
    if status != 200:
        result['failure'] = 'access_or_billing_error' if status in (401, 402, 403) else 'http_error'
        return result
    try:
        choice = raw['choices'][0]
        result['finish_reason'] = choice['finish_reason']
        if result['response_model'] != job['request']['model']:
            result['failure'] = 'model_mismatch'
        elif choice['finish_reason'] != 'stop':
            result['failure'] = 'length' if choice['finish_reason'] == 'length' else 'incomplete_finish'
        else:
            content = choice['message'].get('content')
            if not text_value(content):
                result['failure'] = 'empty_output'
            else:
                try:
                    value = json.loads(content)
                except ValueError:
                    result['failure'] = 'invalid_json'
                else:
                    result['valid_json'] = True
                    result['output'] = value  # Preserve parsed invalid schemas; they receive no success credit.
                    result['valid_output'] = validate_output(value, job['arm'], candidate)
                    if not result['valid_output']:
                        result['failure'] = 'schema_or_ref_error'
    except (KeyError, IndexError, TypeError, AttributeError):
        result['failure'] = 'response_schema_error'
    return result

def load_rows(out=OUT):
    rows = []
    for job in read(P / 'e1_checker/SCHEDULE.json'):
        path = out / 'calls' / job['id']
        if path.with_suffix('.result.json').exists():
            row = read(path.with_suffix('.result.json'))
            if row['request_sha256'] != job['request_sha256'] or row['id'] != job['id']:
                raise ValueError('Request/result mismatch')
        else:
            row = {k: job[k] for k in ('id', 'arm', 'candidate_id', 'qid', 'state_id', 'replicate', 'request_sha256')}
            attempted = path.with_suffix('.attempt.json').exists()
            row.update(attempted=attempted, valid_json=False, valid_output=False, output=None, usage=None,
                       failure='incomplete_attempt' if attempted else 'not_started')
        rows.append(row)
    return rows

def audit(require_committed=True):
    manifest = read(P / 'FREEZE.json'); head = git('rev-parse', 'HEAD')
    for name, expected in manifest['files'].items():
        if sha(ROOT / name) != expected:
            raise ValueError('Frozen file changed: ' + name)
        if require_committed and subprocess.check_output(['git', 'show', head + ':' + name], cwd=ROOT) != (ROOT / name).read_bytes():
            raise ValueError('Frozen file not committed: ' + name)
    if require_committed and subprocess.check_output(['git', 'show', head + ':' + rel(P / 'FREEZE.json')], cwd=ROOT) != (P / 'FREEZE.json').read_bytes():
        raise ValueError('Manifest not committed')
    history = read(P / 'analysis/HISTORICAL_HASHES.json')
    for name, expected in history.items():
        if sha(ROOT / name) != expected:
            raise ValueError('History modified: ' + name)
    candidates = bank(); jobs = read(OUT / 'SCHEDULE.json'); seen = set()
    for job in jobs:
        cid, arm, rep = job['candidate_id'], job['arm'], job['replicate']
        if (cid, arm, rep) in seen:
            raise ValueError('Duplicate schedule')
        seen.add((cid, arm, rep))
        prompt = 'generic_verifier' if arm == 'V0' else 'premise_checker'
        expected = {'model': 'deepseek-flash', 'temperature': 0, 'stream': False, 'response_format': {'type': 'json_object'},
                    'messages': [{'role': 'system', 'content': (P / 'prompts' / (prompt + '.txt')).read_text()},
                                 {'role': 'user', 'content': json.dumps(input_for(candidates[cid]), ensure_ascii=False)}]}
        if job['request'] != expected or job['request_sha256'] != digest(expected):
            raise ValueError('Prompt or payload drift')
    if seen != {(c, a, r) for c in candidates for a in ('V0', 'V1') for r in (1, 2)} or len(jobs) != 88:
        raise ValueError('Planned denominator mismatch')
    return {'status': 'PASS', 'head': head, 'manifest_sha256': sha(P / 'FREEZE.json'),
            'historical_files_unchanged': len(history), 'frozen_files': len(manifest['files']), 'scheduled': len(jobs)}

class Batch:
    def __init__(self, client, key, config, candidates, out, head):
        self.client, self.key, self.config, self.candidates, self.out, self.head = client, key, config, candidates, out, head
        self.halt = threading.Event(); self.abort = threading.Event(); self.lock = threading.Lock()
        self.active = self.peak = 0

    def one(self, job):
        path = self.out / 'calls' / job['id']
        with self.lock:
            blocked = self.halt.is_set() or self.abort.is_set()
            if not blocked:
                self.active += 1; self.peak = max(self.peak, self.active)
        row = {k: job[k] for k in ('id', 'arm', 'candidate_id', 'qid', 'state_id', 'replicate', 'request_sha256')}
        row.update(head=self.head, attempted=False, valid_json=False, valid_output=False, output=None, usage=None, started_utc=now())
        if blocked:
            row.update(failure='blocked_by_access_billing_or_harness', elapsed_seconds=0)
            write(path.with_suffix('.result.json'), row)
            return
        start = time.monotonic()
        try:
            write(path.with_suffix('.request.json'), {'head': self.head, 'request': job['request'], 'request_sha256': job['request_sha256']})
            write(path.with_suffix('.attempt.json'), {'id': job['id'], 'send_intent_utc': now()})
            row['attempted'] = True
            try:
                response = self.client.post(self.config['base_url'] + '/chat/completions', json=job['request'],
                                            headers={'Authorization': 'Bearer ' + self.key})
            except Exception as exc:
                import httpx
                if not isinstance(exc, httpx.RequestError):
                    self.abort.set(); raise
                row.update(failure='timeout' if isinstance(exc, httpx.TimeoutException) else 'transport_error', error_type=type(exc).__name__)
            else:
                if response.status_code in self.config['halt_http_statuses']:
                    self.halt.set()
                write(path.with_suffix('.response.json'), {'status': response.status_code, 'body': response.text, 'completed_utc': now()})
                row.update(http_status=response.status_code, **parse_response(response.status_code, response.text, job, self.candidates[job['candidate_id']]))
            row.update(elapsed_seconds=time.monotonic()-start, completed_utc=now(), accounting=usage_audit(row['usage']))
            write(path.with_suffix('.result.json'), row)
            print(job['id'], 'valid-output' if row['valid_output'] else row['failure'], flush=True)
        except BaseException:
            self.abort.set(); raise
        finally:
            with self.lock:
                self.active -= 1

    def run(self, jobs):
        self.one(jobs[0])  # Formal first replicate is the only authentication preflight.
        with ThreadPoolExecutor(max_workers=self.config['max_workers']) as pool:
            futures = [pool.submit(self.one, job) for job in jobs[1:]]
            for future in as_completed(futures):
                future.result()

def execute():
    checked = audit(); config = read(P / 'CONFIG.json')
    if config['paid_authorization'] != 'User TASK section40 explicitly authorizes this bounded experiment':
        raise PermissionError('Missing recorded authorization')
    if (OUT / 'RUN.json').exists() or (OUT / 'calls').exists():
        raise FileExistsError('Execution already exists; no overwrite, resume or resampling')
    from dotenv import dotenv_values
    import httpx
    key = os.environ.get('DEEPSEEK_API_KEY') or dotenv_values(ROOT / '.env.deepseek').get('DEEPSEEK_API_KEY')
    if not key:
        raise RuntimeError('Credential unavailable; no call sent')
    jobs = read(OUT / 'SCHEDULE.json'); candidates = bank()
    write(OUT / 'RUN.json', {**checked, 'started_utc': now(), 'authorization': config['paid_authorization']})
    start = time.monotonic(); error = None
    with httpx.Client(timeout=config['timeout_seconds'], transport=httpx.HTTPTransport(retries=0), follow_redirects=False) as client:
        batch = Batch(client, key, config, candidates, OUT, checked['head'])
        try:
            batch.run(jobs)
        except BaseException as exc:
            error = type(exc).__name__; raise
        finally:
            rows = load_rows()
            write(OUT / 'ACCOUNTING.json', {**accounting_summary(rows), 'wall_seconds': time.monotonic()-start,
                  'peak_concurrency': batch.peak, 'harness_error': error,
                  'valid_json': sum(r['valid_json'] for r in rows), 'valid_outputs': sum(r['valid_output'] for r in rows)})

def export_review():
    if not (OUT / 'ACCOUNTING.json').exists():
        raise ValueError('Run must finish before review')
    candidates = bank(); reference = {r['candidate_id']: r for r in read(P / 'e0_reference/REFERENCE_AUDIT.json')}
    packets, key = [], {}
    for i, row in enumerate(sorted(load_rows(), key=lambda r: digest(['checker-review-order', r['id']]))):
        rid = 'R%03d' % (i+1); key[rid] = row['id']
        packets.append({'review_id': rid, 'input': input_for(candidates[row['candidate_id']]),
                        'reference': reference[row['candidate_id']], 'arm_format': row['arm'],
                        'valid_output': row['valid_output'], 'output': row['output'], 'failure': row.get('failure')})
    write(OUT / 'review/PACKETS.json', packets); write(OUT / 'review/KEY.json', key)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('audit', 'execute', 'export_review'))
    value = globals()[parser.parse_args().mode]()
    if value is not None:
        print(json.dumps(value, indent=2))
