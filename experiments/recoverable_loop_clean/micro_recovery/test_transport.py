import asyncio
import json
from pathlib import Path
import httpx
import pytest
from .transport import Transport,TrajectoryPort,usage_record,payload
from .common import read
from llm_chat.recoverable_loop.roles import request


def config():return read(Path(__file__).with_name('CONFIG.json'))
def response():return {'id':'mock','model':'deepseek-flash','choices':[{'finish_reason':'stop','message':{'content':'{"decision":"request_closure"}'}}],
                       'usage':{'prompt_tokens':100,'completion_tokens':10,'total_tokens':110,'prompt_cache_hit_tokens':64,'prompt_cache_miss_tokens':36}}


def test_success_headers_not_archived_usage_and_forced_decision(tmp_path):
    calls=[]
    async def handler(req):
        calls.append(req);assert req.headers['authorization']=='Bearer TEST_ONLY'
        return httpx.Response(200,json=response())
    t=Transport(config(),tmp_path,lambda:httpx.AsyncClient(transport=httpx.MockTransport(handler)),key='TEST_ONLY')
    p=TrajectoryPort(t,tmp_path/'trajectory',{'decision':'request_closure'});req=request('actor',{'Q':'test'})
    assert p.complete(req)=={'decision':'request_closure'}
    assert json.loads(p.complete(req))=={'decision':'request_closure'}
    t.close();assert len(calls)==1
    files=list(tmp_path.rglob('*'))
    for f in files:
        if f.is_file():assert 'TEST_ONLY' not in f.read_text()
    result=read(next(tmp_path.rglob('*.result.json')))
    assert result['accounting']['complete'] and result['accounting']['tokens']['hit']==64


@pytest.mark.parametrize('mode',['429','timeout','bad_json','length','wrong_model','401'])
def test_failure_retained_no_retry_and_concurrency_policy(tmp_path,mode):
    calls=[]
    async def handler(req):
        calls.append(req)
        if mode=='timeout':raise httpx.ReadTimeout('mock timeout')
        if mode in ['429','401']:return httpx.Response(int(mode),json={'error':'mock'})
        raw=response()
        if mode=='bad_json':raw['choices'][0]['message']['content']='not JSON'
        elif mode=='length':raw['choices'][0]['finish_reason']='length'
        elif mode=='wrong_model':raw['model']='wrong'
        return httpx.Response(200,json=raw)
    t=Transport(config(),tmp_path,lambda:httpx.AsyncClient(transport=httpx.MockTransport(handler)),key='TEST_ONLY')
    req=request('actor',{'Q':'test'})
    with pytest.raises(Exception):t.call(tmp_path/'calls','001_actor',req)
    assert len(calls)==1
    if mode in ['429','timeout']:assert t.limit==6
    if mode in ['401','wrong_model']:assert t.halt
    t.close();assert read(tmp_path/'calls/001_actor.result.json')['error']


def test_budget_no_dispatch_after_limit(tmp_path):
    calls=[]
    async def handler(req):calls.append(req);return httpx.Response(200,json=response())
    c=config();c['max_paid_requests']=1
    t=Transport(c,tmp_path,lambda:httpx.AsyncClient(transport=httpx.MockTransport(handler)),key='TEST_ONLY')
    req=request('actor',{'Q':'test'});t.call(tmp_path/'calls','001',req)
    with pytest.raises(RuntimeError):t.call(tmp_path/'calls','002',req)
    t.close();assert len(calls)==1
    assert read(tmp_path/'calls/002.result.json')['attempted'] is False


def test_usage_mismatch_excluded():
    x=response()['usage'];x['prompt_cache_miss_tokens']=35
    assert not usage_record(x)['complete']
    assert not usage_record(None)['complete']


def test_parallel_io_really_overlaps(tmp_path):
    from concurrent.futures import ThreadPoolExecutor
    active=0;peak=0
    async def handler(req):
        nonlocal active,peak
        active+=1;peak=max(peak,active);await asyncio.sleep(.02);active-=1
        return httpx.Response(200,json=response())
    t=Transport(config(),tmp_path,lambda:httpx.AsyncClient(transport=httpx.MockTransport(handler)),key='TEST_ONLY')
    req=request('actor',{'Q':'test'})
    with ThreadPoolExecutor(max_workers=12) as pool:
        futures=[pool.submit(t.call,tmp_path/'calls',str(i),req) for i in range(12)]
        for f in futures:f.result()
    t.close();assert peak>1 and t.peak==12
