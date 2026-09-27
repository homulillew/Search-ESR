"""Async HTTP under synchronous narrow roles; one paid attempt per request ID."""
import asyncio
import os
import threading
import time
from pathlib import Path
import httpx
from dotenv import dotenv_values
from .common import *
from llm_chat.recoverable_loop.contracts import parse_json, check


def usage_record(u):
    if not isinstance(u,dict):return {'complete':False,'issues':['missing usage'],'tokens':{}}
    t={'input':u.get('prompt_tokens'),'output':u.get('completion_tokens'),'total':u.get('total_tokens'),
       'hit':u.get('prompt_cache_hit_tokens'),'miss':u.get('prompt_cache_miss_tokens'),
       'reasoning':(u.get('completion_tokens_details') or {}).get('reasoning_tokens')}
    issues=[]
    for k in ['input','output','total','hit','miss']:
        if type(t[k]) is not int or t[k]<0:issues.append('missing/invalid '+k)
    if not issues:
        if t['input']+t['output']!=t['total']:issues.append('input+output != total')
        if t['hit']+t['miss']!=t['input']:issues.append('hit+miss != input')
    nested=(u.get('prompt_tokens_details') or {}).get('cached_tokens')
    if nested is not None and nested!=t['hit']:issues.append('cached_tokens != hit')
    return {'complete':not issues,'issues':issues,'tokens':t}


def payload(req,config):
    return {'model':config['model'],'temperature':config['temperature'],'thinking':config['thinking'],
            'reasoning_effort':config['reasoning_effort'],'max_tokens':config['max_tokens'],
            'stream':False,'response_format':{'type':'json_object'},
            'messages':[{'role':'system','content':req.prompt+'\nReturn one JSON object matching this schema:\n'+req.schema_json},
                        {'role':'user','content':req.input_json}]}


