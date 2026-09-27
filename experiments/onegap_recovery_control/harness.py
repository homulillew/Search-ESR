"""Frozen single-attempt Actor requests; action proposals are never executed."""
import argparse
import asyncio
from collections import Counter
from datetime import datetime, timezone
import json
import os
import subprocess
import time
from .prepare import ROOT, P, digest, sha, write

STRATEGIES = ['LOCATE_SOURCE', 'IDENTIFY_CANDIDATE', 'VERIFY_RELATION', 'VERIFY_ATTRIBUTE',
              'DISCRIMINATE_CANDIDATES', 'CROSS_CHECK_CONFLICT', 'LOCALIZE_IN_SOURCE', 'OTHER']
BASE = '1fb9c886fa3744aeed2422f654954e5579ee2e37'


def read(path):
    return json.loads((P / path).read_text())


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def now():
    return datetime.now(timezone.utc).isoformat()


def compile_jobs():
    config = read('CONFIG.json')
    contract = ('Available proposal actions: SEARCH (query, no source_ref/pattern); '
                'FIND (observed D# source_ref and pattern, no query); OPEN (observed W# source_ref '
                'and pattern before/after, no query); REQUEST_CLOSURE_AUDIT (null action arguments, '
                'explain the request in one_gap). These are proposals only. '
                'Allowed strategy labels: ' + ', '.join(STRATEGIES) + '. '
                'Use only the five top-level JSON fields shown in the system prompt. '
                'Return JSON with null for unused action fields.')
    jobs = []
    for v in read('e0_state_bank/VARIANTS.json'):
        request = {'model': config['model'], 'temperature': 0, 'response_format': {'type': 'json_object'},
                   'messages': [{'role': 'system', 'content': (P / 'prompts/actor.txt').read_text()},
                                {'role': 'user', 'content': contract + '\n\n' + json.dumps(v['state'], ensure_ascii=False)}]}
        jobs.append({k: v[k] for k in ('id', 'state_id', 'condition', 'state_sha256')} |
                    {'request': request, 'request_sha256': digest(request)})
    # Fixed interleaving of conditions, independent of outputs or speed.
    return sorted(jobs, key=lambda j: digest(j['id']))


def valid_output(x, state):
    if not isinstance(x, dict) or set(x) != {'focus_requirement_id', 'one_gap', 'strategy', 'hypothesis_ids_under_test', 'action'}:
        return False
    if x['focus_requirement_id'] not in {r['requirement_id'] for r in state['R']}:
        return False
    if not isinstance(x['one_gap'], str) or not x['one_gap'].strip() or x['strategy'] not in STRATEGIES:
        return False
    hs = x['hypothesis_ids_under_test']
    if not isinstance(hs, list) or any(not isinstance(h, str) for h in hs) or len(set(hs)) != len(hs):
        return False
    if not set(hs) <= {h['hypothesis_id'] for h in state['H']}:
        return False
    a = x['action']
    if not isinstance(a, dict) or set(a) != {'type', 'query', 'source_ref', 'pattern'}:
        return False
    sources = state['TraceView']['visited_sources'] + state['TraceView']['pending_source_opportunities']
    ds = {s['source_ref'] for s in sources}; ws = {s['window_ref'] for s in sources}
    def text(v): return isinstance(v, str) and bool(v.strip())
    if a['type'] == 'SEARCH':
        return text(a['query']) and a['source_ref'] is None and a['pattern'] is None
    if a['type'] == 'FIND':
        return isinstance(a['source_ref'], str) and a['source_ref'] in ds and text(a['pattern']) and a['query'] is None
    if a['type'] == 'OPEN':
        return isinstance(a['source_ref'], str) and a['source_ref'] in ws and a['pattern'] in ('before', 'after') and a['query'] is None
    return a['type'] == 'REQUEST_CLOSURE_AUDIT' and all(a[k] is None for k in ('query', 'source_ref', 'pattern'))


def history_unchanged():
    changed = git('diff', '--name-only', BASE, '--', 'experiments', ':(exclude)experiments/onegap_recovery_control')
    assert not changed, changed
    sources = read('e0_state_bank/SOURCE_HASHES.json')
    for path, h in sources.items():
        assert sha(ROOT / path) == h, path
    return {'historical_experiment_diff': [], 'source_hashes_checked': len(sources)}


