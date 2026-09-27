"""Read-only request/response/freeze audit; writes one append-only result on demand."""
import json
from pathlib import Path
import subprocess
import sys
from experiments.minimal_need_multiquery.prepare import P, ROOT, digest, read, sha, write
from experiments.minimal_need_multiquery.run import accounting_summary, load_rows, parse_response

def inspect(run, schedule_path, freeze_path):
    run = Path(run)
    schedule = read(schedule_path)
    freeze = read(freeze_path)
    record = read(run / 'RUN.json')
    head = record['head']
    if record['manifest_sha256'] != sha(freeze_path):
        raise ValueError('Manifest changed since execution')
    for name, expected in freeze['files'].items():
        if sha(ROOT / name) != expected:
            raise ValueError('Frozen file mutated: ' + name)
        blob = subprocess.check_output(['git', 'show', head + ':' + name], cwd=ROOT)
        if blob != (ROOT / name).read_bytes():
            raise ValueError('File was not committed at execution HEAD: ' + name)
    history = read(P / 'analysis/HISTORICAL_HASHES.json')
    for name, expected in history.items():
        if sha(ROOT / name) != expected:
            raise ValueError('Historical mutation: ' + name)
    rows = load_rows(run, schedule)
    request_count = response_count = 0
    for row, job in zip(rows, schedule):
        prefix = run / 'calls' / job['id']
        request_file = prefix.with_suffix('.request.json')
        response_file = prefix.with_suffix('.response.json')
        if request_file.exists():
            request_count += 1
            request = read(request_file)
            if request['head'] != head or request['request'] != job['request'] or request['request_sha256'] != digest(job['request']):
                raise ValueError('Request identity/HEAD drift: ' + job['id'])
            if any(k in request['request'] for k in ('max_tokens', 'tools', 'tool_choice')):
                raise ValueError('Unexpected tokens/tools: ' + job['id'])
        if response_file.exists():
            response_count += 1
            response = read(response_file)
            parsed = parse_response(response['status'], response['body'], job['request']['model'])
            for key in ('valid_output', 'output', 'finish_reason', 'usage', 'failure'):
                if row.get(key) != parsed.get(key):
                    raise ValueError('Raw response/result mismatch: ' + job['id'] + ':' + key)
        elif row.get('valid_output'):
            raise ValueError('Valid output without raw response')
    result_ids = {p.name[:-len('.result.json')] for p in (run / 'calls').glob('*.result.json')}
    if result_ids - {j['id'] for j in schedule}:
        raise ValueError('Unscheduled result present')
    return {'status': 'PASS', 'execution_head': head, 'manifest_sha256': sha(freeze_path),
            'scheduled': len(schedule), 'requests_archived': request_count, 'responses_archived': response_count,
            'results_archived': len(result_ids), 'historical_files_unchanged': len(history),
            'frozen_files_unchanged': len(freeze['files']), 'accounting': accounting_summary(rows),
            'tool_calls': 0, 'no_retries_or_extra_scheduled_results': True,
            'limitation': 'Mechanical integrity, not an independent semantic review or provider billing audit.'}

if __name__ == '__main__':
    run = P / 'e1_need/development_run'
    result = inspect(run, P / 'e1_need/SCHEDULE.json', P / 'FREEZE.json')
    if '--save' in sys.argv:
        write(run / 'INTEGRITY.json', result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
