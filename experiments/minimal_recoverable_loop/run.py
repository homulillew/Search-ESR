"""Explicitly authorized frozen E1 batches, one attempt and exclusive archives."""
import argparse
import threading
import time
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime,timezone
from .common import *
from .requests import writer_jobs,compile_admissions,valid_output
from experiments.skeleton_state_alignment.prepare import credential
from experiments.contextual_subtraction_qualification.run import accounting
from experiments.minimal_need_multiquery.run import usage_audit

OUT=P/'e1_admission'
def now():return datetime.now(timezone.utc).isoformat()
def jobs(phase):return read(OUT/f'{phase.upper()}_REQUESTS.json')
def rows(phase):
    out=[]
    for j in jobs(phase):
        p=OUT/phase/'calls'/f"{j['id']}.result.json"
        if p.exists():
            r=read(p);assert r['id']==j['id'] and r['request_sha256']==j['request_sha256']
        else:
            r={k:v for k,v in j.items() if k!='request'}
            attempted=p.with_name(f"{j['id']}.attempt.json").exists()
            r.update(attempted=attempted,valid_output=False,output=None,usage=None,failure='incomplete_attempt' if attempted else 'not_started')
        out.append(r)
    return out

def audit(phase,authorization=False):
    fpath=OUT/f'{phase.upper()}_FREEZE.json';f=read(fpath);committed(fpath)
    for path,h in f['files'].items():assert sha(ROOT/path)==h,path;committed(ROOT/path)
    schedule=jobs(phase)
    assert len(schedule)==f['actual_requests'] and all(j['request_sha256']==digest(j['request']) for j in schedule)
    if phase=='writer':assert schedule==writer_jobs()
    else:
        expected,ledger=compile_admissions(rows('writer'));assert schedule==expected and ledger==read(OUT/'CANDIDATE_LEDGER.json')
        committed(OUT/'CANDIDATE_REVIEW.json')
    if authorization:
        ap=P/f'AUTHORIZATION_{phase.upper()}.json'
        if not ap.exists():raise PermissionError('TASK47: fresh explicit authorization required after exact request freeze; no HTTP/credential accessed')
        a=read(ap);committed(ap)
        assert a['phase']==phase and a['maximum_attempts']==len(schedule)
        assert a['freeze_sha256']==sha(fpath) and a['task_sha256']==sha(P/'TASK.md')
        assert a['scope']==f'E1 {phase} only' and a['provider']=='deepseek' and a['model']=='deepseek-flash'
        assert a['user_message'].strip() and a['authorized_utc']
    return {'status':'PASS','head':git('rev-parse','HEAD'),'phase':phase,'planned':len(schedule),
            'historical_files_unchanged':verify_history(),'freeze_sha256':sha(fpath),'paid_calls_authorized':authorization}

def parse(status,body,j):
    r={'valid_json':False,'valid_output':False,'output':None,'usage':None,'response_model':None,'finish_reason':None,'failure':None}
    try:d=json.loads(body)
    except (ValueError,TypeError):d=None
    if isinstance(d,dict):r.update(usage=d.get('usage'),response_model=d.get('model'))
    if status!=200:r['failure']='http_error';return r
    try:
        c=d['choices'][0];r['finish_reason']=c['finish_reason']
        if r['response_model']!=j['request']['model']:r['failure']='model_mismatch'
        elif r['finish_reason']!='stop':r['failure']='incomplete_finish'
        else:
            content=c['message'].get('content')
            if not isinstance(content,str) or not content.strip():r['failure']='empty_output'
            else:
                try:v=json.loads(content)
                except ValueError:r['failure']='invalid_json'
                else:
                    r.update(valid_json=True,output=v,valid_output=valid_output(v,j['phase']))
                    if not r['valid_output']:r['failure']='output_contract'
    except (TypeError,KeyError,IndexError,AttributeError):r['failure']='response_schema_error'
    return r

