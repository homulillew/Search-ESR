"""Paired same-prefix, no-tool explicit planning probe."""

import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
from datetime import datetime, timezone
from importlib.metadata import version
from urllib.parse import urlsplit

from dotenv import dotenv_values
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'experiments/search_find_v3b/orthogonal_search'))
from llm_chat.client import Config
from run_partial import COHORTS, checkpoint, file_sha

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
ATRIA = json.loads((STUDY / 'provider.json').read_text())
DIAGNOSTIC = ("Diagnostic only. Do not continue the original research task and do not call tools.\n\n"
              "Based only on the information already visible in this conversation, identify the next research-control decision.\n\n"
              "Return exactly:\n"
              "Current unresolved need:\n"
              "Expected source type:\n"
              "Best scope: corpus | document | window | stop\n"
              "Target document/window: D# | W# | none\n"
              "Reason:\n"
              "Keep Reason to about 1–3 sentences.")
CASES = [(str(q), seq) for cells in COHORTS.values() for q, seq in cells]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def request(qid, seq):
    original, _, _ = checkpoint(qid, seq)
    messages = json.loads(json.dumps(original['messages']))
    messages.append({'role': 'user', 'content': DIAGNOSTIC})
    return messages


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def approved_annotations():
    path = STUDY / 'PREFIX_ONLY_ANNOTATIONS.json'
    data = json.loads(path.read_text())
    if data.get('status') != 'human_reviewed_frozen' or not data.get('human_reviewed_at_utc'):
        raise ValueError('M1 requires human-reviewed prefix-only annotation freeze')
    if len(data.get('rows', [])) != 13:
        raise ValueError('M1 requires 13 annotations')
    return data


def freeze():
    path = HERE / 'freeze.json'
    if path.exists():
        raise FileExistsError(path)
    approved_annotations()
    qwen = Config.load()
    if qwen.model != 'qwen3.7-flash':
        raise ValueError('historical Qwen model changed')
    sources = ['experiments/model_backend_atria/planning_probe/run.py',
               'experiments/model_backend_atria/provider.json',
               'llm_chat/client.py',
               'experiments/search_find_v3b/orthogonal_search/run_partial.py']
    old = json.loads((ROOT / 'experiments/search_find_v3b/orthogonal_search/freeze.json').read_text())
    doc = {'frozen_at_utc': datetime.now(timezone.utc).isoformat(),
      'git_head': subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
      'cases': CASES, 'arm_order': ['qwen3.7-flash', ATRIA['model']],
      'samples_per_cell': 1, 'tools': None, 'stream': False,
      'sampling_overrides': {}, 'sdk_max_retries': 0,
      'diagnostic_prompt': DIAGNOSTIC,
      'diagnostic_prompt_sha256': hashlib.sha256(DIAGNOSTIC.encode()).hexdigest(),
      'qwen_model': qwen.model, 'qwen_host': urlsplit(qwen.base_url).hostname,
      'qwen_timeout_seconds': qwen.timeout,
      'atria_model': ATRIA['model'], 'atria_host': urlsplit(ATRIA['base_url']).hostname,
      'atria_timeout_seconds': ATRIA['timeout_seconds'],
      'openai_sdk_version': version('openai'), 'python_version': platform.python_version(),
      'annotations_sha256': sha(STUDY/'PREFIX_ONLY_ANNOTATIONS.json'),
      'protocol_summary_sha256': sha(STUDY/'protocol_summary.json'),
      'source_sha256': {p: file_sha(ROOT/p) for p in sources},
      'original_event_sha256': old['run_events_sha256'],
      'original_request_sha256': old['checkpoint_request_sha256'],
      'messages_sha256': {f'{q}:{s}':digest(request(q,s)) for q,s in CASES},
      'strong_signal': 'Atria >=4 more compatible scopes of 13, not all stop, and >=2 better source/target judgments',
      'failure_policy': 'attempt all 26 model cells in order; no selective retry or best-of; record all failures',
    }
    path.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
    return doc


def gate():
    frozen = json.loads((HERE/'freeze.json').read_text())
    approved_annotations()
    old = json.loads((ROOT / 'experiments/search_find_v3b/orthogonal_search/freeze.json').read_text())
    checks = {
      'annotation': sha(STUDY/'PREFIX_ONLY_ANNOTATIONS.json') == frozen['annotations_sha256'],
      'protocol': sha(STUDY/'protocol_summary.json') == frozen['protocol_summary_sha256']
                  and json.loads((STUDY/'protocol_summary.json').read_text())['pass'],
      'sources': all(file_sha(ROOT/p)==h for p,h in frozen['source_sha256'].items()),
      'old_events': all(file_sha((ROOT/'experiments/runs/v003a_search_find'/
                        ('qid_546/20260922T121742.932067Z/events.jsonl' if q=='546' else
                         'qid_1094/20260922T113202.256169Z/events.jsonl')))==h
                        for q,h in frozen['original_event_sha256'].items()),
      'old_requests': old['checkpoint_request_sha256']==frozen['original_request_sha256'],
      'same_messages': all(digest(request(q,s))==frozen['messages_sha256'][f'{q}:{s}']
                           for q,s in CASES),
      'no_tools': frozen['tools'] is None and frozen['sampling_overrides']=={},
      'sample_count': len(CASES)==13 and frozen['samples_per_cell']==1,
    }
    (HERE/'gate.txt').write_text('\n'.join(f'{"PASS" if v else "FAIL"} {k}' for k,v in checks.items())
                           +f'\n{sum(checks.values())}/{len(checks)} PASS\n')
    if not all(checks.values()): raise AssertionError('M1 offline gate failed')
    return checks


def emit(kind, **fields):
    with (HERE/'events.jsonl').open('a') as out:
        out.write(json.dumps({'time':datetime.now(timezone.utc).isoformat(),
                              'kind':kind,**fields},ensure_ascii=False)+'\n')
        out.flush()


def run():
    gate()
    if (HERE/'events.jsonl').exists():
        raise FileExistsError('M1 events already exist; do not rerun completed cells')
    qwen = Config.load()
    key = dotenv_values(ROOT / ATRIA['credential_file']).get(ATRIA['credential_field'])
    if not key: raise ValueError('Atria key unavailable')
    if qwen.model!='qwen3.7-flash' or urlsplit(qwen.base_url).hostname!=json.loads((HERE/'freeze.json').read_text())['qwen_host']:
        raise ValueError('Qwen config differs from freeze')
    with OpenAI(api_key=qwen.api_key,base_url=qwen.base_url,timeout=qwen.timeout,max_retries=0) as qc, \
         OpenAI(api_key=key,base_url=ATRIA['base_url'],timeout=ATRIA['timeout_seconds'],max_retries=0) as ac:
      for q,s in CASES:
        messages=request(q,s)
        for model,client in ((qwen.model,qc),(ATRIA['model'],ac)):
            cell=f'{q}:{s}:{model}'
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
    if action=='freeze': print(json.dumps(freeze(),ensure_ascii=False,indent=2))
    elif action=='gate': print(gate())
    elif action=='run': run()
    else: raise SystemExit('use freeze|gate|run')
