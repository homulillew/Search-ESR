"""Run an isolated BC+ question through the unchanged baseline with durable traces."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import sys
import time
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from llm_chat.agent import AgentSession, BCPlusTools
from llm_chat.client import Config
from openai import OpenAI


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


class Recorder:
    def __init__(self, directory):
        self.directory = directory
        self.events = []

    def emit(self, kind, **data):
        event = {'seq': len(self.events) + 1, 'time': datetime.now(timezone.utc).isoformat(),
                 'kind': kind, **data}
        with (self.directory / 'events.jsonl').open('a', encoding='utf-8') as f:
            f.write(json.dumps(event, ensure_ascii=False) + '\n')
            f.flush()
        self.events.append(event)
        print(f"[{event['seq']}] {kind} {data.get('name', '')}", flush=True)

    def render(self):
        parts = ['# 完整 rollout 轨迹', '', 'API 请求是 SDK 调用参数；响应是 SDK 解析结果。未记录密钥或 HTTP 头。',
                 '仅记录 API 实际返回的内容，不推断未返回的内部推理。', '']
        for event in self.events:
            parts.extend([f"## {event['seq']}. {event['kind']} · {event['time']}", '',
                          '```json', json.dumps(event, ensure_ascii=False, indent=2), '```', ''])
        (self.directory / 'trajectory.md').write_text('\n'.join(parts), encoding='utf-8')


class RecordedClient:
    def __init__(self, client, recorder):
        self.client, self.recorder = client, recorder
        self.chat = SimpleNamespace(completions=self)

    def create(self, **kwargs):
        # Snapshot before the agent mutates its pending message list.
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


class RecordedTools:
    def __init__(self, recorder, inner=None):
        self.inner, self.recorder = inner if inner is not None else BCPlusTools(), recorder

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
                  'chars': len(d['text']), 'text_sha256': hashlib.sha256(d['text'].encode()).hexdigest()}
                 for d in docs if 'text' in d]
        self.recorder.emit('tool_result', name=name, result=result, views=views,
                           elapsed_seconds=time.monotonic() - start)
        return result

    def close(self):
        self.inner.close()


def run_question(qid, max_tool_rounds=12, tools=None, batch_id=None):
    args = SimpleNamespace(qid=str(qid), max_tool_rounds=max_tool_rounds)
    if args.max_tool_rounds < 1 or not args.qid.isdigit():
        raise ValueError('qid must be numeric and max-tool-rounds must be positive')
    dataset = ROOT / 'BCPlus/data/bcplus/qa.jsonl'
    with dataset.open() as f:
        item = next((row for line in f if str((row := json.loads(line))['query_id']) == args.qid), None)
    if item is None:
        raise ValueError('qid not found')
    config = Config.load()
    run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    directory = ROOT / 'experiments/runs/v000_baseline' / f'qid_{args.qid}' / run_id
    directory.mkdir(parents=True, exist_ok=False)
    sources = directory / 'source'
    sources.mkdir()
    hashes = {}
    for relative in ['llm_chat/agent.py', 'llm_chat/client.py', 'BCPlus/scripts/search_bcplus.py', 'experiments/run_rollout.py', 'experiments/run_batch.py']:
        path = ROOT / relative
        hashes[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
        dest = sources / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dest)
    shutil.copy2(ROOT / 'BCPlus/indexes/bcplus-qwen3-8b/metadata.json', directory / 'retrieval_metadata.json')
    write_json(directory / 'input.json', {'qid': args.qid, 'question': item['query']})
    # Gold is deliberately not persisted in the online run or passed to the agent.
    write_json(directory / 'manifest.json', {
        'variant': 'v000_baseline', 'run_id': run_id, 'qid': args.qid, 'batch_id': batch_id,
        'execution': 'parallel_api_serial_shared_retrieval' if batch_id else 'single',
        'model': config.model, 'base_url': config.base_url, 'system_prompt': config.system_prompt,
        'request_options': config.request_options(), 'timeout': config.timeout, 'sdk_max_retries': 2,
        'max_tool_rounds': args.max_tool_rounds, 'max_tool_calls_per_round': 8,
        'dataset': str(dataset.relative_to(ROOT)), 'dataset_sha256': hashlib.sha256(dataset.read_bytes()).hexdigest(),
        'source_sha256': hashes, 'python': sys.version,
        'notes': 'Unchanged AgentSession policy. SDK retries are internal to each recorded API call. No gold supplied.'})
    recorder = Recorder(directory)
    client = RecordedClient(OpenAI(api_key=config.api_key, base_url=config.base_url,
                                    timeout=config.timeout, max_retries=2), recorder)
    session = AgentSession(config, client=client, tools=RecordedTools(recorder, tools), max_rounds=args.max_tool_rounds)
    print(f'RUN_DIR={directory}', flush=True)
    start = time.monotonic()
    status = 'error'
    try:
        answer = session.ask(item['query'])
        (directory / 'answer.md').write_text(answer + '\n', encoding='utf-8')
        requests = [e for e in recorder.events if e['kind'] == 'api_request']
        status = 'budget_forced_answer' if requests[-1]['request']['tool_choice'] == 'none' else 'natural_answer'
    except BaseException as exc:
        status = 'interrupted' if isinstance(exc, KeyboardInterrupt) else 'error'
        recorder.emit('run_error', error_type=type(exc).__name__)
        raise
    finally:
        recorder.emit('run_end', status=status, elapsed_seconds=time.monotonic() - start)
        responses = [e['response'] for e in recorder.events if e['kind'] == 'api_response']
        counts = Counter(e['name'] for e in recorder.events if e['kind'] == 'tool_start')
        usage = Counter()
        for response in responses:
            for key in ['prompt_tokens', 'completion_tokens', 'total_tokens']:
                usage[key] += (response.get('usage') or {}).get(key, 0) or 0
        write_json(directory / 'summary.json', {'status': status, 'api_responses': len(responses),
                   'tool_calls': dict(counts), 'reported_usage': dict(usage),
                   'elapsed_seconds': time.monotonic() - start, 'accuracy': 'not_evaluated'})
        recorder.render()
        session.close()

    return directory


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qid', required=True)
    parser.add_argument('--max-tool-rounds', type=int, default=12)
    args = parser.parse_args()
    run_question(args.qid, args.max_tool_rounds)


if __name__ == '__main__':
    main()
