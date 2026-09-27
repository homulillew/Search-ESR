"""Offline aggregation of completed semantic reviews; never an automatic judge."""
from collections import Counter
import json
from .prepare import P, read, write
from .run import DIMENSIONS, accounting_summary, load_rows

def validate_review(row, review):
    if set(review['dimensions']) != set(DIMENSIONS):
        raise ValueError('Missing dimensions')
    if not isinstance(review['reason'], str) or not review['reason'].strip():
        raise ValueError('Review reason required')
    codes = review['codes']
    if not isinstance(codes, list) or len(codes) != len(set(codes)) or not set(codes) <= set('PAWQSRX'):
        raise ValueError('Invalid codes')
    dims = review['dimensions']
    if not row['valid_output']:
        if codes != ['X'] or any(v is not None for v in dims.values()):
            raise ValueError('Missing output has unknown semantics, not a semantic success')
        return False
    if 'X' in codes or any(type(v) is not bool for v in dims.values()):
        raise ValueError('Valid output requires six semantic judgments')
    strict = all(dims.values())
    if strict != (not codes):
        raise ValueError('Labels inconsistent with dimensions')
    required_false = {'P': 'PremiseClosed', 'A': 'Grounded', 'W': 'Coherent', 'S': 'Unresolved', 'R': 'Relevant', 'Q': 'Actionable'}
    for code in codes:
        if dims[required_false[code]]:
            raise ValueError('Code/dimension mismatch: ' + code)
    if review.get('ambiguity') not in ('low', 'medium', 'high'):
        raise ValueError('Semantic ambiguity required')
    if not isinstance(review.get('premise_anchors'), list) or not isinstance(review.get('objective_decomposition'), list) or not review['objective_decomposition']:
        raise ValueError('Offline premise/objective analysis required')
    return strict

def counts(rows):
    n = len(rows)
    returned = sum(r['valid_output'] for r in rows)
    strict = sum(r['strict_valid'] for r in rows)
    c = Counter(k for r in rows for k in r['codes'])
    return {'n': n, 'valid_output': returned, 'strict_valid': strict,
            'strict_rate': strict / n if n else None,
            'strict_given_output': strict / returned if returned else None,
            'codes': {k: c[k] for k in 'PAWQSRX'}, 'pa_union': sum(bool(set(r['codes']) & {'P', 'A'}) for r in rows),
            'p_plus_a_sum': c['P'] + c['A']}

def fresh_gate(b0, b3, qid_count, eligible_fresh):
    n = b3['n']
    checks = {'eligible_fresh_bank': eligible_fresh is True, 'qid_count': 12 <= qid_count <= 15,
              'state_count': 30 <= n <= 40, 'paired_denominator': b0['n'] == n,
              'strict_80': 5 * b3['strict_valid'] >= 4 * n if n else False,
              'pa_5': 20 * b3['p_plus_a_sum'] <= n if n else False,
              'w_10': 10 * b3['codes']['W'] <= n if n else False,
              'gain_15pp': 20 * (b3['strict_valid'] - b0['strict_valid']) >= 3 * n if n else False}
    return {'status': 'PASS' if all(checks.values()) else 'FAIL', 'checks': checks}

def mechanism_gate(metrics):
    b0, b1, b2, b3 = (metrics[a] for a in ('B0', 'B1', 'B2', 'B3'))
    checks = {
        'execution_at_least90_each': all(10 * m['valid_output'] >= 9 * m['n'] for m in metrics.values()),
        'B1_PA_drop2': b0['pa_union'] - b1['pa_union'] >= 2,
        'B1_W_stable': abs(b0['codes']['W'] - b1['codes']['W']) <= 1,
        'B2_W_drop1': b0['codes']['W'] - b2['codes']['W'] >= 1,
        'B2_PA_stable': abs(b0['pa_union'] - b2['pa_union']) <= 1,
        'B3_PA_drop2': b0['pa_union'] - b3['pa_union'] >= 2,
        'B3_W_drop1': b0['codes']['W'] - b3['codes']['W'] >= 1,
        'B3_strict_gain2': b3['strict_valid'] - b0['strict_valid'] >= 2}
    return {'status': 'PATTERN_SUPPORTED_REVIEW_BEFORE_FRESH' if all(checks.values()) else 'STOP_FOR_MECHANISM_ANALYSIS',
            'checks': checks, 'opens_E2': False, 'bounded_revisions_max': 1}

def summarize(rows, reviews, bank):
    if set(reviews) != {r['id'] for r in rows}:
        raise ValueError('Review coverage does not match scheduled denominator')
    scored = []
    for r in rows:
        v = reviews[r['id']]
        scored.append({**r, 'strict_valid': validate_review(r, v), 'codes': v['codes'],
                       'no_h': not bank[r['state_id']]['belief']['hypothesis']})
    by_arm = {a: counts([r for r in scored if r['arm'] == a]) for a in ('B0', 'B1', 'B2', 'B3')}
    no_h = {a: counts([r for r in scored if r['arm'] == a and r['no_h']]) for a in by_arm}
    by_qid = {q: {a: counts([r for r in scored if r['arm'] == a and r['qid'] == q]) for a in by_arm} for q in sorted({r['qid'] for r in scored}, key=int)}
    indexed = {(r['arm'], r['state_id']): r for r in scored}
    paired = {}
    for a in ('B1', 'B2', 'B3'):
        cells = [(indexed['B0', sid], indexed[a, sid]) for sid in bank]
        paired[a] = {'strict_gain_ids': [x['state_id'] for x, y in cells if not x['strict_valid'] and y['strict_valid']],
                     'strict_loss_ids': [x['state_id'] for x, y in cells if x['strict_valid'] and not y['strict_valid']],
                     'both_output': sum(x['valid_output'] and y['valid_output'] for x, y in cells),
                     'both_output_strict_B0': sum(x['strict_valid'] for x, y in cells if x['valid_output'] and y['valid_output']),
                     'both_output_strict_treatment': sum(y['strict_valid'] for x, y in cells if x['valid_output'] and y['valid_output'])}
    return {'cohort': 'exposed_development_NOT_FRESH', 'by_arm': by_arm, 'no_h': no_h, 'by_qid': by_qid,
            'paired': paired, 'mechanism_gate': mechanism_gate(by_arm), 'accounting': accounting_summary(rows),
            'accounting_by_arm': {a: accounting_summary([r for r in rows if r['arm'] == a]) for a in by_arm},
            'fresh_gate': 'NOT_RUN', 'E2': 'BLOCKED_PENDING_FRESH_GATE', 'scored': scored}

def main():
    out = P / 'e1_need/development_run'
    jobs = read(P / 'e1_need/SCHEDULE.json')
    key = read(out / 'review/SEALED_KEY.json')
    review = read(out / 'review/REVIEW.json')
    if set(review) != set(key):
        raise ValueError('Masked review incomplete')
    bank = {s['state_id']: s for s in read(P / 'e1_need/BANK.json')}
    result = summarize(load_rows(out, jobs), {key[k]: v for k, v in review.items()}, bank)
    write(out / 'METRICS.json', result)
    print(json.dumps(result['mechanism_gate'], indent=2))

if __name__ == '__main__':
    main()