def audit(check_freeze=True):
    bank = read('e0_state_bank/STATES.json'); variants = read('e0_state_bank/VARIANTS.json')
    byid = {v['id']: v for v in variants}
    assert len(bank) == 16 and len(byid) == 42
    assert Counter(v['condition'] for v in variants) == {'P0': 16, 'P1': 8, 'P2': 16, 'P3': 2}
    for v in variants:
        s = v['state']; b = bank[v['state_id']]
        assert digest(s) == v['state_sha256']
        assert set(s) == {'qid', 'Q', 'R', 'C', 'H', 'TraceView'}
        assert all(s[k] == b[k] for k in ('qid', 'Q', 'R', 'C'))
        assert all(span['text'] in s['Q'] for r in s['R'] for span in r['source_spans'])
        if v['condition'] == 'P1':
            assert s['TraceView'] == b['TraceView'] and s['H'][:-1] == b['H']
        if v['condition'] == 'P2':
            assert s['H'] == b['H']
            acts = s['TraceView']['recent_actions']
            assert len(acts) == 2 and all(a['feedback'] == 'NoGain' and a['origin'] == 'EXPERIMENTAL_PERTURBATION' for a in acts)
            assert acts[0]['action'] == acts[1]['action']
        if v['condition'] == 'P3':
            assert s['H'] == b['H'] and s['TraceView']['recent_actions'] == b['TraceView']['recent_actions']
            assert all(not x['locally_inspected'] for x in s['TraceView']['pending_source_opportunities'])
    jobs = compile_jobs()
    assert jobs == read('REQUESTS.json')
    assert all('tools' not in j['request'] and j['request']['temperature'] == 0 for j in jobs)
    if check_freeze:
        f = read('FREEZE.json')
        assert f['request_set_sha256'] == sha(P / 'REQUESTS.json')
        for path, h in f['files'].items():
            assert sha(ROOT / path) == h, path
            assert subprocess.check_output(['git', 'show', 'HEAD:' + path], cwd=ROOT) == (ROOT / path).read_bytes(), path
        assert subprocess.check_output(['git', 'show', 'HEAD:experiments/onegap_recovery_control/FREEZE.json'], cwd=ROOT) == (P / 'FREEZE.json').read_bytes()
    return {'status': 'PASS', 'calls': len(jobs), 'states': len(bank), 'qids': len({s['qid'] for s in bank.values()}),
            'head': git('rev-parse', 'HEAD'), **history_unchanged()}


def freeze():
    audit(False)
    files = {}
    for p in sorted(P.rglob('*')):
        if not p.is_file() or '__pycache__' in p.parts or p.name == 'FREEZE.json':
            continue
        rel = str(p.relative_to(ROOT))
        assert subprocess.check_output(['git', 'show', 'HEAD:' + rel], cwd=ROOT) == p.read_bytes(), rel
        files[rel] = sha(p)
    files['AGENTS.md'] = sha(ROOT / 'AGENTS.md')
    write('FREEZE.json', {'created_utc': now(), 'preparation_head': git('rev-parse', 'HEAD'),
                          'provider': 'deepseek', 'model': 'deepseek-flash', 'files': files,
                          'request_set_sha256': sha(P / 'REQUESTS.json'), 'planned_calls': 42,
                          'replicates': 1, 'actor_decisions_per_condition': 1, 'tool_calls': 0,
                          'max_retries': 0, 'maximum_concurrency': 42})


def parse_response(status, body, state):
    r = {'http_status': status, 'valid_output': False, 'output': None, 'usage': None, 'failure': None}
    try:
        d = json.loads(body)
    except ValueError:
        r['failure'] = 'response_not_json'; return r
    if isinstance(d, dict): r['usage'] = d.get('usage')
    if status != 200:
        r['failure'] = 'http_error'; return r
    try:
        c = d['choices'][0]
        r.update(response_model=d.get('model'), finish_reason=c.get('finish_reason'))
        r['output'] = json.loads(c['message']['content'])
        r['valid_output'] = valid_output(r['output'], state) and d.get('model') == 'deepseek-flash' and c.get('finish_reason') == 'stop'
        if not r['valid_output']: r['failure'] = 'output_contract_or_incomplete'
    except (KeyError, ValueError, TypeError, IndexError):
        r['failure'] = 'parse_error'
    return r