class Batch:
    def __init__(self,client,key,phase,head,config):
        self.client,self.key,self.phase,self.head,self.config=client,key,phase,head,config
        self.lock=threading.Lock();self.halt=threading.Event();self.active=self.peak=0
    def one(self,j):
        path=OUT/self.phase/'calls'/j['id'];r={k:v for k,v in j.items() if k!='request'}
        r.update(head=self.head,attempted=False,valid_json=False,valid_output=False,output=None,usage=None,started_utc=now())
        with self.lock:
            blocked=self.halt.is_set()
            if not blocked:self.active+=1;self.peak=max(self.peak,self.active)
        if blocked:
            r.update(failure='halted_unsent',elapsed_seconds=0);write(path.with_suffix('.result.json'),r);return
        started=time.monotonic()
        try:
            write(path.with_suffix('.request.json'),{'head':self.head,'request':j['request'],'request_sha256':j['request_sha256']})
            write(path.with_suffix('.attempt.json'),{'id':j['id'],'send_intent_utc':now()});r['attempted']=True
            try:response=self.client.post(self.config['endpoint'],json=j['request'],headers={'Authorization':'Bearer '+self.key})
            except Exception as exc:
                import httpx
                if not isinstance(exc,httpx.RequestError):self.halt.set();raise
                r.update(failure='timeout' if isinstance(exc,httpx.TimeoutException) else 'transport_error',error_type=type(exc).__name__)
            else:
                if response.status_code in self.config['halt_http_statuses']:self.halt.set()
                write(path.with_suffix('.response.json'),{'status':response.status_code,'body':response.text,'completed_utc':now()})
                r.update(http_status=response.status_code,**parse(response.status_code,response.text,j))
            r.update(elapsed_seconds=time.monotonic()-started,completed_utc=now(),accounting=usage_audit(r['usage']))
            write(path.with_suffix('.result.json'),r);print(j['id'],'valid-output' if r['valid_output'] else r['failure'],flush=True)
        except BaseException:self.halt.set();raise
        finally:
            with self.lock:self.active-=1

def execute(phase):
    checked=audit(phase,authorization=True);folder=OUT/phase
    if (folder/'RUN.json').exists() or (folder/'calls').exists():raise FileExistsError('No overwrite, resume, retry or repeated paid attempt')
    config=read(P/'CONFIG.json');key=credential()
    write(folder/'RUN.json',{**checked,'authorization_sha256':sha(P/f'AUTHORIZATION_{phase.upper()}.json'),'started_utc':now()})
    import httpx
    started=time.monotonic();error=None
    with httpx.Client(timeout=config['timeout_seconds'],transport=httpx.HTTPTransport(retries=0),follow_redirects=False) as client:
        batch=Batch(client,key,phase,checked['head'],config)
        try:
            with ThreadPoolExecutor(max_workers=config['max_workers']) as pool:
                fs=[pool.submit(batch.one,j) for j in jobs(phase)]
                for f in as_completed(fs):f.result()
        except BaseException as e:error=type(e).__name__;raise
        finally:
            for r in rows(phase):
                path=folder/'calls'/f"{r['id']}.result.json"
                if not path.exists():write(path,r)
            write(folder/'ACCOUNTING.json',{**accounting(rows(phase)),'wall_seconds':time.monotonic()-started,'peak_concurrency':batch.peak,'harness_error':error})

def materialize_admissions():
    committed(OUT/'writer/ACCOUNTING.json')
    for r in rows('writer'):committed(OUT/'writer/calls'/f"{r['id']}.result.json")
    js,ledger=compile_admissions(rows('writer'))
    write(OUT/'ADMISSION_REQUESTS.json',js);write(OUT/'CANDIDATE_LEDGER.json',ledger)
    write(OUT/'ADMISSION_CALL_ESTIMATE.json',{'actual_requests':len(js),'candidate_claims':len(ledger),
          'mechanical_rejects':sum(not r['exact_excerpt_valid'] for r in ledger),'network_calls':0,
          'next_step':'content-only candidate reference review, commit, freeze exact requests, then fresh explicit authorization'})
    return {'actual_admission_requests':len(js),'network_calls':0}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['audit','execute','materialize_admissions']);p.add_argument('--phase',choices=['writer','admission'],default='writer');a=p.parse_args()
    result=materialize_admissions() if a.mode=='materialize_admissions' else globals()[a.mode](a.phase)
    if result is not None:print(json.dumps(result,indent=2))
