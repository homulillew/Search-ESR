"""Frozen Q-only skeleton requests; no semantic scoring in execution."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import subprocess
import threading
import time
from .common import *
from .prepare import credential, preflight, request_for
from .source_units import validate
from experiments.minimal_need_multiquery.run import accounting_summary, now, usage_audit
OUT=None
STAGE=None
def text_value(x): return isinstance(x,str) and bool(x.strip())
def validate_output(v,c,arm):
 return validate(v,arm,c['source_units'])['valid']
def load_rows():
 rows=[]
 for j in read(OUT/'SCHEDULE.json'):
  p=OUT/'calls'/f"{j['id']}.result.json"
  if p.exists():
   r=read(p);assert r['request_sha256']==j['request_sha256'];rows.append(r)
  else:
   rows.append({**{k:j[k] for k in ('id','qid','arm','replicate','request_sha256')},'attempted':(OUT/'calls'/f"{j['id']}.attempt.json").exists(),'valid_json':False,'valid_output':False,'output':None,'usage':None,'failure':'not_completed'})
 return rows

def audit(require_committed=True, check_paths=False):
 frozen=read(P/'FREEZE.json'); head=git('rev-parse','HEAD')
 for name,h in frozen['files'].items():
  assert sha(ROOT/name)==h, 'Frozen file changed: '+name
  if require_committed:assert subprocess.check_output(['git','show',head+':'+name],cwd=ROOT)==(ROOT/name).read_bytes()
 if require_committed:assert subprocess.check_output(['git','show',head+':'+rel(P/'FREEZE.json')],cwd=ROOT)==(P/'FREEZE.json').read_bytes()
 history=read(P/'analysis/HISTORICAL_HASHES.json')
 for name,h in history.items():assert sha(ROOT/name)==h, 'History changed: '+name
 checked=preflight(read(OUT/'SCHEDULE.json'),bank(STAGE),read(P/'CONFIG.json'),STAGE,check_paths)
 return {**checked,'head':head,'manifest_sha256':sha(P/'FREEZE.json'),'historical_files_unchanged':len(history)}

def parse_response(status, body, job, candidate):
    result = {'valid_json': False, 'valid_output': False, 'output': None, 'usage': None,
              'response_model': None, 'finish_reason': None, 'failure': None}
    try:
        raw = json.loads(body)
    except (ValueError, TypeError):
        raw = None
    if isinstance(raw, dict):
        result.update(usage=raw.get('usage'), response_model=raw.get('model'))
    if status != 200:
        result['failure'] = 'access_or_billing_error' if status in (401, 402, 403) else 'http_error'
        return result
    try:
        choice = raw['choices'][0]
        result['finish_reason'] = choice['finish_reason']
        if result['response_model'] != job['request']['model']:
            result['failure'] = 'model_mismatch'
        elif choice['finish_reason'] != 'stop':
            result['failure'] = 'length' if choice['finish_reason'] == 'length' else 'incomplete_finish'
        else:
            content = choice['message'].get('content')
            if not text_value(content):
                result['failure'] = 'empty_output'
            else:
                try:
                    value = json.loads(content)
                except ValueError:
                    result['failure'] = 'invalid_json'
                else:
                    result['valid_json'] = True
                    result['output'] = value  # Preserve parsed invalid schemas; they receive no success credit.
                    result['valid_output'] = validate_output(value, candidate, job['arm'])
                    if not result['valid_output']:
                        result['failure'] = 'schema_or_ref_error'
    except (KeyError, IndexError, TypeError, AttributeError):
        result['failure'] = 'response_schema_error'
    return result

class Batch:
    def __init__(self, client, key, config, candidates, out, head):
        self.client, self.key, self.config, self.candidates, self.out, self.head = client, key, config, candidates, out, head
        self.halt = threading.Event(); self.abort = threading.Event(); self.lock = threading.Lock()
        self.active = self.peak = 0

    def one(self, job):
        path = self.out / 'calls' / job['id']
        if job['request'] != request_for(self.candidates[job['qid']], job['arm']):
            raise ValueError('STOP_BEFORE_PAID_CALL: request drift')
        if 'json' not in '\n'.join(m['content'] for m in job['request']['messages']).lower():
            raise ValueError('STOP_BEFORE_PAID_CALL: JSON literal missing')
        with self.lock:
            blocked = self.halt.is_set() or self.abort.is_set()
            if not blocked:
                self.active += 1; self.peak = max(self.peak, self.active)
        row = {k: job[k] for k in ('id', 'arm', 'qid', 'replicate', 'request_sha256')}
        row.update(head=self.head, attempted=False, valid_json=False, valid_output=False, output=None, usage=None, started_utc=now())
        if blocked:
            row.update(failure='blocked_by_access_billing_or_harness', elapsed_seconds=0)
            write(path.with_suffix('.result.json'), row)
            return
        start = time.monotonic()
        try:
            write(path.with_suffix('.request.json'), {'head': self.head, 'request': job['request'], 'request_sha256': job['request_sha256']})
            write(path.with_suffix('.attempt.json'), {'id': job['id'], 'send_intent_utc': now()})
            row['attempted'] = True
            try:
                response = self.client.post(self.config['base_url'] + '/chat/completions', json=job['request'],
                                            headers={'Authorization': 'Bearer ' + self.key})
            except Exception as exc:
                import httpx
                if not isinstance(exc, httpx.RequestError):
                    self.abort.set(); raise
                row.update(failure='timeout' if isinstance(exc, httpx.TimeoutException) else 'transport_error', error_type=type(exc).__name__)
            else:
                if response.status_code in self.config['halt_http_statuses']:
                    self.halt.set()
                write(path.with_suffix('.response.json'), {'status': response.status_code, 'body': response.text, 'completed_utc': now()})
                row.update(http_status=response.status_code, **parse_response(response.status_code, response.text, job, self.candidates[job['qid']]))
            row.update(elapsed_seconds=time.monotonic()-start, completed_utc=now(), accounting=usage_audit(row['usage']))
            write(path.with_suffix('.result.json'), row)
            print(job['id'], 'valid-output' if row['valid_output'] else row['failure'], flush=True)
        except BaseException:
            self.abort.set(); raise
        finally:
            with self.lock:
                self.active -= 1

    def run(self, jobs):
        self.one(jobs[0])  # Formal first replicate is the only authentication preflight.
        with ThreadPoolExecutor(max_workers=self.config['max_workers']) as pool:
            futures = [pool.submit(self.one, job) for job in jobs[1:]]
            for future in as_completed(futures):
                future.result()

def execute():
 if STAGE=='e2_fresh':
  assert read(P/'e1_development/METRICS.json')['gate']['pass']
  assert subprocess.check_output(['git','show',git('rev-parse','HEAD')+':'+rel(P/'e1_development/METRICS.json')],cwd=ROOT)==(P/'e1_development/METRICS.json').read_bytes()
 checked=audit(check_paths=True);config=read(P/'CONFIG.json');key=credential()
 assert config['planned_calls']==60 and config['paid_authorization'].startswith('Prior user explicitly authorized')
 if (OUT/'RUN.json').exists() or (OUT/'calls').exists():raise FileExistsError('No overwrite/resume/retry')
 import httpx
 write(OUT/'RUN.json',{**checked,'started_utc':now(),'authorization':config['paid_authorization'],'pid':__import__('os').getpid()})
 start=time.monotonic();error=None
 with httpx.Client(timeout=config['timeout_seconds'],transport=httpx.HTTPTransport(retries=0),follow_redirects=False) as client:
  batch=Batch(client,key,config,bank(STAGE),OUT,checked['head'])
  try:batch.run(read(OUT/'SCHEDULE.json'))
  except BaseException as exc:error=type(exc).__name__;raise
  finally:
   rows=load_rows()
   write(OUT/'ACCOUNTING.json',{**accounting_summary(rows),'wall_seconds':time.monotonic()-start,'peak_concurrency':batch.peak,'harness_error':error,
    'valid_json':sum(r['valid_json'] for r in rows),'valid_outputs':sum(r['valid_output'] for r in rows)})

def export_review():
 assert (OUT/'ACCOUNTING.json').exists()
 cases=bank(STAGE);packets=[];key={}
 for i,r in enumerate(sorted(load_rows(),key=lambda r:digest(['skeleton-mask-v1',STAGE,r['id']]))):
  rid=f'R{i+1:03d}';key[rid]=r['id'];c=cases[r['qid']];v=r.get('output')
  units=[]
  if isinstance(v,dict) and isinstance(v.get('requirements'),list):
   for node in v['requirements']:
    if not isinstance(node,dict):continue
    if r['arm']=='D2':
     units.append('\n'.join(s.get('text','') for s in node.get('source_spans',[]) if isinstance(s,dict) and isinstance(s.get('text'),str)))
    else:units.append(node.get('requirement',''))
  packets.append({'review_id':rid,'question':c['question'],'candidate_task_units':units})
 write(OUT/'review/PACKETS.json',packets);write(OUT/'review/KEY.json',key)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['audit','execute','export_review']);p.add_argument('stage',choices=STAGES)
 args=p.parse_args();STAGE=args.stage;OUT=P/STAGE;value=globals()[args.mode]()
 if value is not None:print(json.dumps(value,indent=2))
