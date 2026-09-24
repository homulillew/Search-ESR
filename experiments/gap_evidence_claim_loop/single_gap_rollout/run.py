"""Paired four-decision Orthogonal Search single-Gap continuations."""
import hashlib
import json
import sqlite3
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

from dotenv import dotenv_values
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from llm_chat.raw_windows import Window
from llm_chat.search_find_agent import SEARCH_FIND_PROMPT, SEARCH_FIND_TOOLS
from llm_chat.search_find_v3b_agent import OrthogonalSearchFindTools
from experiments.model_backend_deepseek.cache_usage import extract
from experiments.model_backend_deepseek.protocol import validate_batch
from experiments.search_find_v3b.orthogonal_search.run_partial import checkpoint, restore_prefix, RUNS

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
CONFIG = json.loads((ROOT / 'experiments/model_backend_deepseek/provider.json').read_text())
BANK = json.loads((HERE / 'BANK.json').read_text())
PROMPTS = {name: (STUDY / f'prompts/{name}.md').read_text() for name in
           ('actor', 'gap_claim_fact_reader', 'finding_verifier', 'gap_reviewer')}
FREEZE = HERE / 'freeze.json'
EVENTS = HERE / 'events.jsonl'
HORIZON = 4


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def source_paths():
    own = ['PROTOCOL.md', 'REVIEW_RUBRIC.md', 'PREFIX_REVIEW.md',
           'prepare_bank.py', 'BANK.json', 'run.py']
    paths = [HERE / name for name in own]
    paths += [STUDY / f'prompts/{name}.md' for name in PROMPTS]
    paths += [ROOT / name for name in (
        'llm_chat/search_find_agent.py', 'llm_chat/search_find_v3b_agent.py',
        'llm_chat/raw_windows.py', 'llm_chat/window_locator.py',
        'BCPlus/scripts/search_bcplus.py',
        'experiments/search_find_v3b/orthogonal_search/run_partial.py',
        'experiments/model_backend_deepseek/provider.json',
        'experiments/model_backend_deepseek/protocol.py')]
    paths += [RUNS[q] / 'events.jsonl' for q in ('546', '1094')]
    return paths


def source_hashes():
    return {str(p.relative_to(ROOT)): sha(p) for p in source_paths()}


def arm_order(index):
    return ('R0', 'R1') if index % 2 == 0 else ('R1', 'R0')


def legacy_prefix(case):
    w = case['relevant_observed_window']
    return [{'role': 'system', 'content': SEARCH_FIND_PROMPT},
            {'role': 'user', 'content': case['raw_question']},
            {'role': 'user', 'content': 'Historical observed workspace at the frozen checkpoint:\n'
             + f"{w['doc_ref']} — {w['title']}\n{w['ref']}:\n{w['text']}"}]


def baseline_prefix(case):
    if case['source_kind'] == 'legacy':
        return legacy_prefix(case)
    request, _, _ = checkpoint(case['qid'], case['checkpoint_seq'])
    return request['messages']


def checkpoint_hashes(case):
    if case['source_kind'] == 'legacy':
        return {'prefix': digest(legacy_prefix(case)),
                'workspace': digest(case['relevant_observed_window'])}
    request, prior, _ = checkpoint(case['qid'], case['checkpoint_seq'])
    return {'prefix': digest(request['messages']), 'request': digest(request),
            'prior': digest(prior),
            'workspace': digest([e['audit']['handles'] for e in prior if e['kind'] == 'tool_internal'][-1])}


