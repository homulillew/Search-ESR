"""Pre-register and run Q1 complementary query writing; no retrieval in this script."""
import hashlib
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE.parents[2]))
from experiments.global_retrieval_robustness.common import HERE, ROOT, U1, bank, read, sha, write


def request(c, prompt, provider):
    inp = c['writer_input']
    content = {'Question': inp['raw_question'], 'Current Gap': inp['current_gap'],
               'Committed factual Claims': inp['relevant_committed_claims'],
               'Provisional hypothesis': inp['working_hypothesis'],
               'Query1': c['queries']['search_query']}
    return {'model': provider['model'], 'messages': [{'role': 'system', 'content': prompt},
            {'role': 'user', 'content': json.dumps(content, ensure_ascii=False)}], 'stream': False}


def prepare():
    assert read(HERE / 'rank_depth/summary.json')['single_query_10_pass'] is False
    cases = bank()
    provider = read(ROOT / 'experiments/model_backend_deepseek/provider.json')
    assert provider['model'] == 'deepseek-flash' and provider['max_retries'] == 0
    prompt = (HERE / 'prompts/complementary_query_writer.md').read_text()
    inputs = []
    for c in cases:
        inputs.append({'case_id': c['case_id'], 'qid': c['qid'], 'primary_type': c['primary_type'],
                       'request': request(c, prompt, provider)})
    write(BASE / 'BANK.json', inputs)
    freeze = {'base_head': read(HERE / 'rank_depth/freeze.json')['base_head'],
              'provider': {k: provider[k] for k in ['model', 'base_url', 'timeout_seconds', 'max_retries']},
              'case_order': [x['case_id'] for x in inputs], 'requests_sha256': sha(BASE / 'BANK.json'),
              'prompt_sha256': sha(HERE / 'prompts/complementary_query_writer.md'),
              'query1_sha256': sha(U1 / 'QUERIES.json'), 'rrf_constant': 60,
              'candidate_budget': 10, 'arm_S10': 'Query1 top10',
              'arm_D5_5': 'deduplicate Query1 top5 + Query2 top5, rank by RRF',
              'selection_gate': {'A/B_min': 19, 'C/D_min': 18, 'overall_min': 37,
                                 'net_paired_rescue_min': 2, 'reverse_regression_max': 1},
              'failure_policy': 'Exactly one call per case; invalid output retained as failure; no retry or repair'}
    write(BASE / 'freeze.json', freeze)


def one(client, case):
    cid = case['case_id']; started = time.monotonic()
    event = {'case_id': cid, 'request': case['request'],
             'started_utc': datetime.now(timezone.utc).isoformat()}
    try:
        raw = client.chat.completions.create(**case['request']).model_dump(mode='json')
        event['response'] = raw
        choice = raw['choices'][0]
        if choice['finish_reason'] != 'stop':
            raise ValueError('abnormal_finish')
        parsed = json.loads(choice['message']['content'])
        if not isinstance(parsed, dict) or set(parsed) != {'search_query'}:
            raise ValueError('schema')
        query = parsed['search_query']
        if not isinstance(query, str) or not query.strip() or len(query) >= 1000:
            raise ValueError('query_content')
        result = {'case_id': cid, 'search_query': query, 'error': None}
    except Exception as exc:
        event['error'] = {'type': type(exc).__name__, 'status': getattr(exc, 'status_code', None),
                          'message': str(exc)[:500]}
        result = {'case_id': cid, 'search_query': None, 'error': type(exc).__name__}
    event['elapsed_seconds'] = time.monotonic() - started
    return event, result


def query():
    from dotenv import dotenv_values
    from openai import OpenAI
    freeze = read(BASE / 'freeze.json')
    assert freeze['requests_sha256'] == sha(BASE / 'BANK.json')
    cases = read(BASE / 'BANK.json')
    assert [x['case_id'] for x in cases] == freeze['case_order']
    events_path = BASE / 'query2_events.jsonl'
    results_path = BASE / 'QUERY2.json'
    assert not events_path.exists() and not results_path.exists()
    provider = read(ROOT / 'experiments/model_backend_deepseek/provider.json')
    key = dotenv_values(ROOT / provider['credential_file']).get(provider['credential_field'])
    if not key:
        raise ValueError('DeepSeek credential unavailable')
    completed = {}
    with OpenAI(api_key=key, base_url=provider['base_url'], timeout=provider['timeout_seconds'],
                max_retries=0) as client, events_path.open('w') as events:
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = {pool.submit(one, client, case): case['case_id'] for case in cases}
            for future in as_completed(futures):
                event, result = future.result()
                completed[result['case_id']] = result
                events.write(json.dumps(event, ensure_ascii=False) + '\n')
                events.flush()
                print(result['case_id'], 'ok' if result['error'] is None else result['error'], flush=True)
    write(results_path, [completed[c['case_id']] for c in cases])


if __name__ == '__main__':
    if sys.argv[1:] == ['prepare']:
        prepare()
    elif sys.argv[1:] == ['query']:
        query()
    else:
        raise SystemExit('Usage: run.py prepare|query')
