"""Bounded async, one attempt, append-only archives. Live construction requires new authorization."""
import asyncio
import json
import os
import statistics
import subprocess
import time
from datetime import datetime,timezone
from pathlib import Path
import httpx
from .harness import HERE,ROOT,read,save,digest,file_hash,request,validate

def now():return datetime.now(timezone.utc).isoformat()

def verify_freeze():
    frozen=read(HERE/'FREEZE.json')
    for path,sha in frozen['files'].items():
        if file_hash(HERE/path)!=sha:raise ValueError('freeze mismatch: '+path)
    for path,sha in read(HERE/'bank/provenance.json')['source_file_hashes'].items():
        if file_hash(ROOT/path)!=sha:raise ValueError('historical source changed: '+path)
    return frozen

def authorize(path,stage):
    verify_freeze()
    auth=read(path)
    if auth.get('authorized') is not True or stage not in auth.get('stages',[]):raise PermissionError('new stage authorization absent')
    if auth.get('freeze_sha256')!=file_hash(HERE/'FREEZE.json'):raise PermissionError('authorization does not bind this freeze')
    if not auth.get('user_message_reference') or not auth.get('authorized_at_utc'):raise PermissionError('new user authorization provenance required')
    authorized=datetime.fromisoformat(auth['authorized_at_utc']);frozen=datetime.fromisoformat(read(HERE/'FREEZE.json')['created_utc'])
    if authorized.tzinfo is None or authorized<=frozen:raise PermissionError('standing/historical authorization is not sufficient')
    return auth

def accounting(usage):
    if not isinstance(usage,dict):return {'complete':False,'issues':['missing usage'],'tokens':{}}
    t={'input':usage.get('prompt_tokens'),'output':usage.get('completion_tokens'),'total':usage.get('total_tokens'),
       'hit':usage.get('prompt_cache_hit_tokens'),'miss':usage.get('prompt_cache_miss_tokens'),
       'reasoning':(usage.get('completion_tokens_details') or {}).get('reasoning_tokens')}
    issues=[k+' missing/invalid' for k in ['input','output','total','hit','miss'] if type(t[k]) is not int or t[k]<0]
    if not issues:
        if t['input']+t['output']!=t['total']:issues.append('input+output != total')
        if t['hit']+t['miss']!=t['input']:issues.append('hit+miss != input')
    nested=(usage.get('prompt_tokens_details') or {}).get('cached_tokens')
    if nested is not None and nested!=t['hit']:issues.append('cached_tokens != hit')
    return {'complete':not issues,'issues':issues,'tokens':t}

def usage_summary(records):
    good=[r['accounting']['tokens'] for r in records if r['accounting']['complete']]
    sums={k:sum(t[k] for t in good) for k in ['input','output','total','hit','miss']}
    return {'complete_consistent_records':len(good),'missing_or_inconsistent_records':len(records)-len(good),
        'tokens_from_complete_consistent_records':sums,'cache_hit_rate':sums['hit']/sums['input'] if sums['input'] else None}

