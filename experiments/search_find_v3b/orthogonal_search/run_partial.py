"""Frozen-checkpoint P0/P1 partial continuations for Orthogonal Search."""

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
import time
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from llm_chat.client import Config
from llm_chat.raw_windows import Window
from llm_chat.search_find_agent import SEARCH_FIND_TOOLS, SearchFindTools
from llm_chat.search_find_v3b_agent import OrthogonalSearchFindTools
from openai import OpenAI

HERE = Path(__file__).resolve().parent
RUNS = {
    '546': ROOT / 'experiments/runs/v003a_search_find/qid_546/20260922T121742.932067Z',
    '1094': ROOT / 'experiments/runs/v003a_search_find/qid_1094/20260922T113202.256169Z',
}
COHORTS = {
    'broad_relocation': [('546', s) for s in (9, 17, 25, 33, 41)]
                        + [('1094', s) for s in (23, 34, 45, 53, 61)],
    'local_verification': [('1094', s) for s in (69, 77, 93)],
}
HORIZON = 4
DECLARED = {x['function']['name'] for x in SEARCH_FIND_TOOLS}


def file_sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_events(qid):
    return [json.loads(line) for line in (RUNS[qid] / 'events.jsonl').open()]


def checkpoint(qid, seq):
    events = load_events(qid)
    cp = next(x for x in events if x['seq'] == seq and x['kind'] == 'api_request')
    prior = [x for x in events if x['seq'] < seq]
    return cp['request'], prior, events


def original_windows(prior):
    for x in prior:
        if x['kind'] != 'tool_internal':
            continue
        raw = x['audit']['raw_result']
        views = raw if isinstance(raw, list) else [raw]
        for view in views:
            if isinstance(view, dict) and 'window_ref' in view:
                yield view


def restore_prefix(tools, prior):
    """Reconstruct exact D/W identities without searching or relocalizing."""
    audits = [x['audit'] for x in prior if x['kind'] == 'tool_internal']
    if not audits:
        raise AssertionError('checkpoint has no tool state')
    snap = audits[-1]['handles']
    db_path = ROOT / 'BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite'
    db = sqlite3.connect(f'{db_path.as_uri()}?mode=ro', uri=True)
    try:
        builder = tools._windows()
        for d in snap['documents']:
            ref = d['doc_ref']
            key = (str(d['docid']), d['document_sha256'])
            row = db.execute('SELECT text, url FROM documents WHERE docid=?', (key[0],)).fetchone()
            if row is None or hashlib.sha256(row[0].encode()).hexdigest() != key[1]:
                raise AssertionError(f'corpus identity mismatch: {ref}')
            assert builder.register(key[0], row[0], row[1]) == key
            got_ref, is_new = tools.handles.document(key)
            if got_ref != ref or not is_new:
                raise AssertionError(f'document handle mismatch: {ref}')
        views = {}
        first_preview = {}
        for x in prior:
            if x['kind'] != 'tool_internal':
                continue
            audit = x['audit']
            raw = audit['raw_result']
            results = audit.get('model_result', {}).get('results', [])
            if audit['tool'] == 'search':
                for model_hit in results:
                    first_preview.setdefault(model_hit['doc_ref'], model_hit['preview_ref'])
            for view in (raw if isinstance(raw, list) else [raw]):
                if isinstance(view, dict) and 'window_ref' in view:
                    views[view['window_ref']] = view
        for w in snap['windows']:
            ref, source = w['window_ref'], w['source_window_ref']
            view = views.get(source)
            if view is None:
                raise AssertionError(f'missing source window: {ref}')
            key = (str(view['docid']), view['document_sha256'])
            start, end = view['offset'], view['end_char']
            if builder.documents[key]['text'][start:end] != view['text']:
                raise AssertionError(f'window slice mismatch: {ref}')
            builder.windows[source] = Window(key[0], key[1], start, end)
            got_ref, is_new = tools.handles.window(source)
            if got_ref != ref or not is_new:
                raise AssertionError(f'window handle mismatch: {ref}')
        if tools.handles.snapshot() != snap:
            raise AssertionError('restored registry differs from frozen prefix')
        if isinstance(tools, OrthogonalSearchFindTools):
            if set(first_preview) != {x['doc_ref'] for x in snap['documents']}:
                raise AssertionError('no discovery preview for some prefix documents')
            tools.discovery_previews.update(first_preview)
        return {'documents': len(snap['documents']), 'windows': len(snap['windows']),
                'first_preview_refs': first_preview}
    finally:
        db.close()


def emit(kind, **fields):
    event = {'time': datetime.now(timezone.utc).isoformat(), 'kind': kind, **fields}
    with (HERE / 'events.jsonl').open('a', encoding='utf-8') as f:
        f.write(json.dumps(event, ensure_ascii=False) + '\n')
        f.flush()


