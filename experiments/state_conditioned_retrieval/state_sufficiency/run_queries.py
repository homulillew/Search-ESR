"""One frozen DeepSeek query-writing call per S1/control request; no retry."""
import hashlib
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[2]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def json_digest(v):
    return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True).encode()).hexdigest()

def one(client,item):
    start=time.monotonic()
    event={'case_id':item['case_id'],'arm':item['arm'],'request_sha256':item['request_sha256'],
           'request':item['request'],'started_utc':datetime.now(timezone.utc).isoformat()}
    query=None; error=None
    try:
        raw=client.chat.completions.create(**item['request']).model_dump(mode='json')
        event['response']=raw
        if raw['choices'][0]['finish_reason']!='stop':
            raise ValueError('abnormal_finish')
        parsed=json.loads(raw['choices'][0]['message']['content'])
        if not isinstance(parsed,dict) or set(parsed)!={'search_query'}:
            raise ValueError('schema')
        query=parsed['search_query']
        if not isinstance(query,str) or not query.strip() or len(query)>=1000:
            raise ValueError('query_content')
    except Exception as exc:
        error={'type':type(exc).__name__,'status':getattr(exc,'status_code',None),
               'message':str(exc)[:500]}
        event['error']=error
        query=None
    event['elapsed_seconds']=time.monotonic()-start
    result={'case_id':item['case_id'],'qid':item['qid'],'arm':item['arm'],
            'request_sha256':item['request_sha256'],'search_query':query,
            'query_sha256':hashlib.sha256(query.encode()).hexdigest() if query else None,
            'error':error['type'] if error else None,
            'usage':event.get('response',{}).get('usage')}
    return event,result

def main():
    from dotenv import dotenv_values
    from openai import OpenAI
    freeze=json.loads((BASE/'freeze.json').read_text())
    assert sha(BASE/'REQUESTS.json')==freeze['requests_sha256']
    bank=json.loads((BASE/'REQUESTS.json').read_text())
    assert [(x['case_id'],x['arm'],x['request_sha256']) for x in bank]==[tuple(x) for x in freeze['call_order']]
    assert all(json_digest(x['request'])==x['request_sha256'] for x in bank)
    events_path=BASE/'query_events.jsonl'; result_path=BASE/'QUERIES.json'
    assert not events_path.exists() and not result_path.exists(), 'query outputs already exist; never rerun'
    provider=json.loads((ROOT/'experiments/model_backend_deepseek/provider.json').read_text())
    assert provider['model']==freeze['provider']['model'] and provider['max_retries']==0
    key=dotenv_values(ROOT/provider['credential_file']).get(provider['credential_field'])
    if not key: raise ValueError('DeepSeek credential unavailable')
    completed={}
    with OpenAI(api_key=key,base_url=provider['base_url'],timeout=provider['timeout_seconds'],
                max_retries=0) as client, events_path.open('w') as out:
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures={pool.submit(one,client,item):(item['case_id'],item['arm']) for item in bank}
            for future in as_completed(futures):
                event,result=future.result()
                completed[(result['case_id'],result['arm'])]=result
                out.write(json.dumps(event,ensure_ascii=False)+'\n');out.flush()
                print(result['case_id'],result['arm'],
                      'ok' if result['error'] is None else result['error'],flush=True)
    assert len(completed)==len(bank)
    result=[completed[(x['case_id'],x['arm'])] for x in bank]
    result_path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('complete',len(result),'valid',sum(x['search_query'] is not None for x in result),flush=True)

if __name__=='__main__':main()
