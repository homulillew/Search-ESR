"""Mechanism metrics for one rollout directory (CLAUDE_NEXT.md section 4).

Reads only what the online run itself recorded: events.jsonl tool_start /
tool_result / tool_internal, summary.json and answer.md. Gold/reference is
never consulted here; that belongs to the offline semantic review in step 5.

Usage: python experiments/search_find_v3a/analyze_mechanism.py <run_dir>...
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_events(run_dir):
    path = Path(run_dir) / 'events.jsonl'
    if not path.exists():
        raise SystemExit(f'no events.jsonl in {run_dir}')
    with path.open() as f:
        return [json.loads(line) for line in f]


def analyze(run_dir):
    events = load_events(run_dir)
    starts = [e for e in events if e['kind'] == 'tool_start']
    results = [e for e in events if e['kind'] == 'tool_result']
    internals = [e for e in events if e['kind'] == 'tool_internal']
    errors = [e for e in events if e['kind'] == 'tool_error']

    by_seq = {e['seq']: e for e in results}
    # tool_internal has its own seq and is emitted right after the tool_result
    # it belongs to, so pair them positionally rather than by seq.
    audit_by_result_seq = {}
    pending = None
    for e in events:
        if e['kind'] == 'tool_result':
            pending = e
        elif e['kind'] == 'tool_internal' and pending is not None:
            audit_by_result_seq[pending['seq']] = e.get('audit') or {}
            pending = None

    metrics = Counter()
    metrics['tool_calls_total'] = len(starts)
    for e in starts:
        metrics[f'{e["name"]}_calls'] += 1

    # Model-visible D#/W# and the canonical identities behind them.
    doc_ref_to_canon = {}      # D# -> (docid, sha)
    window_ref_to_canon = {}   # W# -> canonical w_...
    windows_observed = {}      # (D#, canonical window) -> first W# seen

    def note_doc(dref, docid, sha):
        doc_ref_to_canon.setdefault(dref, (docid, sha))

    for e in results:
        audit = audit_by_result_seq.get(e['seq']) or {}
        snap = audit.get('handles') or {}
        for d in snap.get('documents', []):
            note_doc(d['doc_ref'], d['docid'], d['document_sha256'])
        for w in snap.get('windows', []):
            window_ref_to_canon.setdefault(w['window_ref'], w['source_window_ref'])

    # Per-search rows as (doc_key, canonical window_ref). doc_key is the
    # model-visible document identity: D# for search_find_v3a, docid for the
    # baseline. The canonical window_ref comes from the v3a tool_internal
    # audit; the baseline exposes it directly on each result row.
    def search_rows_for(e):
        audit = audit_by_result_seq.get(e['seq']) or {}
        raw_hits = audit.get('raw_result') or []
        r = e['result']
        if isinstance(r, dict):
            out = []
            for i, row in enumerate(r.get('results', [])):
                canon = (raw_hits[i] or {}).get('window_ref') if i < len(raw_hits) else None
                out.append((row.get('doc_ref'), canon))
            return out, r.get('status')
        if isinstance(r, list):
            return [(row.get('docid'), row.get('window_ref')) for row in r], 'baseline_rows'
        return [], 'legacy_shape'

    search_docs = []           # (search seq, status, [(doc_key, window_ref)])
    for e in results:
        if e['name'] != 'search':
            continue
        rows, status = search_rows_for(e)
        search_docs.append((e['seq'], status, rows))
        metrics['search_result_rows'] += len(rows)

    # Document identity seen in the rows themselves (works for both protocols;
    # the registry snapshot further below only exists for search_find_v3a).
    row_doc_keys = set()
    row_window_refs = set()
    per_search_keys = []       # [{doc_key}] per search, in order
    per_search_windows = []    # [{doc_key: set(window_ref)}] per search, in order
    for seq, status, rows in search_docs:
        keys, wins = set(), {}
        for dkey, canon in rows:
            if dkey:
                keys.add(dkey)
                row_doc_keys.add(dkey)
            if dkey and canon:
                wins.setdefault(dkey, set()).add(canon)
                row_window_refs.add(canon)
        per_search_keys.append(keys)
        per_search_windows.append(wins)
    metrics['distinct_documents'] = len(row_doc_keys)
    metrics['distinct_windows'] = len(row_window_refs)
    metrics['registered_doc_handles'] = len(doc_ref_to_canon)
    metrics['registered_window_handles'] = len(window_ref_to_canon)

    # Same document returned by more than one global search.
    repeat_doc_counter = Counter()
    for keys in per_search_keys:
        for dkey in keys:
            repeat_doc_counter[dkey] += 1
    metrics['docs_returned_by_multiple_searches'] = sum(1 for v in repeat_doc_counter.values() if v > 1)
    metrics['extra_search_returns_of_known_docs'] = sum(v - 1 for v in repeat_doc_counter.values() if v > 1)

    # A document relocates globally when a later Search returns it at a window
    # no earlier Search had shown for that document. This is the behaviour find
    # is meant to absorb: re-running a global Search just to move inside a
    # document the model already knew about.
    seen_before = {}           # doc_key -> set(window_ref) from earlier searches
    relocation_docs = set()
    for wins in per_search_windows:
        for dkey, wset in wins.items():
            if dkey in seen_before and not wset <= seen_before[dkey]:
                relocation_docs.add(dkey)
        for dkey, wset in wins.items():
            seen_before.setdefault(dkey, set()).update(wset)
    metrics['global_same_doc_relocation_docs'] = len(relocation_docs)

    # find behaviour
    find_windows = []           # (seq, D#, query, canonical window or None)
    for e in results:
        if e['name'] != 'find':
            continue
        r = e['result']
        dref = r.get('doc_ref')
        query = r.get('query')
        matches = r.get('matches') or []
        canon = window_ref_to_canon.get(matches[0]['window_ref']) if matches else None
        find_windows.append((e['seq'], dref, query, canon))
        if r.get('status') == 'no_match':
            metrics['find_no_match'] += 1

    # Find producing a window never before observed for that document.
    # seen_before holds exactly the windows earlier Searches showed per doc.
    seen_windows_per_doc = seen_before

    new_window_finds = []
    for seq, dref, query, canon in find_windows:
        if canon is None:
            continue
        known = seen_windows_per_doc.get(dref, set())
        if canon not in known:
            new_window_finds.append((seq, dref, query, canon))
            metrics['local_find_relocation'] += 1
        else:
            metrics['find_rediscovers_known_window'] += 1

    # Ordering signals
    order = [e['name'] for e in starts]
    first_search_idx = order.index('search') if 'search' in order else None
    first_find_idx = order.index('find') if 'find' in order else None
    if first_search_idx is not None and first_find_idx is not None:
        metrics['searches_before_first_find'] = sum(1 for n in order[:first_find_idx] if n == 'search')
    # Immediately after a find, did the model go back to global search?
    if 'find' in order:
        for i, n in enumerate(order):
            if n == 'find' and i + 1 < len(order):
                metrics[f'next_after_find_{order[i + 1]}'] += 1
    if 'open' in order:
        for i, n in enumerate(order):
            if n == 'open' and i + 1 < len(order):
                metrics[f'next_after_open_{order[i + 1]}'] += 1

    metrics['tool_errors'] = len(errors)
    for e in errors:
        metrics[f'error_{e["name"]}'] += 1

    summary_path = Path(run_dir) / 'summary.json'
    summary = json.load(summary_path.open()) if summary_path.exists() else {}
    answer_path = Path(run_dir) / 'answer.md'
    answer = answer_path.read_text(encoding='utf-8') if answer_path.exists() else ''

    manifest_path = Path(run_dir) / 'manifest.json'
    manifest = json.load(manifest_path.open()) if manifest_path.exists() else {}

    return {
        'run_dir': str(run_dir),
        'protocol': manifest.get('agent_protocol'),
        'qid': manifest.get('qid'),
        'status': summary.get('status'),
        'metrics': dict(metrics),
        'first_window_finds': new_window_finds,
        'relocation_doc_refs': sorted(relocation_docs),
        'repeat_doc_refs': sorted(d for d, v in repeat_doc_counter.items() if v > 1),
        'doc_ref_to_canonical': {k: list(v) for k, v in doc_ref_to_canon.items()},
        'answer_chars': len(answer),
        'reported_usage': summary.get('reported_usage'),
        'elapsed_seconds': summary.get('elapsed_seconds'),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('run_dirs', nargs='+')
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()
    out = [analyze(d) for d in args.run_dirs]
    if args.json:
        print(json.dumps(out, indent=1, ensure_ascii=False))
        return
    for r in out:
        print(f"\n===== {r['run_dir']} =====")
        print(f"protocol={r['protocol']} qid={r['qid']} status={r['status']} "
              f"elapsed={r['elapsed_seconds']} answer_chars={r['answer_chars']}")
        for k in sorted(r['metrics']):
            print(f"  {k}: {r['metrics'][k]}")
        if r['first_window_finds']:
            print("  local_find_relocation details:")
            for seq, dref, query, canon in r['first_window_finds']:
                print(f"    seq={seq} {dref} query={query!r} -> {canon}")
        if r['relocation_doc_refs']:
            print(f"  global relocation doc refs: {r['relocation_doc_refs']}")
        if r['repeat_doc_refs']:
            print(f"  docs returned by multiple searches: {r['repeat_doc_refs']}")


if __name__ == '__main__':
    main()
