"""Frozen synthetic-provider and strict-harness compatibility preflight."""

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

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from llm_chat.search_find_agent import SEARCH_FIND_PROMPT, SEARCH_FIND_TOOLS
from experiments.model_backend_deepseek.protocol import validate_batch, validate_then_execute
from experiments.model_backend_deepseek.cache_usage import extract

HERE = Path(__file__).resolve().parent
CONFIG = json.loads((HERE / 'provider.json').read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def emit(kind, **data):
    with (HERE / 'protocol_events.jsonl').open('a') as out:
        out.write(json.dumps({'time': datetime.now(timezone.utc).isoformat(),
                              'kind': kind, **data}, ensure_ascii=False) + '\n')
        out.flush()


def freeze():
    path = HERE / 'freeze_protocol.json'
    if path.exists():
        raise FileExistsError(path)
    source = ['experiments/model_backend_deepseek/provider.json',
              'experiments/model_backend_deepseek/protocol.py',
              'experiments/model_backend_deepseek/cache_usage.py',
              'experiments/model_backend_deepseek/preflight.py',
              'llm_chat/client.py', 'llm_chat/agent.py',
              'llm_chat/search_find_agent.py', 'llm_chat/search_find_v3b_agent.py',
              'experiments/search_find_v3b/orthogonal_search/run_partial.py']
    checkpoints = json.loads((ROOT / 'experiments/search_find_v3b/orthogonal_search/freeze.json').read_text())
    doc = {
        'frozen_at_utc': datetime.now(timezone.utc).isoformat(),
        'git_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'model': CONFIG['model'], 'base_url_host': urlsplit(CONFIG['base_url']).hostname,
        'allow_tool_calls_with_stop': CONFIG['allow_tool_calls_with_stop'],
        'timeout_seconds': CONFIG['timeout_seconds'], 'max_retries': CONFIG['max_retries'],
        'openai_sdk_version': version('openai'), 'python_version': platform.python_version(),
        'jsonschema_version': version('jsonschema'),
        'tool_schema_sha256': digest(SEARCH_FIND_TOOLS),
        'agent_prompt_sha256': hashlib.sha256(SEARCH_FIND_PROMPT.encode()).hexdigest(),
        'baseline_fingerprints_sha256': sha(HERE / 'BASELINE_FINGERPRINTS.json'),
        'checkpoint_request_sha256': checkpoints['checkpoint_request_sha256'],
        'checkpoint_source_event_sha256': checkpoints['run_events_sha256'],
        'source_sha256': {p: sha(ROOT / p) for p in source},
        'live_requests': ['ordinary_chat', 'auto_tool', 'forced_single_tool', 'multi_tool_prompt'],
        'synthetic_cases': ['stop_with_calls', 'malformed_json', 'undeclared_tool',
                            'missing_required', 'batch_atomicity'],
        'success_gate': 'ordinary response; auto and forced legal Search; all synthetic validation expectations; raw finish preserved. Multi-tool prompt is observational because provider may choose one call.',
    }
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n')
    return doc


def gate():
    doc = json.loads((HERE / 'freeze_protocol.json').read_text())
    checks = {
        'model': doc['model'] == CONFIG['model'],
        'host': doc['base_url_host'] == urlsplit(CONFIG['base_url']).hostname,
        'compatibility': doc['allow_tool_calls_with_stop'] is True,
        'timeout': doc['timeout_seconds'] == CONFIG['timeout_seconds'],
        'sdk': doc['openai_sdk_version'] == version('openai'),
        'schema': doc['tool_schema_sha256'] == digest(SEARCH_FIND_TOOLS),
        'prompt': doc['agent_prompt_sha256'] == hashlib.sha256(SEARCH_FIND_PROMPT.encode()).hexdigest(),
        'baseline_fingerprints': doc['baseline_fingerprints_sha256'] == sha(HERE / 'BASELINE_FINGERPRINTS.json'),
        'sources': all(sha(ROOT / p) == h for p, h in doc['source_sha256'].items()),
    }
    old = json.loads((ROOT / 'experiments/search_find_v3b/orthogonal_search/freeze.json').read_text())
    checks['checkpoint_hashes'] = doc['checkpoint_request_sha256'] == old['checkpoint_request_sha256']
    checks['checkpoint_events'] = all(sha(ROOT / 'experiments/runs/v003a_search_find' /
                  ('qid_546/20260922T121742.932067Z/events.jsonl' if q == '546' else
                   'qid_1094/20260922T113202.256169Z/events.jsonl')) == h
                  for q, h in doc['checkpoint_source_event_sha256'].items())
    (HERE / 'gate_protocol.txt').write_text('\n'.join(f'{"PASS" if v else "FAIL"} {k}'
                  for k, v in checks.items()) + f'\n{sum(checks.values())}/{len(checks)} PASS\n')
    if not all(checks.values()):
        raise AssertionError('protocol freeze gate failed')
    return checks


def fake(name, args):
    return {'name': name, 'arguments': args, 'synthetic_result': 'ok'}


def synthetic_choice(calls, finish='tool_calls'):
    return {'finish_reason': finish, 'message': {'tool_calls': calls}}


def tool_call(identifier, name, arguments):
    return {'id': identifier, 'type': 'function',
            'function': {'name': name, 'arguments': arguments}}


def run():
    gate()
    if (HERE / 'protocol_events.jsonl').exists():
        raise FileExistsError('preflight already attempted; retain raw failures')
    key = dotenv_values(ROOT / CONFIG['credential_file']).get(CONFIG['credential_field'])
    if not key:
        raise ValueError('DeepSeek credential unavailable')
    requests = [
      ('ordinary_chat', [{'role': 'user', 'content': 'Reply exactly PONG.'}], None),
      ('auto_tool', [{'role': 'system', 'content': 'Use the supplied tool for the requested operation.'},
                     {'role': 'user', 'content': 'Call search once with query synthetic preflight and k=1. Do not answer without a tool result.'}], 'auto'),
      ('forced_single_tool', [{'role': 'user', 'content': 'Call search with query synthetic preflight and k=1.'}],
       {'type': 'function', 'function': {'name': 'search'}}),
      ('multi_tool_prompt', [{'role': 'system', 'content': 'Use the supplied tools.'},
                             {'role': 'user', 'content': 'In the SAME response, call search twice: query alpha with k=1 and query beta with k=1. Do not answer yet.'}], 'auto'),
    ]
    with OpenAI(api_key=key, base_url=CONFIG['base_url'], timeout=CONFIG['timeout_seconds'],
                max_retries=CONFIG['max_retries']) as client:
        for label, messages, tool_choice in requests:
            params = {'model': CONFIG['model'], 'messages': messages, 'stream': False}
            if tool_choice is not None:
                params.update(tools=SEARCH_FIND_TOOLS, tool_choice=tool_choice)
            emit('request', label=label, request=params)
            try:
                response = client.chat.completions.create(**params)
                raw = response.model_dump(mode='json')
                choice = raw['choices'][0]
                parsed, error = validate_batch(choice, SEARCH_FIND_TOOLS,
                      allow_stop_with_calls=CONFIG['allow_tool_calls_with_stop'])
                executed = [fake(c['name'], c['arguments']) for c in parsed] if not error else []
                emit('response', label=label, response=raw, raw_finish_reason=choice.get('finish_reason'),
                     raw_tool_calls=(choice.get('message') or {}).get('tool_calls'),
                     validation='valid' if error is None else error, execution=executed,
                     cache_usage=extract(raw))
            except Exception as exc:
                emit('api_error', label=label, error_type=type(exc).__name__,
                     http_status=getattr(exc, 'status_code', None), error=str(exc)[:500])
    cases = {
      'stop_with_calls': (synthetic_choice([tool_call('s1','search','{"query":"x","k":1}')], 'stop'), 'valid', 1),
      'malformed_json': (synthetic_choice([tool_call('s1','search','{')]), 'malformed_json', 0),
      'undeclared_tool': (synthetic_choice([tool_call('s1','not_declared','{}')]), 'undeclared_tool', 0),
      'missing_required': (synthetic_choice([tool_call('s1','find','{"query":"x"}')]), 'schema_invalid', 0),
      'batch_atomicity': (synthetic_choice([tool_call('s1','search','{"query":"x"}'),
                         tool_call('s2','find','{"query":"x"}')]), 'schema_invalid', 0),
    }
    for label, (choice, expected, count) in cases.items():
        result = validate_then_execute(choice, SEARCH_FIND_TOOLS, fake,
                        allow_stop_with_calls=CONFIG['allow_tool_calls_with_stop'])
        emit('synthetic', label=label, raw_finish_reason=choice['finish_reason'],
             raw_tool_calls=choice['message']['tool_calls'], validation=result['validation'],
             execution=result['executed'], passed=result['validation']==expected and len(result['executed'])==count)
    return summarize()


def summarize():
    events = [json.loads(line) for line in (HERE / 'protocol_events.jsonl').open()]
    by_label = {e['label']: e for e in events if e['kind'] in ('response','api_error','synthetic')}
    checks = {
      'ordinary_chat': by_label.get('ordinary_chat',{}).get('validation')=='valid' and
          bool(by_label.get('ordinary_chat',{}).get('response',{}).get('choices',[{}])[0].get('message',{}).get('content')),
      'auto_tool': by_label.get('auto_tool',{}).get('validation')=='valid' and
          any(x['name']=='search' for x in by_label.get('auto_tool',{}).get('execution',[])),
      'forced_single_tool': by_label.get('forced_single_tool',{}).get('validation')=='valid' and
          len(by_label.get('forced_single_tool',{}).get('execution',[]))==1,
      'synthetic_validation': all(by_label.get(k,{}).get('passed') for k in
          ('stop_with_calls','malformed_json','undeclared_tool','missing_required','batch_atomicity')),
    }
    doc = {'checks': checks, 'pass': all(checks.values()),
           'observed': {k: {'finish_reason':v.get('raw_finish_reason'),
                           'tool_count': len(v.get('raw_tool_calls') or []),
                           'validation':v.get('validation'), 'error_type':v.get('error_type'),
                           'cache_usage':v.get('cache_usage')}
                        for k,v in by_label.items()}}
    (HERE/'protocol_summary.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
    return doc


if __name__ == '__main__':
    action = sys.argv[1] if len(sys.argv)>1 else 'gate'
    if action == 'freeze': print(json.dumps(freeze(),ensure_ascii=False,indent=2))
    elif action == 'gate': print(gate())
    elif action == 'run': print(json.dumps(run(),ensure_ascii=False,indent=2))
    elif action == 'summarize': print(json.dumps(summarize(),ensure_ascii=False,indent=2))
    else: raise SystemExit('use freeze|gate|run|summarize')
