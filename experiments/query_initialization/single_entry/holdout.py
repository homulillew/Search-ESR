"""Prepare a local holdout after development review and verify its frozen inputs."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random
import re


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def collect_ids(value, known, found):
    if isinstance(value, dict):
        for key, item in value.items():
            if key in {'qid', 'query_id', 'source_qid'} and str(item) in known:
                found.add(str(item))
            elif key in {'qids', 'query_ids', 'source_qids'} and isinstance(item, list):
                found.update(str(q) for q in item if str(q) in known)
            collect_ids(item, known, found)
    elif isinstance(value, list):
        for item in value:
            collect_ids(item, known, found)


def validate_lock(lock, root, config, args):
    if lock['phase'] != 'holdout' or args.qids != lock['qids'] or args.arms != lock['arms'] or args.repeats != lock['repeats']:
        raise ValueError('Run arguments differ from holdout lock')
    if config.model != lock['model'] or config.base_url != lock['base_url'] or config.request_options() != lock['request_options']:
        raise ValueError('API configuration differs from holdout lock')
    if digest(root / 'BCPlus/data/bcplus/qa.jsonl') != lock['dataset_sha256']:
        raise ValueError('Dataset changed after selection')
    if set(lock['qids']) & set(lock['excluded_qids']):
        raise ValueError('Holdout overlaps previously used questions')
    for path, expected in lock['source_sha256'].items():
        if digest(root / path) != expected:
            raise ValueError('Frozen source changed: ' + path)
    review = root / lock['development_review']
    if digest(review) != lock['development_review_sha256'] or not json.loads(review.read_text())['proceed_holdout']:
        raise ValueError('Missing or changed development decision')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('development_run', type=Path)
    parser.add_argument('--count', type=int, default=20)
    parser.add_argument('--seed', type=int, default=20260921)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[3]
    review = args.development_run.resolve() / 'dev_review.json'
    if not json.loads(review.read_text())['proceed_holdout']:
        raise ValueError('Development review did not allow holdout')
    dataset = root / 'BCPlus/data/bcplus/qa.jsonl'
    known = {str(json.loads(line)['query_id']) for line in dataset.read_text().splitlines()}
    excluded, scanned = set(), {}
    # Read historical experiment metadata and traces, including nested task lists.
    # No answer is copied into the lock or any generation payload.
    for path in sorted((root / 'experiments').rglob('*')):
        if not path.is_file() or path.suffix not in {'.json', '.jsonl', '.py', '.md'}:
            continue
        found = set(re.findall(r'qid[_=\s]+(\d+)', str(path))) & known
        text = path.read_text(errors='replace')
        found.update(set(re.findall(r'qid[_=\s]+(\d+)', text)) & known)
        if path.suffix in {'.json', '.jsonl'}:
            values = [json.loads(line) for line in text.splitlines() if line.strip()] if path.suffix == '.jsonl' else [json.loads(text)]
            for value in values:
                collect_ids(value, known, found)
        if found:
            scanned[str(path.relative_to(root))] = dict(sha256=digest(path), qids=sorted(found, key=int))
            excluded.update(found)
    eligible = sorted(known - excluded, key=int)
    if not 1 <= args.count <= len(eligible):
        raise ValueError('Insufficient locally unused questions')
    selected = random.Random(args.seed).sample(eligible, args.count)
    from llm_chat.client import Config
    config = Config.load()
    dev = json.loads((args.development_run / 'manifest.json').read_text())
    paths = set(dev['source_sha256']) | {str(p.relative_to(root)) for p in Path(__file__).parent.glob('*.py')}
    lock = dict(phase='holdout', created_at=datetime.now(timezone.utc).isoformat(),
                development_review=str(review.relative_to(root)), development_review_sha256=digest(review),
                qids=selected, excluded_qids=sorted(excluded, key=int), eligible_count=len(eligible),
                selection_seed=args.seed, arms=['minimal', 'entry_v1'], repeats=2,
                model=config.model, base_url=config.base_url, request_options=config.request_options(),
                dataset_sha256=digest(dataset), source_sha256={p: digest(root / p) for p in sorted(paths)},
                exclusion_sources=scanned)
    output = args.development_run / 'holdout_lock.json'
    if output.exists():
        raise ValueError('Holdout lock already exists; do not resample')
    output.write_text(json.dumps(lock, ensure_ascii=False, indent=2))
    print(json.dumps(dict(path=str(output), qids=selected, excluded=len(excluded), eligible=len(eligible)), indent=2))


if __name__ == '__main__':
    main()
