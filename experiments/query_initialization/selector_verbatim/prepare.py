"""Freeze locally unused questions before requests; never resample an existing lock."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from experiments.query_initialization.single_entry.holdout import collect_ids
from experiments.query_initialization.single_entry.source_units import build_question


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def historical_ids(path, known):
    found = set(re.findall(r'qid[_=\s]+(\d+)', str(path))) & known
    # Line streaming avoids materializing large API archives. JSONL records and
    # ordinary small JSON metadata also use the existing recursive scanner.
    with path.open(errors='replace') as stream:
        for line in stream:
            found.update(set(re.findall(r'qid[_=\s]+(\d+)', line)) & known)
            found.update(set(re.findall(r'"(?:qid|query_id|source_qid)"\s*:\s*"?(\d+)', line)) & known)
            for group in re.findall(r'"(?:qids|query_ids|source_qids)"\s*:\s*\[([^\]]*)\]', line):
                found.update(set(re.findall(r'\d+', group)) & known)
            if path.suffix == '.jsonl':
                try:
                    collect_ids(json.loads(line), known, found)
                except json.JSONDecodeError:
                    pass
    if path.suffix == '.json' and path.stat().st_size <= 8 * 1024 * 1024:
        try:
            collect_ids(json.loads(path.read_text()), known, found)
        except json.JSONDecodeError:
            pass
    return found


def main():
    output = BASE / 'selection_lock.json'
    if output.exists() or (BASE / 'tasks.json').exists():
        raise ValueError('Frozen sample already exists; do not resample')
    dataset = ROOT / 'BCPlus/data/bcplus/qa.jsonl'
    # Answers never leave this dataset reader or enter task files.
    questions = {}
    for line in dataset.read_text().splitlines():
        row = json.loads(line)
        questions[str(row['query_id'])] = row['query']
    known = set(questions)
    excluded, sources = set(), {}
    scanned_count = 0
    for folder in ['experiments', '全链路排查报告', '旧仓库bad_case分析', '指令提示词']:
        scanroot = ROOT / folder
        if not scanroot.exists():
            continue
        for path in sorted(scanroot.rglob('*')):
            if (not path.is_file() or BASE in path.parents
                    or path.suffix not in {'.json', '.jsonl', '.py', '.md', '.txt'}):
                continue
            scanned_count += 1
            found = historical_ids(path, known)
            if found:
                sources[str(path.relative_to(ROOT))] = dict(sha256=digest(path), qids=sorted(found, key=int))
                excluded.update(found)
    eligible = sorted(known - excluded, key=int)
    selected = random.Random(20260923).sample(eligible, 20)
    tasks = [dict(qid=qid, question=build_question(questions[qid])) for qid in selected]
    tasks_path = BASE / 'tasks.json'
    tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + '\n')
    lock = dict(
        schema_version='selector_verbatim_selection_v1',
        created_at=datetime.now(timezone.utc).isoformat(),
        phase='locally_unused_question_holdout', seed=20260923, count=20,
        qids=selected, excluded_qids=sorted(excluded, key=int), eligible_count=len(eligible),
        exclusion_scanned_files=scanned_count, exclusion_sources=sources,
        scan_policy='experiments + reports + prototype notes; skip own new directory; qid metadata and explicit qid text; no claim of globally unseen/model-unseen data',
        arms={'full_question': 1, 'selector': 2},
        max_searches=60, initial_api_requests=40, format_repair_limit=1,
        dataset_sha256=digest(dataset), tasks_sha256=digest(tasks_path),
        question_sha256={t['qid']: t['question']['sha256'] for t in tasks},
        preparation_source_sha256={str(p.relative_to(ROOT)): digest(p) for p in [Path(__file__), ROOT / 'experiments/query_initialization/single_entry/source_units.py', ROOT / 'experiments/query_initialization/single_entry/holdout.py']},
        resampling_forbidden=True,
        note='Lock sample before API requests. Runtime prompt/config/source snapshots frozen separately before execution. Gold absent from tasks. Difficult, over-budget and empty-selection cases retained.')
    output.write_text(json.dumps(lock, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(dict(lock=str(output), qids=selected, excluded=len(excluded), eligible=len(eligible)), ensure_ascii=False))


if __name__ == '__main__':
    main()
