"""Single, separately frozen development revision; no downstream execution."""
import argparse
import copy
import json
import os
import subprocess
import time

from experiments.minimal_need_multiquery.prepare import P, ROOT, digest, git, read, relative, sha, write
from experiments.minimal_need_multiquery.run import (
    Batch, DIMENSIONS, accounting_summary, audit_prepared, load_rows, now,
)
from experiments.minimal_need_multiquery.score import counts, validate_review

R = P / 'e1_need/revision'
OUT = R / 'run'


def gate(by_arm, no_h):
    b0, b3 = by_arm['B0'], by_arm['B3']
    checks = {
        'paired_18': b0['n'] == b3['n'] == 18,
        'B3_strict_at_least16': b3['strict_valid'] >= 16,
        'B3_P_plus_A_at_most1': b3['p_plus_a_sum'] <= 1,
        'B3_W_zero': b3['codes']['W'] == 0,
        'strict_gain_at_least3': b3['strict_valid'] - b0['strict_valid'] >= 3,
        'NoH_8_and_strict_at_least7': no_h['B3']['n'] == 8 and no_h['B3']['strict_valid'] >= 7,
        'valid_output_at_least17_each': all(m['valid_output'] >= 17 for m in by_arm.values()),
    }
    return {'status': 'PASS_TO_FRESH_E1' if all(checks.values()) else 'STOP_E1_NO_MORE_REVISIONS',
            'checks': checks, 'opens_E2': False, 'remaining_development_revisions': 0}


def prepare():
    audit_prepared()
    if read(P / 'e1_need/development_run/METRICS.json')['mechanism_gate']['status'] != 'STOP_FOR_MECHANISM_ANALYSIS':
        raise ValueError('Revision requires the documented initial mechanism failure')
    jobs = []
    for old in read(P / 'e1_need/SCHEDULE.json'):
        if old['arm'] not in ('B0', 'B3'):
            continue
        job = copy.deepcopy(old)
        if job['arm'] == 'B3':
            job['request']['messages'][0]['content'] = (R / 'b3.txt').read_text()
        job['request_sha256'] = digest(job['request'])
        jobs.append(job)
    jobs.sort(key=lambda j: digest(['revision-r1-schedule', j['id']]))
    write(R / 'SCHEDULE.json', jobs)
    config = read(P / 'CONFIG.json')
    config.update(stage='E1 development sole bounded revision r1', paid_calls_authorized=True)
    write(R / 'CONFIG.json', config)
    a = read(P / 'e1_need/development_run/ACCOUNTING.json')
    write(R / 'CALL_ESTIMATE.json', {
        'calls': 36, 'horizon': 1, 'tools': 0, 'retries': 0,
        'output_tokens_projection': a['reported_partial_totals']['output'] / 2,
        'input_tokens_projection_rough': a['reported_partial_totals']['input'] / 2,
        'basis': 'Half of observed 72-call v1 cost; prompt lengths and hidden reasoning vary. No monetary price asserted.',
    })
    paths = set(read(P / 'FREEZE.json')['files'])
    paths.add(relative(P / 'FREEZE.json'))
    paths.add(relative(P / 'AUTHORIZATION.md'))
    paths.add(relative(P / 'analysis/audit_execution.py'))
    paths.update(relative(p) for p in (P / 'e1_need/development_run').rglob('*') if p.is_file())
    paths.update(relative(p) for p in R.iterdir() if p.is_file() and p.name != 'FREEZE.json')
    write(R / 'FREEZE.json', {
        'version': 'sole-development-revision-r1', 'prepared_against_head': git('rev-parse', 'HEAD'),
        'provider': config['provider'], 'model': config['model'], 'model_calls': 36,
        'horizon': 1, 'tools': [], 'max_retries': 0,
        'files': {name: sha(ROOT / name) for name in sorted(paths)},
        'execution_head_rule': 'Record and verify exact committed HEAD before the first call.',
    })


def audit(require_committed=True):
    audit_prepared(require_committed)
    head = git('rev-parse', 'HEAD')
    manifest = read(R / 'FREEZE.json')
    for name, expected in manifest['files'].items():
        if sha(ROOT / name) != expected:
            raise ValueError('Frozen revision input changed: ' + name)
        if require_committed and subprocess.check_output(['git', 'show', head + ':' + name], cwd=ROOT) != (ROOT / name).read_bytes():
            raise ValueError('Revision input not committed: ' + name)
    if require_committed and subprocess.check_output(['git', 'show', head + ':' + relative(R / 'FREEZE.json')], cwd=ROOT) != (R / 'FREEZE.json').read_bytes():
        raise ValueError('Revision manifest not committed')
    old = {j['id']: j for j in read(P / 'e1_need/SCHEDULE.json')}
    jobs = read(R / 'SCHEDULE.json')
    if len(jobs) != 36 or {j['id'] for j in jobs} != {k for k, j in old.items() if j['arm'] in ('B0', 'B3')}:
        raise ValueError('Revision denominator mismatch')
    for job in jobs:
        expected = copy.deepcopy(old[job['id']])
        if job['arm'] == 'B3':
            expected['request']['messages'][0]['content'] = (R / 'b3.txt').read_text()
        expected['request_sha256'] = digest(expected['request'])
        if job != expected:
            raise ValueError('Revision payload differs beyond system prompt')
    return {'status': 'PASS', 'head': head, 'manifest_sha256': sha(R / 'FREEZE.json'),
            'scheduled': 36, 'frozen_files': len(manifest['files']), 'B0_exact': True,
            'same_QCH': True, 'only_B3_system_replaced': True}