def accounting(rows):
    sums = Counter(); complete = 0; missing = 0; inconsistent = 0
    durations = []
    for r in rows:
        if 'elapsed_seconds' in r: durations.append(r['elapsed_seconds'])
        u = r.get('usage')
        if not isinstance(u, dict): missing += 1; continue
        for field, target in [('prompt_tokens', 'input_tokens'), ('completion_tokens', 'output_tokens'), ('total_tokens', 'total_tokens')]:
            if isinstance(u.get(field), int): sums[target] += u[field]
        reason = u.get('completion_tokens_details', {}).get('reasoning_tokens')
        if isinstance(reason, int): sums['reasoning_tokens_subset_of_output'] += reason
        n, hit, miss = [u.get(k) for k in ('prompt_tokens', 'prompt_cache_hit_tokens', 'prompt_cache_miss_tokens')]
        if not all(isinstance(v, int) and v >= 0 for v in (n, hit, miss)):
            missing += 1
        elif hit + miss != n:
            inconsistent += 1
        else:
            complete += 1; sums['cache_input_tokens'] += n; sums['cache_hit_tokens'] += hit; sums['cache_miss_tokens'] += miss
    durations.sort()
    return {**sums, 'planned_slots': len(rows), 'sent': sum(r.get('attempted', False) for r in rows),
            'valid_outputs': sum(r.get('valid_output', False) for r in rows),
            'failures': dict(Counter(r['failure'] for r in rows if r.get('failure'))),
            'usage_complete_consistent': complete, 'usage_missing': missing, 'usage_inconsistent': inconsistent,
            'cache_hit_rate': sums['cache_hit_tokens'] / sums['cache_input_tokens'] if sums['cache_input_tokens'] else None,
            'latency_p50_seconds': durations[len(durations)//2] if durations else None,
            'latency_p95_seconds': durations[max(0, (95*len(durations)+99)//100-1)] if durations else None}


async def execute():
    import httpx
    from dotenv import dotenv_values
    checked = audit()
    auth = read('AUTHORIZATION.json')
    assert auth['request_set_sha256'] == sha(P / 'REQUESTS.json') and auth['maximum_attempts'] == 42
    folder = P / 'e1_actor/calls'
    if folder.exists() or (P / 'e1_actor/RUN.json').exists():
        raise FileExistsError('No overwrite, retry, resume or replacement.')
    key = os.environ.get('DEEPSEEK_API_KEY') or dotenv_values(ROOT / '.env.deepseek').get('DEEPSEEK_API_KEY')
    if not isinstance(key, str) or not key.strip() or '\n' in key or '\r' in key:
        raise ValueError('Credential unavailable; no request sent.')
    config = read('CONFIG.json'); jobs = read('REQUESTS.json')
    states = {v['id']: v['state'] for v in read('e0_state_bank/VARIANTS.json')}
    write('e1_actor/RUN.json', {**checked, 'started_utc': now(), 'freeze_sha256': sha(P / 'FREEZE.json'),
                              'authorization_sha256': sha(P / 'AUTHORIZATION.json'), 'config': config})
    limits = httpx.Limits(max_connections=42, max_keepalive_connections=42)
    timeout = httpx.Timeout(connect=30, read=660, write=60, pool=60)
    pending = list(jobs); running = {}; results = []; peak = 0; cap = 42; halt = False; changes = []
    started = time.monotonic()

    async def one(j, client):
        r = {k: v for k, v in j.items() if k != 'request'}
        r.update(attempted=True, started_utc=now(), valid_output=False, output=None, usage=None, failure=None)
        prefix = 'e1_actor/calls/' + j['id']
        write(prefix + '.request.json', j)
        write(prefix + '.attempt.json', {'id': j['id'], 'send_intent_utc': now()})
        begin = time.monotonic()
        try:
            response = await asyncio.wait_for(client.post(config['endpoint'], json=j['request'],
                                              headers={'Authorization': 'Bearer ' + key}), timeout=900)
            write(prefix + '.response.json', {'http_status': response.status_code, 'body': response.text, 'completed_utc': now()})
            r.update(parse_response(response.status_code, response.text, states[j['id']]))
        except (httpx.RequestError, asyncio.TimeoutError) as exc:
            r.update(failure='timeout' if isinstance(exc, (httpx.TimeoutException, asyncio.TimeoutError)) else 'transport_error',
                     error_type=type(exc).__name__)
        r.update(completed_utc=now(), elapsed_seconds=time.monotonic()-begin)
        write(prefix + '.result.json', r)
        print(j['id'], 'valid' if r['valid_output'] else r['failure'], flush=True)
        return r

    async with httpx.AsyncClient(timeout=timeout, transport=httpx.AsyncHTTPTransport(retries=0, limits=limits), follow_redirects=False) as client:
        while pending or running:
            while pending and len(running) < cap and not halt:
                j = pending.pop(0); t = asyncio.create_task(one(j, client)); running[t] = j
                peak = max(peak, len(running))
            if not running: break
            done, _ = await asyncio.wait(running, return_when=asyncio.FIRST_COMPLETED)
            for t in done:
                running.pop(t); r = t.result(); results.append(r)
                if r.get('http_status') in config['halt_http_statuses']: halt = True
                if r.get('http_status') in (429, 503) or r.get('failure') in ('timeout', 'transport_error'):
                    cap = max(1, cap // 2)
                    changes.append({'at_utc': now(), 'new_cap': cap, 'trigger': r['id'], 'pending': len(pending)})
    for j in pending:
        r = {k: v for k, v in j.items() if k != 'request'}
        r.update(attempted=False, valid_output=False, output=None, usage=None, failure='halted_unsent')
        write('e1_actor/calls/' + j['id'] + '.result.json', r); results.append(r)
    assert len(results) == 42
    write('e1_actor/ACCOUNTING.json', {**accounting(results), 'wall_seconds': time.monotonic()-started,
                                     'peak_concurrency': peak, 'concurrency_changes': changes})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('mode', choices=['requests', 'audit', 'freeze', 'execute'])
    mode = parser.parse_args().mode
    if mode == 'requests': write('REQUESTS.json', compile_jobs())
    elif mode == 'freeze': freeze()
    elif mode == 'audit': print(json.dumps(audit(), indent=2))
    else: asyncio.run(execute())