def freeze():
    if (HERE / 'freeze.json').exists():
        raise FileExistsError('freeze.json already exists; do not overwrite a frozen batch')
    paths = [
        'llm_chat/agent.py', 'llm_chat/search_find_agent.py',
        'llm_chat/search_find_v3b_agent.py', 'llm_chat/raw_windows.py',
        'llm_chat/window_locator.py', 'llm_chat/window_units.py',
        'BCPlus/scripts/search_bcplus.py',
        'experiments/search_find_v3b/orthogonal_search/run_partial.py',
    ]
    config = Config.load()
    doc = {
        'frozen_at': datetime.now(timezone.utc).isoformat(),
        'design': 'P0 v3a vs P1 orthogonal Search; paired checkpoint partial rollouts',
        'cohorts': COHORTS, 'horizon_api_decisions': HORIZON,
        'arm_order': ['P0', 'P1'], 'replicates': 1,
        'tool_schema_sha256': hashlib.sha256(json.dumps(SEARCH_FIND_TOOLS, sort_keys=True).encode()).hexdigest(),
        'model': config.model, 'base_url_host': urlsplit(config.base_url).hostname,
        'request_options': config.request_options(),
        'source_sha256': {p: file_sha(ROOT / p) for p in paths},
        'run_events_sha256': {q: file_sha(p / 'events.jsonl') for q, p in RUNS.items()},
        'checkpoint_request_sha256': {
            f'{q}:{s}': hashlib.sha256(json.dumps(checkpoint(q, s)[0], sort_keys=True).encode()).hexdigest()
            for cells in COHORTS.values() for q, s in cells},
        'failure_policy': 'all cells attempted in order; every failure recorded; no selective retry',
        'continuation': 'natural stop only; no forced final answer',
    }
    (HERE / 'freeze.json').write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n')
    return doc


def gate(frozen=None, *, restore=True):
    frozen = frozen or json.loads((HERE / 'freeze.json').read_text())
    checks = []
    def check(label, ok):
        checks.append((label, bool(ok)))
    check('source hashes match freeze', all(file_sha(ROOT / p) == sha for p, sha in frozen['source_sha256'].items()))
    check('original event hashes match freeze', all(file_sha(RUNS[q] / 'events.jsonl') == sha
                                                    for q, sha in frozen['run_events_sha256'].items()))
    for qid, run_dir in RUNS.items():
        manifest = json.loads((run_dir / 'manifest.json').read_text())
        check(f'{qid} original v3a source matches run manifest',
              all(file_sha(ROOT / p) == sha for p, sha in manifest['source_sha256'].items()))
    check('model matches freeze', Config.load().model == frozen['model'])
    check('schema exposes search/find/open', DECLARED == {'search', 'find', 'open'})
    check('fixed four-decision horizon', HORIZON == frozen['horizon_api_decisions'] == 4)
    check('13 unique checkpoint cells', len({cell for cells in COHORTS.values() for cell in cells}) == 13)
    check('B disjoint from A', not set(COHORTS['broad_relocation']) & set(COHORTS['local_verification']))
    for cells in COHORTS.values():
        for q, seq in cells:
            request, prior, events = checkpoint(q, seq)
            check(f'{q}:{seq} exact request hash', hashlib.sha256(json.dumps(request, sort_keys=True).encode()).hexdigest()
                  == frozen['checkpoint_request_sha256'][f'{q}:{seq}'])
            check(f'{q}:{seq} last message is tool', request['messages'][-1]['role'] == 'tool')
            check(f'{q}:{seq} auto/no sampling override', request['tool_choice'] == 'auto'
                  and 'temperature' not in request and 'max_tokens' not in request)
            check(f'{q}:{seq} frozen v3a schema', request['tools'] == SEARCH_FIND_TOOLS)
            check(f'{q}:{seq} no harness gold injection', all('docid' not in str(m) for m in request['messages']
                                                               if m['role'] in ('system', 'user')))
            if (q, seq) in COHORTS['local_verification']:
                next_resp = next(x for x in events if x['seq'] > seq and x['kind'] == 'api_response')
                calls = next_resp['response']['choices'][0]['message'].get('tool_calls') or []
                names = [c['function']['name'] for c in calls]
                check(f'{q}:{seq} historical next Search/Answer', not names or names[0] == 'search')
            if restore:
                for cls in (SearchFindTools, OrthogonalSearchFindTools):
                    tools = cls()
                    try:
                        state = restore_prefix(tools, prior)
                        check(f'{q}:{seq} {cls.__name__} restored', state['documents'] > 0 and state['windows'] > 0)
                    finally:
                        tools.close()
    lines = [f'{"PASS" if ok else "FAIL"} {label}' for label, ok in checks]
    lines.append(f'{sum(ok for _, ok in checks)}/{len(checks)} PASS')
    (HERE / 'gate.txt').write_text('\n'.join(lines) + '\n')
    if not all(ok for _, ok in checks):
        raise AssertionError('offline gate failed; see gate.txt')
    return lines[-1]


