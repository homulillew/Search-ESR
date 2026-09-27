"""Commit first-pass visible-mask judgments before frozen-reference aggregation."""
import argparse
from .common import *
from .run import OUT, audit, load_rows, schedule
from .selection import selection_metrics,evaluate_gates

def seal_review():
    assert not (OUT/'METRICS.json').exists()
    packets=read(OUT/'review/PACKETS.json');judgments=read(OUT/'review/JUDGMENTS.json')
    assert set(judgments)=={p['review_id'] for p in packets} and len(packets)==108
    allowed=set(read(P/'SCHEMAS.json')['review_error_codes'])
    for judgment in judgments.values():
        assert isinstance(judgment['reason'],str) and judgment['reason'].strip()
        assert judgment['selection_appropriate_under_visible_mask'] is None or type(judgment['selection_appropriate_under_visible_mask']) is bool
        assert set(judgment['error_codes'])<=allowed
    paths=[OUT/'review'/n for n in ('PACKETS.json','KEY.json','JUDGMENTS.json')]
    for path in paths:committed(path)
    write(OUT/'review/REVIEW_SEAL.json',{'judgment_commit':git('rev-parse','HEAD'),'files':{rel(p):sha(p) for p in paths},
        'scope':'Single familiar Codex reviewer; masked packets, no independent-review or erased-memory claim.'})

def assert_review():
    seal=read(OUT/'review/REVIEW_SEAL.json')
    for name,h in seal['files'].items():
        assert sha(ROOT/name)==h;committed(ROOT/name,seal['judgment_commit'])

def calculate():
    refs={r['case_id']:r for r in read(OUT/'SELECTION_REFERENCE.json')};jobs={j['id']:j for j in schedule()};rows=load_rows()
    states={s['case_id']:s for s in read(OLD/'e0_reference/STATES.json')}
    address={r['case_id']:r['status'] for r in read(OLD/'e0_addressability/ADDRESSABILITY.json') if r['skeleton_arm']=='D2'}
    arms={}
    for arm in ('S0','S1'):
        sub=[r for r in rows if r['arm']==arm];strata={}
        for field,get in [('qid',lambda r:r['qid']),('replicate',lambda r:r['replicate']),('claims_empty',lambda r:not states[r['case_id']]['claims']),('addressability',lambda r:address[r['case_id']])]:
            strata[field]={str(v):selection_metrics([r for r in sub if get(r)==v],jobs,refs) for v in sorted({get(r) for r in sub},key=str)}
        arms[arm]={**selection_metrics(sub,jobs,refs),'strata':strata}
    loss=arms['S0']['metrics']['valid_selection']['value']-arms['S1']['metrics']['valid_selection']['value']
    for arm in arms:arms[arm]['gate']=evaluate_gates(arms[arm]['metrics'],read(P/'GATES.json')[arm],loss)
    return {'arms':arms,'selection_loss':loss,'joint_gate_pass':all(v['gate']['pass'] for v in arms.values()),
      'stop_positive_controls':sum(r['stop_allowed'] for r in refs.values()),'ceiling':metric(25,27),
      'new_rollout_authorized':False,'mandatory_stop':'after this selection batch'}

def aggregate():
    audit();assert_review();value=calculate();write(OUT/'METRICS.json',value)
    write(OUT/'REPORT.md','# E1 selection\n\nJoint gate: '+('PASS' if value['joint_gate_pass'] else 'FAIL')+'.\n\nSee METRICS.json for every frozen metric, denominator, qid/replicate/addressability strata and stability. Stop: no Gap, tools, Writer or rollout.\n')
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['seal_review','aggregate']);args=parser.parse_args();globals()[args.mode]()
