"""Create immutable, gold-blind inputs and the offline experiment freeze."""
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import random
import re
import statistics
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DATASET = ROOT / 'BCPlus/data/bcplus/qa.jsonl'
SEED = 20260928


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def save(name, value):
    (HERE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def percentile(values, p):
    values = sorted(values)
    pos = (len(values) - 1) * p / 100
    lo = int(pos)
    return values[lo] + (values[min(lo + 1, len(values) - 1)] - values[lo]) * (pos - lo)


def main():
    rows = [json.loads(line) for line in DATASET.open(encoding='utf-8') if line.strip()]
    qids = [str(row.get('query_id', '')) for row in rows]
    counts = Counter(qids)
    eligible = {qid: row['query'] for qid, row in zip(qids, rows)
                if qid.isdigit() and counts[qid] == 1
                and isinstance(row.get('query'), str) and row['query'].strip()
                and isinstance(row.get('answer'), str) and row['answer'].strip()}
    save('DATASET_AUDIT.json', {
        'path': str(DATASET.relative_to(ROOT)), 'sha256': digest(DATASET),
        'row_count': len(rows), 'unique_query_id_count': len(counts),
        'duplicate_query_id_count': sum(n - 1 for n in counts.values() if n > 1),
        'actual_schema': dict(Counter(','.join(sorted(row)) for row in rows)),
        'missing_question_count': sum(not isinstance(r.get('query'), str) or not r['query'].strip() for r in rows),
        'missing_gold_answer_count': sum(not isinstance(r.get('answer'), str) or not r['answer'].strip() for r in rows),
        'eligible_population_count': len(eligible)})
    selected = random.Random(SEED).sample(sorted(eligible, key=int), 50)
    online = [{'qid': qid, 'question': eligible[qid]} for qid in selected]
    save('ONLINE_INPUTS.json', online)
    save('SELECTION_FREEZE.json', {
        'dataset_sha256': digest(DATASET), 'population_size': len(eligible),
        'seed': SEED, 'algorithm': 'Python random.Random(seed).sample(sorted_numeric_qids, 50)',
        'sample_size': 50, 'selected_qids': selected,
        'selected_questions_sha256': digest(HERE / 'ONLINE_INPUTS.json'),
        'selection_created_before_model_calls': True})

    # Scan tracked historical metadata and run directories. This is a documented
    # discovery scan, not a claim that every possible historical use is indexed.
    paths = subprocess.check_output(['git', 'ls-files', 'experiments'], cwd=ROOT, text=True).splitlines()
    matched = {qid: [] for qid in selected}
    for rel in paths:
        if rel.startswith('experiments/bcplus_native_deepseek50/'):
            continue
        p = ROOT / rel
        if not p.is_file():
            continue
        path_ids = set(re.findall(r'(?:^|/)qid_(\d+)(?:/|$)', rel))
        found = path_ids & set(selected)
        if p.suffix in {'.json', '.jsonl'} and p.stat().st_size <= 2_000_000:
            content = p.read_text(encoding='utf-8', errors='replace')
            found |= set(re.findall(r'"(?:qid|query_id)"\s*:\s*"?(\d+)"?', content)) & set(selected)
        for qid in found:
            if len(matched[qid]) < 10:
                matched[qid].append(rel)
    save('HISTORICAL_OVERLAP.json', {
        'scope': 'git-tracked experiments paths; qid_<id> path segments and qid/query_id JSON keys in files <=2 MB',
        'selected_count': 50, 'overlap_count': sum(bool(v) for v in matched.values()),
        'overlap_qids': [qid for qid in selected if matched[qid]],
        'evidence_paths_up_to_10_per_qid': {qid: p for qid, p in matched.items() if p},
        'resampled': False})

    histories = []
    for path in (ROOT / 'experiments/runs/v000_baseline').glob('qid_*/20*/events.jsonl'):
        events = [json.loads(line) for line in path.open(encoding='utf-8')]
        histories.append({'qid': path.parts[-3].removeprefix('qid_'),
                          'api_responses': sum(e.get('kind') == 'api_response' for e in events),
                          'api_requests': sum(e.get('kind') == 'api_request' for e in events),
                          'tool_rounds': sum(e.get('kind') == 'api_response' and
                                             bool((e.get('response', {}).get('choices') or [{}])[0].get('message', {}).get('tool_calls'))
                                             for e in events)})
    stats = {}
    for field in ('api_responses', 'api_requests', 'tool_rounds'):
        vals = [r[field] for r in histories]
        stats[field] = {'mean': statistics.mean(vals), 'median': statistics.median(vals),
                        'p75': percentile(vals, 75), 'p90': percentile(vals, 90), 'max': max(vals)}
    save('CALL_ESTIMATE.json', {
        'questions': 50, 'emergency_max_tool_rounds': 200,
        'absolute_max_model_requests_per_qid': 201,
        'absolute_max_model_requests_total': 10050,
        'absolute_max_local_tool_calls_per_qid': 1600,
        'absolute_max_local_tool_calls_total': 80000,
        'semantic_retries': 0, 'sdk_retries': 0, 'sample_replacement': False,
        'historical_v000_run_count': len(histories),
        'historical_unique_qid_count': len(set(r['qid'] for r in histories)),
        'historical_stats': stats,
        'expected_model_requests_per_qid': 'roughly 11-20, extrapolated from historical median through max; exploratory only',
        'expected_model_requests_total': 'roughly 550-1000; heavy tails possible with 200-round cap',
        'caveat': 'Historical v000 used Qwen3.7-Flash and a mix of 12/64 round caps, so these are not a DeepSeek forecast.'})

    import openai
    save('MODEL_FREEZE.json', {
        'provider': 'DeepSeek', 'base_url': 'https://api.deepseek.com',
        'model': 'deepseek-flash', 'model_version_from_official_pricing_page': 'DeepSeek-V4.1-Flash',
        'temperature': 0, 'thinking': True,
        'temperature_effective': False,
        'thinking_extra_body': {'thinking': {'type': 'enabled'}},
        'timeout_seconds': 900, 'sdk': 'openai', 'sdk_version': openai.__version__,
        'max_retries': 0, 'max_tool_rounds': 200, 'max_tool_calls_per_round': 8,
        'credential_source': '.env.deepseek:DEEPSEEK_API_KEY or process environment',
        'official_model_and_pricing_url': 'https://api-docs.deepseek.com/zh-cn/quick_start/pricing/',
        'official_thinking_url': 'https://api-docs.deepseek.com/zh-cn/guides/thinking_mode/',
        'price_cny_per_million_tokens': {
            'peak': {'cache_hit_input': 0.04, 'cache_miss_input': 2.0, 'output': 8.0},
            'off_peak': {'cache_hit_input': 0.02, 'cache_miss_input': 1.0, 'output': 4.0}},
        'price_checked_date': '2026-09-28'})
    save('GRADER_SOURCE.json', {
        'upstream_commit': json.loads((ROOT / 'BCPlus/upstream.manifest.json').read_text())['revision'],
        'official_qwen_judge': 'BCPlus/upstream/scripts_evaluation/evaluate_run.py',
        'official_qwen_judge_sha256': digest(ROOT / 'BCPlus/upstream/scripts_evaluation/evaluate_run.py'),
        'official_openai_judge': 'BCPlus/upstream/scripts_evaluation/evaluate_with_openai.py',
        'official_openai_judge_sha256': digest(ROOT / 'BCPlus/upstream/scripts_evaluation/evaluate_with_openai.py'),
        'selected_primary': 'deterministic exact/entity comparison plus blinded investigator adjudication; no Qwen3-32B judge'})
    sources = ['native_agent.py', 'native_client.py', 'runner.py', 'evaluate.py',
               'test_preflight.py', 'freeze.py', 'BASELINE_AUDIT.md', 'EVALUATION_PROTOCOL.md',
               'BCPlus/scripts/search_bcplus.py']
    hashes = {}
    for name in sources:
        p = (ROOT / name) if name.startswith('BCPlus/') else (HERE / name)
        hashes[name] = digest(p)
    save('RUN_CONFIG.json', {
        'sample_size': 50, 'replicates': 1, 'workers': 50,
        'initial_api_concurrency': 50, 'max_api_concurrency': 50,
        'concurrency_change_rule': 'fixed for this frozen batch; no dynamic increase or decrease',
        'retrieval_worker_count': 1, 'retrieval_mode': 'serialized local GPU worker',
        'user_directed_full_restart_after_aborted_six_worker_batch': True,
        'restart_freeze_sha256': digest(HERE / 'RESTART_FREEZE.json'),
        'http_max_connections_per_client': 2, 'http_max_keepalive_connections_per_client': 1,
        'timeout_seconds': 900, 'sdk_max_retries': 0, 'semantic_retries': 0,
        'max_tool_rounds': 200, 'max_tool_calls_per_round': 8,
        'source_sha256': hashes,
        'retrieval_metadata_sha256': digest(ROOT / 'BCPlus/indexes/bcplus-qwen3-8b/metadata.json'),
        'created_at_utc': datetime.now(timezone.utc).isoformat()})


if __name__ == '__main__':
    main()
