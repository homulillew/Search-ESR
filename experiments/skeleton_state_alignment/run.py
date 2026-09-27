"""One attempt per frozen slot; raw retention, bounded concurrency, no repair."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import math
import statistics
import threading
import time
from .common import *
from .contracts import validate_output
from .inputs import selection_input, request_for
from .prepare import build_schedule, credential
from experiments.minimal_need_multiquery.run import usage_audit, accounting_summary, now

def committed(path,head=None):
    head=head or git('rev-parse','HEAD')
    assert subprocess.check_output(['git','show',head+':'+rel(path)],cwd=ROOT)==Path(path).read_bytes(), 'Not committed: '+rel(path)

def schedule(stage):
    return read(P/stage/('EXECUTION_SCHEDULE.json' if stage==STAGES[1] else 'SCHEDULE.json'))

def load_rows(stage):
    rows=[]
    for j in schedule(stage):
        p=P/stage/'calls'/f"{j['id']}.result.json"
        if p.exists():
            row=read(p)
            assert row['id']==j['id'] and row['request_sha256']==j['request_sha256']
        else:
            attempted=(p.parent/f"{j['id']}.attempt.json").exists()
            row={k:j[k] for k in ('id','stage','case_id','state_id','qid','arm','replicate','request_sha256')}
            row.update(attempted=attempted,valid_json=False,valid_output=False,output=None,usage=None,
                       failure='incomplete_attempt' if attempted else 'not_started')
        rows.append(row)
    return rows

def audit(stage,require_committed=True):
    frozen=read(P/'FREEZE.json');head=git('rev-parse','HEAD')
    for name,h in frozen['files'].items():
        assert sha(ROOT/name)==h,'Frozen file changed: '+name
        if require_committed:committed(ROOT/name,head)
    if require_committed:committed(P/'FREEZE.json',head)
    history=read(P/'analysis/HISTORICAL_HASHES.json')
    for name,h in history.items():assert sha(ROOT/name)==h,'Historical file changed: '+name
    assert read(P/'e1_alignment/SCHEDULE.json')==build_schedule(STAGES[0])
    assert read(P/'e2_selection/SCHEDULE.json')==build_schedule(STAGES[1])
    if stage==STAGES[1]:
        frozen2=read(P/stage/'EXECUTION_FREEZE.json')
        assert frozen2['parent_freeze_sha256']==sha(P/'FREEZE.json')
        assert frozen2['execution_schedule_sha256']==sha(P/stage/'EXECUTION_SCHEDULE.json')
        if require_committed:
            committed(P/stage/'EXECUTION_FREEZE.json',head);committed(P/stage/'EXECUTION_SCHEDULE.json',head)
        for name,h in frozen2['source_files'].items():
            assert sha(ROOT/name)==h
            if require_committed:committed(ROOT/name,head)
        from .score import calculate_stage, assert_review_sealed
        assert_review_sealed(STAGES[0])
        metrics=read(P/STAGES[0]/'METRICS.json')
        assert metrics==calculate_stage(STAGES[0]) and metrics['joint_gate_pass']
        expected=build_schedule(stage)
        for row,base in zip(schedule(stage),expected):
            if base['arm']=='S0':assert row==base;continue
            result=read(P/base['mask_source']);base['mask_source_sha256']=sha(P/base['mask_source'])
            if result['valid_output']:
                base['request']=request_for(stage,selection_input(bank()[base['case_id']],result['output']))
                base['request_sha256']=digest(base['request'])
            else:base['blocked_reason']='invalid_A1_replicate1_mask'
            assert row==base,'E2 source/projection drift'
    config=read(P/'CONFIG.json')
    assert config['max_retries']==0 and config['max_workers']==8 and config['temperature']==0
    assert config['endpoint']=='https://api.deepseek.com/chat/completions'
    for row in schedule(stage):
        r=row['request']
        if r is None:assert stage==STAGES[1] and row['arm']=='S1';continue
        assert digest(r)==row['request_sha256']
        assert set(r)=={'model','temperature','stream','response_format','messages'}
        assert r['model']=='deepseek-flash' and r['response_format']=={'type':'json_object'} and r['temperature']==0
        assert 'JSON' in r['messages'][0]['content']
    return {'status':'PASS','head':head,'manifest_sha256':sha(P/'FREEZE.json'),'stage':stage,
            'planned':108,'historical_files_unchanged':len(history),'network_calls':0}

def authorization(stage):
    path=P/'AUTHORIZATION.json'
    if not path.exists():raise PermissionError('TASK section70: this experiment needs a new applicable paid-budget authorization. PREPARED_FOR_EXECUTION.')
    a=read(path);committed(path)
    assert a['status']=='APPROVED_BY_USER' and a['experiment']=='skeleton-state-alignment'
    assert a['freeze_sha256']==sha(P/'FREEZE.json')
    assert a['authorized_stages'].get(stage)==108
    assert isinstance(a.get('user_instruction'),str) and a['user_instruction'].strip()
    return {'authorization_sha256':sha(path),'authorized_stage':stage,'authorized_planned_slots':108}

def parse_response(status,body,job):
    result=dict(valid_json=False,valid_output=False,output=None,usage=None,response_model=None,finish_reason=None,failure=None)
    try:raw=json.loads(body)
    except (ValueError,TypeError):raw=None
    if isinstance(raw,dict):result.update(usage=raw.get('usage'),response_model=raw.get('model'))
    if status!=200:
        result['failure']='access_or_billing_error' if status in (401,402,403) else 'http_error'
        return result
    try:
        choice=raw['choices'][0];result['finish_reason']=choice['finish_reason']
        if result['response_model']!=job['request']['model']:result['failure']='model_mismatch'
        elif choice['finish_reason']!='stop':result['failure']='length' if choice['finish_reason']=='length' else 'incomplete_finish'
        else:
            content=choice['message'].get('content')
            if not isinstance(content,str) or not content.strip():result['failure']='empty_output'
            else:
                try:value=json.loads(content)
                except ValueError:result['failure']='invalid_json'
                else:
                    result.update(valid_json=True,output=value,valid_output=validate_output(value,job))
                    if not result['valid_output']:result['failure']='output_contract'
    except (KeyError,IndexError,TypeError,AttributeError):result['failure']='response_schema_error'
    return result

class Batch:
    def __init__(self,client,key,config,out,head):
        self.client,self.key,self.config,self.out,self.head=client,key,config,out,head
        self.halt=threading.Event();self.abort=threading.Event();self.lock=threading.Lock()
        self.active=self.peak=0

    def one(self,job):
        path=self.out/'calls'/job['id']
        row={k:job[k] for k in ('id','stage','case_id','state_id','qid','arm','replicate','request_sha256')}
        row.update(head=self.head,attempted=False,valid_json=False,valid_output=False,output=None,usage=None,started_utc=now())
        with self.lock:
            blocked=job['request'] is None or self.halt.is_set() or self.abort.is_set()
            if not blocked:self.active+=1;self.peak=max(self.peak,self.active)
        if blocked:
            row.update(failure=job.get('blocked_reason','blocked_by_provider_or_harness'),elapsed_seconds=0)
            write(path.with_suffix('.result.json'),row);return
        start=time.monotonic()
        try:
            assert digest(job['request'])==job['request_sha256']
            write(path.with_suffix('.request.json'),{'head':self.head,'request':job['request'],'request_sha256':job['request_sha256']})
            write(path.with_suffix('.attempt.json'),{'id':job['id'],'send_intent_utc':now()})
            row['attempted']=True
            try:
                response=self.client.post(self.config['endpoint'],json=job['request'],headers={'Authorization':'Bearer '+self.key})
            except Exception as exc:
                import httpx
                if not isinstance(exc,httpx.RequestError):self.abort.set();raise
                row.update(failure='timeout' if isinstance(exc,httpx.TimeoutException) else 'transport_error',error_type=type(exc).__name__)
            else:
                if response.status_code in self.config['halt_http_statuses']:self.halt.set()
                write(path.with_suffix('.response.json'),{'status':response.status_code,'body':response.text,'completed_utc':now()})
                row.update(http_status=response.status_code,**parse_response(response.status_code,response.text,job))
            row.update(elapsed_seconds=time.monotonic()-start,completed_utc=now(),accounting=usage_audit(row['usage']))
            write(path.with_suffix('.result.json'),row)
            print(job['id'],'valid-output' if row['valid_output'] else row['failure'],flush=True)
        except BaseException:self.abort.set();raise
        finally:
            with self.lock:self.active-=1

    def run(self,jobs):
        # Blocked dependent slots may precede the first sendable formal canary.
        first=next((i for i,j in enumerate(jobs) if j['request'] is not None),len(jobs))
        for j in jobs[:first+1]:self.one(j)
        with ThreadPoolExecutor(max_workers=self.config['max_workers']) as pool:
            futures=[pool.submit(self.one,j) for j in jobs[first+1:]]
            try:
                for f in as_completed(futures):f.result()
            except BaseException:self.abort.set();raise

def accounting(rows):
    times=sorted(r['elapsed_seconds'] for r in rows if r.get('attempted') and isinstance(r.get('elapsed_seconds'),(int,float)))
    return {**accounting_summary(rows),'sent_or_send_intent':sum(bool(r.get('attempted')) for r in rows),
      'returned':sum(r.get('http_status') is not None for r in rows),
      'HTTP_errors':sum(r.get('http_status') is not None and r['http_status']!=200 for r in rows),
      'schema_errors':sum(r.get('failure') in ('output_contract','invalid_json','response_schema_error') for r in rows),
      'failures':{f:sum(r.get('failure')==f for r in rows) for f in sorted({r['failure'] for r in rows if r.get('failure')})},
      'latency_seconds':{'median':statistics.median(times) if times else None,'p95':times[math.ceil(.95*len(times))-1] if times else None,'max':max(times) if times else None},
      'latency_scope':'attempted requests with measured duration, including failures; no total wall deadline',
      'valid_outputs':sum(bool(r['valid_output']) for r in rows)}

def execute(stage):
    approved=authorization(stage);checked=audit(stage);config=read(P/'CONFIG.json');out=P/stage
    if (out/'RUN.json').exists() or (out/'calls').exists():raise FileExistsError('No overwrite/resume/retry')
    key=credential()
    import httpx
    write(out/'RUN.json',{**checked,**approved,'started_utc':now()})
    start=time.monotonic();error=None
    with httpx.Client(timeout=config['timeout_seconds'],transport=httpx.HTTPTransport(retries=0),follow_redirects=False) as client:
        batch=Batch(client,key,config,out,checked['head'])
        try:batch.run(schedule(stage))
        except BaseException as exc:error=type(exc).__name__;raise
        finally:
            # Preserve every uncompleted planned slot explicitly on a caught interruption.
            # Existing raw requests, attempts and responses remain untouched.
            for row in load_rows(stage):
                missing=out/'calls'/f"{row['id']}.result.json"
                if not missing.exists():write(missing,row)
            write(out/'ACCOUNTING.json',{**accounting(load_rows(stage)),'wall_seconds':time.monotonic()-start,'peak_concurrency':batch.peak,'harness_error':error})

def export_review(stage):
    assert (P/stage/'ACCOUNTING.json').exists()
    jobs={j['id']:j for j in schedule(stage)};packets=[];key={}
    for i,row in enumerate(sorted(load_rows(stage),key=lambda r:digest(['alignment-blind-review-v1',stage,r['id']]))):
        rid=f'B{i+1:03d}';key[rid]=row['id'];j=jobs[row['id']]
        if j['request'] is None:
            # There was no valid S1 mask, so no selector input or response exists.
            packets.append({'review_id':rid,'no_response':True,'input':None,'generated_output':None})
        else:
            payload=json.loads(j['request']['messages'][1]['content'])
            packets.append({'review_id':rid,'input':payload,'generated_output':row.get('output'),'no_response':row.get('output') is None})
    write(P/stage/'review/PACKETS.json',packets);write(P/stage/'review/KEY.json',key)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['audit','execute','export_review']);parser.add_argument('stage',choices=STAGES)
    args=parser.parse_args();value=globals()[args.mode](args.stage)
    if value is not None:print(json.dumps(value,indent=2))
