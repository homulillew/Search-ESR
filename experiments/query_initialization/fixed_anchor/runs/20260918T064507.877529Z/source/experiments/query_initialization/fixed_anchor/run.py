"""Parallel API expression probes plus preregistered manual retrieval controls."""
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
from experiments.query_initialization.fixed_anchor.generate import generate
from experiments.query_initialization.single_entry.source_units import check_question


def dump(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repeats', type=int, default=3)
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    if args.repeats < 1 or not 1 <= args.workers <= 4:
        parser.error('Positive repeats and workers 1..4 required')
    config = Config.load()
    base = Path(__file__).parent
    cases = json.loads((base / 'cases.json').read_text())
    for case in cases:
        check_question(case['question'])
        a, b = case['removed_span']
        assert case['full_query'][a:b] == case['removed_text']
        assert case['full_query'][:a] + case['full_query'][b:] == case['delete_query']
    out = base / 'runs' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    dump(out / 'tasks.json', cases)
    jobs = [(c, arm, r) for c in cases for arm in ['full', 'delete', 'model']
            for r in range(1, args.repeats + 1 if arm == 'model' else 2)]
    random.Random(20260921).shuffle(jobs)
    dump(out / 'schedule.json', [dict(qid=c['qid'], arm=a, repeat=r) for c, a, r in jobs])
    paths = [str(p.relative_to(ROOT)) for p in base.glob('*') if p.suffix in {'.py', '.txt', '.json'}]
    paths += ['experiments/query_initialization/single_entry/initializer.py',
              'experiments/query_initialization/single_entry/source_units.py',
              'experiments/query_initialization/initializer.py', 'experiments/run_rollout.py',
              'llm_chat/client.py', 'llm_chat/agent.py', 'llm_chat/observed_agent.py', 'llm_chat/observations.py',
              'llm_chat/raw_windows.py', 'llm_chat/window_locator.py', 'llm_chat/window_units.py',
              'BCPlus/scripts/search_bcplus.py', 'BCPlus/indexes/bcplus-qwen3-8b/metadata.json']
    hashes = {}
    for name in paths:
        dest = out / 'source' / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, dest)
        hashes[name] = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
    reference_file = ROOT / 'experiments/query_initialization/runs/20260918T053659.834656Z/evidence_annotations.json'
    shutil.copy2(reference_file, out / 'reference_annotations.json')
    dump(out / 'manifest.json', dict(reference_annotations_sha256=hashlib.sha256(reference_file.read_bytes()).hexdigest(), version='fixed_anchor_v001', phase='known_case_diagnostic',
         model=config.model, base_url=config.base_url, request_options=config.request_options(),
         source_sha256=hashes, workers=args.workers, model_repeats=args.repeats, control_repeats=1,
         max_tokens=1536, timeout=120, sdk_retries=0, repair_limit=1, schedule_seed=20260921,
         window='baseline', k=6, window_tokens=400, total_window_budget=2400,
         note='Full/delete are human-specified controls, not API variants. Model receives original question, fixed target and exact clue units only. No gold, manual queries, or retrieval feedback.'))
    print('OUTPUT_DIR=' + str(out), flush=True)
    tokenizer = AutoTokenizer.from_pretrained('/data/model/Qwen3-Embedding-8B', local_files_only=True)
    worker = ThreadPoolExecutor(max_workers=1)
    holder = {}

    def search(query, k):
        if 'searcher' not in holder:
            from BCPlus.scripts.search_bcplus import BCPlusSearcher
            holder['searcher'] = BCPlusSearcher()
        return holder['searcher'].search(query, k)

    class Proxy:
        def search(self, query, k):
            return worker.submit(search, query, k).result()

    def run(case, arm, repeat):
        sid = f"qid_{case['qid']}__{arm}__r{repeat}"
        folder = out / sid
        folder.mkdir()
        recorder = Recorder(folder)
        client = None
        store = ObservationStore(folder / 'observations.sqlite')
        tools = ObservedTools(store)
        tools.window_builder = RawWindowBuilder(tokenizer)
        tools.searcher = Proxy()
        start = time.monotonic()
        data = dict(session=sid, qid=case['qid'], arm=arm, repeat=repeat, status='pending', plan=None, result=[])
        dump(folder / 'input.json', dict(qid=case['qid'], question=case['question'], basis_refs=case['basis_refs'], fixed_target=case['fixed_target']))
        try:
            if arm == 'model':
                client = RecordedClient(OpenAI(api_key=config.api_key, base_url=config.base_url,
                                               timeout=120, max_retries=0), recorder)
                plan = generate(client, config, case)
            else:
                plan = dict(status='valid', query=case[arm + '_query'], initial_valid=True, repairs=0,
                            origin='preregistered_manual_control')
                recorder.emit('control_query', arm=arm, query=plan['query'])
            data['plan'] = plan
            recorder.emit('query_finalized', plan=plan)
            if plan['status'] == 'valid':
                arguments = dict(query=plan['query'], k=6)
                recorder.emit('search_start', arguments=arguments)
                data['result'] = tools.execute('search', arguments)
                recorder.emit('search_result', arguments=arguments, result=data['result'])
                data['status'] = 'complete'
            else:
                data['status'] = plan['status']
        except Exception as exc:
            data.update(status='error', error_type=type(exc).__name__, error_detail=str(exc).replace(config.api_key, '[redacted]'))
            recorder.emit('run_error', error_type=type(exc).__name__)
        finally:
            dump(folder / 'result.json', data)
            dump(folder / 'observations.json', store.events())
            summary = {key: data[key] for key in ['session', 'qid', 'arm', 'repeat', 'status']}
            summary.update(elapsed_seconds=time.monotonic() - start,
                           api_requests=sum(e['kind'] == 'api_request' for e in recorder.events),
                           search_calls=sum(e['kind'] == 'search_start' for e in recorder.events))
            summary['usage'] = {key: sum(((e['response'].get('usage') or {}).get(key) or 0)
                                       for e in recorder.events if e['kind'] == 'api_response')
                                for key in ['prompt_tokens', 'completion_tokens', 'total_tokens']}
            dump(folder / 'summary.json', summary)
            recorder.render()
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
        worker.shutdown()
    print('FINISHED', out, flush=True)


if __name__ == '__main__':
    main()
