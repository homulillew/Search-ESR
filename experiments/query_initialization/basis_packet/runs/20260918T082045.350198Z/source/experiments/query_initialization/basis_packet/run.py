"""Fixed source packets: concurrent model requests and shared serial retrieval."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random
import shutil
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from openai import OpenAI
from transformers import AutoTokenizer
from llm_chat.client import Config
from llm_chat.observations import ObservationStore
from llm_chat.observed_agent import ObservedTools
from llm_chat.raw_windows import RawWindowBuilder
from experiments.run_rollout import Recorder, RecordedClient
from experiments.query_initialization.basis_packet.packet import (
    build_packet, check_packet, verbatim, query_token_count)
from experiments.query_initialization.basis_packet.generate import generate

ARMS = ['verbatim', 'conservative', 'expression_packet', 'expression_full_context']


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repeats', type=int, default=3)
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    if args.repeats < 1 or not 1 <= args.workers <= 4:
        parser.error('Positive repeats and workers 1..4 required')
    config = Config.load()
    if config.model != 'qwen3.7-flash' or config.enable_thinking is not False:
        raise ValueError('This preregistered run requires qwen3.7-flash with thinking=false')
    base = Path(__file__).parent
    cases = json.loads((base / 'cases.json').read_text())
    metadata = json.loads((ROOT / 'BCPlus/indexes/bcplus-qwen3-8b/metadata.json').read_text())
    prefix = metadata['query_prefix']
    tokenizer = AutoTokenizer.from_pretrained('/data/model/Qwen3-Embedding-8B', local_files_only=True)
    for case in cases:
        case['packet'] = build_packet(case['question'], case['basis_refs'])
        check_packet(case['packet'], case['question'])
        if query_token_count(verbatim(case['packet']), tokenizer, prefix) > 1024:
            raise ValueError('Fixed packet over budget: ' + case['qid'])
    out = base / 'runs' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    dump(out / 'tasks.json', cases)
    jobs = [(c, arm, r) for c in cases for arm in ARMS
            for r in range(1, 2 if arm == 'verbatim' else args.repeats + 1)]
    random.Random(20260922).shuffle(jobs)
    dump(out / 'schedule.json', [dict(qid=c['qid'], arm=a, repeat=r) for c, a, r in jobs])
    paths = [str(p.relative_to(ROOT)) for p in base.iterdir() if p.suffix in {'.py', '.txt', '.json', '.md'}]
    paths += ['experiments/query_initialization/single_entry/initializer.py',
              'experiments/query_initialization/single_entry/source_units.py',
              'experiments/query_initialization/initializer.py', 'experiments/run_rollout.py',
              'llm_chat/client.py', 'llm_chat/agent.py', 'llm_chat/observed_agent.py', 'llm_chat/observations.py',
              'llm_chat/raw_windows.py', 'llm_chat/window_locator.py', 'llm_chat/window_units.py',
              'BCPlus/scripts/search_bcplus.py', 'BCPlus/indexes/bcplus-qwen3-8b/metadata.json',
              '全链路排查报告/BasisPacket与保守查询编译设计.md']
    hashes = {}
    for name in paths:
        dest = out / 'source' / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, dest)
        hashes[name] = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
    reference = base / 'reference_annotations.json'
    shutil.copy2(reference, out / 'reference_annotations.json')
    dump(out / 'manifest.json', dict(
        version='basis_packet_v001', phase='fixed_packet_known_case_diagnostic', arms=ARMS,
        python=sys.version,
        reference_annotations_sha256=hashlib.sha256(reference.read_bytes()).hexdigest(),
        source_sha256=hashes, tasks_sha256=hashlib.sha256((out / 'tasks.json').read_bytes()).hexdigest(),
        dataset_sha256=hashlib.sha256((ROOT / 'BCPlus/data/bcplus/qa.jsonl').read_bytes()).hexdigest(),
        model=config.model, base_url=config.base_url, request_options=config.request_options(),
        workers=args.workers, model_repeats=args.repeats, control_repeats=1,
        max_tokens=1536, query_max_tokens=1024, query_prefix=prefix,
        timeout=120, sdk_retries=0, repair_limit=1, schedule_seed=20260922,
        window='baseline', k=6, window_tokens=400, total_window_budget=2400,
        note='Human-selected exact source packets. Compiler only sees text; D also sees original question. No Selector, gold, final answer, verifier or retrieval-feedback retries.'))
    print('OUTPUT_DIR=' + str(out), flush=True)
    retrieval = ThreadPoolExecutor(max_workers=1)
    holder = {}

    def search(query, k):
        if 'searcher' not in holder:
            from BCPlus.scripts.search_bcplus import BCPlusSearcher
            holder['searcher'] = BCPlusSearcher()
        return holder['searcher'].search(query, k)

    class Proxy:
        def search(self, query, k):
            return retrieval.submit(search, query, k).result()

    def run(case, arm, repeat):
        sid = f"qid_{case['qid']}__{arm}__r{repeat}"
        folder = out / sid
        folder.mkdir()
        rec = Recorder(folder)
        client = None
        store = ObservationStore(folder / 'observations.sqlite')
        tools = ObservedTools(store)
        tools.window_builder = RawWindowBuilder(tokenizer)
        tools.searcher = Proxy()
        packet = case['packet']
        start = time.monotonic()
        data = dict(session=sid, qid=case['qid'], arm=arm, repeat=repeat, status='pending', plan=None, result=[])
        handoff = dict(schema_version='basis_packet_handoff_v1', original_question=case['question'],
                       packet_id=packet['packet_id'], status='pending', search_attempts=[])
        dump(folder / 'input.json', case)
        dump(folder / 'packet.json', packet)
        stage = 'compilation'
        try:
            if arm == 'verbatim':
                query = verbatim(packet)
                plan = dict(status='valid', query=query, initial_valid=True, repairs=0,
                            initial_errors=[], errors=[], input_refs=packet['input_refs'],
                            query_tokens=query_token_count(query, tokenizer, prefix), origin='deterministic_verbatim')
                rec.emit('control_query', arm=arm, query=query)
            else:
                client = RecordedClient(OpenAI(api_key=config.api_key, base_url=config.base_url,
                                               timeout=120, max_retries=0), rec)
                plan = generate(client, config, packet, arm, tokenizer, prefix,
                                question=case['question'] if arm == 'expression_full_context' else None)
            data['plan'] = plan
            rec.emit('query_finalized', plan=plan)
            if plan['status'] == 'valid':
                if query_token_count(plan['query'], tokenizer, prefix) > 1024:
                    raise ValueError('Query over budget before search')
                stage = 'search'
                arguments = dict(query=plan['query'], k=6)
                attempt = dict(attempt_id=out.name + '/' + sid, packet_id=packet['packet_id'],
                               input_refs=plan['input_refs'], method=arm, query=plan['query'],
                               arguments=arguments, status='pending', result=[])
                handoff['search_attempts'].append(attempt)
                rec.emit('search_start', arguments=arguments)
                data['result'] = tools.execute('search', arguments)
                rec.emit('search_result', arguments=arguments, result=data['result'])
                data['status'] = 'complete'
                attempt.update(status='complete', result=data['result'])
            else:
                data['status'] = plan['status']
        except Exception as exc:
            data.update(status='search_error' if stage == 'search' else 'generation_error',
                        error_type=type(exc).__name__, error_detail=str(exc).replace(config.api_key, '[redacted]'))
            rec.emit('run_error', stage=stage, error_type=type(exc).__name__)
            if handoff['search_attempts']:
                handoff['search_attempts'][-1]['status'] = data['status']
        finally:
            handoff['status'] = data['status']
            dump(folder / 'handoff.json', handoff)
            dump(folder / 'result.json', data)
            dump(folder / 'observations.json', store.events())
            summary = {key: data[key] for key in ['session', 'qid', 'arm', 'repeat', 'status']}
            summary.update(elapsed_seconds=time.monotonic() - start,
                           api_requests=sum(e['kind'] == 'api_request' for e in rec.events),
                           search_calls=sum(e['kind'] == 'search_start' for e in rec.events))
            summary['usage'] = {key: sum(((e['response'].get('usage') or {}).get(key) or 0)
                                       for e in rec.events if e['kind'] == 'api_response')
                                for key in ['prompt_tokens', 'completion_tokens', 'total_tokens']}
            dump(folder / 'summary.json', summary)
            rec.render()
            tools.close()
            store.close()
            if client:
                client.close()
        return summary

    results = []
    try:
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            for future in as_completed([pool.submit(run, *job) for job in jobs]):
                result = future.result()
                results.append(result)
                dump(out / 'results.json', results)
                print('DONE', result['session'], result['status'], flush=True)
    finally:
        retrieval.shutdown()
    print('FINISHED', out, flush=True)


if __name__ == '__main__':
    main()
