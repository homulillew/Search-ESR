"""Offline preparation/review CLI and separately authorized live stage entrypoints."""
import argparse
import asyncio
from pathlib import Path
from .harness import (HERE,read,save,digest,file_hash,bank,export_review,review_candidates,
    freeze_e2_candidates,run_e1,run_e2,run_e3)
from .transport import Transport,verify_freeze
from . import metrics

def artifact_freeze(stage,paths,call_ceiling,extra=None):
    return {'stage':stage,'experiment_freeze_sha256':file_hash(HERE/'FREEZE.json'),
        'files':{str(Path(p).resolve()):file_hash(p) for p in paths},
        'call_ceiling':call_ceiling,**(extra or {})}

def check_stage_freeze(path,stage,required):
    f=read(path)
    if f['stage']!=stage or f['experiment_freeze_sha256']!=file_hash(HERE/'FREEZE.json'):raise ValueError('stage freeze mismatch')
    if not {str(Path(p).resolve()) for p in required}<=set(f['files']):raise ValueError('required stage artifact not frozen')
    for p,h in f['files'].items():
        if file_hash(p)!=h:raise ValueError('stage input changed: '+p)
    return f

def export_inventories(run,out):
    out=Path(out);mapping=[]
    for f in sorted((Path(run)/'calls').glob('*.request.json')):
        req=read(f)
        if req['role']!='g1_evidence_inventory':continue
        result=f.with_name(f.name.replace('.request.json','.parsed.json'))
        if not result.exists():continue
        inv=read(result);payload=read_payload(req)
        rid='I_'+digest([f.name,payload,inv])[:24]
        save(out/'source'/f'{rid}.json',{'review_id':rid,'Observation':payload['Evidence'],'commitments':inv['facts']})
        mapping.append({'review_id':rid,'request_path':str(f.resolve()),'inventory_path':str(result.resolve()),'facts':len(inv['facts'])})
    save(out/'private_mapping.json',mapping)
    return mapping

def read_payload(req):
    import json
    return json.loads(req['request']['messages'][-1]['content'])

def check_inventory_review(mapping,labels):
    if {m['review_id'] for m in mapping}!=set(labels):raise ValueError('incomplete inventory review')
    for m in mapping:
        l=labels[m['review_id']]
        if len(l.get('facts',[]))!=m['facts']:raise ValueError('inventory fact review missing')
        for f in l['facts']:
            if type(f.get('source_supported')) is not bool or not f.get('reason'):raise ValueError('incomplete inventory fact support')
        if not isinstance(l.get('omitted_observed_commitments'),list) or not l.get('reason'):raise ValueError('inventory omission review missing')

async def live(args):
    verify_freeze();config=read(HERE/'CONFIG.json');stage=args.stage
    packets=bank(['D','H_diagnostic'] if stage=='E1' else ['H_confirmation'])
    sf=None
    if stage=='E2':
        sf=check_stage_freeze(args.stage_freeze,stage,[args.candidates]);pairs=read(args.candidates)['pairs']
        if not pairs or len(pairs)>60 or any(p['split']=='H_confirmation' for p in pairs):raise ValueError('invalid E2 bank')
        exact=2*len(pairs)+len({digest(p['Evidence']) for p in pairs})
        if sf['call_ceiling']!=exact:raise ValueError('E2 call estimate mismatch')
        config['stage_call_ceiling'][stage]=exact
        config['stage_independent_requests'][stage]=len(pairs)+len({digest(p['Evidence']) for p in pairs})
    if stage=='E3':
        sf=check_stage_freeze(args.stage_freeze,stage,[args.decision]);decision=read(args.decision)
        if not decision['eligible']:raise ValueError('E3 gate closed')
        if sf['call_ceiling']!=e3_ceiling(decision):raise ValueError('E3 budget mismatch')
        config['stage_call_ceiling'][stage]=sf['call_ceiling']
    port=Transport(config,args.out,stage,args.authorization,account_available=args.account_available)
    try:
        save(Path(args.out)/'EXECUTION_FREEZE.json',{'stage':stage,'experiment_freeze_sha256':file_hash(HERE/'FREEZE.json'),
            'authorization_sha256':file_hash(args.authorization),'stage_freeze':sf,'effective_config':config,'actual_head':port.head})
        if stage=='E1':results=await run_e1(port,packets)
        elif stage=='E2':results=await run_e2(port,pairs)
        else:
            results=await run_e3(port,packets,decision)
            results=[{**r,'construction_arm':r['arm'],'arm':r['pipeline']} for r in results]
        save(Path(args.out)/'RESULTS.json',results)
        if stage!='E2':export_review(packets,results,Path(args.out)/'review')
        if stage in ['E2','E3']:export_inventories(args.out,Path(args.out)/'inventory_review')
    finally:await port.close()