def execute(authorized, note):
    if not authorized or not note.strip():
        raise PermissionError('Explicit paid authorization must be recorded')
    checked = audit()
    if OUT.exists():
        raise FileExistsError('Revision already started; no resampling or overwrite')
    config, jobs = read(R / 'CONFIG.json'), read(R / 'SCHEDULE.json')
    from dotenv import dotenv_values
    import httpx
    key = os.environ.get(config['credential_field']) or dotenv_values(ROOT / config['credential_file']).get(config['credential_field'])
    if not key:
        raise RuntimeError('Credential missing; no request sent')
    OUT.mkdir()
    write(OUT / 'RUN.json', {**checked, 'authorized_paid_calls': True, 'authorization_note': note, 'started_utc': now()})
    start = time.monotonic()
    error_type = None
    with httpx.Client(timeout=config['timeout_seconds'], transport=httpx.HTTPTransport(retries=0), follow_redirects=False) as client:
        batch = Batch(client, key, config, OUT, checked['head'])
        try:
            batch.run(jobs)
        except BaseException as exc:
            error_type = type(exc).__name__
            raise
        finally:
            rows = load_rows(OUT, jobs)
            write(OUT / 'ACCOUNTING.json', {**accounting_summary(rows), 'wall_seconds': time.monotonic() - start,
                  'peak_concurrency': batch.peak, 'harness_error_type': error_type,
                  'valid_outputs': sum(r['valid_output'] for r in rows),
                  'status': 'AWAITING_SEMANTIC_REVIEW' if error_type is None else 'INTERRUPTED_RETAINED'})


def export_review():
    if not (OUT / 'ACCOUNTING.json').exists():
        raise ValueError('Finish the real run before review export')
    rows = load_rows(OUT, read(R / 'SCHEDULE.json'))
    bank = {s['state_id']: s for s in read(P / 'e1_need/BANK.json')}
    packets, template, key = [], {}, {}
    for i, row in enumerate(sorted(rows, key=lambda r: digest(['revision-r1-masked-review', r['id']]))):
        mask = 'R%03d' % (i + 1)
        key[mask] = row['id']
        packets.append({'review_id': mask, 'belief': bank[row['state_id']]['belief'],
                        'valid_output': row['valid_output'], 'output': row['output'], 'execution_failure': row.get('failure')})
        template[mask] = {'dimensions': {d: None for d in DIMENSIONS}, 'codes': [] if row['valid_output'] else ['X'],
                          'reason': '', 'premise_anchors': [], 'objective_decomposition': [], 'ambiguity': ''}
    write(OUT / 'review/PACKETS.json', packets)
    write(OUT / 'review/TEMPLATE.json', template)
    write(OUT / 'review/SEALED_KEY.json', key)


def score():
    review = read(OUT / 'review/REVIEW.json')
    if not (OUT / 'review/FIRST_PASS_ATTESTATION.json').exists():
        raise ValueError('Record first-pass review before unmasking')
    key = read(OUT / 'review/SEALED_KEY.json')
    if set(review) != set(key):
        raise ValueError('Incomplete masked review')
    reviews = {key[k]: v for k, v in review.items()}
    rows = load_rows(OUT, read(R / 'SCHEDULE.json'))
    bank = {s['state_id']: s for s in read(P / 'e1_need/BANK.json')}
    scored = [{**r, 'strict_valid': validate_review(r, reviews[r['id']]), 'codes': reviews[r['id']]['codes'],
               'no_h': not bank[r['state_id']]['belief']['hypothesis']} for r in rows]
    by_arm = {a: counts([r for r in scored if r['arm'] == a]) for a in ('B0', 'B3')}
    no_h = {a: counts([r for r in scored if r['arm'] == a and r['no_h']]) for a in by_arm}
    indexed = {(r['arm'], r['state_id']): r for r in scored}
    result = {'cohort': 'exposed_development_NOT_FRESH', 'by_arm': by_arm, 'no_h': no_h,
              'by_qid': {q: {a: counts([r for r in scored if r['qid'] == q and r['arm'] == a]) for a in by_arm}
                         for q in sorted({r['qid'] for r in scored}, key=int)},
              'paired': {'strict_gain_ids': [sid for sid in bank if not indexed['B0', sid]['strict_valid'] and indexed['B3', sid]['strict_valid']],
                         'strict_loss_ids': [sid for sid in bank if indexed['B0', sid]['strict_valid'] and not indexed['B3', sid]['strict_valid']]},
              'gate': gate(by_arm, no_h), 'accounting': accounting_summary(rows), 'scored': scored}
    write(OUT / 'METRICS.json', result)
    print(json.dumps({k: result[k] for k in ('by_arm', 'no_h', 'paired', 'gate')}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('prepare', 'audit', 'execute', 'export-review', 'score'))
    parser.add_argument('--paid-calls-authorized', action='store_true')
    parser.add_argument('--authorization-note', default='')
    args = parser.parse_args()
    if args.mode == 'execute':
        execute(args.paid_calls_authorized, args.authorization_note)
    elif args.mode == 'audit':
        print(json.dumps(audit(), indent=2))
    else:
        {'prepare': prepare, 'export-review': export_review, 'score': score}[args.mode]()


if __name__ == '__main__':
    main()
