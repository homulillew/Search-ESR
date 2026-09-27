"""Post-score descriptive diagnostics; never alter frozen gates or references."""
from collections import Counter
from .common import P, read, write, metric
from .run import load_rows
from .score import aggregate, gate


def main():
    m = read(P/'e1_qualification/METRICS.json')
    refs = {c['certificate_id']: c for c in read(P/'e0_reference/CERTIFICATES.json')}
    rows = load_rows()
    by_id = {r['id']: r for r in rows}
    by_slot = {(r['certificate_id'], r['arm'], r['replicate']): r for r in rows}
    cards = []
    for cid, c in refs.items():
        d = {k: c[k] for k in ('certificate_id', 'cell_id', 'qid', 'category', 'gold_verdict', 'case_tags', 'ambiguity_reason', 'false_full_risk')}
        for arm in ('Q0', 'Q1'):
            rr = [by_slot[cid, arm, rep] for rep in (1, 2)]
            d[arm] = {'accepted': sum(r['output']['verdict'] == 'SUBTRACTABLE' for r in rr),
                      'denominator': len(rr), 'verdicts': [r['output']['verdict'] for r in rr]}
        cards.append(d)
    pairs = []
    for d in read(P/'analysis/PAIRED_DIAGNOSTIC_DESIGN.json')['pairs']:
        p = dict(d)
        for arm in ('Q0', 'Q1'):
            a = [by_slot[d['first'], arm, rep] for rep in (1, 2)]
            b = [by_slot[d['second'], arm, rep] for rep in (1, 2)]
            p[arm] = {'first_accept': metric(sum(r['output']['verdict'] == 'SUBTRACTABLE' for r in a), len(a)),
                       'second_accept': metric(sum(r['output']['verdict'] == 'SUBTRACTABLE' for r in b), len(b)),
                       'both_reference_verdicts_correct': metric(sum(x['output']['verdict'] == d['first_gold'] and y['output']['verdict'] == d['second_gold'] for x, y in zip(a, b)), 2)}
        pairs.append(p)
    transitions = {}
    for label, gold in [('all', None), ('gold_positive', 'SUBTRACTABLE'), ('gold_negative', 'NOT_SUBTRACTABLE')]:
        counts = Counter()
        for cid, c in refs.items():
            if gold is not None and c['gold_verdict'] != gold:
                continue
            for rep in (1, 2):
                a, b = by_slot[cid, 'Q0', rep], by_slot[cid, 'Q1', rep]
                good0 = a['valid_output'] and a['output']['verdict'] == c['gold_verdict']
                good1 = b['valid_output'] and b['output']['verdict'] == c['gold_verdict']
                counts['both_correct' if good0 and good1 else 'Q1_loses' if good0 else 'Q1_gains' if good1 else 'both_wrong'] += 1
        transitions[label] = dict(counts)
    errors = []
    for r in m['ledger']:
        j = r['judgment']
        if r['gold'] == r['predicted']:
            continue
        assert j['diagnostic'] != 'consistent', r['id']
        errors.append({**r, 'actual_content_output': by_id[r['id']]['output']})
    exclusion = {c['certificate_id'] for c in refs.values() if c['ambiguity_reason']} | {'A24_CAND2'}
    sensitivity = aggregate([r for r in rows if r['certificate_id'] not in exclusion], refs)
    tags = sorted({t for c in refs.values() for t in c['case_tags']})
    strata = {t: aggregate([r for r in rows if t in refs[r['certificate_id']]['case_tags']], refs) for t in tags}
    result = {'status': 'descriptive post-score diagnostics; no gate replacement',
              'by_certificate': cards, 'paired_contrasts': pairs,
              'matched_Q0_Q1_correctness': transitions,
              'by_case_tag': strata,
              'errors_with_content': errors,
              'error_taxonomy_counts': {arm: dict(Counter(r['judgment']['diagnostic'] for r in errors if r['arm'] == arm)) for arm in ('Q0', 'Q1')},
              'predeclared_ambiguity_exclusion_gate_if_applied': gate(m['nonambiguous_sensitivity']),
              'additional_posthoc_letter_reference_sensitivity': {
                  'excluded_certificates': sorted(exclusion),
                  'reason': 'three predeclared ambiguities plus the selected letter pair whose literal claims omit author-country rulership',
                  'metrics': sensitivity, 'gate_if_applied': gate(sensitivity),
                  'not_primary': True},
              'E2': 'NOT_RUN_E1_GATE_FAILED', 'E3': 'NOT_RUN_E1_GATE_FAILED'}
    write(P/'analysis/DIAGNOSTICS.json', result)
    for arm in ('Q0', 'Q1'):
        v = sensitivity[arm]
        print('posthoc sensitivity', arm, v['subtraction_precision'], v['subtraction_recall'])
    print('transitions', transitions)
    print('taxonomy', result['error_taxonomy_counts'])
    for qid, arms in m['by_qid'].items():
        print('qid', qid, {a: {k: v[k] for k in ('planned', 'TP', 'FP', 'TN', 'missed_positives')} for a, v in arms.items()})


if __name__ == '__main__':
    main()
