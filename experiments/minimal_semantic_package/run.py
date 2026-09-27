"""One-attempt, explicitly authorized batches; no network during preparation.

Transport pattern and usage accounting reuse the previous frozen experiments.
Each concrete verifier/auditor batch is committed and SHA-frozen independently.
"""
import argparse
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from .common import *
from .inputs import validate, verifier_schedule, auditor_job
from experiments.skeleton_state_alignment.prepare import credential
from experiments.skeleton_state_alignment.run import now
from experiments.contextual_subtraction_qualification.run import accounting
from experiments.minimal_need_multiquery.run import usage_audit

OUT = P/'e1_gold_support'
META = ('id','stage','phase','certificate_id','cell_id','case_id','qid','package_id','replicate','request_sha256')

def jobs(phase):
    return read(OUT/f'{phase.upper()}_SCHEDULE.json')

def load_rows(phase):
    result=[]
    for job in jobs(phase):
        path=OUT/phase/'calls'/f"{job['id']}.result.json"
        if path.exists():
            row=read(path)
            assert row['id']==job['id'] and row['request_sha256']==job['request_sha256']
        else:
            attempted=path.with_name(f"{job['id']}.attempt.json").exists()
            row={k:job[k] for k in META}
            row.update(attempted=attempted,valid_json=False,valid_output=False,output=None,usage=None,
                       failure='incomplete_attempt' if attempted else 'not_started')
        result.append(row)
    return result

def audit(phase, require_authorization=False):
    freeze_path=OUT/f'{phase.upper()}_FREEZE.json'
    frozen=read(freeze_path)
    committed(freeze_path)
    for path,h in frozen['files'].items():
        assert sha(ROOT/path)==h,path
        committed(ROOT/path)
    schedule=jobs(phase)
    assert len(schedule)==frozen['actual_requests']
    assert all(j['request_sha256']==digest(j['request']) for j in schedule)
    if phase=='verifier':
        assert schedule==verifier_schedule() and len(schedule)==96
    else:
        compiled=[]
        for job,row in zip(jobs('verifier'),load_rows('verifier')):
            item=auditor_job(job,row)
            if item is not None:compiled.append(item)
        assert schedule==compiled
    authorization=None
    if require_authorization:
        ap=P/f'AUTHORIZATION_{phase.upper()}.json'
        if not ap.exists():
            raise PermissionError('TASK33 requires NEW explicit user authorization for this frozen batch; no credential or HTTP request is accessed.')
        authorization=read(ap)
        committed(ap)
        assert authorization['phase']==phase and authorization['maximum_attempts']==len(schedule)
        assert authorization['freeze_sha256']==sha(freeze_path)
        assert authorization['task_sha256']==sha(P/'TASK.md')
        assert authorization['provider']=='deepseek' and authorization['model']=='deepseek-flash'
        assert authorization['user_message'].strip() and authorization['authorized_utc']
        assert authorization['scope']==f'E1 {phase} only'
        # An honestly recorded user message is required. A manifest cannot create consent.
    return {'status':'PASS','head':git('rev-parse','HEAD'),'phase':phase,
            'planned':len(schedule),'freeze_sha256':sha(freeze_path),
            'historical_files_unchanged':verify_history(),
            'paid_calls_authorized':authorization is not None}

def parse(status, body, job):
    row={'valid_json':False,'valid_output':False,'output':None,'usage':None,
         'response_model':None,'finish_reason':None,'failure':None}
    try:raw=json.loads(body)
    except (TypeError,ValueError):raw=None
    if isinstance(raw,dict):row.update(usage=raw.get('usage'),response_model=raw.get('model'))
    if status!=200:
        row['failure']='http_error'
        return row
    try:
        choice=raw['choices'][0]
        row['finish_reason']=choice['finish_reason']
        if row['response_model']!=job['request']['model']:row['failure']='model_mismatch'
        elif choice['finish_reason']!='stop':row['failure']='incomplete_finish'
        else:
            content=choice['message'].get('content')
            if not isinstance(content,str) or not content.strip():row['failure']='empty_output'
            else:
                try:value=json.loads(content)
                except ValueError:row['failure']='invalid_json'
                else:
                    row.update(valid_json=True,output=value,valid_output=validate(value,job))
                    if not row['valid_output']:row['failure']='output_contract'
    except (KeyError,IndexError,TypeError,AttributeError):row['failure']='response_schema_error'
    return row

