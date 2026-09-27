"""Deterministic scoring of recorded semantic judgments; never labels semantics."""
import argparse
from .common import *
from .source_units import validate
def score(row, review, ref):
    expected={x['id'] for x in ref['material_units']};assert set(review['coverage'])==expected
    assert all(type(v) is bool for v in review['coverage'].values())
    material=sum(x['weight'] for x in ref['material_units'])
    covered=sum(x['weight']*review['coverage'][x['id']] for x in ref['material_units'])
    crit=[x for x in ref['material_units'] if x['importance']=='critical']
    critical=sum(review['coverage'][x['id']] for x in crit)
    assert set(review['dependency'])=={x['id'] for x in ref['dependency_checkpoints']}
    dep=sum(review['dependency'].values());n_dep=len(review['dependency'])
    types={t for x in review['critical_violations'] for t in x['types']}
    assert types <= {'relation_argument','role_identity','temporal','ownership','numeric'}
    inv=bool(review['invented_semantics'])
    return dict(id=row['id'],qid=row['qid'],arm=row['arm'],replicate=row['replicate'],review_id=review['review_id'],
      mechanical=bool(row['valid_output']),weighted_covered=covered,weighted_total=material,coverage=covered/material,
      critical_covered=critical,critical_total=len(crit),critical_coverage=critical/len(crit),
      dependency_covered=dep,dependency_total=n_dep,dependency=dep/n_dep if n_dep else 1,
      corruption=bool(types),corruption_types=sorted(types),invented=inv,broad=review['severe_broadness'],fragmented=review['severe_fragmentation'],
      harmful_merge=review['harmful_merge'],harmful_split=review['harmful_split'],
      strict=bool(row['valid_output'] and critical==len(crit) and covered/material>=.9 and not types and not inv and dep/n_dep>=.9 and not review['severe_broadness'] and not review['severe_fragmentation']))
def aggregate(rows,pairs):
    arms={}
    for arm in sorted({r['arm'] for r in rows}):
        rs=[r for r in rows if r['arm']==arm];n=len(rs);ps=[x for x in pairs if x['arm']==arm]
        rate=lambda k:sum(r[k] for r in rs)/n
        both=sum(all(r['strict'] for r in rs if r['qid']==x['qid']) for x in ps)
        stable=sum(all(r['strict'] for r in rs if r['qid']==x['qid']) and x['label'] in ('same_structure','compatible_structure') for x in ps)
        arms[arm]={'n':n,'qids':len(ps),'strict':rate('strict'),'strict_count':sum(r['strict'] for r in rs),
         'critical_coverage':rate('critical_coverage'),'critical_coverage_micro':sum(r['critical_covered'] for r in rs)/sum(r['critical_total'] for r in rs),
         'material_coverage':rate('coverage'),'material_coverage_micro':sum(r['weighted_covered'] for r in rs)/sum(r['weighted_total'] for r in rs),
         'dependency':rate('dependency'),'dependency_micro':sum(r['dependency_covered'] for r in rs)/sum(r['dependency_total'] for r in rs),
         'structural_corruption':rate('corruption'),'invented':rate('invented'),'severe_broad':rate('broad'),'severe_fragmentation':rate('fragmented'),
         'mechanical':rate('mechanical'),'both_strict':both/len(ps),'both_strict_count':both,'stability':stable/len(ps),'stable_count':stable,
         'harmful_merge':rate('harmful_merge'),'harmful_split':rate('harmful_split'),
         'error_rates':{t:sum(t in r['corruption_types'] for r in rs)/n for t in ('relation_argument','role_identity','temporal','ownership','numeric')},
         'relation_role_time_union':sum(bool(set(r['corruption_types']) & {'relation_argument','role_identity','temporal'}) for r in rs)/n}
    return arms
def gate(arms,stage):
    gs=read(P/'GATES.json');label='E1' if stage==STAGES[0] else 'E2';v=arms['D2'];checks={}
    for name,threshold in gs[label].items():
        field,way=name.rsplit('_',1);checks[name]={'value':v[field],'threshold':threshold,'pass':v[field]>=threshold-1e-12 if way=='min' else v[field]<=threshold+1e-12}
    if label=='E1':
        c=gs['E1_comparison'];ok=v['structural_corruption']<=arms['D0']['structural_corruption']-c['corruption_reduction_min']+1e-12 or v['structural_corruption']<=c['or_absolute_corruption_max']+1e-12
        checks['comparison_corruption']={'pass':ok,'D0':arms['D0']['structural_corruption'],'D2':v['structural_corruption']}
        checks['comparison_coverage']={'pass':v['material_coverage']>=arms['D0']['material_coverage']-c['coverage_loss_max']-1e-12,'D0':arms['D0']['material_coverage'],'D2':v['material_coverage']}
    else:checks['comparison_strict_direction']={'pass':v['structural_corruption']<arms['D0']['structural_corruption']-1e-12,'D0':arms['D0']['structural_corruption'],'D2':v['structural_corruption']}
    return {'pass':all(c['pass'] for c in checks.values()),'checks':checks}
def finalize(stage):
    from . import run
    run.STAGE=stage;run.OUT=P/stage
    reviews=read(P/stage/'review/FIRST_PASS.json');assert len(reviews)==len(run.load_rows())
    # Enforce a committed semantic pass before any arm-level aggregate.
    path=P/stage/'review/FIRST_PASS.json'
    assert __import__('subprocess').check_output(['git','show',git('rev-parse','HEAD')+':'+rel(path)],cwd=ROOT)==path.read_bytes()
    key=read(P/stage/'review/KEY.json');rs={key[r['review_id']]:r for r in reviews};refs=read(P/'e0_reference/REFERENCE_TASK_STRUCTURE.json')
    rows=[score(r,rs[r['id']],refs[r['qid']]) for r in run.load_rows()]
    pairs=read(P/stage/'review/PAIRS.json')
    assert {(r['qid'],r['arm']) for r in rows}=={(p['qid'],p['arm']) for p in pairs}
    assert len(pairs)*2==len(rows)
    for p in pairs:
        valid=sum(r['strict'] for r in rows if r['qid']==p['qid'] and r['arm']==p['arm'])
        assert p['label'] in ({'same_structure','compatible_structure','different_but_valid'} if valid==2 else {'one_valid_one_invalid'} if valid==1 else {'both_invalid'})
    arms=aggregate(rows,pairs)
    write(P/stage/'METRICS.json',{'arms':arms,'gate':gate(arms,stage),'rows':rows,'semantic_pass_commit':git('rev-parse','HEAD')})
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=STAGES);finalize(p.parse_args().stage)
