"""One natural next decision per model; record and validate, never execute."""

import hashlib
import json
from pathlib import Path
import sys
from datetime import datetime, timezone
from importlib.metadata import version
from urllib.parse import urlsplit

from dotenv import dotenv_values
from openai import OpenAI

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'experiments/search_find_v3b/orthogonal_search'))
from llm_chat.client import Config
from llm_chat.search_find_agent import SEARCH_FIND_TOOLS
from experiments.model_backend_atria.protocol import validate_batch
from run_partial import checkpoint,file_sha

HERE=Path(__file__).resolve().parent
STUDY=HERE.parent
ATRIA=json.loads((STUDY/'provider.json').read_text())


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def digest(obj):return hashlib.sha256(json.dumps(obj,sort_keys=True).encode()).hexdigest()


def selection():
    result=json.loads((STUDY/'planning_probe/mechanical_summary.json').read_text())
    paired=result['paired']
    group_a=[(r['qid'],r['seq']) for r in paired if r['atria_scope']=='document' and r['qwen_scope']=='corpus'][:3]
    group_b=[(r['qid'],r['seq']) for r in paired if r['atria_scope']=='document' and r['qwen_scope']=='document'][:2]
    group_c=[(r['qid'],r['seq']) for r in paired if r['atria_scope']=='corpus' and r['qwen_scope']=='corpus'][:2]
    if len(group_a)<3 or len(group_b)<2 or len(group_c)<2:
        return [(r['qid'],r['seq']) for r in paired], 'all_13_due_to_short_stratum',
    return list(dict.fromkeys(group_a+group_b+group_c)), 'stratified_first_in_frozen_order'


def request(q,seq,model):
    original,_,_=checkpoint(q,seq)
    params=json.loads(json.dumps(original))
    params['model']=model
    return params


def freeze():
    path=HERE/'freeze.json'
    if path.exists():raise FileExistsError(path)
    chosen,rule=selection()
    qwen=Config.load()
    if qwen.model!='qwen3.7-flash':raise ValueError('Qwen model differs')
    sources=['experiments/model_backend_atria/natural_action_probe/run.py',
             'experiments/model_backend_atria/natural_action_probe/analyze.py',
             'experiments/model_backend_atria/protocol.py',
             'experiments/model_backend_atria/provider.json',
             'llm_chat/client.py',
             'llm_chat/search_find_agent.py',
             'llm_chat/search_find_v3b_agent.py',
             'experiments/search_find_v3b/orthogonal_search/run_partial.py']
    doc={'frozen_at_utc':datetime.now(timezone.utc).isoformat(),
         'selection_rule':rule,'selection':chosen,'one_decision_per_model':True,
         'no_tool_execution':True,'samples_per_cell':1,
         'qwen_model':qwen.model,'qwen_host':urlsplit(qwen.base_url).hostname,
         'atria_model':ATRIA['model'],'atria_host':urlsplit(ATRIA['base_url']).hostname,
         'qwen_allow_stop_with_calls':False,
         'atria_allow_stop_with_calls':ATRIA['allow_tool_calls_with_stop'],
         'qwen_timeout_seconds':qwen.timeout,
         'atria_timeout_seconds':ATRIA['timeout_seconds'],
         'max_retries':0,'sdk_version':version('openai'),
         'schema_sha256':digest(SEARCH_FIND_TOOLS),
         'm1_summary_sha256':sha(STUDY/'planning_probe/mechanical_summary.json'),
         'source_sha256':{p:file_sha(ROOT/p) for p in sources},
         'request_sha256':{f'{q}:{s}':digest(request(q,s,qwen.model)) for q,s in chosen},
         'failure_policy':'all selected paired cells; record errors; no best-of'}
    path.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
    return doc


def gate():
    d=json.loads((HERE/'freeze.json').read_text())
    chosen,rule=selection()
    checks={'selection':chosen==[tuple(x) for x in d['selection']] and rule==d['selection_rule'],
            'm1_unchanged':sha(STUDY/'planning_probe/mechanical_summary.json')==d['m1_summary_sha256'],
            'sources':all(file_sha(ROOT/p)==h for p,h in d['source_sha256'].items()),
            'schema':digest(SEARCH_FIND_TOOLS)==d['schema_sha256'],
            'requests':all(digest(request(q,s,d['qwen_model']))==d['request_sha256'][f'{q}:{s}']
                           for q,s in chosen),
            'one_step_no_execute':d['one_decision_per_model'] and d['no_tool_execution']}
    (HERE/'gate.txt').write_text('\n'.join(f'{"PASS" if v else "FAIL"} {k}' for k,v in checks.items())
                            +f'\n{sum(checks.values())}/{len(checks)} PASS\n')
    if not all(checks.values()):raise AssertionError('M2 gate failed')
    return checks


def emit(kind,**fields):
    with (HERE/'events.jsonl').open('a') as out:
        out.write(json.dumps({'time':datetime.now(timezone.utc).isoformat(),
                              'kind':kind,**fields},ensure_ascii=False)+'\n')
        out.flush()


def run():
    gate()
    if (HERE/'events.jsonl').exists():raise FileExistsError('M2 already attempted')
    qwen=Config.load()
    frozen=json.loads((HERE/'freeze.json').read_text())
    if qwen.model!=frozen['qwen_model'] or urlsplit(qwen.base_url).hostname!=frozen['qwen_host'] \
            or qwen.timeout!=frozen['qwen_timeout_seconds']:
        raise ValueError('Qwen config changed')
    key=dotenv_values(ROOT/ATRIA['credential_file']).get(ATRIA['credential_field'])
    if not key:raise ValueError('Atria key missing')
    selected,_=selection()
    with OpenAI(api_key=qwen.api_key,base_url=qwen.base_url,timeout=qwen.timeout,max_retries=0) as qc, \
         OpenAI(api_key=key,base_url=ATRIA['base_url'],timeout=ATRIA['timeout_seconds'],max_retries=0) as ac:
      for q,s in selected:
       for model,client,allow in ((qwen.model,qc,False),
                                  (ATRIA['model'],ac,ATRIA['allow_tool_calls_with_stop'])):
        cell=f'{q}:{s}:{model}'
        params=request(q,s,model)
        emit('api_request',cell=cell,request=params)
        try:
            response=client.chat.completions.create(**params)
            raw=response.model_dump(mode='json')
            choice=(raw.get('choices') or [{}])[0]
            parsed,error=validate_batch(choice,SEARCH_FIND_TOOLS,allow_stop_with_calls=allow)
            emit('api_response',cell=cell,response=raw,
                 raw_finish_reason=choice.get('finish_reason'),
                 raw_tool_calls=(choice.get('message') or {}).get('tool_calls'),
                 validation=error or 'valid',parsed_calls=parsed,
                 action=parsed[0]['name'] if len(parsed)==1 and error is None
                        else 'batch' if len(parsed)>1 and error is None
                        else 'stop' if not parsed and error is None else 'invalid')
            print(cell,'response',flush=True)
        except Exception as exc:
            emit('api_error',cell=cell,error_type=type(exc).__name__,
                 http_status=getattr(exc,'status_code',None),error=str(exc)[:500])
            print(cell,'error',type(exc).__name__,flush=True)


if __name__=='__main__':
    action=sys.argv[1] if len(sys.argv)>1 else 'gate'
    if action=='freeze':print(json.dumps(freeze(),ensure_ascii=False,indent=2))
    elif action=='gate':print(gate())
    elif action=='run':run()
    else:raise SystemExit('use freeze|gate|run')
