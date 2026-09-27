"""Offline replay of archived response parsing, metrics, usage and frozen inputs."""
import json
from .harness import read, write, audit, parse_response, accounting, P, digest
from .score import calculate


def main():
    frozen = audit()
    jobs = read('REQUESTS.json')
    variants = {v['id']: v for v in read('e0_state_bank/VARIANTS.json')}
    reviews = {r['id']: r for r in read('e1_actor/REVIEW.json')}
    packets = {p['id']: p for p in read('e1_actor/REVIEW_PACKETS.json')}
    results, rows = [], []
    assert len(list((P / 'e1_actor/calls').glob('*.attempt.json'))) == len(jobs)
    assert len(list((P / 'e1_actor/calls').glob('*.result.json'))) == len(jobs)
    for j in jobs:
        base = 'e1_actor/calls/' + j['id']
        assert read(base + '.request.json') == j
        r = read(base + '.result.json'); raw = read(base + '.response.json')
        assert r['request_sha256'] == j['request_sha256'] == digest(j['request'])
        parsed = parse_response(raw['http_status'], raw['body'], variants[j['id']]['state'])
        for k, v in parsed.items(): assert r[k] == v, (j['id'], k)
        assert r['response_model'] == 'deepseek-flash' and r['finish_reason'] == 'stop'
        assert raw['http_status'] == 200
        packet = packets[j['id']]
        assert packet['state'] == variants[j['id']]['state'] and packet['output'] == r['output']
        review = reviews[j['id']]
        assert review['schema_valid'] == r['valid_output']
        rows.append({**review, 'condition': j['condition'], 'state_id': j['state_id'], 'action_type': r['output']['action']['type']})
        results.append(r)
    assert digest(calculate(rows)) == digest(read('e1_actor/METRICS.json'))
    a = read('e1_actor/ACCOUNTING.json')
    for k, v in accounting(results).items(): assert a[k] == v, k
    d = read('analysis/DIAGNOSTICS.json')
    assert len(d['open_contract_errors']) == 11
    assert all(x['ref_visible'] for x in d['open_contract_errors'])
    assert set(x['id'] for x in d['open_contract_errors']) == {r['id'] for r in results if not r['valid_output']}
    assert len(d['closure_requests']) == 10
    assert read('e1_actor/METRICS.json')['gate'] == 'FAIL'
    result = {'status': 'PASS', 'scope': 'artifact integrity and deterministic replay, not empirical gate',
              'response_parses_reproduced': len(results), 'metrics_reproduced': True, 'usage_reproduced': True,
              'frozen_files_unchanged': True, 'historical_source_hashes_checked': frozen['source_hashes_checked'],
              'historical_experiment_diff': frozen['historical_experiment_diff'],
              'all_output_contract_failures_are_visible_ref_open_keyword_errors': True,
              'empirical_gate': 'FAIL', 'actual_tool_calls': 0, 'writer_admission_closure_calls': 0,
              'stage_5c_executed': False, 'stage_5l_executed': False}
    target = P / 'analysis/COMPLETION_VALIDATION.json'
    if target.exists(): assert read('analysis/COMPLETION_VALIDATION.json') == result
    else: write('analysis/COMPLETION_VALIDATION.json', result)
    print(json.dumps(result, indent=2))


if __name__ == '__main__': main()