class Transport:
    def __init__(self,config,root,client_factory=None,key=None):
        self.config=config;self.root=Path(root);self.loop=asyncio.new_event_loop()
        self.thread=threading.Thread(target=self.loop.run_forever,daemon=True);self.thread.start()
        self.key=key or os.environ.get('DEEPSEEK_API_KEY') or dotenv_values(ROOT/'.env.deepseek').get('DEEPSEEK_API_KEY')
        if not self.key:raise ValueError('Missing DEEPSEEK_API_KEY')
        self.factory=client_factory;self.runhead=head()
        asyncio.run_coroutine_threadsafe(self._init(),self.loop).result()

    async def _init(self):
        c=self.config
        self.condition=asyncio.Condition();self.active=0;self.peak=0;self.count=0;self.limit=c['concurrency'];self.halt=None
        self.events=[{'utc':now(),'limit':self.limit,'reason':'initial'}]
        self.client=self.factory() if self.factory else httpx.AsyncClient(
            timeout=httpx.Timeout(**c['timeouts_seconds']),
            limits=httpx.Limits(max_connections=c['http_connections'],max_keepalive_connections=c['http_connections']),
            transport=httpx.AsyncHTTPTransport(retries=0,limits=httpx.Limits(max_connections=c['http_connections'],max_keepalive_connections=c['http_connections'])),
            follow_redirects=False)

    async def _acquire(self):
        async with self.condition:
            await self.condition.wait_for(lambda:self.active<self.limit or self.halt is not None)
            if self.halt:raise RuntimeError('batch halted: '+self.halt)
            if self.count>=self.config['max_paid_requests']:raise RuntimeError('request budget exhausted')
            self.count+=1;self.active+=1;self.peak=max(self.peak,self.active)

    async def _release(self,reduce_reason=None,halt=None):
        async with self.condition:
            self.active-=1
            if reduce_reason:
                self.limit=max(1,self.limit//2);self.events.append({'utc':now(),'limit':self.limit,'active':self.active,'reason':reduce_reason})
            if halt:self.halt=halt
            self.condition.notify_all()

    async def _call(self,directory,ident,req):
        prefix=Path(directory)/ident;data=payload(req,self.config)
        save(prefix.with_suffix('.request.json'),{'head':self.runhead,'request':data,'request_hash':digest(data),
             'role_request_hash':req.request_hash,'role':req.role,'created_utc':now()})
        result={'id':ident,'role':req.role,'attempted':False,'status':None,'usage':None,'error':None,
                'request_hash':digest(data),'response_model':None,'finish_reason':None}
        start=time.monotonic();reduce_reason=None;halt=None;acquired=False;response_bytes=bytearray()
        try:
            await self._acquire();acquired=True;result['attempted']=True;result['started_utc']=now()
            save(prefix.with_suffix('.attempt.json'),{'utc':now(),'active':self.active,'limit':self.limit,'sequence':self.count})
            async with asyncio.timeout(self.config['total_timeout_seconds']):
                async with self.client.stream('POST',self.config['endpoint'],json=data,headers={'Authorization':'Bearer '+self.key}) as response:
                    result['status']=response.status_code
                    # Archive partial bytes too if timeout occurs after headers/keep-alive.
                    with prefix.with_suffix('.response.body').open('xb') as bodyfile:
                        async for chunk in response.aiter_bytes():
                            bodyfile.write(chunk);bodyfile.flush();response_bytes.extend(chunk)
            raw_text=response_bytes.decode('utf-8')
            try:raw=json.loads(raw_text)
            except (ValueError,TypeError):raw=None
            if isinstance(raw,dict):
                result['usage']=raw.get('usage');result['response_model']=raw.get('model');result['provider_id']=raw.get('id')
            if result['status'] in (429,503):reduce_reason='HTTP '+str(result['status'])
            if result['status'] in (400,401,402,403,404,422):halt='HTTP '+str(result['status'])
            if result['status']!=200:raise RuntimeError('HTTP '+str(result['status']))
            if result['response_model']!=self.config['model']:halt='model mismatch';raise ValueError(halt)
            choice=raw['choices'][0];result['finish_reason']=choice['finish_reason']
            if choice['finish_reason']!='stop':raise ValueError('incomplete finish: '+str(choice['finish_reason']))
            content=choice['message'].get('content')
            if not isinstance(content,str) or not content.strip():raise ValueError('empty final content')
            # H contract failures belong to the engine's isolated transaction.
            # Preserve the original content and its hash in role_response.
            if req.role != 'hypotheses':
                check(parse_json(content),json.loads(req.schema_json))
            return content
        except Exception as exc:
            if isinstance(exc,(TimeoutError,httpx.TimeoutException)):reduce_reason=type(exc).__name__
            result['error']={'type':type(exc).__name__,'message':str(exc)[:1000]}
            raise
        finally:
            if acquired:await self._release(reduce_reason,halt)
            result['elapsed_seconds']=time.monotonic()-start;result['completed_utc']=now()
            result['accounting']=usage_record(result['usage']);result['response_bytes']=len(response_bytes)
            save(prefix.with_suffix('.result.json'),result)
            print('CALL',Path(directory).parent.name,ident,result['status'],result['finish_reason'],result['error'],flush=True)

    def call(self,directory,ident,req):
        return asyncio.run_coroutine_threadsafe(self._call(directory,ident,req),self.loop).result()

    def close(self):
        asyncio.run_coroutine_threadsafe(self.client.aclose(),self.loop).result()
        save(self.root/'TRANSPORT_SUMMARY.json',{'count':self.count,'peak':self.peak,'final_limit':self.limit,'changes':self.events,'halt':self.halt})
        self.loop.call_soon_threadsafe(self.loop.stop);self.thread.join()


class TrajectoryPort:
    def __init__(self,transport,directory,forced_first=None,expected=None):
        self.transport=transport;self.directory=Path(directory);self.forced=forced_first;self.counter=0;self.actor_count=0
        self.expected=expected
    def complete(self,req):
        if req.role=='actor':
            self.actor_count+=1
            if self.actor_count==1 and self.expected:
                assert req.request_hash==self.expected['actor_hash'],'initial Actor differs from frozen prefix'
            if self.actor_count==1 and self.forced is not None:
                save(self.directory/'forced_first.json',{'source':'frozen_intervention_not_model','role_request_hash':req.request_hash,
                     'input':json.loads(req.input_json),'output':self.forced,'paid_request':False})
                return self.forced
        if self.counter==0 and self.expected and self.expected.get('first_paid_hash'):
            assert req.request_hash==self.expected['first_paid_hash'],'initial paid request differs from freeze'
        self.counter+=1
        return self.transport.call(self.directory/'calls',f'{self.counter:03}_{req.role}',req)
