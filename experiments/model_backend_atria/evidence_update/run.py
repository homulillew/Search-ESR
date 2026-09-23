"""E0/E1 exact-evidence diagnostic, paired across Qwen and Atria."""

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
from run_partial import checkpoint,file_sha

HERE=Path(__file__).resolve().parent
STUDY=HERE.parent
ATRIA=json.loads((STUDY/'provider.json').read_text())

INSTRUCTION=("Diagnostic only. Do not call tools or continue the original research. "
"Evaluate this tentative claim against only the visible prefix and any additional observed source evidence below. "
"An excerpt's failure to mention a fact does not by itself refute the fact. "
"Do not invent a final answer or source.\n\n"
"Tentative claim: {claim}\n\n{evidence}"
"Return exactly:\n"
"Evidence relation: supports | refutes | inconclusive | irrelevant\n"
"Current leading candidate:\n"
"Did the candidate change? yes | no\n"
"What remains unresolved:\n"
"Best next scope: corpus | document | window | stop")


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def digest(obj):return hashlib.sha256(json.dumps(obj,sort_keys=True).encode()).hexdigest()


def cases():
    rows=json.loads((HERE/'cases.json').read_text())['cases']
    if not 6<=len(rows)<=10:raise ValueError('M4 requires 6-10 cases')
    if {'supports','refutes','inconclusive','irrelevant'}- {x['expected_relation'] for x in rows}:
        raise ValueError('M4 relation coverage incomplete')
    return rows


def request(case,arm):
    original,_,_=checkpoint(case['qid'],case['seq'])
    messages=json.loads(json.dumps(original['messages']))
    if arm=='E0':evidence='No additional source evidence was observed.\n\n'
    elif arm=='E1':evidence=(f"Observed source evidence [{case['evidence_ref']}]:\n"
       f"{case['evidence_text']}\n\n")
    else:raise ValueError(arm)
    messages.append({'role':'user','content':INSTRUCTION.format(
        claim=case['tentative_claim'],evidence=evidence)})
    return messages


def freeze():
    path=HERE/'freeze.json'
    if path.exists():raise FileExistsError(path)
    qwen=Config.load()
    if qwen.model!='qwen3.7-flash':raise ValueError('Qwen model differs')
    rows=cases()
    sources=['experiments/model_backend_atria/evidence_update/run.py',
             'experiments/model_backend_atria/evidence_update/build_cases.py',
             'experiments/model_backend_atria/provider.json',
             'experiments/search_find_v3b/orthogonal_search/run_partial.py']
    doc={'frozen_at_utc':datetime.now(timezone.utc).isoformat(),
      'cases':[x['case_id'] for x in rows],'arm_order':['E0','E1'],
      'model_order':[qwen.model,ATRIA['model']],'samples_per_cell':1,
      'tools':None,'stream':False,'sampling_overrides':{},'max_retries':0,
      'qwen_model':qwen.model,'qwen_host':urlsplit(qwen.base_url).hostname,
      'atria_model':ATRIA['model'],'atria_host':urlsplit(ATRIA['base_url']).hostname,
      'timeout_seconds':120,'sdk_version':version('openai'),
      'case_file_sha256':sha(HERE/'cases.json'),
      'instruction_sha256':hashlib.sha256(INSTRUCTION.encode()).hexdigest(),
      'source_sha256':{p:file_sha(ROOT/p) for p in sources},
      'request_sha256':{f"{c['case_id']}:{arm}":digest(request(c,arm))
                        for c in rows for arm in ('E0','E1')},
      'failure_policy':'all 8 cases x 2 arms x 2 models, no selective retry'}
    path.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
    return doc


def gate():
    d=json.loads((HERE/'freeze.json').read_text())
    rows=cases()
    checks={'cases':sha(HERE/'cases.json')==d['case_file_sha256'],
            'instruction':hashlib.sha256(INSTRUCTION.encode()).hexdigest()==d['instruction_sha256'],
            'sources':all(file_sha(ROOT/p)==h for p,h in d['source_sha256'].items()),
            'requests':all(digest(request(c,arm))==d['request_sha256'][f"{c['case_id']}:{arm}"]
                           for c in rows for arm in ('E0','E1')),
            'one_sample_no_tools':d['samples_per_cell']==1 and d['tools'] is None}
    (HERE/'gate.txt').write_text('\n'.join(f'{"PASS" if v else "FAIL"} {k}' for k,v in checks.items())
                           +f'\n{sum(checks.values())}/{len(checks)} PASS\n')
    if not all(checks.values()):raise AssertionError('M4 gate failed')
    return checks


def emit(kind,**fields):
    with (HERE/'events.jsonl').open('a') as out:
        out.write(json.dumps({'time':datetime.now(timezone.utc).isoformat(),
                              'kind':kind,**fields},ensure_ascii=False)+'\n');out.flush()


def run():
    gate()
    if (HERE/'events.jsonl').exists():raise FileExistsError('M4 already attempted')
    qwen=Config.load();key=dotenv_values(ROOT/ATRIA['credential_file']).get(ATRIA['credential_field'])
    if not key:raise ValueError('Atria key missing')
    with OpenAI(api_key=qwen.api_key,base_url=qwen.base_url,timeout=120,max_retries=0) as qc, \
         OpenAI(api_key=key,base_url=ATRIA['base_url'],timeout=120,max_retries=0) as ac:
      for case in cases():
       for arm in ('E0','E1'):
        messages=request(case,arm)
        for model,client in ((qwen.model,qc),(ATRIA['model'],ac)):
         cell=f"{case['case_id']}:{arm}:{model}"
         params={'model':model,'messages':messages,'stream':False}
         emit('api_request',cell=cell,request=params,messages_sha256=digest(messages))
         try:
          response=client.chat.completions.create(**params)
          emit('api_response',cell=cell,response=response.model_dump(mode='json'))
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
