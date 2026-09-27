"""Full fresh E1 only. Original DAG, review exporter and metrics are unchanged."""
import argparse
import asyncio
from pathlib import Path
from ..harness import bank,run_e1,export_review,read,save,file_hash
from .contracts import HERE,BASE,ROOT

def verify_freeze():
    f=read(HERE/'FREEZE_V2.json')
    for path,sha in f['files'].items():
        if file_hash(ROOT/path)!=sha:raise ValueError('V2 freeze mismatch: '+path)
    return f

def authorize(path,stage):
    verify_freeze();auth=read(path)
    if stage!='E1' or auth.get('stages')!=['E1'] or not auth.get('authorized'):raise PermissionError('only corrected E1 is authorized')
    if auth['freeze_sha256']!=file_hash(HERE/'FREEZE_V2.json'):raise PermissionError('authorization freeze mismatch')
    if auth['task_sha256']!=file_hash(HERE/'TASK.md'):raise PermissionError('authorization task mismatch')
    return auth

async def execute(args):
    from .transport import Transport
    authorize(args.authorization,'E1');config=read(HERE/'CONFIG_V2.json')
    packets=bank(['D','H_diagnostic'])
    port=Transport(config,args.out,'E1',args.authorization,account_available=args.account_available)
    try:
        save(Path(args.out)/'EXECUTION_FREEZE.json',{'git_head':port.head,'freeze_sha256':file_hash(HERE/'FREEZE_V2.json'),
            'authorization_sha256':file_hash(args.authorization),'config':config,'full_fresh_E1':True,'historical_response_reuse':False})
        results=await run_e1(port,packets)
        save(Path(args.out)/'RESULTS.json',results)
        complete=len(results)==72 and all(r['status']=='ok' for r in results)
        save(Path(args.out)/'COMPLETENESS_GATE.json',{'complete':complete,'expected_chains':72,'valid_chains':sum(r['status']=='ok' for r in results),
            'semantic_review_allowed':complete,'E2_E3_authorized':False})
        if complete:export_review(packets,results,Path(args.out)/'review')
    finally:await port.close()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=['preflight','run-e1']);ap.add_argument('--authorization');ap.add_argument('--out');ap.add_argument('--account-available',type=int,default=72);args=ap.parse_args()
    if args.command=='preflight':verify_freeze();print('V2 freeze valid; only E1 is eligible for authorized execution.');return
    asyncio.run(execute(args))

if __name__=='__main__':main()
