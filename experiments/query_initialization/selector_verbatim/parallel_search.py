"""Two isolated replicas of the unchanged retriever; no batched embedding changes."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
import multiprocessing
import os
import threading
import time

_searcher = None


def initialize():
    global _searcher
    import torch
    torch.set_num_threads(4)
    from BCPlus.scripts.search_bcplus import BCPlusSearcher
    _searcher = BCPlusSearcher()


def search_worker(query, k):
    start = time.monotonic()
    started_at = datetime.now(timezone.utc).isoformat()
    hits = _searcher.search(query, k)
    return dict(hits=hits, pid=os.getpid(), started_at=started_at,
                finished_at=datetime.now(timezone.utc).isoformat(),
                elapsed_seconds=time.monotonic() - start)


class ParallelSearch:
    def __init__(self, workers=2):
        if not 1 <= workers <= 2:
            raise ValueError('This machine profile allows one or two retrieval replicas')
        context = multiprocessing.get_context('spawn')
        self.pools = [ProcessPoolExecutor(max_workers=1, mp_context=context,
                                         initializer=initialize) for _ in range(workers)]
        self.lock = threading.Lock()
        self.next_worker = 0

    def search(self, query, k):
        with self.lock:
            worker = self.next_worker
            self.next_worker = (worker + 1) % len(self.pools)
        result = self.pools[worker].submit(search_worker, query, k).result()
        result['worker_index'] = worker
        return result

    def preflight(self, queries, k=6):
        # Both replicas receive the same old development queries concurrently.
        # Rank/score equivalence is checked before any new-question API request.
        jobs = [(i, j, pool.submit(search_worker, query, k))
                for j, query in enumerate(queries) for i, pool in enumerate(self.pools)]
        results = [(i, j, future.result()) for i, j, future in jobs]
        for j in range(len(queries)):
            compared = [r for i, q, r in results if q == j]
            reference = compared[0]['hits']
            for result in compared[1:]:
                assert [h['docid'] for h in result['hits']] == [h['docid'] for h in reference]
                assert all(abs(a['score'] - b['score']) <= 1e-5 for a, b in zip(reference, result['hits']))
                assert all(a['text'] == b['text'] and a['url'] == b['url'] for a, b in zip(reference, result['hits']))
        return dict(status='passed', replicas=len(self.pools), queries=queries,
                    note='Unchanged single-query embedding and ranking per replica; no batching/truncation-policy changes. These old-question probes are separate from experimental Search attempts.',
                    probes=[dict(worker_index=i, query_index=j, pid=r['pid'],
                                 started_at=r['started_at'], finished_at=r['finished_at'],
                                 docids=[h['docid'] for h in r['hits']],
                                 scores=[h['score'] for h in r['hits']],
                                 elapsed_seconds=r['elapsed_seconds']) for i, j, r in results])

    def close(self):
        for pool in self.pools:
            pool.shutdown()