class Batch:
    def __init__(self,client,key,config,phase,head):
        self.client,self.key,self.config,self.phase,self.head=client,key,config,phase,head
        self.lock=threading.Lock()
        self.halt=threading.Event()
        self.active=self.peak=0

    def one(self,job):
        path=OUT/self.phase/'calls'/job['id']
        row={k:job[k] for k in META}
        row.update(head=self.head,attempted=False,valid_json=False,valid_output=False,output=None,usage=None,started_utc=now())
        with self.lock:
            blocked=self.halt.is_set()
            if not blocked:
                self.active+=1
                self.peak=max(self.peak,self.active)
        if blocked:
            row.update(failure='halted_unsent',elapsed_seconds=0)
            write(path.with_suffix('.result.json'),row)
            return
        started=time.monotonic()
        try:
            write(path.with_suffix('.request.json'),{'head':self.head,'request':job['request'],'request_sha256':job['request_sha256']})
            write(path.with_suffix('.attempt.json'),{'id':job['id'],'send_intent_utc':now()})
            row['attempted']=True
            try:
                response=self.client.post(self.config['endpoint'],json=job['request'],headers={'Authorization':'Bearer '+self.key})
            except Exception as exc:
                import httpx
                if not isinstance(exc,httpx.RequestError):
                    self.halt.set()
                    raise
                row.update(failure='timeout' if isinstance(exc,httpx.TimeoutException) else 'transport_error',error_type=type(exc).__name__)
            else:
                if response.status_code in self.config['halt_http_statuses']:self.halt.set()
                write(path.with_suffix('.response.json'),{'status':response.status_code,'body':response.text,'completed_utc':now()})
                row.update(http_status=response.status_code,**parse(response.status_code,response.text,job))
            row.update(elapsed_seconds=time.monotonic()-started,completed_utc=now(),accounting=usage_audit(row['usage']))
            write(path.with_suffix('.result.json'),row)
            print(job['id'],'valid-output' if row['valid_output'] else row['failure'],flush=True)
        except BaseException:
            self.halt.set()
            raise
        finally:
            with self.lock:self.active-=1

    def run(self,schedule):
        with ThreadPoolExecutor(max_workers=self.config['max_workers']) as pool:
            futures=[pool.submit(self.one,job) for job in schedule]
            for future in as_completed(futures):future.result()

def execute(phase):
    checked=audit(phase,require_authorization=True)
    folder=OUT/phase
    if (folder/'RUN.json').exists() or (folder/'calls').exists():
        raise FileExistsError('No overwrite/resume/retry or duplicate paid attempt')
    config=read(P/'CONFIG.json')
    key=credential()
    write(folder/'RUN.json',{**checked,'authorization_sha256':sha(P/f'AUTHORIZATION_{phase.upper()}.json'),'started_utc':now()})
    import httpx
    started=time.monotonic()
    error=None
    with httpx.Client(timeout=config['timeout_seconds'],transport=httpx.HTTPTransport(retries=0),follow_redirects=False) as client:
        batch=Batch(client,key,config,phase,checked['head'])
        try:batch.run(jobs(phase))
        except BaseException as exc:
            error=type(exc).__name__
            raise
        finally:
            for row in load_rows(phase):
                path=folder/'calls'/f"{row['id']}.result.json"
                if not path.exists():write(path,row)
            write(folder/'ACCOUNTING.json',{**accounting(load_rows(phase)),
                  'wall_seconds':time.monotonic()-started,'peak_concurrency':batch.peak,'harness_error':error})

def materialize_auditors():
    """No calls: compile exact dependent requests, then stop for commit/freeze/consent."""
    committed(OUT/'verifier/ACCOUNTING.json')
    schedule=[]
    for job,row in zip(jobs('verifier'),load_rows('verifier')):
        committed(OUT/'verifier/calls'/f"{job['id']}.result.json")
        item=auditor_job(job,row)
        if item is not None:schedule.append(item)
    write(OUT/'AUDITOR_SCHEDULE.json',schedule)
    write(OUT/'AUDITOR_CALL_ESTIMATE.json',{'actual_requests':len(schedule),
          'authorized':False,'parent_accounting_sha256':sha(OUT/'verifier/ACCOUNTING.json'),
          'next_step':'commit actual requests, create and commit AUDITOR_FREEZE.json, then obtain a new explicit authorization per TASK33'})
    return {'actual_auditor_requests':len(schedule),'network_calls':0,'authorization_required':bool(schedule)}

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('mode',choices=['audit','execute','materialize_auditors'])
    parser.add_argument('--phase',choices=['verifier','auditor'],default='verifier')
    args=parser.parse_args()
    result=materialize_auditors() if args.mode=='materialize_auditors' else globals()[args.mode](args.phase)
    if result is not None:print(json.dumps(result,indent=2))
