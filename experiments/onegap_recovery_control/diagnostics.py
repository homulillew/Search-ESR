"""Descriptive decomposition only; never changes frozen scores or outputs."""
from collections import Counter
from .harness import read, write


def main():
    jobs = read('REQUESTS.json'); review = {r['id']: r for r in read('e1_actor/REVIEW.json')}
    variants = {v['id']: v for v in read('e0_state_bank/VARIANTS.json')}
    rows = []; action_counts = Counter(); http = Counter(); closure = []; bad_open = []
    for j in jobs:
        r = read('e1_actor/calls/' + j['id'] + '.result.json')
        http[str(r.get('http_status'))] += 1
        x = r.get('output'); a = x.get('action', {}) if isinstance(x, dict) else {}
        action_counts[a.get('type', 'MISSING')] += 1
        if a.get('type') == 'OPEN' and a.get('pattern') not in ('before', 'after'):
            sources = variants[j['id']]['state']['TraceView']['visited_sources']
            sources += variants[j['id']]['state']['TraceView']['pending_source_opportunities']
            bad_open.append({'id': j['id'], 'source_ref': a['source_ref'], 'pattern': a['pattern'],
                             'ref_visible': a['source_ref'] in {s['window_ref'] for s in sources},
                             'error': 'OPEN expects before/after; keyword is not silently interpreted as FIND'})
        if a.get('type') == 'REQUEST_CLOSURE_AUDIT': closure.append(j['id'])
        rows.append({**review[j['id']], 'condition': j['condition'], 'action_type': a.get('type')})
    p2 = [r for r in rows if r['condition'] == 'P2']
    changed = [r['id'] for r in p2 if r['material_route_change'] is True]
    changed_invalid = [r['id'] for r in p2 if r['material_route_change'] is True and not r['schema_valid']]
    write('analysis/DIAGNOSTICS.json', {
        'scope': 'Post-score descriptive decomposition; no relabeling, repair or gate substitution',
        'http_statuses': dict(http), 'parseable_json_outputs': sum(isinstance(read('e1_actor/calls/'+j['id']+'.result.json')['output'], dict) for j in jobs),
        'proposed_actions_all_including_invalid': dict(action_counts), 'open_contract_errors': bad_open,
        'closure_requests': closure, 'closure_requests_after_two_nogain': [x for x in closure if x.endswith('P2')],
        'semantically_changed_route_proposals_P2': {'ids': changed, 'numerator': len(changed), 'denominator': len(p2)},
        'changed_but_invalid_P2': changed_invalid,
        'failure_taxonomy': {
            'action_serialization': len(bad_open),
            'unsupported_premise': [r['id'] for r in rows if 'UNSUPPORTED_PREMISE' in r['tags']],
            'premature_closure_request': closure,
            'already_solved_recollection': [r['id'] for r in rows if 'ALREADY_SOLVED_RECOLLECTION' in r['tags']],
            'observed_same_route_after_nogain': [r['id'] for r in rows if 'SAME_ROUTE_AFTER_NOGAIN' in r['tags']],
            'query_only_paraphrase': [r['id'] for r in rows if 'QUERY_ONLY_PARAPHRASE' in r['tags']],
        },
        'ambiguity_sensitivity': 'Even if S02P1 reported-childlessness and S04P0 University-of-Minnesota narrowing were adjudicated leniently, unchanged schema31/42 and valid NoGain escape7/10 still fail. Primary labels are untouched.',
        'cache_interpretation': 'All42 complete consistent usage counters report hit0. Shared new-prefix concurrent cold requests are a plausible explanation, not an identified cause; no serialized/cache-warm control was run.',
        'causal_limit': 'P2 normal-to-perturbed pairs do not constitute actual multi-turn recovery; P3 changes preview packaging as well as source salience.'})


if __name__ == '__main__': main()
