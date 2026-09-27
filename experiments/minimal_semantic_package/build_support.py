"""New support references for the already-committed source-only packages."""
from collections import Counter
from .common import *

# Minimal sufficient witness subsets, not a promotion of every member Claim to
# standalone substantive support. Supersets within the actual ClaimSet suffice.
WITNESSES = {
'A02_CAND1': [['C2']], 'A02_CAND2': [['C2']],
'A03_CAND1': [['C2', 'C5'], ['C4', 'C5']], 'A03_CAND2': [['C4', 'C5']],
'A07_CAND1': [['C5']],
'A14_CAND1': [['C1', 'C3']], 'A14_CAND2': [['C1', 'C3']], 'A14_CAND3': [['C1', 'C3']],
'A17_CAND1': [['C7']], 'A17_CAND2': [['C7']], 'A17_CAND3': [['C7']],
'A19_CAND1': [['C3', 'C5']], 'A19_CAND2': [['C3', 'C5']], 'A19_CAND3': [['C3', 'C5']],
'A20_CAND1': [['C3', 'C4']], 'A20_CAND2': [['C3', 'C6']],
'A20_CAND3': [['C3', 'C4']], 'A20_CAND4': [['C3', 'C7']],
'A21_CAND1': [['C1', 'C2']], 'A21_CAND2': [['C1', 'C2']],
'A24_CAND1': [['C1', 'C3']],
}

# Anchors of material missing semantics, not an exhaustive token-level gold
# explanation. The primary gate uses support and witness eligibility, not exact
# matching of the model's missing-ID explanation to this list.
GAPS = {
'A01_CAND1': ([1], 'Professor identity does not establish two-person authorship.'),
'A02_CAND3': ([1], 'Paper content/tables do not establish two-person authorship.'),
'A03_CAND3': ([1], 'The singleton that-paper statement lacks a supplied concrete paper/table antecedent under the strict frozen binding reference.'),
'A04_CAND1': ([3,4,5,7], 'Game division/release/ranking and university-founding qualifications are not established.'),
'A05_CAND1': ([1,2,3], 'Founder/degree facts do not establish the spouse or 2019 childlessness.'),
'A06_CAND1': ([1,2,4], 'Person attendance does not establish the dated building-university affiliation.'),
'A07_CAND2': ([2,3], 'A 2025 family-status statement does not establish 2019 childlessness.'),
'A07_CAND3': ([4,5,6], 'Ding marriage does not establish the gift/building/complex predicates.'),
'A08_CAND1': ([1,2,3,4], 'Ding biography supplies no building schedule or affiliation.'),
'A09_CAND1': ([2], 'Artist identity does not establish an artist-charity shared-name relation.'),
'A10_CAND1': ([2,3], 'Death city alone supplies neither the required aviation site nor distance.'),
'A11_CAND1': ([2], 'Partner/tribute evidence does not establish a charity-name relation.'),
'A12_CAND1': ([3], 'The Canadian doctorate has no observed Iranian guidance relation.'),
'A13_CAND1': ([1,3], 'A book publication leaves the later article and its six-year relation unsupported.'),
'A14_CAND4': ([3,4], 'Article-only evidence lacks the book operand/date needed for the interval.'),
'A15_CAND1': ([1], 'Euler birth attributes do not establish that the source references him.'),
'A16_CAND1': ([1,4,6], 'Generic SPS progression is not an individual half-year clinical case.'),
'A17_CAND4': ([2,3], 'Patient nationality supplies neither report-country attribution nor country-history qualification.'),
'A17_CAND5': ([1,4,6], 'Generic FOP genetics/trauma facts do not establish the specific clinical history.'),
'A18_CAND1': ([1,2,3,4], 'Thesis/advisor facts do not establish DLC release, game genre or interval.'),
'A19_CAND4': ([3,4], 'DLC date alone lacks base-game genre/date and the interval.'),
'A20_CAND5': ([7,8], 'Ottoman details do not establish new mechanics for a specific playable European nation.'),
'A20_CAND6': ([7,8], 'Local DLC changes leave the qualified playable-European-nation condition unsupported.'),
'A21_CAND3': ([2,4], 'Australian coder identity lacks the championship-team relation.'),
'A22_CAND1': ([2], 'Jerry nationality and teammate names do not establish the other two teammates same-country relation.'),
'A23_CAND1': ([1,2,3], 'Memo transmission date is not letter-writing date; accession timing is also absent.'),
'A24_CAND2': ([3], 'Selected C2/C3 mention Michael and Romania but never establish Romania as the letter author country. Do not borrow withheld C1 or outside knowledge.'),
}
AMBIGUOUS = {
'A03_CAND3': 'AMBIGUOUS_REFERENCE: strict antecedent binding versus existential reading of the singleton that-paper claim; primary OPEN.',
'A14_CAND2': 'AMBIGUOUS_REFERENCE: calendar publication years versus exact elapsed days; primary SUPPORTED under the year-level convention.',
'A20_CAND4': 'AMBIGUOUS_REFERENCE: general mechanics predicate can be separated from enumerated particular changes; primary SUPPORTED under the task local-positive convention.',
'A24_CAND2': 'AMBIGUOUS_REFERENCE: letter author-country shorthand versus explicit binding; primary OPEN. Previous experiment label is preserved separately, not edited.',
}

