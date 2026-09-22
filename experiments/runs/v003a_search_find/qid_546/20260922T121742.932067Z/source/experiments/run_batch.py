"""Parallel independent API sessions sharing a serialized local retrieval worker."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from experiments.run_rollout import run_question, write_json
from llm_chat.agent import BCPlusTools


class SharedTools:
    def __init__(self):
        self.worker = ThreadPoolExecutor(max_workers=1)
        self.inner = None

    def _execute(self, name, arguments):
        if self.inner is None:
            self.inner = BCPlusTools()
        return self.inner.execute(name, arguments)

    def execute(self, name, arguments):
        return self.worker.submit(self._execute, name, arguments).result()

    def close(self):
        # Individual sessions must not close a resource still used by other sessions.
        pass

    def shutdown(self):
        if self.inner is not None:
            self.worker.submit(self.inner.close).result()
        self.worker.shutdown()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qids', nargs='+', required=True)
    parser.add_argument('--workers', type=int, default=6)
    parser.add_argument('--max-tool-rounds', type=int, default=64)
    args = parser.parse_args()
    if args.workers < 1 or len(set(args.qids)) != len(args.qids):
        parser.error('positive workers and unique qids required')
    batch_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    directory = ROOT / 'experiments/batches' / batch_id
    directory.mkdir(parents=True, exist_ok=False)
    manifest = {'batch_id': batch_id, 'variant': 'v002_raw_windows_mechanical', 'qids': args.qids,
                'workers': args.workers, 'max_tool_rounds': args.max_tool_rounds,
                'execution': 'Independent API sessions; one serialized GPU/SQLite worker; per-tool latency includes queue wait.',
                'runs': {}}
    write_json(directory / 'batch.json', manifest)
    print(f'BATCH_DIR={directory}', flush=True)
    shared = SharedTools()
    try:
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = {pool.submit(run_question, qid, args.max_tool_rounds, shared, batch_id): qid for qid in args.qids}
            for future in as_completed(futures):
                qid = futures[future]
                try:
                    path = future.result()
                    manifest['runs'][qid] = {'directory': str(path.relative_to(ROOT)), 'completed': True}
                except Exception as exc:
                    manifest['runs'][qid] = {'completed': False, 'error_type': type(exc).__name__}
                write_json(directory / 'batch.json', manifest)
                print(f'QID_DONE={qid} {manifest["runs"][qid]}', flush=True)
    finally:
        shared.shutdown()
    if any(not run['completed'] for run in manifest['runs'].values()):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
