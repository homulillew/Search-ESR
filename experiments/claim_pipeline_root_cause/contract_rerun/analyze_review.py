"""Offline reporting only; frozen metrics/labels and historical files are untouched."""
import json
import re
from collections import Counter
from .contracts import HERE, BASE, ROOT, read, save, file_hash
from .runner import verify_freeze
from ..harness import bank, normalize, freeze_e2_candidates
from ..metrics import fraction, mean


def main():
    verify_freeze()
    out = HERE / 'review'
    packets = bank(['D', 'H_diagnostic'])
    by = {p['packet_id']: p for p in packets}
    reviewed = read(out / 'REVIEWED.json')
    primary = read(out / 'E1_METRICS.json')
    results = read(HERE / 'run002/RESULTS.json')
    annotations = {a['packet_id']: a for a in read(BASE / 'bank/annotations.json')['packets']}
    assert primary['complete'] and len(results) == 72
    for stage in ['source', 'relevance', 'atoms']:
        for path, sha in read(out / (stage + '_FREEZE.json'))['files'].items():
            assert file_hash(HERE / path) == sha

    # Complete compound atoms can be expressed across two supported candidates.
    # These two offline packet-level judgments supplement, never replace, the
    # individually frozen candidate labels or the unchanged primary algorithm.
    joint = [
        {'packet_id': 'P_5f891a4579a59d87', 'arm': 'A1',
         'atom_id': 'P_5f891a4579a59d87_U1',
         'review_ids': ['B_6ac007329ae08481e46814f8', 'B_f3b9525d73a4f3bdd02c0cae'],
         'reason': 'Both claims explicitly refer to the same D4 patient. One gives sixteen-year-old male; the other gives classic FOP. Together they cover U1 without supplying an unobserved relation.'},
        {'packet_id': 'P_0a49c4e89489de08', 'arm': 'A2',
         'atom_id': 'P_0a49c4e89489de08_U3',
         'review_ids': ['B_ef5a5f2d738e3e1e46fa1a59', 'B_2c33b65802bb4a974ceb113f'],
         'reason': 'Both claims name Ahebi Ugbabe in the same description. The book/Igbo woman/kingship clause and multilingual clause jointly cover U3.'},
    ]
    indexed = {c['review_id']: c for c in reviewed}
    for j in joint:
        for rid in j['review_ids']:
            c = indexed[rid]
            assert c['packet_id'] == j['packet_id'] and c['arm'] == j['arm']
            assert c['source_supported'] and c['gap_relevant'] and not c['duplicate_with_C']
        assert j['atom_id'] in {a['atom_id'] for a in annotations[j['packet_id']]['required_atoms']}
    save(out / 'PACKET_JOINT_ATOM_REVIEW.json', {
        'phase': 'post-unblinding whole-output sensitivity; no new atom or denominator',
        'judgments': joint,
        'limitation': 'Same Codex reviewer; this supplement is not a newly preregistered gate.',
    })

    mode_rows = []
    for r in results:
        p = by[r['packet_id']]
        cs = sorted([c for c in reviewed if c['packet_id'] == r['packet_id'] and c['arm'] == r['arm']], key=lambda c: c['index'])
        for mode in ['raw', 'exact', 'semantic']:
            seen = {normalize(c['statement']) for c in p['C']}; groups = set(); kept = []
            for c in cs:
                text = normalize(c['candidate']['statement'])
                group = c['duplicate_group'] or 'single:' + str(c['index'])
                if mode != 'raw' and (text in seen or (mode == 'semantic' and (c['duplicate_with_C'] or group in groups))):
                    continue
                kept.append(c); seen.add(text); groups.add(group)
            coverage = set().union(*(set(c['covered_atom_ids']) for c in kept if c['source_supported'] and c['gap_relevant'])) if kept else set()
            joint_coverage = set(coverage)
            for j in joint:
                if (j['packet_id'], j['arm']) == (p['packet_id'], r['arm']) and set(j['review_ids']) <= {c['review_id'] for c in kept}:
                    joint_coverage.add(j['atom_id'])
            a = annotations[p['packet_id']]
            mode_rows.append(dict(packet_id=p['packet_id'], qid=p['qid'], split=p['split'], arm=r['arm'], mode=mode,
                count=len(kept), strengthened=sum(c['semantic_strengthening'] and not c['source_supported'] for c in kept),
                supported=sum(c['source_supported'] for c in kept), relevant=sum(c['gap_relevant'] for c in kept),
                new_useful=sum(c['source_supported'] and c['gap_useful_if_supported'] for c in kept),
                covered=len(coverage), joint_covered=len(joint_coverage), required=len(a['required_atoms']),
                silence_eligible=a['correct_silence_primary_eligible'], silent=not kept,
                offgap_silence_eligible=not a['required_atoms'] and not a['correct_silence_primary_eligible']))
    def aggregate(rows):
        n = sum(x['count'] for x in rows)
        return {'packets': len(rows), 'candidates': n,
            'FSSR': fraction(sum(x['strengthened'] for x in rows), n),
            'SSP': fraction(sum(x['supported'] for x in rows), n),
            'gap_relevance': fraction(sum(x['relevant'] for x in rows), n),
            'new_useful_precision': fraction(sum(x['new_useful'] for x in rows), n),
            'GRSR_individual': fraction(sum(x['covered'] for x in rows), sum(x['required'] for x in rows)),
            'GRSR_joint_sensitivity': fraction(sum(x['joint_covered'] for x in rows), sum(x['required'] for x in rows)),
            'correct_silence': fraction(sum(x['silent'] and x['silence_eligible'] for x in rows), sum(x['silence_eligible'] for x in rows)),
            'offgap_silence_separate': fraction(sum(x['silent'] and x['offgap_silence_eligible'] for x in rows), sum(x['offgap_silence_eligible'] for x in rows)),
            'bloat': fraction(n, len(rows))}
    tables = {s: {m: {a: aggregate([x for x in mode_rows if x['mode'] == m and x['arm'] == a and (s == 'pooled' or x['split'] == s)])
        for a in ['A0', 'A1', 'A2']} for m in ['raw', 'exact', 'semantic']} for s in ['pooled', 'D', 'H_diagnostic']}
    for s, arms in primary['tables'].items():
        for a, metrics in arms.items():
            assert tables[s]['raw'][a]['FSSR'] == metrics['FSSR']
            assert tables[s]['semantic'][a]['GRSR_individual'] == metrics['GRSR']
    save(out / 'DEDUP_AND_JOINT_SENSITIVITY.json', {'tables': tables, 'packet_rows': mode_rows})

    # Inspect only protocol-defined machine fields, never classify source prose.
    requests = [read(f) for f in sorted((HERE / 'run002/calls').glob('*.request.json'))]
    residue = []; field_sets = Counter()
    for r in requests:
        u = json.loads(r['request']['messages'][1]['content'])
        for w in u.get('Observation', u.get('Evidence', [])):
            assert set(w) <= {'window_ref', 'doc_ref', 'title', 'url', 'text', 'date'}
            assert re.fullmatch(r'W[1-9][0-9]*', w['window_ref'])
            field_sets[','.join(sorted(w))] += 1
        for c in u.get('C', []):
            for ref in c.get('evidence_refs', []):
                if re.fullmatch(r'w_[0-9a-f]+', ref):
                    residue.append({'packet_id': r['packet_id'], 'role': r['role'], 'claim_id': c['claim_id'], 'ref': ref})
    save(out / 'CONTRACT_SCOPE_AUDIT.json', {
        'requests': len(requests), 'evidence_field_sets': dict(field_sets),
        'evidence_alias_fields_exposed': 0, 'output_contract_failures': 0,
        'historical_C_private_ref_occurrences': residue,
        'interpretation': 'Evidence W/private alias pairs are removed. Frozen C remains verbatim and one historical C item retains a private ref in two requests. Therefore whole-payload absence of private handles is NOT established. No runtime acceptance or posthoc alias mapping uses it.',
    })
    # Compute a future budget from original deterministic rules; do not create an
    # E2 freeze, send calls, or read confirmation data into any semantic role.
    future = freeze_e2_candidates(reviewed, read(BASE / 'bank/historical_candidates.json'))
    save(out / 'E2_PLAN_ESTIMATE_ONLY.json', {'not_an_execution_freeze': True, 'authorized': False,
        'pairs': future['count'], 'inventories': future['inventory_count'], 'calls_if_later_authorized': future['calls'],
        'strata': {s: {str(b): sum(p['split'] == s and p['label']['source_supported'] == b for p in future['pairs']) for b in [True, False]} for s in ['D', 'H_diagnostic']}})
    selection = []
    for r in results:
        if r['arm'] != 'A2': continue
        p = by[r['packet_id']]; a = annotations[p['packet_id']]
        selection.append({'packet_id': p['packet_id'], 'qid': p['qid'], 'required': len(a['required_atoms']),
            'selected': bool(r['selections']), 'findings': len(r['findings'])})
    save(out / 'SELECTION_DIAGNOSTIC.json', {'rows': selection,
        'positive_packets': sum(x['required'] > 0 for x in selection),
        'positive_packets_selected': sum(x['required'] > 0 and x['selected'] for x in selection),
        'selected_formulators': sum(x['selected'] for x in selection),
        'three_findings_formulators': sum(x['findings'] == 3 for x in selection)})
    save(out / 'ERROR_CATALOG.json', [{k: c[k] for k in ['review_id', 'packet_id', 'qid', 'arm', 'candidate', 'strengthening_type', 'ambiguous_relation', 'reason']} for c in reviewed if not c['source_supported']])
    print(json.dumps({'pooled_sensitivity': tables['pooled'], 'legacy_C_residue': residue,
        'E2_plan_calls_only': future['calls']}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
