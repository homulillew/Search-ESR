"""Read-only replay of an executed batch; no provider/network calls."""
import argparse
from .common import *
from .run import OUT, audit, jobs, load_rows, parse, accounting


def verify(phase):
    checked = audit(phase, require_authorization=True)
    schedule = jobs(phase)
    rows = load_rows(phase)
    run = read(OUT/phase/'RUN.json')
    for job, row in zip(schedule, rows):
        path = OUT/phase/'calls'/job['id']
        if row['attempted']:
            request = read(path.with_suffix('.request.json'))
            assert request['request'] == job['request']
            assert request['request_sha256'] == digest(job['request'])
            assert request['head'] == run['head']
            assert path.with_suffix('.attempt.json').exists()
        response = path.with_suffix('.response.json')
        if response.exists():
            raw = read(response)
            reparsed = parse(raw['status'], raw['body'], job)
            assert row['http_status'] == raw['status']
            assert all(row.get(k) == v for k, v in reparsed.items()), job['id']
        else:
            assert row.get('http_status') is None
    actual = read(OUT/phase/'ACCOUNTING.json')
    replay = accounting(rows)
    assert all(actual[k] == v for k, v in replay.items())
    assert len(rows) == len(schedule) == actual['planned']
    assert actual['peak_concurrency'] <= 8
    result = {**checked, 'raw_response_reparse_identical': True,
              'usage_accounting_replay_identical': True,
              'all_actual_requests_match_frozen_schedule': True,
              'all_send_heads_match_run': True,
              'gold_and_frozen_code_unchanged': True,
              'attempted': sum(bool(r['attempted']) for r in rows),
              'valid_outputs': sum(bool(r['valid_output']) for r in rows),
              'verification_provider_calls': 0,
              'replay_accounting_sha256': digest(replay)}
    write(P/f'analysis/{phase.upper()}_INTEGRITY.json', result)
    print(result)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('phase', choices=['verifier', 'auditor'])
    verify(parser.parse_args().phase)
