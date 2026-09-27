"""One frozen paid batch, disabled until this experiment has applicable approval."""
import argparse
import time
from .common import *
from .selection import build_schedule
from .e0 import compute
from experiments.skeleton_state_alignment.run import Batch, accounting, now
from experiments.skeleton_state_alignment.prepare import credential
OUT=P/'e1_selection'

def schedule():return read(OUT/'SCHEDULE.json')
def audit(require_committed=True):
    frozen=read(P/'FREEZE.json')
    for name,h in frozen['files'].items():
        assert sha(ROOT/name)==h, name
        if require_committed:committed(ROOT/name)
    if require_committed:committed(P/'FREEZE.json')
    check=verify_sources(); rows,times,m=compute()
    assert m==read(P/'e0_control_equivalence/METRICS.json') and m['gate']['pass']
    assert rows==read(P/'e0_control_equivalence/CONTROL_EQUIVALENT_MASKS.json')
    assert times==read(P/'e0_control_equivalence/RECOVERABILITY.json')
    assert schedule()==build_schedule()
    config=read(P/'CONFIG.json')
    assert config['max_retries']==0 and 1<=config['max_workers']<=8 and config['model']=='deepseek-flash'
    assert len(schedule())==108
    for job in schedule():
        request=job['request'];payload=json.loads(request['messages'][1]['content'])
        assert set(payload)=={'Original Question','Task Skeleton','Control Mask'}
        assert set(request)=={'model','temperature','stream','response_format','messages'}
        assert all(v in ('OPEN','CLOSED') for v in payload['Control Mask'].values())
        assert digest(request)==job['request_sha256']
        if job['arm']=='S1':assert job['source_replicate']==1 and '__R1.result.json' in job['mask_source']
    return {'status':'PASS','head':git('rev-parse','HEAD'),'freeze_sha256':sha(P/'FREEZE.json'),'planned':108,'network_calls':0,**check}

def authorization():
    path=P/'AUTHORIZATION.json'
    if not path.exists():raise PermissionError('TASK46: PREPARED_FOR_E1_EXECUTION; old paid authorization is not applicable.')
    a=read(path);committed(path)
    assert a['status']=='APPROVED_BY_USER' and a['experiment']=='recoverable-control-equivalence'
    assert a['freeze_sha256']==sha(P/'FREEZE.json') and a['authorized_stages']=={'e1_selection':108}
    assert a['maximum_calls']==108 and a.get('user_instruction','').strip()
    return {'authorization_sha256':sha(path),'authorized_planned_slots':108}

def load_rows():
    rows=[]
    for job in schedule():
        path=OUT/'calls'/f"{job['id']}.result.json"
        if path.exists():
            row=read(path);assert row['id']==job['id'] and row['request_sha256']==job['request_sha256']
        else:
            row={k:job[k] for k in ('id','stage','case_id','state_id','qid','arm','replicate','request_sha256')}
            attempted=(path.parent/f"{job['id']}.attempt.json").exists()
            row.update(attempted=attempted,valid_json=False,valid_output=False,output=None,usage=None,failure='incomplete_attempt' if attempted else 'not_started')
        rows.append(row)
    return rows

def execute():
    approved=authorization();checked=audit();config=read(P/'CONFIG.json')
    if (OUT/'RUN.json').exists() or (OUT/'calls').exists():raise FileExistsError('No overwrite/resume/retry')
    key=credential()
    import httpx
    write(OUT/'RUN.json',{**checked,**approved,'started_utc':now()})
    start=time.monotonic();error=None
    with httpx.Client(timeout=config['timeout_seconds'],transport=httpx.HTTPTransport(retries=0),follow_redirects=False) as client:
        batch=Batch(client,key,config,OUT,checked['head'])
        try:batch.run(schedule())
        except BaseException as exc:error=type(exc).__name__;raise
        finally:
            for row in load_rows():
                path=OUT/'calls'/f"{row['id']}.result.json"
                if not path.exists():write(path,row)
            write(OUT/'ACCOUNTING.json',{**accounting(load_rows()),'wall_seconds':time.monotonic()-start,'peak_concurrency':batch.peak,'harness_error':error})

def export_review():
    assert (OUT/'ACCOUNTING.json').exists();jobs={j['id']:j for j in schedule()};packets=[];key={}
    for i,row in enumerate(sorted(load_rows(),key=lambda r:digest(['recoverable-selector-blind-v1',r['id']]))):
        rid=f'B{i+1:03d}';key[rid]=row['id']
        packets.append({'review_id':rid,'input':json.loads(jobs[row['id']]['request']['messages'][1]['content']),
            'selection':row.get('output'),'no_response':row.get('output') is None})
    write(OUT/'review/PACKETS.json',packets);write(OUT/'review/KEY.json',key)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['audit','execute','export_review']);args=parser.parse_args()
    result=globals()[args.mode]()
    if result is not None:print(json.dumps(result,indent=2))
