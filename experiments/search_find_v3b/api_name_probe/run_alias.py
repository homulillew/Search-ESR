"""Frozen search_document alias continuations against the S2 baseline."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import time
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'experiments/search_find_v3b/orthogonal_search'))
sys.path.insert(0,str(ROOT/'experiments/search_find_v3b/verification_state'))

from llm_chat.client import Config
from llm_chat.search_find_agent import SEARCH_FIND_PROMPT, SEARCH_FIND_TOOLS
from llm_chat.search_document_alias_agent import ALIAS_PROMPT, ALIAS_TOOLS, SearchDocumentAliasTools
from openai import OpenAI
from run_partial import checkpoint,file_sha,restore_prefix
from run_state import CASES,state_request

HERE=Path(__file__).resolve().parent
STATE=HERE.parent/'verification_state'
DECLARED={'search','search_document','open'}
HORIZON=4


def alias_request(case):
    request=state_request(case,'S2')
    system=request['messages'][0]['content']
    if system.count(SEARCH_FIND_PROMPT)!=1:
        raise AssertionError('original prompt not found exactly once')
    request['messages'][0]['content']=system.replace(SEARCH_FIND_PROMPT,ALIAS_PROMPT,1)
    request['tools']=ALIAS_TOOLS
    return request


def emit(kind,**fields):
    event={'time':datetime.now(timezone.utc).isoformat(),'kind':kind,**fields}
    with (HERE/'events.jsonl').open('a',encoding='utf-8') as f:
        f.write(json.dumps(event,ensure_ascii=False)+'\n');f.flush()


def freeze():
    path=HERE/'freeze.json'
    if path.exists():raise FileExistsError('alias freeze exists')
    config=Config.load()
    sources=[
        'llm_chat/agent.py','llm_chat/search_find_agent.py',
        'llm_chat/search_find_v3b_agent.py','llm_chat/search_document_alias_agent.py',
        'llm_chat/raw_windows.py','llm_chat/window_locator.py','llm_chat/window_units.py',
        'BCPlus/scripts/search_bcplus.py',
        'experiments/search_find_v3b/orthogonal_search/run_partial.py',
        'experiments/search_find_v3b/verification_state/run_state.py',
        'experiments/search_find_v3b/api_name_probe/run_alias.py',
    ]
    doc={
        'frozen_at':datetime.now(timezone.utc).isoformat(),
        'cases':CASES,'arm':'search_document_alias_plus_S2','comparison':'state S2 reused',
        'horizon_api_decisions':HORIZON,'replicates':1,
        'model':config.model,'base_url_host':urlsplit(config.base_url).hostname,
        'request_options':config.request_options(),
        'state_events_sha256':file_sha(STATE/'events.jsonl'),
        'source_sha256':{p:file_sha(ROOT/p) for p in sources},
        'request_sha256':{
            f"{c['qid']}:{c['seq']}":hashlib.sha256(json.dumps(alias_request(c),sort_keys=True).encode()).hexdigest()
            for c in CASES},
        'failure_policy':'all four cells; no repair, selective retry or best-of',
    }
    path.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
    return doc


def gate():
    doc=json.loads((HERE/'freeze.json').read_text())
    checks=[]
    def check(label,ok):checks.append((label,bool(ok)))
    check('sources match freeze',all(file_sha(ROOT/p)==sha for p,sha in doc['source_sha256'].items()))
    check('S2 events unchanged',file_sha(STATE/'events.jsonl')==doc['state_events_sha256'])
    config=Config.load()
    check('provider same',config.model==doc['model'] and urlsplit(config.base_url).hostname==doc['base_url_host'])
    check('same three tool names except local alias',{x['function']['name'] for x in ALIAS_TOOLS}==DECLARED)
    check('horizon four',doc['horizon_api_decisions']==HORIZON==4)
    originals={x['function']['name']:x for x in SEARCH_FIND_TOOLS}
    aliases={x['function']['name']:x for x in ALIAS_TOOLS}
    check('local argument schema unchanged',aliases['search_document']['function']['parameters']==originals['find']['function']['parameters'])
    check('corpus/open argument schemas unchanged',all(aliases[n]['function']['parameters']==originals[n]['function']['parameters'] for n in ('search','open')))
    state_events=[json.loads(x) for x in (STATE/'events.jsonl').open()]
    for case in CASES:
        qid,seq=case['qid'],case['seq']
        check(f'{qid}:{seq} S2 completed',any(x['kind']=='cell_end' and x.get('cell')==f'{qid}:{seq}:S2' for x in state_events))
        base=state_request(case,'S2');alias=alias_request(case)
        check(f'{qid}:{seq} exact request',hashlib.sha256(json.dumps(alias,sort_keys=True).encode()).hexdigest()==doc['request_sha256'][f'{qid}:{seq}'])
        check(f'{qid}:{seq} history unchanged',alias['messages'][1:]==base['messages'][1:])
        check(f'{qid}:{seq} other fields unchanged',
              {k:v for k,v in alias.items() if k not in ('messages','tools')}
              =={k:v for k,v in base.items() if k not in ('messages','tools')})
        check(f'{qid}:{seq} prompt name-only substitution',
              alias['messages'][0]['content']==base['messages'][0]['content'].replace(SEARCH_FIND_PROMPT,ALIAS_PROMPT,1))
        _,prior,_=checkpoint(qid,seq)
        tools=SearchDocumentAliasTools()
        try:
            restored=restore_prefix(tools,prior)
            check(f'{qid}:{seq} state restored',restored['documents']>0 and restored['windows']>0)
        finally:tools.close()
    lines=[f'{"PASS" if ok else "FAIL"} {label}' for label,ok in checks]
    lines.append(f'{sum(ok for _,ok in checks)}/{len(checks)} PASS')
    (HERE/'gate.txt').write_text('\n'.join(lines)+'\n')
    if not all(ok for _,ok in checks):raise AssertionError('alias gate failed')
    return lines[-1]


def run_cell(client,shared_searcher,case):
    qid,seq=case['qid'],case['seq'];cell=f'{qid}:{seq}:AL'
    request=alias_request(case);_,prior,_=checkpoint(qid,seq)
    tools=SearchDocumentAliasTools()
    status='horizon';prompt_tokens=total_tokens=0;began=time.monotonic()
    try:
        restoration=restore_prefix(tools,prior);tools.searcher=shared_searcher
        emit('cell_start',cell=cell,case=case,restoration=restoration)
        messages=request['messages']
        for decision in range(1,HORIZON+1):
            params={**request,'messages':messages}
            emit('api_request',cell=cell,decision=decision,request=params)
            start=time.monotonic()
            try:response=client.chat.completions.create(**params)
            except BaseException as exc:
                emit('api_error',cell=cell,decision=decision,error_type=type(exc).__name__,
                     error=str(exc)[:1000],elapsed_seconds=time.monotonic()-start)
                status='api_error';break
            raw=response.model_dump(mode='json')
            emit('api_response',cell=cell,decision=decision,response=raw,elapsed_seconds=time.monotonic()-start)
            usage=raw.get('usage') or {}
            prompt_tokens+=usage.get('prompt_tokens') or 0
            total_tokens+=usage.get('total_tokens') or 0
            if not response.choices:status='empty_choices';break
            choice=response.choices[0];msg=choice.message;calls=list(msg.tool_calls or [])
            if not calls:
                status='natural_stop' if choice.finish_reason=='stop' else 'abnormal_finish'
                emit('answer',cell=cell,decision=decision,finish_reason=choice.finish_reason,
                     text=msg.content or msg.refusal or '')
                break
            if choice.finish_reason!='tool_calls' or len(calls)>8:
                status='invalid_tool_batch'
                emit('invalid_tool_batch',cell=cell,decision=decision,
                     finish_reason=choice.finish_reason,count=len(calls))
                break
            ids=[c.id for c in calls]
            if any(not i for i in ids) or len(ids)!=len(set(ids)) or any(c.type!='function' for c in calls):
                status='invalid_tool_batch'
                emit('invalid_tool_batch',cell=cell,decision=decision,reason='id/type');break
            messages.append(msg.model_dump(exclude_none=True))
            invalid=[c.function.name for c in calls if c.function.name not in DECLARED]
            if invalid:
                status='undeclared_tool_call'
                emit('undeclared_tool_call',cell=cell,decision=decision,names=invalid)
                for c in calls:
                    messages.append({'role':'tool','tool_call_id':c.id,
                                     'content':json.dumps({'error':'undeclared_tool_call'})})
                break
            for call_index,call in enumerate(calls,start=1):
                name=call.function.name
                try:
                    args=json.loads(call.function.arguments)
                    if not isinstance(args,dict):raise ValueError('tool arguments must be object')
                except (ValueError,TypeError) as exc:
                    emit('malformed_tool_call',cell=cell,decision=decision,
                         call_index=call_index,name=name,error=str(exc))
                    result={'error':'malformed_tool_call'}
                else:
                    emit('tool_start',cell=cell,decision=decision,call_index=call_index,
                         name=name,arguments=args)
                    start=time.monotonic()
                    try:result=tools.execute(name,args)
                    except (ValueError,TypeError) as exc:
                        emit('invalid_tool_arguments',cell=cell,decision=decision,
                             call_index=call_index,name=name,error=str(exc))
                        result={'error':'invalid_tool_arguments','detail':str(exc)}
                    except BaseException as exc:
                        emit('tool_error',cell=cell,decision=decision,call_index=call_index,
                             name=name,error_type=type(exc).__name__,error=str(exc)[:1000],
                             elapsed_seconds=time.monotonic()-start)
                        status='tool_error';raise
                    emit('tool_result',cell=cell,decision=decision,call_index=call_index,
                         name=name,result=result,elapsed_seconds=time.monotonic()-start)
                    if 'error' not in result:
                        emit('tool_internal',cell=cell,decision=decision,call_index=call_index,
                             name=name,audit=tools.audit_record())
                messages.append({'role':'tool','tool_call_id':call.id,
                                 'content':json.dumps(result,ensure_ascii=False)})
    except BaseException as exc:
        if status!='tool_error':
            status='harness_error'
            emit('harness_error',cell=cell,error_type=type(exc).__name__,error=str(exc)[:1000])
    finally:
        emit('cell_end',cell=cell,status=status,prompt_tokens=prompt_tokens,
             total_tokens=total_tokens,elapsed_seconds=time.monotonic()-began)
        tools.close()
    return status


def run():
    gate()
    if (HERE/'events.jsonl').exists():raise FileExistsError('alias events exist; no best-of restart')
    doc=json.loads((HERE/'freeze.json').read_text());config=Config.load()
    if config.model!=doc['model'] or urlsplit(config.base_url).hostname!=doc['base_url_host']:
        raise AssertionError('provider differs from freeze')
    from BCPlus.scripts.search_bcplus import BCPlusSearcher
    searcher=None
    client=OpenAI(api_key=config.api_key,base_url=config.base_url,
                  timeout=config.timeout,max_retries=2)
    try:
        searcher=BCPlusSearcher()
        for case in CASES:
            print(f"{case['qid']}:{case['seq']}:AL {run_cell(client,searcher,case)}",flush=True)
    finally:
        client.close()
        if searcher is not None:searcher.close()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['freeze','gate','run'])
    args=parser.parse_args()
    if args.action=='freeze':freeze()
    elif args.action=='gate':print(gate())
    else:run()
