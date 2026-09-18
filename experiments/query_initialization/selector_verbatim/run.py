"""Locked unseen-question Selector experiment with parallel API and retrieval."""
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
from experiments.query_initialization.single_entry.source_units import check_question
from experiments.query_initialization.basis_packet.packet import build_packet, verbatim, query_token_count
from experiments.query_initialization.selector_verbatim.selector import generate
from experiments.query_initialization.selector_verbatim.parallel_search import ParallelSearch


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=8)
    parser.add_argument('--retrieval-workers', type=int, default=2)
    args = parser.parse_args()
    if not 1 <= args.workers <= 8 or not 1 <= args.retrieval_workers <= 2:
        parser.error('API workers 1..8, retrieval replicas 1..2')
    base = Path(__file__).parent
    config = Config.load()
    if config.model != 'qwen3.7-flash' or config.enable_thinking is not False:
        raise ValueError('Locked model profile requires qwen3.7-flash thinking=false')
    lock = json.loads((base / 'selection_lock.json').read_text())
    cases = json.loads((base / 'tasks.json').read_text())
    assert digest(base / 'tasks.json') == lock['tasks_sha256']
    assert digest(ROOT / 'BCPlus/data/bcplus/qa.jsonl') == lock['dataset_sha256']
    assert [c['qid'] for c in cases] == lock['qids']
    assert not set(lock['qids']) & set(lock['excluded_qids'])
    for name, expected in lock['preparation_source_sha256'].items():
        assert digest(ROOT / name) == expected, name
    for case in cases:
        check_question(case['question'])
        assert case['question']['sha256'] == lock['question_sha256'][case['qid']]
    metadata = json.loads((ROOT / 'BCPlus/indexes/bcplus-qwen3-8b/metadata.json').read_text())
    prefix = metadata['query_prefix']
    tokenizer = AutoTokenizer.from_pretrained('/data/model/Qwen3-Embedding-8B', local_files_only=True)
    out = base / 'runs' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    shutil.copy2(base / 'selection_lock.json', out / 'selection_lock.json')
    shutil.copy2(base / 'tasks.json', out / 'tasks.json')
    jobs = [(c, arm, rep) for c in cases for arm in ['full_question', 'selector']
            for rep in range(1, 2 if arm == 'full_question' else 3)]
    random.Random(20260924).shuffle(jobs)
    dump(out / 'schedule.json', [dict(qid=c['qid'], arm=a, repeat=r) for c, a, r in jobs])
    names = [str(p.relative_to(ROOT)) for p in base.iterdir() if p.suffix in {'.py', '.md', '.json', '.txt'}]
    names += ['experiments/query_initialization/basis_packet/packet.py',
              'experiments/query_initialization/single_entry/source_units.py',
              'experiments/query_initialization/single_entry/initializer.py',
              'experiments/query_initialization/initializer.py', 'experiments/run_rollout.py',
              'llm_chat/client.py', 'llm_chat/agent.py', 'llm_chat/observed_agent.py',
              'llm_chat/observations.py', 'llm_chat/raw_windows.py', 'llm_chat/window_locator.py',
              'llm_chat/window_units.py', 'BCPlus/scripts/search_bcplus.py',
              'BCPlus/indexes/bcplus-qwen3-8b/metadata.json']
    hashes = {}
    for name in names:
        destination = out / 'source' / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, destination)
        hashes[name] = digest(ROOT / name)
    manifest = dict(version='selector_verbatim_v001', phase='locally_unused_questions',
        source_sha256=hashes, dataset_sha256=lock['dataset_sha256'],
        tasks_sha256=digest(out / 'tasks.json'), selection_lock_sha256=digest(out / 'selection_lock.json'),
        arms=['full_question', 'selector'], model_repeats=2, control_repeats=1,
        model=config.model, base_url=config.base_url, request_options=config.request_options(),
        max_tokens=1536, query_max_tokens=1024, query_prefix=prefix, timeout=120,
        sdk_retries=0, repair_limit=1, workers=args.workers, retrieval_workers=args.retrieval_workers,
        schedule_seed=20260924, window='baseline', k=6, window_tokens=400,
        total_window_budget=2400, python=sys.version,
        note='No Compiler. Selector chooses refs; Harness executes exact source text. Full-question baseline uses all original units and identical separators. All failures retained. New locally unused tasks, not model-pretraining holdout. Offline relevance labels are post-run; no gold in requests.')
    dump(out / 'manifest.json', manifest)
    print('OUTPUT_DIR=' + str(out), flush=True)
    retrieval = ParallelSearch(args.retrieval_workers)
    # Prior development inputs only: never use held-out questions to tune replicas.
    old = json.loads((ROOT / 'experiments/query_initialization/basis_packet/cases.json').read_text())
    probes = [verbatim(build_packet(c['question'], c['basis_refs'])) for c in old[:3]]
    try:
        preflight = retrieval.preflight(probes)
        dump(out / 'retrieval_preflight.json', preflight)
        print('RETRIEVAL_PREFLIGHT passed', flush=True)
    except BaseException:
        retrieval.close()
        raise

    def run(case, arm, repeat):
        sid = f"qid_{case['qid']}__{arm}__r{repeat}"
        folder = out / sid
        folder.mkdir()
        rec = Recorder(folder)
        store = ObservationStore(folder / 'observations.sqlite')
        tools = ObservedTools(store)
        tools.window_builder = RawWindowBuilder(tokenizer)

        class Proxy:
            def search(self, query, k):
                result = retrieval.search(query, k)
                rec.emit('retrieval_worker', **{k: v for k, v in result.items() if k != 'hits'})
                return result['hits']

        tools.searcher = Proxy()
        client = None
        start = time.monotonic()
        data = dict(session=sid, qid=case['qid'], arm=arm, repeat=repeat, status='pending', plan=None, result=[])
        handoff = dict(schema_version='basis_packet_handoff_v1', original_question=case['question'],
                       packet_id=None, status='pending', search_attempts=[])
        dump(folder / 'input.json', case)
        dump(folder / 'packet.json', None)
        stage = 'selection'
        try:
            if arm == 'full_question':
                refs = [u['ref'] for u in case['question']['units']]
                packet = build_packet(case['question'], refs)
                query = verbatim(packet)
                count = query_token_count(query, tokenizer, prefix)
                plan = dict(status='valid' if count <= 1024 else 'packet_over_budget',
                    selected_units=refs, selector_input_refs=[], packet=packet, query=query,
                    input_refs=refs, query_tokens=count, initial_valid=True, repairs=0,
                    initial_errors=[], errors=[], origin='full_question_verbatim')
                rec.emit('control_query', query=query)
            else:
                client = RecordedClient(OpenAI(api_key=config.api_key, base_url=config.base_url,
                                               timeout=120, max_retries=0), rec)
                plan = generate(client, config, case['question'], tokenizer, prefix)
            data['plan'] = plan
            dump(folder / 'packet.json', plan['packet'])
            handoff['packet_id'] = plan['packet']['packet_id'] if plan['packet'] else None
            rec.emit('query_finalized', plan=plan)
            if plan['status'] == 'valid':
                assert query_token_count(plan['query'], tokenizer, prefix) <= 1024
                stage = 'search'
                arguments = dict(query=plan['query'], k=6)
                attempt = dict(attempt_id=out.name + '/' + sid, packet_id=plan['packet']['packet_id'],
                    input_refs=plan['input_refs'], method=arm, query=plan['query'], arguments=arguments,
                    status='pending', result=[])
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
        retrieval.close()
    print('FINISHED', out, flush=True)


if __name__ == '__main__':
    main()