def freeze():
    if FREEZE.exists():
        raise FileExistsError(FREEZE)
    assert len(BANK) == len({c['qid'] for c in BANK}) == 6
    assert all(c['prefix_review']['semantic_gap'] and c['prefix_review']['gap_open']
               and c['prefix_review']['seed_claims_supported'] for c in BANK)
    doc = {'frozen_at_utc': datetime.now(timezone.utc).isoformat(),
           'git_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
           'provider': {'host': urlsplit(CONFIG['base_url']).hostname,
                        'model': CONFIG['model'], 'timeout_seconds': CONFIG['timeout_seconds'],
                        'max_retries': 0},
           'source_hashes': source_hashes(), 'tool_schema_sha256': digest(SEARCH_FIND_TOOLS),
           'prompt_hashes': {n: digest(p) for n, p in PROMPTS.items()},
           'case_order': [c['case_id'] for c in BANK],
           'arm_order': {c['case_id']: arm_order(i) for i, c in enumerate(BANK)},
           'checkpoint_hashes': {c['case_id']: checkpoint_hashes(c) for c in BANK},
           'question_hashes': {c['case_id']: digest(c['raw_question']) for c in BANK},
           'gap_hashes': {c['case_id']: digest(c['active_gap']) for c in BANK},
           'seed_claim_hashes': {c['case_id']: digest(c['initial_claims']) for c in BANK},
           'visible_window_hashes': {c['case_id']: digest(c['relevant_observed_window']) for c in BANK},
           'sample_count': 12, 'horizon_actor_decisions': HORIZON,
           'rubric_sha256': sha(HERE / 'REVIEW_RUBRIC.md'),
           'gate': {'net_paired_resolution_or_useful_wins_min': 3,
                    'claim_precision_min': .95, 'premature_close_max': .10},
           'failure_policy': 'One call per step, max_retries=0, all errors retained, no replacement or best-of; cell stops on failure.'}
    FREEZE.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n')


def gate():
    f = json.loads(FREEZE.read_text())
    checks = {'sources': f['source_hashes'] == source_hashes(),
              'provider': f['provider'] == {'host': urlsplit(CONFIG['base_url']).hostname,
                  'model': CONFIG['model'], 'timeout_seconds': CONFIG['timeout_seconds'], 'max_retries': CONFIG['max_retries']},
              'schema': f['tool_schema_sha256'] == digest(SEARCH_FIND_TOOLS),
              'prompts': f['prompt_hashes'] == {n: digest(p) for n, p in PROMPTS.items()},
              'bank': f['case_order'] == [c['case_id'] for c in BANK],
              'checkpoints': f['checkpoint_hashes'] == {c['case_id']: checkpoint_hashes(c) for c in BANK},
              'rubric': f['rubric_sha256'] == sha(HERE / 'REVIEW_RUBRIC.md'),
              'horizon': f['horizon_actor_decisions'] == HORIZON}
    (HERE / 'gate.txt').write_text(''.join(f'{"PASS" if ok else "FAIL"} {name}\n' for name, ok in checks.items()))
    if not all(checks.values()):
        raise AssertionError(checks)


def emit(kind, **fields):
    with EVENTS.open('a') as out:
        out.write(json.dumps({'time': datetime.now(timezone.utc).isoformat(),
                              'kind': kind, **fields}, ensure_ascii=False) + '\n')
        out.flush()


def restore_legacy(tools, case):
    w = case['relevant_observed_window']
    docid = case['source_checkpoint']['historical_doc_ref']
    db_path = ROOT / 'BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite'
    with sqlite3.connect(f'{db_path.as_uri()}?mode=ro', uri=True) as db:
        text, url = db.execute('select text,url from documents where docid=?', (docid,)).fetchone()
    offset = text.find(w['text'])
    if offset < 0 or text.count(w['text']) != 1:
        raise AssertionError('historical W is not a unique exact corpus slice')
    key = tools._windows().register(docid, text, url)
    assert tools.handles.document(key) == ('D1', True)
    source_ref = case['source_checkpoint']['historical_ref']
    tools._windows().windows[source_ref] = Window(docid, key[1], offset, offset + len(w['text']))
    assert tools.handles.window(source_ref) == ('W1', True)
    tools.discovery_previews['D1'] = 'W1'
    return {'documents': 1, 'windows': 1, 'exact_slice': True}


def restore(tools, case):
    if case['source_kind'] == 'legacy':
        return restore_legacy(tools, case)
    _, prior, _ = checkpoint(case['qid'], case['checkpoint_seq'])
    return restore_prefix(tools, prior)


def workspace_view(tools, case, latest):
    snap = tools.handles.snapshot()
    docs = []
    for d in snap['documents']:
        key = (d['docid'], d['document_sha256'])
        doc = tools._windows().documents[key]
        docs.append({'doc_ref': d['doc_ref'], 'title': doc['title']})
    relevant = case['relevant_observed_window']
    return {'known_documents': docs,
            'relevant_observed_window': relevant,
            'observed_window_refs': [w['window_ref'] for w in snap['windows']],
            'latest_tool_result': latest}


