"""Fresh E2 only; no E3 entry point and no resume mode."""
import argparse
import asyncio
import subprocess
from pathlib import Path
from ..harness import inputs, freeze_e2_candidates
from .contracts import HERE, BASE, ROOT, read, save, digest, file_hash, project_payload, request

def verify_freeze():
    f=read(HERE/'EXECUTION_FREEZE.json')
    for p,h in f['files'].items():
        if file_hash(ROOT/p)!=h:raise ValueError('frozen file changed: '+p)
    b=freeze_e2_candidates(read(BASE/'contract_rerun/review/REVIEWED.json'),read(BASE/'bank/historical_candidates.json'))
    if b!=read(HERE/'CANDIDATE_BANK.json'):raise ValueError('bank not deterministic reproduction')
    return f

def authorize(path,stage):
    verify_freeze();a=read(path)
    if stage!='E2' or a.get('stages')!=['E2'] or not a.get('authorized'):raise PermissionError('E2 only')
    if a['freeze_sha256']!=file_hash(HERE/'EXECUTION_FREEZE.json'):raise PermissionError('authorization freeze changed')
    if a['task_sha256']!=file_hash(HERE/'TASK.md') or a['call_ceiling']!=85:raise PermissionError('authorization mismatch')
    return a

def make_plan(pairs,config):
    inventory={};rows=[]
    for p in pairs:
        key=digest(p['Evidence'])
        payload=inputs('g1_evidence_inventory',windows=p['Evidence'])
        req=request('g1_evidence_inventory',payload,config)
        if key not in inventory:
            inventory[key]={'request_id':'E2_I_'+key[:24],'role':'g1_evidence_inventory','evidence_key':key,
                'request_hash':digest(req),'public_evidence_hash':digest(project_payload('g1_evidence_inventory',payload)['Evidence'])}
        rows.append({'request_id':p['pair_id']+'_G0','role':'g0_current_grounding','pair_id':p['pair_id'],
            'request_hash':digest(request('g0_current_grounding',inputs('g0_current_grounding',candidate=p['candidate'],windows=p['Evidence']),config))})
        rows.append({'request_id':p['pair_id']+'_G1','role':'g1_candidate_coverage','pair_id':p['pair_id'],
            'evidence_key':key,'candidate_sha256':digest(p['candidate']),
            'dependency':'E2_I_'+key[:24],'request_hash':'computed and archived after frozen inventory exists'})
    if len({r['request_hash'] for r in inventory.values()})!=len(inventory):raise ValueError('duplicate public inventory request')
    return list(inventory.values())+rows

async def run_e2(port,pairs):
    # Create all independent requests first. Linked candidates remain private metadata.
    inventory={}
    for p in pairs:
        key=digest(p['Evidence'])
        if key not in inventory:
            linked=[x for x in pairs if digest(x['Evidence'])==key]
            meta={'stage':'E2','arm':'G1_inventory','evidence_key':key,'pair_ids':[x['pair_id'] for x in linked]}
            inventory[key]=asyncio.create_task(port.call('E2_I_'+key[:24],'g1_evidence_inventory',inputs('g1_evidence_inventory',windows=p['Evidence']),meta))
    async def one(p,arm):
        key=digest(p['Evidence'])
        meta={'stage':'E2','pair_id':p['pair_id'],'qid':p['qid'],'split':p['split'],'arm':arm,'evidence_key':key}
        try:
            if arm=='G0':
                role='g0_current_grounding';payload=inputs(role,candidate=p['candidate'],windows=p['Evidence'])
            else:
                inv=await inventory[key]
                # Independent transport check also verifies this archive before dispatch.
                role='g1_candidate_coverage';payload=inputs(role,candidate=p['candidate'],inventory=inv)
            val=await port.call(p['pair_id']+'_'+arm,role,payload,meta)
            return {**meta,'status':'ok',**val}
        except Exception as exc:return {**meta,'status':'failed','error':type(exc).__name__+': '+str(exc)}
    return await asyncio.gather(*(one(p,a) for p in pairs for a in ['G0','G1']))

def export_source_review(out):
    import json
    mapping=[]
    for f in sorted((out/'inventories').glob('*.json')):
        frozen=read(f);req=read(out/'calls'/(frozen['request_id']+'.request.json'))
        evidence=json.loads(req['request']['messages'][-1]['content'])['Evidence']
        rid='I_'+digest([evidence,frozen['inventory']])[:24]
        save(HERE/'review/inventory_source'/f'{rid}.json',{'review_id':rid,'Evidence':evidence,'Inventory':frozen['inventory']})
        mapping.append({'review_id':rid,'evidence_key':frozen['evidence_key'],
            'inventory_path':str(f.relative_to(ROOT)),'facts':len(frozen['inventory']['facts'])})
    save(HERE/'review/private_mapping.json',mapping)

async def execute(args):
    from .transport import Transport
    authorize(args.authorization,'E2');config=read(HERE/'CONFIG.json');b=read(HERE/'CANDIDATE_BANK.json')
    out=HERE/'run001'
    port=Transport(config,out,'E2',args.authorization,account_available=50)
    try:
        save(out/'EXECUTION_FREEZE.json',{'git_head':port.head,'freeze_sha256':file_hash(HERE/'EXECUTION_FREEZE.json'),
            'authorization_sha256':file_hash(args.authorization),'config':config,'plan':make_plan(b['pairs'],config)})
        results=await run_e2(port,b['pairs']);save(out/'RESULTS.json',results)
    finally: summary=await port.close()
    complete=len(results)==2*b['count'] and all(r['status']=='ok' for r in results) and summary['attempted']==b['calls'] and summary['halt'] is None
    save(out/'COMPLETENESS_GATE.json',{'complete':complete,'expected_calls':b['calls'],'expected_pair_arms':2*b['count'],
        'valid_pair_arms':sum(r['status']=='ok' for r in results),'semantic_review_allowed':complete,'STOP_AFTER_E2':True})
    export_source_review(out)
    actual={r['request_id'] for r in port.records}
    save(out/'UNSENT_DEPENDENCIES.json',[p for p in make_plan(b['pairs'],config) if p['request_id'] not in actual])
    print('E2 completed; calls:',summary['attempted'],'complete:',complete,'peak:',summary['peak_concurrency'])

def main():
    a=argparse.ArgumentParser();a.add_argument('command',choices=['preflight','run-e2']);a.add_argument('--authorization');args=a.parse_args()
    if args.command=='preflight':verify_freeze();print('E2 freeze verified');return
    asyncio.run(execute(args))

if __name__=='__main__':main()
