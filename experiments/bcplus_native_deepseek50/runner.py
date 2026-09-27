"""One frozen, gold-blind DeepSeek Flash run over 50 independent questions."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
from types import SimpleNamespace

import httpx
from openai import OpenAI

from .native_agent import AgentSession, BCPlusTools
from .native_client import Config

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RUNS = HERE / 'runs'


def read_json(name):
    return json.loads((HERE / name).read_text(encoding='utf-8'))


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def sha(path):
    return sha256(path.read_bytes()).hexdigest()


class Recorder:
    def __init__(self, directory):
        self.directory = directory
        self.events = []

    def emit(self, kind, **data):
        event = {'seq': len(self.events) + 1, 'time_utc': datetime.now(timezone.utc).isoformat(),
                 'kind': kind, **data}
        with (self.directory / 'events.jsonl').open('a', encoding='utf-8') as out:
            out.write(json.dumps(event, ensure_ascii=False) + '\n')
            out.flush()
        self.events.append(event)

    def render(self):
        parts = ['# Native BC+ trajectory', '',
                 'API requests are SDK arguments; responses are parsed SDK results. No credentials or HTTP headers are recorded.',
                 'Only returned model content is shown; no hidden reasoning is inferred.', '']
        for event in self.events:
            parts.extend([f"## {event['seq']}. {event['kind']}", '', '```json',
                          json.dumps(event, ensure_ascii=False, indent=2), '```', ''])
        (self.directory / 'trajectory.md').write_text('\n'.join(parts), encoding='utf-8')


class RecordedClient:
    def __init__(self, client, recorder):
        self.client = client
        self.recorder = recorder
        self.chat = SimpleNamespace(completions=self)

    def create(self, **kwargs):
        self.recorder.emit('api_request', request=json.loads(json.dumps(kwargs)))
        start = time.monotonic()
        try:
            response = self.client.chat.completions.create(**kwargs)
        except BaseException as exc:
            self.recorder.emit('api_error', error_type=type(exc).__name__,
                               elapsed_seconds=time.monotonic() - start)
            raise
        self.recorder.emit('api_response', response=response.model_dump(mode='json'),
                           elapsed_seconds=time.monotonic() - start)
        return response

    def close(self):
        self.client.close()


class SerializedRetrieval:
    """Keep one search model and its SQLite connections on one worker thread."""
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix='bcplus-retrieval')
        self.future = self.executor.submit(BCPlusTools)

    def execute(self, name, arguments):
        return self.executor.submit(self.future.result().execute, name, arguments).result()

    def close(self):
        inner = self.future.result()
        self.executor.submit(inner.close).result()
        if inner.searcher is not None:
            self.executor.submit(inner.searcher.close).result()
        self.executor.shutdown()


class RecordedTools:
    def __init__(self, inner, recorder):
        self.inner, self.recorder = inner, recorder

    def execute(self, name, arguments):
        self.recorder.emit('tool_start', name=name, arguments=arguments)
        start = time.monotonic()
        try:
            result = self.inner.execute(name, arguments)
        except BaseException as exc:
            self.recorder.emit('tool_error', name=name, error_type=type(exc).__name__,
                               elapsed_seconds=time.monotonic() - start)
            raise
        docs = result if isinstance(result, list) else [result]
        views = [{'docid': d.get('docid'), 'offset': d.get('offset', 0),
                  'chars': len(d['text']), 'text_sha256': sha256(d['text'].encode()).hexdigest()}
                 for d in docs if isinstance(d, dict) and isinstance(d.get('text'), str)]
        self.recorder.emit('tool_result', name=name, result=result, views=views,
                           elapsed_seconds=time.monotonic() - start)
        return result

    def close(self):
        pass  # Shared read-only retrieval worker is closed after all questions.


def summarize(events, status, elapsed):
    kinds = [e['kind'] for e in events]
    responses = [e['response'] for e in events if e['kind'] == 'api_response']
    usage = [r.get('usage') for r in responses]
    complete_usage = [u for u in usage if isinstance(u, dict)
                      and all(isinstance(u.get(k), int) for k in ('prompt_tokens', 'completion_tokens', 'total_tokens'))]
    cache_records = []
    bad_cache = 0
    for u in complete_usage:
        hit = u.get('prompt_cache_hit_tokens')
        miss = u.get('prompt_cache_miss_tokens')
        if isinstance(hit, int) and isinstance(miss, int) and hit + miss == u['prompt_tokens']:
            cache_records.append((hit, u['prompt_tokens']))
        else:
            bad_cache += 1
    calls = [e for e in events if e['kind'] == 'tool_start']
    search_queries = [e['arguments'].get('query') for e in calls if e['name'] == 'search']
    doc_reads = [(e['arguments'].get('docid'), e['arguments'].get('offset', 0))
                 for e in calls if e['name'] == 'get_document']
    docids = {str(d['docid']) for e in events if e['kind'] == 'tool_result'
              for d in (e['result'] if isinstance(e['result'], list) else [e['result']])
              if isinstance(d, dict) and d.get('docid') is not None}
    return {
        'status': status, 'elapsed_seconds': elapsed,
        'api_requests': kinds.count('api_request'), 'api_responses': len(responses),
        'api_errors': kinds.count('api_error'),
        'model_response_count': len(responses),
        'tool_round_count': sum(bool((r.get('choices') or [{}])[0].get('message', {}).get('tool_calls')) for r in responses),
        'search_calls': sum(e['name'] == 'search' for e in calls),
        'get_document_calls': sum(e['name'] == 'get_document' for e in calls),
        'total_tool_calls': len(calls), 'unique_docids': len(docids),
        'unique_search_queries': len(set(search_queries)),
        'exact_duplicate_queries': len(search_queries) - len(set(search_queries)),
        'repeated_document_reads': len(doc_reads) - len(set(doc_reads)),
        'prompt_tokens': sum(u['prompt_tokens'] for u in complete_usage),
        'completion_tokens': sum(u['completion_tokens'] for u in complete_usage),
        'total_tokens': sum(u['total_tokens'] for u in complete_usage),
        'usage_missing_or_incomplete_records': len(usage) - len(complete_usage),
        'cache_usage_valid_records': len(cache_records),
        'cache_usage_missing_or_inconsistent_records': len(usage) - len(complete_usage) + bad_cache,
        'cache_hit_tokens': sum(h for h, _ in cache_records),
        'cache_input_tokens': sum(n for _, n in cache_records),
        'api_latency_seconds': [e['elapsed_seconds'] for e in events if e['kind'] in {'api_response', 'api_error'}],
    }


def run_one(item, batch_id, config, retrieval, run_config):
    qid = item['qid']
    directory = RUNS / batch_id / f'qid_{qid}'
    directory.mkdir(parents=True, exist_ok=False)
    write_json(directory / 'input.json', item)
    shutil.copy2(ROOT / 'BCPlus/indexes/bcplus-qwen3-8b/metadata.json',
                 directory / 'retrieval_metadata.json')
    write_json(directory / 'manifest.json', {
        'batch_id': batch_id, 'qid': qid, 'model': config.model,
        'base_url': config.base_url, 'system_prompt': config.system_prompt,
        'request_options': config.request_options(), 'timeout_seconds': config.timeout,
        'sdk_max_retries': 0, 'max_tool_rounds': 200, 'max_tool_calls_per_round': 8,
        'run_config_sha256': sha(HERE / 'RUN_CONFIG.json'),
        'source_sha256': run_config['source_sha256'],
        'selection_freeze_sha256': sha(HERE / 'SELECTION_FREEZE.json'),
        'gold_supplied': False})
    recorder = Recorder(directory)
    http = httpx.Client(limits=httpx.Limits(max_connections=2, max_keepalive_connections=1))
    client = RecordedClient(OpenAI(api_key=config.api_key, base_url=config.base_url,
                                   timeout=config.timeout, max_retries=0, http_client=http), recorder)
    session = AgentSession(config, client=client, tools=RecordedTools(retrieval, recorder), max_rounds=200)
    start = time.monotonic()
    status = 'RUN_FAILED'
    answer = ''
    try:
        answer = session.ask(item['question'])
        requests = [e for e in recorder.events if e['kind'] == 'api_request']
        status = ('emergency_cap_forced_answer' if requests[-1]['request']['tool_choice'] == 'none'
                  else 'natural_answer')
    except BaseException as exc:
        recorder.emit('run_error', error_type=type(exc).__name__)
    finally:
        (directory / 'answer.md').write_text(answer + ('\n' if answer else ''), encoding='utf-8')
        recorder.emit('run_end', status=status, elapsed_seconds=time.monotonic() - start)
        write_json(directory / 'summary.json', summarize(recorder.events, status, time.monotonic() - start))
        recorder.render()
        session.close()
    return qid, status


def main():
    selection = read_json('SELECTION_FREEZE.json')
    online = read_json('ONLINE_INPUTS.json')
    run_config = read_json('RUN_CONFIG.json')
    model = read_json('MODEL_FREEZE.json')
    if sha(HERE / 'RESTART_FREEZE.json') != run_config['restart_freeze_sha256']:
        raise ValueError('Restart freeze changed')
    if sha(HERE / 'ONLINE_INPUTS.json') != selection['selected_questions_sha256']:
        raise ValueError('Online inputs differ from selection freeze')
    if [x['qid'] for x in online] != selection['selected_qids'] or len(online) != 50:
        raise ValueError('Selected qids differ from freeze')
    for name, expected in run_config['source_sha256'].items():
        path = ROOT / name if name.startswith('BCPlus/') else HERE / name
        if sha(path) != expected:
            raise ValueError(f'Source changed after freeze: {name}')
    if model['model'] != 'deepseek-flash' or model['max_retries'] != 0:
        raise ValueError('Model freeze mismatch')
    if RUNS.exists() and any(RUNS.iterdir()):
        restart = read_json('RESTART_FREEZE.json')
        existing = [p for p in RUNS.iterdir() if p.is_dir()]
        if (len(existing) != 1 or existing[0].name != restart['aborted_batch_id']
                or not (existing[0] / 'ABORTED.json').exists()
                or (RUNS / 'BATCH_MANIFEST.json').exists()
                or (RUNS / 'BATCH_END.json').exists()
                or run_config['workers'] != 50):
            raise ValueError('Only the user-directed 50-worker restart is permitted')
    config = Config.load()
    if (config.model != model['model'] or config.base_url != model['base_url']
            or config.timeout != model['timeout_seconds']
            or config.request_options() != {'temperature': 0, 'extra_body': model['thinking_extra_body']}):
        raise ValueError('Client configuration mismatch')
    batch_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    RUNS.mkdir(exist_ok=True)
    write_json(RUNS / 'BATCH_MANIFEST.json', {
        'batch_id': batch_id, 'selection_sha256': sha(HERE / 'SELECTION_FREEZE.json'),
        'run_config_sha256': sha(HERE / 'RUN_CONFIG.json'),
        'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'started_at_utc': datetime.now(timezone.utc).isoformat()})
    retrieval = SerializedRetrieval()
    results = []
    try:
        with ThreadPoolExecutor(max_workers=run_config['workers']) as executor:
            futures = {executor.submit(run_one, item, batch_id, config, retrieval, run_config): item['qid']
                       for item in online}
            for future in as_completed(futures):
                qid = futures[future]
                try:
                    result = future.result()
                except BaseException as exc:
                    result = (qid, 'RUN_FAILED')
                    print(f'qid={qid} worker_error={type(exc).__name__}', flush=True)
                results.append(result)
                print(f'completed {len(results)}/50 qid={qid} status={result[1]}', flush=True)
    finally:
        retrieval.close()
    write_json(RUNS / 'BATCH_END.json', {'batch_id': batch_id, 'completed_at_utc': datetime.now(timezone.utc).isoformat(),
                                         'results': results})
    if len(results) != 50:
        raise ValueError('Batch ended without 50 results')


if __name__ == '__main__':
    main()