def actor_request(case, arm, history, claims, tools, latest):
    if arm == 'R0':
        messages = history
    else:
        view = {'ORIGINAL QUESTION': case['raw_question'],
                'COMMITTED FACTS': claims,
                'ACTIVE GAP': case['active_gap'],
                'WORKSPACE': workspace_view(tools, case, latest)}
        if case['working_hypothesis'] is not None:
            view['WORKING HYPOTHESIS'] = case['working_hypothesis']
        messages = [{'role': 'system', 'content': SEARCH_FIND_PROMPT + '\n\n' + PROMPTS['actor']},
                    {'role': 'user', 'content': json.dumps(view, ensure_ascii=False)}]
    return {'model': CONFIG['model'], 'messages': messages,
            'tools': SEARCH_FIND_TOOLS, 'tool_choice': 'auto', 'stream': False}


def model_json(client, cell, decision, kind, prompt, payload, keys):
    req = {'model': CONFIG['model'], 'messages': [
        {'role': 'system', 'content': prompt},
        {'role': 'user', 'content': json.dumps(payload, ensure_ascii=False)}], 'stream': False}
    emit(kind + '_request', cell=cell, decision=decision, request=req, request_hash=digest(req))
    began = time.monotonic()
    try:
        raw = client.chat.completions.create(**req).model_dump(mode='json')
        emit(kind + '_response', cell=cell, decision=decision, response=raw,
             cache_usage=extract(raw), elapsed_seconds=time.monotonic() - began)
        if raw['choices'][0]['finish_reason'] != 'stop':
            raise ValueError('abnormal_finish')
        parsed = json.loads(raw['choices'][0]['message']['content'])
        if not isinstance(parsed, dict) or set(parsed) != set(keys):
            raise ValueError('schema_keys')
        return parsed
    except Exception as exc:
        emit(kind + '_error', cell=cell, decision=decision,
             error_type=type(exc).__name__, http_status=getattr(exc, 'status_code', None),
             error=str(exc)[:500], elapsed_seconds=time.monotonic() - began)
        raise


def observations(result, name):
    if name == 'search':
        return [{'ref': r['preview_ref'], 'doc_ref': r['doc_ref'], 'text': r['preview'],
                 'title': r['title']} for r in result.get('results', []) if 'preview_ref' in r]
    if name == 'find':
        return [{'ref': m['window_ref'], 'doc_ref': result['doc_ref'], 'text': m['text']}
                for m in result.get('matches', [])]
    if name == 'open' and result.get('text'):
        return [{'ref': result['window_ref'], 'doc_ref': result['doc_ref'], 'text': result['text']}]
    return []


def process_observation(client, case, cell, decision, obs, claims):
    emit('observation', cell=cell, decision=decision, observation=obs)
    found = model_json(client, cell, decision, 'reader', PROMPTS['gap_claim_fact_reader'],
                       {'raw_question': case['raw_question'], 'active_gap': case['active_gap'],
                        'relevant_committed_claims': claims,
                        'latest_observation': {'ref': obs['ref'], 'text': obs['text']}},
                       ('findings',))
    if not isinstance(found['findings'], list) or len(found['findings']) > 3:
        raise ValueError('finding_count')
    new_claims = []
    for finding in found['findings']:
        if not isinstance(finding, dict) or set(finding) != {'statement', 'evidence_refs'} or \
           not isinstance(finding['statement'], str) or not finding['statement'].strip() or \
           finding['evidence_refs'] != [obs['ref']]:
            raise ValueError('finding_schema')
        verdict = model_json(client, cell, decision, 'verifier', PROMPTS['finding_verifier'],
                             {'active_gap': case['active_gap'], 'finding': finding,
                              'exact_observation': {'ref': obs['ref'], 'text': obs['text']},
                              'relevant_committed_claims': claims}, ('verdict', 'reason'))
        if verdict['verdict'] not in ('supported', 'insufficient') or not verdict['reason']:
            raise ValueError('verifier_schema')
        emit('verdict', cell=cell, decision=decision, observation_ref=obs['ref'],
             finding=finding, verdict=verdict)
        if verdict['verdict'] == 'supported':
            claim = {'claim_id': f'C{len(claims)+1}', 'statement': finding['statement'],
                     'evidence_refs': finding['evidence_refs'], 'version': 1}
            claims.append(claim)
            new_claims.append(claim)
            emit('claim_commit', cell=cell, decision=decision, claim=claim)
    review = model_json(client, cell, decision, 'gap_review', PROMPTS['gap_reviewer'],
                        {'raw_question': case['raw_question'], 'active_gap': case['active_gap'],
                         'relevant_committed_claims': claims, 'newly_committed_claims': new_claims},
                        ('status', 'reason'))
    if review['status'] not in ('resolved', 'open') or not review['reason']:
        raise ValueError('gap_review_schema')
    emit('gap_status', cell=cell, decision=decision, observation_ref=obs['ref'], review=review)
    return review['status'] == 'resolved'


