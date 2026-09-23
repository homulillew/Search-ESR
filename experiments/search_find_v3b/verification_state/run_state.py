"""S1/S2 minimal-state continuations with frozen S0 Orthogonal Search reuse."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import time
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'experiments/search_find_v3b/orthogonal_search'))

from llm_chat.client import Config
from llm_chat.search_find_agent import SEARCH_FIND_TOOLS
from llm_chat.search_find_v3b_agent import OrthogonalSearchFindTools
from openai import OpenAI
from run_partial import DECLARED, checkpoint, file_sha, restore_prefix

HERE = Path(__file__).resolve().parent
ORTH = HERE.parent / 'orthogonal_search'
CASES = [
    {'qid': '546', 'seq': 9, 'need': "Which candidate's 2023 run had a decider win followed by 4-3 and 4-0 wins and then a loss?", 'focus': 'D5'},
    {'qid': '1094', 'seq': 69, 'need': 'Which early-21st-century Inter match had the 95th-minute free kick, and who took it?', 'focus': 'D38'},
    {'qid': '1094', 'seq': 77, 'need': 'Which player took the 95th-minute free kick in a match matching the Inter clue?', 'focus': 'D14'},
    {'qid': '1094', 'seq': 93, 'need': 'Which player took the 95th-minute free kick in a match matching the Inter clue?', 'focus': 'D14'},
]
HORIZON = 4


def state_request(case, arm):
    request, _, _ = checkpoint(case['qid'], case['seq'])
    request = json.loads(json.dumps(request))
    if arm not in ('S1', 'S2'):
        raise ValueError('state arm must be S1 or S2')
    addition = '\n\nCurrent unresolved need:\n' + case['need']
    if arm == 'S2':
        addition += '\n\nPromising existing document:\n' + case['focus']
    request['messages'][0]['content'] += addition
    return request


def emit(kind, **fields):
    event = {'time': datetime.now(timezone.utc).isoformat(), 'kind': kind, **fields}
    with (HERE / 'events.jsonl').open('a', encoding='utf-8') as f:
        f.write(json.dumps(event, ensure_ascii=False) + '\n')
        f.flush()


def freeze():
    path = HERE / 'freeze.json'
    if path.exists():
        raise FileExistsError('state freeze already exists')
    config = Config.load()
    sources = [
        'llm_chat/agent.py', 'llm_chat/search_find_agent.py',
        'llm_chat/search_find_v3b_agent.py', 'llm_chat/raw_windows.py',
        'llm_chat/window_locator.py', 'llm_chat/window_units.py',
        'BCPlus/scripts/search_bcplus.py',
        'experiments/search_find_v3b/orthogonal_search/run_partial.py',
        'experiments/search_find_v3b/verification_state/run_state.py',
    ]
    doc = {
        'frozen_at': datetime.now(timezone.utc).isoformat(), 'cases': CASES,
        'arms': ['S1', 'S2'], 's0_reuse_arm': 'orthogonal_search P1',
        'horizon_api_decisions': HORIZON, 'replicates': 1,
        'model': config.model, 'base_url_host': urlsplit(config.base_url).hostname,
        'request_options': config.request_options(),
        'orthogonal_events_sha256': file_sha(ORTH / 'events.jsonl'),
        'source_sha256': {p: file_sha(ROOT / p) for p in sources},
        'request_sha256': {
            f"{c['qid']}:{c['seq']}:{arm}": hashlib.sha256(json.dumps(state_request(c, arm), sort_keys=True).encode()).hexdigest()
            for c in CASES for arm in ('S1', 'S2')},
        'failure_policy': 'all eight cells attempted; no selective retry or best-of',
    }
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n')
    return doc


def gate():
    doc = json.loads((HERE / 'freeze.json').read_text())
    checks = []
    def check(name, ok):
        checks.append((name, bool(ok)))
    check('frozen sources unchanged', all(file_sha(ROOT / p) == sha for p, sha in doc['source_sha256'].items()))
    check('S0 source events unchanged', file_sha(ORTH / 'events.jsonl') == doc['orthogonal_events_sha256'])
    check('model and endpoint unchanged', Config.load().model == doc['model'] and
          urlsplit(Config.load().base_url).hostname == doc['base_url_host'])
    check('declared names unchanged', DECLARED == {'search', 'find', 'open'})
    check('four decisions', doc['horizon_api_decisions'] == HORIZON == 4)
    orth_events = [json.loads(x) for x in (ORTH / 'events.jsonl').open()]
    for c in CASES:
        qid, seq = c['qid'], c['seq']
        cell = f'{qid}:{seq}:P1'
        check(f'{cell} S0 completed', any(x['kind'] == 'cell_end' and x.get('cell') == cell for x in orth_events))
        base, prior, _ = checkpoint(qid, seq)
        snap = [x['audit']['handles'] for x in prior if x['kind'] == 'tool_internal'][-1]
        check(f'{qid}:{seq} focus existed in prefix', c['focus'] in [d['doc_ref'] for d in snap['documents']])
        check(f'{qid}:{seq} no gold in state', 'Ding Junhui' not in c['need'] and 'Andrea Pirlo' not in c['need'])
        for arm in ('S1', 'S2'):
            request = state_request(c, arm)
            digest = hashlib.sha256(json.dumps(request, sort_keys=True).encode()).hexdigest()
            check(f'{qid}:{seq}:{arm} exact request', digest == doc['request_sha256'][f'{qid}:{seq}:{arm}'])
            check(f'{qid}:{seq}:{arm} same schema/history', request['tools'] == base['tools'] == SEARCH_FIND_TOOLS
                  and request['messages'][1:] == base['messages'][1:]
                  and {k:v for k,v in request.items() if k != 'messages'} == {k:v for k,v in base.items() if k != 'messages'})
            added = request['messages'][0]['content'][len(base['messages'][0]['content']):]
            expected = '\n\nCurrent unresolved need:\n' + c['need']
            if arm == 'S2': expected += '\n\nPromising existing document:\n' + c['focus']
            check(f'{qid}:{seq}:{arm} only frozen state appended', added == expected)
        tools = OrthogonalSearchFindTools()
        try:
            state = restore_prefix(tools, prior)
            check(f'{qid}:{seq} restored', state['documents'] > 0 and state['windows'] > 0)
        finally:
            tools.close()
    lines = [f'{"PASS" if ok else "FAIL"} {name}' for name, ok in checks]
    lines.append(f'{sum(ok for _, ok in checks)}/{len(checks)} PASS')
    (HERE / 'gate.txt').write_text('\n'.join(lines) + '\n')
    if not all(ok for _, ok in checks):
        raise AssertionError('state offline gate failed')
    return lines[-1]


def run_cell(client, shared_searcher, case, arm):
    qid, seq = case['qid'], case['seq']
    request = state_request(case, arm)
    _, prior, _ = checkpoint(qid, seq)
    cell = f'{qid}:{seq}:{arm}'
    tools = OrthogonalSearchFindTools()
    status = 'horizon'
    prompt_tokens = total_tokens = 0
    began = time.monotonic()
    try:
        restoration = restore_prefix(tools, prior)
        tools.searcher = shared_searcher
        emit('cell_start', cell=cell, case=case, restoration=restoration)
        messages = request['messages']
        for decision in range(1, HORIZON+1):
            params = {**request, 'messages': messages}
            emit('api_request', cell=cell, decision=decision, request=params)
            start = time.monotonic()
            try:
                response = client.chat.completions.create(**params)
            except BaseException as exc:
                emit('api_error', cell=cell, decision=decision, error_type=type(exc).__name__,
                     error=str(exc)[:1000], elapsed_seconds=time.monotonic()-start)
                status = 'api_error'; break
            raw = response.model_dump(mode='json')
            emit('api_response', cell=cell, decision=decision, response=raw,
                 elapsed_seconds=time.monotonic()-start)
            usage = raw.get('usage') or {}
            prompt_tokens += usage.get('prompt_tokens') or 0
            total_tokens += usage.get('total_tokens') or 0
            if not response.choices:
                status = 'empty_choices'; break
            choice = response.choices[0]
            msg = choice.message
            calls = list(msg.tool_calls or [])
            if not calls:
                status = 'natural_stop' if choice.finish_reason == 'stop' else 'abnormal_finish'
                emit('answer', cell=cell, decision=decision, finish_reason=choice.finish_reason,
                     text=msg.content or msg.refusal or '')
                break
            if choice.finish_reason != 'tool_calls' or len(calls) > 8:
                status = 'invalid_tool_batch'
                emit('invalid_tool_batch', cell=cell, decision=decision,
                     finish_reason=choice.finish_reason, count=len(calls))
                break
            ids = [c.id for c in calls]
            if any(not i for i in ids) or len(ids) != len(set(ids)) or any(c.type != 'function' for c in calls):
                status = 'invalid_tool_batch'
                emit('invalid_tool_batch', cell=cell, decision=decision, reason='id/type')
                break
            messages.append(msg.model_dump(exclude_none=True))
            invalid = [c.function.name for c in calls if c.function.name not in DECLARED]
            if invalid:
                status = 'undeclared_tool_call'
                emit('undeclared_tool_call', cell=cell, decision=decision, names=invalid)
                for c in calls:
                    messages.append({'role': 'tool', 'tool_call_id': c.id,
                                     'content': json.dumps({'error':'undeclared_tool_call'})})
                break
            for call_index, call in enumerate(calls, start=1):
                name = call.function.name
                try:
                    args = json.loads(call.function.arguments)
                    if not isinstance(args, dict): raise ValueError('tool arguments must be object')
                except (ValueError, TypeError) as exc:
                    emit('malformed_tool_call', cell=cell, decision=decision,
                         call_index=call_index, name=name, error=str(exc))
                    result = {'error':'malformed_tool_call'}
                else:
                    emit('tool_start', cell=cell, decision=decision, call_index=call_index,
                         name=name, arguments=args)
                    start = time.monotonic()
                    try:
                        result = tools.execute(name, args)
                    except BaseException as exc:
                        emit('tool_error', cell=cell, decision=decision, call_index=call_index,
                             name=name, error_type=type(exc).__name__, error=str(exc)[:1000],
                             elapsed_seconds=time.monotonic()-start)
                        status = 'tool_error'; raise
                    emit('tool_result', cell=cell, decision=decision, call_index=call_index,
                         name=name, result=result, elapsed_seconds=time.monotonic()-start)
                    emit('tool_internal', cell=cell, decision=decision, call_index=call_index,
                         name=name, audit=tools.audit_record())
                messages.append({'role':'tool','tool_call_id':call.id,
                                 'content':json.dumps(result,ensure_ascii=False)})
    except BaseException as exc:
        if status != 'tool_error':
            status = 'harness_error'
            emit('harness_error', cell=cell, error_type=type(exc).__name__, error=str(exc)[:1000])
    finally:
        emit('cell_end', cell=cell, status=status, prompt_tokens=prompt_tokens,
             total_tokens=total_tokens, elapsed_seconds=time.monotonic()-began)
        tools.close()
    return status


def run():
    gate()
    if (HERE / 'events.jsonl').exists():
        raise FileExistsError('state events already exist; no best-of restart')
    frozen = json.loads((HERE / 'freeze.json').read_text())
    config = Config.load()
    if config.model != frozen['model'] or urlsplit(config.base_url).hostname != frozen['base_url_host']:
        raise AssertionError('provider differs from freeze')
    from BCPlus.scripts.search_bcplus import BCPlusSearcher
    searcher = None
    client = OpenAI(api_key=config.api_key, base_url=config.base_url,
                    timeout=config.timeout, max_retries=2)
    try:
        searcher = BCPlusSearcher()
        for case in CASES:
            for arm in ('S1', 'S2'):
                print(f"{case['qid']}:{case['seq']}:{arm} {run_cell(client, searcher, case, arm)}", flush=True)
    finally:
        client.close()
        if searcher is not None: searcher.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['freeze','gate','run'])
    args = parser.parse_args()
    if args.action == 'freeze': freeze()
    elif args.action == 'gate': print(gate())
    else: run()
