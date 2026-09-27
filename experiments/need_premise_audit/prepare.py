"""Mechanical candidate selection, exact prompt payloads and pre-call freeze."""
import argparse
from collections import Counter
import hashlib
import statistics
from .common import P, ROOT, OLD, bank, digest, git, input_for, read, rel, sha, write

RUNS = {'v1': OLD / 'e1_need/development_run', 'r1': OLD / 'e1_need/revision/run'}

def select():
    beliefs = {s['state_id']: s for s in read(OLD / 'e1_need/BANK.json')}
    pool = []
    for run_id, directory in RUNS.items():
        key = read(directory / 'review/SEALED_KEY.json')
        review = read(directory / 'review/REVIEW.json')
        review_by_id = {key[k]: v for k, v in review.items()}
        for row in read(directory / 'METRICS.json')['scored']:
            if row['arm'] != 'B0':
                continue
            belief = beliefs[row['state_id']]['belief']
            pool.append({'candidate_id': run_id + '__' + row['state_id'], 'run_id': run_id,
                         'state_id': row['state_id'], 'qid': row['qid'], 'no_h': not belief['hypothesis'],
                         'question': belief['question'], 'claims': [{'id': 'C' + str(i), 'statement': s}
                             for i, s in enumerate(belief['claims'], 1)],
                         'hypothesis': belief['hypothesis'], 'candidate_need': row['output']['need'],
                         'historical_codes': row['codes'], 'historical_strict_valid': row['strict_valid'],
                         'historical_review': review_by_id[row['id']], 'belief_sha256': digest(belief),
                         'source_result': rel(directory / 'calls' / (row['id'] + '.result.json')),
                         'source_result_sha256': sha(directory / 'calls' / (row['id'] + '.result.json')),
                         'selection_hash': hashlib.sha256((row['state_id'] + run_id).encode()).hexdigest()})
    errors = [r for r in pool if set(r['historical_codes']) & {'P', 'A'}]
    valid = [r for r in pool if r['historical_strict_valid']]
    controls = []
    quotas = {}
    for no_h in (False, True):
        n = sum(r['no_h'] == no_h for r in errors)
        available = sorted([r for r in valid if r['no_h'] == no_h], key=lambda r: r['selection_hash'])
        if len(available) < n:
            raise ValueError('Matched stratum insufficient; no silent fallback')
        controls += available[:n]
        quotas['No-H' if no_h else 'H'] = {'errors': n, 'available_controls': len(available), 'selected_controls': n}
    candidates = [{**r, 'selection_group': group} for group, rows in [('error', errors), ('control', controls)] for r in rows]
    candidates.sort(key=lambda r: r['candidate_id'])
    write(P / 'e0_reference/CANDIDATES.json', candidates)
    write(P / 'e0_reference/SELECTION.json', {
        'rule': 'All historical B0 P/A cells from v1/r1; equal strict-valid controls, exactly H/No-H matched; within stratum ascending SHA256(UTF8(state_id + run_id)).',
        'frozen_before_any_call': True, 'pool_instances': len(pool), 'errors': len(errors), 'controls': len(controls),
        'candidate_instances': len(candidates), 'unique_states': len({r['state_id'] for r in candidates}),
        'unique_qids': len({r['qid'] for r in candidates}), 'strata': quotas,
        'excluded_pure_broadness': [r['candidate_id'] for r in pool if r['historical_codes'] == ['W']],
        'selected_ids': [r['candidate_id'] for r in candidates],
        'control_hash_ranking': [{'candidate_id': r['candidate_id'], 'no_h': r['no_h'], 'hash': r['selection_hash']}
                                 for r in sorted(valid, key=lambda x: x['selection_hash'])],
        'duplicates': 'Two historic runs may share state or exact Need. Candidate instances, states and qids are separately reported; no independent-qid interpretation.'})
    history = {}
    for name in git('-c', 'core.quotepath=false', 'ls-files', 'experiments', 'llm_chat', '全链路排查报告').splitlines():
        if not name.startswith(rel(P) + '/') and (ROOT / name).is_file():
            history[name] = sha(ROOT / name)
    write(P / 'analysis/HISTORICAL_HASHES.json', history)

