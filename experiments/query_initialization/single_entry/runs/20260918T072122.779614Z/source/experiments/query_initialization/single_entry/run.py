"""Run development probes only; no automatic holdout or production promotion."""
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
from experiments.query_initialization.single_entry.initializer import ARMS, system_prompt
from experiments.query_initialization.single_entry.source_units import build_question
from experiments.query_initialization.single_entry.pipeline import initialize
from experiments.query_initialization.initializer import prompt as old_prompt


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qids', nargs='+', default=['786', '551', '1072', '1117', '583', '591', '645', '183'])
    parser.add_argument('--arms', nargs='+', choices=ARMS, default=['v2', 'refs_goal', 'refs', 'minimal'])
    parser.add_argument('--repeats', type=int, default=1)
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    if not 1 <= args.workers <= 4 or args.repeats < 1:
        parser.error('workers must be 1..4 and repeats must be positive')
    if len(set(args.qids)) != len(args.qids) or len(set(args.arms)) != len(args.arms):
        parser.error('Duplicate qids or arms')
    dataset = ROOT / 'BCPlus/data/bcplus/qa.jsonl'
    rows = {}
    for line in dataset.read_text().splitlines():
        row = json.loads(line)
        rows[str(row['query_id'])] = row['query']  # Gold never enters tasks or the model input.
    if any(q not in rows for q in args.qids):
        parser.error('Unknown qid')
    config = Config.load()
    run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out = Path(__file__).parent / 'runs' / run_id
    out.mkdir(parents=True)
    tasks = [dict(qid=q, question=build_question(rows[q])) for q in args.qids]
    dump(out / 'tasks.json', tasks)
    jobs = [(t, a, r) for t in tasks for a in args.arms for r in range(1, args.repeats + 1)]
    random.Random(20260920).shuffle(jobs)
    dump(out / 'schedule.json', [dict(qid=t['qid'], arm=a, repeat=r) for t, a, r in jobs])
    paths = [str(p.relative_to(ROOT)) for p in Path(__file__).parent.glob('*.py')]
    paths += ['experiments/query_initialization/single_entry/MINIMAL_PROMPT.txt',
              'experiments/query_initialization/single_entry/ENTRY_PROMPT.txt',
              'experiments/query_initialization/single_entry/ENTRY_EVALUATION.md',
              'experiments/query_initialization/initializer.py', 'experiments/query_initialization/INITIALIZER_PROMPT.md',
              'experiments/run_rollout.py', 'llm_chat/agent.py', 'llm_chat/client.py', 'llm_chat/observed_agent.py',
              'llm_chat/observations.py', 'llm_chat/raw_windows.py', 'llm_chat/window_locator.py',
              'llm_chat/window_units.py', 'BCPlus/scripts/search_bcplus.py',
              'BCPlus/indexes/bcplus-qwen3-8b/metadata.json']
    hashes = {}
    for rel in paths:
        destination = out / 'source' / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, destination)
        hashes[rel] = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
    dump(out / 'manifest.json', dict(version='query_init_v004_entry' if 'entry_v1' in args.arms else 'query_init_v003_single_entry', phase='development', arms=args.arms,
         model=config.model, base_url=config.base_url, request_options=config.request_options(),
         max_tokens=1536, timeout=120, sdk_retries=0, repair_limit=1, repeats=args.repeats, workers=args.workers,
         schedule_seed=20260920, source_sha256=hashes, dataset_sha256=hashlib.sha256(dataset.read_bytes()).hexdigest(),
         window='baseline', k=6, window_tokens=400, max_total_window_tokens=2400,
         note='Known development questions, no holdout claims. Original question retained. No synthesis or rollout.'))
    for arm in args.arms:
        (out / f'prompt_{arm}.txt').write_text(old_prompt() if arm == 'v2' else system_prompt(arm))
    print('OUTPUT_DIR=' + str(out), flush=True)
    tokenizer = AutoTokenizer.from_pretrained('/data/model/Qwen3-Embedding-8B', local_files_only=True)
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

    def run(task, arm, repeat):
        sid = f"qid_{task['qid']}__{arm}__r{repeat}"
        path = out / sid
        path.mkdir()
        rec = Recorder(path)
        client = RecordedClient(OpenAI(api_key=config.api_key, base_url=config.base_url,
                                       timeout=120, max_retries=0), rec)
        store = ObservationStore(path / 'observations.sqlite')
        tools = ObservedTools(store)
        tools.window_builder = RawWindowBuilder(tokenizer)
        tools.searcher = Proxy()
        start = time.monotonic()
        dump(path / 'input.json', task)
        result = None
        try:
            result = initialize(client, config, task['question'], tools, attempt_id=run_id + '/' + sid,
                                arm=arm, emit=rec.emit)
            dump(path / 'handoff.json', result)
            if result['plan'] is not None:
                dump(path / 'plan.json', result['plan'])
        finally:
            dump(path / 'observations.json', store.events())
            summary = dict(session=sid, qid=task['qid'], arm=arm, repeat=repeat,
                           status=result['status'] if result else 'runner_error',
                           initial_valid=result['plan']['initial_valid'] if result and result['plan'] else False,
                           elapsed_seconds=time.monotonic() - start,
                           api_requests=sum(e['kind'] == 'api_request' for e in rec.events),
                           search_calls=sum(e['kind'] == 'search_start' for e in rec.events),
                           observations=store.summary())
            summary['usage'] = {key: sum(((e['response'].get('usage') or {}).get(key) or 0)
                                       for e in rec.events if e['kind'] == 'api_response')
                                for key in ['prompt_tokens', 'completion_tokens', 'total_tokens']}
            dump(path / 'summary.json', summary)
            rec.render()
            tools.close()
            store.close()
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