def main():
    freeze = P/'e0_reference/BOUNDARY_FREEZE.json'
    committed(freeze)
    for path, h in read(freeze)['files'].items():
        assert sha(ROOT/path) == h
        committed(ROOT/path)
    packages = read(P/'e0_reference/GOLD_PACKAGES.json')
    parents = read(P/'e0_reference/UNITS.json')
    parent_by_cell = {cell: p for p in parents for cell in p['cell_ids']}
    pack = {(p['parent_id'],p['candidate_locator']): p for p in packages}
    historical = read(P/'e0_reference/HISTORICAL_CERTIFICATES.json')
    assert set(WITNESSES).isdisjoint(GAPS)
    assert set(WITNESSES) | set(GAPS) == {c['certificate_id'] for c in historical}
    rows, changes = [], []
    for c in historical:
        cid = c['certificate_id']
        par = parent_by_cell[c['cell_id']]
        pkg = pack[par['parent_id'], c['candidate_locator']]
        positive = cid in WITNESSES
        witnesses = WITNESSES.get(cid, [])
        for witness in witnesses:
            assert set(witness) <= set(c['candidate_claim_ids']) and witness
        gap_ids = [f'U{i}' for i in GAPS[cid][0]] if not positive else []
        assert set(gap_ids) <= set(pkg['target_unit_ids'])
        reason = (pkg['gold_reason']+' The supplied Claims jointly establish the selected target on the observed candidate branch; no sibling is thereby discharged.') if positive else GAPS[cid][1]
        row = {k: c[k] for k in ('certificate_id','cell_id','case_id','qid','candidate_locator','candidate_claim_ids','candidate_verified_claims','case_tags')}
        row.update(package_id=pkg['package_id'], parent_id=par['parent_id'],
                   gold_support='SUPPORTED' if positive else 'OPEN',
                   minimal_sufficient_claim_sets=witnesses,
                   material_gap_anchor_unit_ids=gap_ids, gold_reason=reason,
                   ambiguity_reason=AMBIGUOUS.get(cid),
                   false_full_risk=c['false_full_risk'] or cid == 'A24_CAND2',
                   historical_category=c['category'],
                   historical_gold_verdict=c['gold_verdict'],
                   boundary_commit=git('rev-parse','HEAD'))
        rows.append(row)
        if positive != (c['gold_verdict']=='SUBTRACTABLE'):
            changes.append({'certificate_id':cid,'old_verdict':c['gold_verdict'],
                            'new_verdict':row['gold_support'],'reason':reason,
                            'historical_file_edited':False})
    assert len(rows)==48 and sum(r['gold_support']=='SUPPORTED' for r in rows)==21
    write(P/'e0_reference/SUPPORT_REFERENCES.json', rows)
    write(P/'e0_reference/REFERENCE_CHANGES.json', changes)
    write(P/'e0_reference/BANK_COUNTS.json',{
        'certificates':len(rows),'cells':len({r['cell_id'] for r in rows}),
        'natural_snapshots':len({s['state_id'] for s in read(P/'e0_reference/STATES.json')}),
        'qids':len({r['qid'] for r in rows}),'parents':len(parents),'unique_packages':len(packages),
        'units':sum(len(p['units']) for p in parents),
        'support_labels':dict(Counter(r['gold_support'] for r in rows)),
        'support_reference_ambiguous_certificates':list(AMBIGUOUS),
        'nonempty_context_packages':sum(bool(p['interpretive_context_unit_ids']) for p in packages),
        'false_full_risk_certificates':sum(r['false_full_risk'] for r in rows),
        'new_reference_changes':len(changes),'new_model_calls':0,
    })
    print(read(P/'e0_reference/BANK_COUNTS.json'))

if __name__ == '__main__':
    main()