def schedule():
    candidates = bank()
    config = read(P / 'CONFIG.json')
    jobs = []
    for c in candidates.values():
        for arm, prompt in [('V0', 'generic_verifier'), ('V1', 'premise_checker')]:
            for replicate in (1, 2):
                request = {'model': config['model'], 'temperature': 0, 'stream': False,
                           'response_format': {'type': 'json_object'},
                           'messages': [{'role': 'system', 'content': (P / 'prompts' / (prompt + '.txt')).read_text()},
                                        {'role': 'user', 'content': __import__('json').dumps(input_for(c), ensure_ascii=False)}]}
                jobs.append({'id': arm + '__' + c['candidate_id'] + '__rep' + str(replicate), 'arm': arm,
                             'candidate_id': c['candidate_id'], 'qid': c['qid'], 'state_id': c['state_id'],
                             'replicate': replicate, 'request': request, 'request_sha256': digest(request)})
    jobs.sort(key=lambda j: digest(['premise-audit-E1-order', j['id']]))
    write(P / 'e1_checker/SCHEDULE.json', jobs)
    outputs, ratios = [], []
    for d in RUNS.values():
        for f in (d / 'calls').glob('*.result.json'):
            row = read(f); u = row['usage']; outputs.append(u['completion_tokens'])
            request = read(f.with_name(f.name.replace('.result.json', '.request.json')))['request']
            chars = sum(len(m['content']) for m in request['messages'])
            ratios.append(u['prompt_tokens'] / chars)
    ratio = statistics.median(ratios)
    prompt_est = sum(sum(len(m['content']) for m in j['request']['messages']) * ratio for j in jobs)
    ordered = sorted(outputs)
    quantile = lambda q: ordered[min(len(ordered)-1, __import__('math').ceil(q*len(ordered))-1)]
    write(P / 'analysis/CALL_ESTIMATE.json', {
        'E1_calls': len(jobs), 'candidate_instances': len(candidates), 'arms': 2, 'replicates_per_arm_candidate': 2,
        'estimated_prompt_tokens': round(prompt_est), 'estimator': 'Median observed prompt_tokens / message-content characters from all108 prior calls, applied to exact new messages; tokenizer and schema overhead approximate.',
        'historical_completion': {'n': len(outputs), 'mean': statistics.mean(outputs), 'median': statistics.median(outputs),
                                  'p90_nearest_rank': quantile(.90), 'p95_nearest_rank': quantile(.95), 'max': max(outputs)},
        'mean_completion_scenario': round(len(jobs)*statistics.mean(outputs)),
        'observed_tail_per_call_scenario': len(jobs)*max(outputs),
        'tail_risk': 'Previous length failure spent65535 reasoning tokens and yielded no Need. Every replicate is billed exposure and retained. With max_tokens omitted, observed-tail scenario is NOT a guaranteed maximum or hard cost bound.',
        'conditional_later_calls': {'E2_if_E1_PASS': 2*len(candidates), 'E3_if_both_PASS': '90–120:30–40 archived natural states × B0/check/repair; separate freeze required'},
        'tools': 0, 'retries': 0, 'currency_estimate': None})

def freeze():
    refs = read(P / 'e0_reference/REFERENCE_AUDIT.json')
    assert {r['candidate_id'] for r in refs} == set(bank())
    assert not (P / 'e1_checker/calls').exists()
    files = {rel(f): sha(f) for f in sorted(P.rglob('*')) if f.is_file() and '__pycache__' not in f.parts
             and f.name != 'FREEZE.json' and f.suffix != '.pyc'}
    # Pure accounting helpers are reused from the old immutable implementation.
    for name in ('run.py', 'prepare.py'):
        f = OLD / name; files[rel(f)] = sha(f)
    write(P / 'FREEZE.json', {'version': 'premise-checker-E1-v1', 'base_head': git('rev-parse', 'HEAD'),
                             'model': 'deepseek-flash', 'planned_calls': 88, 'replicates': 2, 'tools': [],
                             'horizon': 1, 'max_retries': 0, 'files': files,
                             'execution_head_rule': 'Exact committed HEAD and manifest hash verified before first call.'})

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('select', 'schedule', 'freeze'))
    globals()[parser.parse_args().mode]()