def run_cell(client, searcher, case, arm):
    cell = case['case_id'] + ':' + arm
    tools = OrthogonalSearchFindTools()
    claims = json.loads(json.dumps(case['initial_claims']))
    history = json.loads(json.dumps(baseline_prefix(case))) if arm == 'R0' else []
    latest = None
    status = 'horizon'
    try:
        restored = restore(tools, case)
        tools.searcher = searcher
        emit('cell_start', cell=cell, restoration=restored,
             seed_claims=claims, gap=case['active_gap'])
        for decision in range(1, HORIZON + 1):
            req = actor_request(case, arm, history, claims, tools, latest)
            emit('actor_request', cell=cell, decision=decision, request=req, request_hash=digest(req))
            began = time.monotonic()
            try:
                raw = client.chat.completions.create(**req).model_dump(mode='json')
            except Exception as exc:
                emit('actor_error', cell=cell, decision=decision, error_type=type(exc).__name__,
                     http_status=getattr(exc, 'status_code', None), error=str(exc)[:500])
                status = 'actor_api_error'
                break
            choice = raw['choices'][0]
            parsed, error = validate_batch(choice, SEARCH_FIND_TOOLS,
                         allow_stop_with_calls=CONFIG['allow_tool_calls_with_stop'])
            emit('actor_response', cell=cell, decision=decision, response=raw,
                 cache_usage=extract(raw), validation=error or 'valid',
                 parsed_calls=parsed, elapsed_seconds=time.monotonic() - began)
            if error:
                status = 'invalid_tool_batch'
                break
            if not parsed:
                status = 'natural_stop'
                break
            if arm == 'R0':
                msg = choice['message']
                history.append({k: v for k, v in msg.items() if v is not None and
                                k in ('role', 'content', 'tool_calls', 'reasoning_content')})
            resolved = False
            for call in parsed:
                emit('tool_start', cell=cell, decision=decision,
                     name=call['name'], arguments=call['arguments'])
                result = tools.execute(call['name'], call['arguments'])
                audit = tools.audit_record()
                emit('tool_result', cell=cell, decision=decision, name=call['name'],
                     arguments=call['arguments'], result=result, audit=audit)
                if arm == 'R0':
                    history.append({'role': 'tool', 'tool_call_id': call['id'],
                                    'content': json.dumps(result, ensure_ascii=False)})
                latest = result
                for obs in observations(result, call['name']):
                    if process_observation(client, case, cell, decision, obs, claims):
                        resolved = True
            if resolved:
                status = 'gap_reviewer_resolved'
                break
    except Exception as exc:
        status = 'cell_error'
        emit('cell_error', cell=cell, error_type=type(exc).__name__,
             error=str(exc)[:500], http_status=getattr(exc, 'status_code', None))
    finally:
        emit('cell_end', cell=cell, status=status, final_claims=claims,
             workspace=tools.handles.snapshot())
        tools.close()
    return status


def run():
    gate()
    if EVENTS.exists():
        raise FileExistsError(EVENTS)
    key = dotenv_values(ROOT / CONFIG['credential_file']).get(CONFIG['credential_field'])
    if not key:
        raise ValueError('DeepSeek credential unavailable')
    from BCPlus.scripts.search_bcplus import BCPlusSearcher
    with OpenAI(api_key=key, base_url=CONFIG['base_url'],
                timeout=CONFIG['timeout_seconds'], max_retries=0) as client:
        searcher = BCPlusSearcher()
        try:
            for i, case in enumerate(BANK):
                for arm in arm_order(i):
                    print(case['qid'], arm, run_cell(client, searcher, case, arm), flush=True)
        finally:
            searcher.close()


if __name__ == '__main__':
    action = sys.argv[1]
    if action == 'freeze': freeze()
    elif action == 'gate': gate(); print('PASS')
    elif action == 'run': run()
    else: raise SystemExit('freeze|gate|run')