def e3_ceiling(decision):
    # Current per packet Reader+3 Grounding=4. Repaired 1/2 construction,
    # plus 3 admissions and, only for G1, one independent inventory.
    return 12*(4+(2 if decision['construction']=='A2' else 1)+3+(decision['grounding']=='G1'))

def main():
    ap=argparse.ArgumentParser(description=__doc__);sub=ap.add_subparsers(dest='command',required=True)
    sub.add_parser('preflight')
    run=sub.add_parser('run');run.add_argument('stage',choices=['E1','E2','E3'])
    for name in ['out','authorization']:run.add_argument('--'+name,required=True)
    for name in ['candidates','decision','stage-freeze']:run.add_argument('--'+name)
    run.add_argument('--account-available',type=int,default=256)
    for stage in ['e1','e3']:
        p=sub.add_parser('analyze-'+stage)
        for n in ['run','labels','report']:p.add_argument('--'+n,required=True)
    p=sub.add_parser('freeze-e2')
    for n in ['run','labels','e1-report','candidates','out']:p.add_argument('--'+n,required=True)
    p=sub.add_parser('analyze-e2')
    for n in ['run','candidates','inventory-labels','report']:p.add_argument('--'+n,required=True)
    p=sub.add_parser('freeze-e3')
    for n in ['e1-report','e2-report','decision','out']:p.add_argument('--'+n,required=True)
    args=ap.parse_args()
    if args.command=='preflight':
        f=verify_freeze();print({'status':'OFFLINE_READY_NEW_AUTHORIZATION_REQUIRED','packets':len(bank()),'freeze':file_hash(HERE/'FREEZE.json'),'semantic_calls':0});return
    if args.command=='run':asyncio.run(live(args));return
    verify_freeze()
    annotations=read(HERE/'bank/annotations.json')['packets']
    if args.command in ['analyze-e1','analyze-e3','freeze-e2']:
        e3=args.command=='analyze-e3';packets=bank(['H_confirmation'] if e3 else ['D','H_diagnostic'])
        results=read(Path(args.run)/'RESULTS.json');mapping=read(Path(args.run)/'review/private_mapping.json')
        reviewed=review_candidates(packets,results,mapping,read(args.labels))
        if args.command=='freeze-e2':
            report=read(args.e1_report)
            if not report['complete']:raise ValueError('E1 incomplete; gate stopped')
            expected=metrics.e1(packets,results,reviewed,annotations)
            if digest(report)!=digest(expected):raise ValueError('E1 report does not match current reviewed outputs')
            candidates=freeze_e2_candidates(reviewed,read(HERE/'bank/historical_candidates.json'))
            save(args.candidates,candidates)
            save(args.out,artifact_freeze('E2',[args.candidates,args.labels,args.e1_report,Path(args.run)/'RESULTS.json',Path(args.run)/'review/private_mapping.json'],candidates['calls']))
        else:save(args.report,metrics.e3(packets,results,reviewed,annotations) if e3 else metrics.e1(packets,results,reviewed,annotations))
    elif args.command=='analyze-e2':
        im=read(Path(args.run)/'inventory_review/private_mapping.json');il=read(args.inventory_labels);check_inventory_review(im,il)
        report=metrics.e2(read(args.candidates)['pairs'],read(Path(args.run)/'RESULTS.json'))
        report['inventory_review']={'labels_sha256':file_hash(args.inventory_labels),'inventories':len(im),
            'unsupported_facts':sum(not f['source_supported'] for v in il.values() for f in v['facts']),
            'inventory_omission_records':sum(bool(v['omitted_observed_commitments']) for v in il.values())}
        save(args.report,report)
    elif args.command=='freeze-e3':
        decision=metrics.integrated_decision(read(args.e1_report),read(args.e2_report))
        if not decision['eligible']:raise ValueError('no complete supported mechanism; E3 stopped')
        decision['report_hashes']={'E1':file_hash(args.e1_report),'E2':file_hash(args.e2_report)}
        save(args.decision,decision)
        save(args.out,artifact_freeze('E3',[args.e1_report,args.e2_report,args.decision],e3_ceiling(decision)))

if __name__=='__main__':main()