def run_cell(client, shared_searcher, qid, seq, cohort, arm):
    request, prior, _ = checkpoint(qid, seq)
    tools = SearchFindTools() if arm == 'P0' else OrthogonalSearchFindTools()
    cell = f'{qid}:{seq}:{arm}'
    status = 'horizon'
    prompt_tokens = total_tokens = 0
    began = time.monotonic()
    try:
        restoration = restore_prefix(tools, prior)
        tools.searcher = shared_searcher
        emit('cell_start', cell=cell, cohort=cohort, qid=qid, checkpoint_seq=seq,
             arm=arm, restoration=restoration)
        messages = json.loads(json.dumps(request['messages']))
        for decision in range(1, HORIZON + 1):
            params = {**request, 'messages': messages}
            emit('api_request', cell=cell, decision=decision, request=params)
            start = time.monotonic()
            try:
                response = client.chat.completions.create(**params)
            except BaseException as exc:
                emit('api_error', cell=cell, decision=decision, error_type=type(exc).__name__,
                     error=str(exc)[:1000], elapsed_seconds=time.monotonic()-start)
                status = 'api_error'
                break
            raw = response.model_dump(mode='json')
            emit('api_response', cell=cell, decision=decision, response=raw,
                 elapsed_seconds=time.monotonic()-start)
            usage = raw.get('usage') or {}
            prompt_tokens += usage.get('prompt_tokens') or 0
            total_tokens += usage.get('total_tokens') or 0
            if not response.choices:
                status = 'empty_choices'; break
            choice = response.choices[0]
            message = choice.message
            calls = list(message.tool_calls or [])
            if not calls:
                status = 'natural_stop' if choice.finish_reason == 'stop' else 'abnormal_finish'
                emit('answer', cell=cell, decision=decision, finish_reason=choice.finish_reason,
                     text=message.content or message.refusal or '')
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
            messages.append(message.model_dump(exclude_none=True))
            # Validate the complete returned batch before executing any tool.
            invalid_names = [c.function.name for c in calls if c.function.name not in DECLARED]
            if invalid_names:
                status = 'undeclared_tool_call'
                emit('undeclared_tool_call', cell=cell, decision=decision, names=invalid_names)
                for c in calls:
                    messages.append({'role': 'tool', 'tool_call_id': c.id,
                                     'content': json.dumps({'error': 'undeclared_tool_call'})})
                break
            for call_index, call in enumerate(calls, start=1):
                name = call.function.name
                try:
                    args = json.loads(call.function.arguments)
                    if not isinstance(args, dict):
                        raise ValueError('tool arguments must be object')
                except (ValueError, TypeError) as exc:
                    emit('malformed_tool_call', cell=cell, decision=decision,
                         call_index=call_index, name=name, error=str(exc))
                    result = {'error': 'malformed_tool_call'}
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
                        status = 'tool_error'
                        raise
                    emit('tool_result', cell=cell, decision=decision, call_index=call_index,
                         name=name, result=result, elapsed_seconds=time.monotonic()-start)
                    emit('tool_internal', cell=cell, decision=decision, call_index=call_index,
                         name=name, audit=tools.audit_record())
                messages.append({'role': 'tool', 'tool_call_id': call.id,
                                 'content': json.dumps(result, ensure_ascii=False)})
    except BaseException as exc:
        if status != 'tool_error':
            status = 'harness_error'
            emit('harness_error', cell=cell, error_type=type(exc).__name__, error=str(exc)[:1000])
    finally:
        emit('cell_end', cell=cell, cohort=cohort, status=status,
             prompt_tokens=prompt_tokens, total_tokens=total_tokens,
             elapsed_seconds=time.monotonic()-began)
        tools.close()
    return status


def run():
    frozen = json.loads((HERE / 'freeze.json').read_text())
    gate(frozen)
    if (HERE / 'events.jsonl').exists():
        raise FileExistsError('events.jsonl exists; frozen batch cannot be restarted/best-of')
    config = Config.load()
    if config.model != frozen['model'] or urlsplit(config.base_url).hostname != frozen['base_url_host']:
        raise AssertionError('provider configuration differs from freeze')
    from BCPlus.scripts.search_bcplus import BCPlusSearcher
    searcher = None
    client = OpenAI(api_key=config.api_key, base_url=config.base_url,
                    timeout=config.timeout, max_retries=2)
    try:
        # Instantiate once; all cells still use the same unchanged retriever.
        searcher = BCPlusSearcher()
        for cohort, cells in COHORTS.items():
            for qid, seq in cells:
                for arm in ('P0', 'P1'):
                    status = run_cell(client, searcher, qid, seq, cohort, arm)
                    print(f'{qid}:{seq}:{arm} {status}', flush=True)
    finally:
        client.close()
        if searcher is not None:
            searcher.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['freeze', 'gate', 'run'])
    args = parser.parse_args()
    if args.action == 'freeze':
        freeze()
    elif args.action == 'gate':
        print(gate())
    else:
        run()