class Transport:
    def __init__(self,config,out,stage,authorization_path=None,mock_transport=None,account_available=256):
        # Mock clients exercise wire contracts offline; cannot silently use real I/O.
        self.mock=mock_transport is not None
        if self.mock:
            if not isinstance(mock_transport,httpx.MockTransport):raise TypeError('offline requires httpx.MockTransport')
            self.key='OFFLINE_TEST_ONLY'
        else:
            authorize(authorization_path,stage)  # before credentials/client/network
            self.key=os.environ.get('DEEPSEEK_API_KEY')
            if not self.key:
                from dotenv import dotenv_values
                self.key=dotenv_values(ROOT/'.env.deepseek').get('DEEPSEEK_API_KEY')
            if not self.key:raise ValueError('missing DEEPSEEK_API_KEY')
        self.config=config;self.out=Path(out);self.stage=stage
        if self.out.exists():raise FileExistsError('new run directory required; never resume/retry existing calls')
        self.out.mkdir(parents=True)
        if config['max_retries']!=0:raise ValueError('retries must be zero')
        self.limit=min(config['concurrency_cap'],config['account_budget_ceiling'],account_available,config['stage_independent_requests'][stage])
        if self.limit<1:raise ValueError('no account concurrency available')
        self.sem=asyncio.Semaphore(self.limit);self.lock=asyncio.Lock();self.halt=None
        self.active=0;self.peak=0;self.count=0;self.records=[];self.ids=set()
        self.ceiling=config['stage_call_ceiling'][stage];self.events=[{'utc':now(),'limit':self.limit,'reason':'initial bounded stage/account budget'}]
        limits=httpx.Limits(max_connections=self.limit,max_keepalive_connections=self.limit)
        self.client=httpx.AsyncClient(transport=mock_transport if self.mock else httpx.AsyncHTTPTransport(retries=0,limits=limits),
            limits=limits,timeout=httpx.Timeout(**config['timeouts_seconds']),follow_redirects=False)
        self.start=time.monotonic();self.head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()

    async def call(self,ident,role,payload,meta):
        if ident in self.ids:raise ValueError('duplicate request ID; retry prohibited')
        self.ids.add(ident)
        data=request(role,payload,self.config);prefix=self.out/'calls'/ident
        save(str(prefix)+'.request.json',{'git_head':self.head,'created_utc':now(),'role':role,
            **meta,'request':data,'request_hash':digest(data),'offline_mock':self.mock})
        result={**meta,'request_id':ident,'role':role,'attempted':False,'error':None,'usage':None,
                'request_hash':digest(data),'http_status':None,'offline_mock':self.mock}
        start=time.monotonic();acquired=False;body=bytearray()
        try:
            await self.sem.acquire();acquired=True
            if self.halt:raise RuntimeError('stage halted; unsent: '+self.halt)
            if self.count>=self.ceiling:raise RuntimeError('stage budget exhausted')
            self.count+=1;self.active+=1;self.peak=max(self.peak,self.active);result['attempted']=True
            save(str(prefix)+'.attempt.json',{'utc':now(),'active':self.active,'limit':self.limit,'sequence':self.count})
            async with asyncio.timeout(self.config['total_timeout_seconds']):
                async with self.client.stream('POST',self.config['endpoint'],json=data,headers={'Authorization':'Bearer '+self.key}) as resp:
                    result['http_status']=resp.status_code
                    with Path(str(prefix)+'.response.body').open('xb') as f:
                        async for chunk in resp.aiter_bytes():
                            f.write(chunk);f.flush();body.extend(chunk)
            raw=json.loads(body.decode('utf-8'));result['usage']=raw.get('usage');result['response_model']=raw.get('model')
            result['provider_id']=raw.get('id')
            if resp.status_code!=200:raise ValueError('HTTP '+str(resp.status_code))
            if raw.get('model')!=self.config['model']:raise ValueError('model mismatch')
            choice=raw['choices'][0];result['finish_reason']=choice['finish_reason'];msg=choice['message']
            # Explicit derivative archive, in addition to untouched response bytes.
            save(str(prefix)+'.content.json',{'reasoning_content':msg.get('reasoning_content'),'content':msg.get('content')})
            if choice['finish_reason']!='stop':raise ValueError('incomplete generation')
            value=validate(role,json.loads(msg['content']),payload)
            save(str(prefix)+'.parsed.json',value)
            return value
        except Exception as exc:
            result['error']={'type':type(exc).__name__,'message':str(exc)[:700]}
            if self.halt is None:
                self.halt=type(exc).__name__+': '+str(exc)[:180]
                self.events.append({'utc':now(),'limit':0,'reason':'stop unsent requests under TASK section37: '+self.halt})
            raise
        finally:
            if result['attempted']:self.active-=1
            if acquired:self.sem.release()
            result['latency_seconds']=time.monotonic()-start;result['completed_utc']=now();result['response_bytes']=len(body)
            result['accounting']=accounting(result['usage']);self.records.append(result)
            save(str(prefix)+'.result.json',result)

    async def close(self):
        await self.client.aclose()
        times=sorted(r['latency_seconds'] for r in self.records if r['attempted'])
        def percentile(p):return times[min(len(times)-1,round((len(times)-1)*p))] if times else None
        summary={'stage':self.stage,'attempted':self.count,'peak_concurrency':self.peak,'changes':self.events,
            'halt':self.halt,'wall_seconds':time.monotonic()-self.start,'offline_mock':self.mock,
            'latency_seconds':{'p50':percentile(.5),'p95':percentile(.95),'max':max(times) if times else None},
            'attempted_failures':sum(bool(r['error']) and r['attempted'] for r in self.records),
            'unsent':sum(not r['attempted'] for r in self.records),**usage_summary(self.records)}
        summary['attempted_failure_rate']=summary['attempted_failures']/self.count if self.count else None
        save(self.out/'TRANSPORT_SUMMARY.json',summary)
        return summary
