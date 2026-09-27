"""Offline, conservative project scoring after all 50 frozen trajectories end."""
from collections import Counter
from datetime import datetime
import json
import math
from pathlib import Path
import re
import statistics
import unicodedata
from zoneinfo import ZoneInfo

from .runner import HERE, ROOT, read_json, write_json


def normalize(text):
    text = unicodedata.normalize('NFKC', text).casefold().strip()
    text = re.sub(r'[\u2010-\u2015]', '-', text)
    text = re.sub(r'[^\w\s-]', ' ', text, flags=re.UNICODE)
    return ' '.join(text.split())


def answer_candidate(answer):
    """A deliberately narrow extraction, fixed before seeing model answers."""
    text = answer.strip()
    text = re.sub(r'^#{1,6}\s*', '', text)
    text = re.sub(r'^\*\*(?:answer|final answer)\*\*\s*:\s*', '', text, flags=re.I)
    text = re.sub(r'^(?:answer|final answer)\s*:\s*', '', text, flags=re.I)
    text = re.sub(r'^(?:the answer is|it was|it is)\s+', '', text, flags=re.I)
    text = text.split('\n', 1)[0]
    text = re.sub(r'\s*(?:\[\d+\]|\([^)]*https?://[^)]*\)|https?://\S+)\s*$', '', text)
    text = text.strip(' `*.,;:')
    return text


def exact_score(answer, gold):
    candidate = answer_candidate(answer)
    return bool(candidate and normalize(candidate) == normalize(gold))


def primary_correct(status, answer, gold):
    return status != 'RUN_FAILED' and exact_score(answer, gold)


def insufficient_evidence_answer(answer):
    return bool(re.search(r'\b(?:insufficient evidence|cannot determine|could not (?:find|verify|establish)|corpus does not establish|unable to determine)\b',
                          answer, re.I))


def percentile(values, p):
    if not values:
        return None
    values = sorted(values)
    x = (len(values) - 1) * p / 100
    lo = int(x)
    return values[lo] + (values[min(lo + 1, len(values) - 1)] - values[lo]) * (x - lo)


def distribution(values):
    if not values:
        return None
    return {'total': sum(values), 'mean': statistics.mean(values),
            'median': statistics.median(values),
            'p25': percentile(values, 25), 'p75': percentile(values, 75),
            'p90': percentile(values, 90), 'p95': percentile(values, 95), 'max': max(values)}


def wilson(correct, total, z=1.959963984540054):
    p = correct / total
    den = 1 + z * z / total
    mid = (p + z * z / (2 * total)) / den
    radius = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / den
    return [0.0 if correct == 0 else max(0.0, mid - radius),
            1.0 if correct == total else min(1.0, mid + radius)]


def estimate_cost(events):
    total = 0.0
    priced = 0
    missing = 0
    for event in events:
        if event['kind'] != 'api_response':
            continue
        usage = event['response'].get('usage') or {}
        hit = usage.get('prompt_cache_hit_tokens')
        miss = usage.get('prompt_cache_miss_tokens')
        out = usage.get('completion_tokens')
        inp = usage.get('prompt_tokens')
        if not all(isinstance(n, int) for n in (hit, miss, out, inp)) or hit + miss != inp:
            missing += 1
            continue
        local = datetime.fromisoformat(event['time_utc']).astimezone(ZoneInfo('Asia/Shanghai'))
        peak = local.weekday() < 5 and (9 <= local.hour < 12 or 14 <= local.hour < 18)
        rates = (0.04, 2.0, 8.0) if peak else (0.02, 1.0, 4.0)
        total += (hit * rates[0] + miss * rates[1] + out * rates[2]) / 1_000_000
        priced += 1
    return {'estimated_cny': total, 'priced_responses': priced, 'unpriced_responses': missing,
            'billed_amount_known': False}


def diagnostic(events, gold, answer):
    results = [e['result'] for e in events if e['kind'] == 'tool_result']
    observations = [d for r in results for d in (r if isinstance(r, list) else [r]) if isinstance(d, dict)]
    observed_ids = {str(d['docid']) for d in observations if d.get('docid') is not None}
    observed_urls = {str(d['url']) for d in observations if d.get('url')}
    gold_seen = any(normalize(gold) in normalize(d.get('text', '')) for d in observations if d.get('text'))
    answer_urls = set(re.findall(r'https?://[^\s)\]>]+', answer))
    cited_ids = {qid for qid in observed_ids if re.search(r'(?<!\w)' + re.escape(qid) + r'(?!\w)', answer)}
    explicit_ids = set(re.findall(r'(?:docid|document\s*id)\s*[:=#]?\s*([\w.-]+)', answer, re.I))
    return {'gold_answer_string_observed': gold_seen,
            'gold_string_heuristic_only': True,
            'answer_contains_citation': bool(answer_urls or cited_ids or explicit_ids),
            'cited_observed_docids': sorted(cited_ids),
            'cited_observed_urls': sorted(answer_urls & observed_urls),
            'invented_explicit_docids': sorted(explicit_ids - observed_ids),
            'invented_urls': sorted(answer_urls - observed_urls)}


def api_concurrency_points(events):
    pending = None
    points = []
    for event in events:
        if event['kind'] == 'api_request':
            pending = datetime.fromisoformat(event['time_utc'])
        elif event['kind'] in {'api_response', 'api_error'} and pending is not None:
            points.extend([(pending, 1), (datetime.fromisoformat(event['time_utc']), -1)])
            pending = None
    return points


def main():
    run_root = HERE / 'runs'
    end = json.loads((run_root / 'BATCH_END.json').read_text(encoding='utf-8'))
    batch = run_root / end['batch_id']
    selection = read_json('SELECTION_FREEZE.json')
    dirs = {p.name.removeprefix('qid_'): p for p in batch.glob('qid_*')}
    if set(dirs) != set(selection['selected_qids']) or len(end['results']) != 50:
        raise ValueError('All 50 online outcomes must exist before loading gold')
    for path in dirs.values():
        if not (path / 'summary.json').exists() or not (path / 'events.jsonl').exists():
            raise ValueError('Incomplete online records; do not load gold')
    # Gold is first loaded here, after completeness checks.
    dataset = {str(r['query_id']): r for line in (ROOT / 'BCPlus/data/bcplus/qa.jsonl').open(encoding='utf-8')
               if (r := json.loads(line))}
    rows = []
    adjudication = []
    all_events = []
    concurrency_points = []
    for qid in selection['selected_qids']:
        directory = dirs[qid]
        item = dataset[qid]
        answer = (directory / 'answer.md').read_text(encoding='utf-8').strip()
        summary = json.loads((directory / 'summary.json').read_text(encoding='utf-8'))
        events = [json.loads(x) for x in (directory / 'events.jsonl').open(encoding='utf-8')]
        all_events.extend(events)
        concurrency_points.extend(api_concurrency_points(events))
        correct = primary_correct(summary['status'], answer, item['answer'])
        diag = diagnostic(events, item['answer'], answer)
        if answer and not correct and summary['status'] != 'RUN_FAILED':
            # No trajectory, arm, or qid appears in reviewer cards.
            adjudication.append({'question': item['query'], 'gold_answer': item['answer'],
                                 'model_final_answer': answer, 'decision': None})
        rows.append({'qid': qid, 'question': item['query'], 'gold_answer': item['answer'],
                     'model_final_answer': answer, 'correct_deterministic': correct,
                     'status': summary['status'], 'summary': summary, 'diagnostic': diag,
                     'cost': estimate_cost(events)})
    write_json(HERE / 'PER_QUESTION.json', rows)
    write_json(HERE / 'MANUAL_ADJUDICATION_QUEUE.json', adjudication)
    n = len(rows)
    correct = sum(r['correct_deterministic'] for r in rows)
    statuses = Counter(r['status'] for r in rows)
    fields = ['search_calls', 'get_document_calls', 'total_tool_calls', 'unique_docids',
              'unique_search_queries', 'exact_duplicate_queries', 'repeated_document_reads',
              'tool_round_count', 'model_response_count', 'api_requests', 'prompt_tokens',
              'completion_tokens', 'total_tokens', 'elapsed_seconds']
    dist = {field: distribution([r['summary'][field] for r in rows]) for field in fields}
    api_latency = distribution([latency for r in rows for latency in r['summary']['api_latency_seconds']])
    observed = [r for r in rows if r['diagnostic']['gold_answer_string_observed']]
    concurrent = peak = 0
    for _, change in sorted(concurrency_points, key=lambda x: (x[0], x[1])):
        concurrent += change
        peak = max(peak, concurrent)
    natural = [r for r in rows if r['status'] == 'natural_answer']
    forced = [r for r in rows if r['status'] == 'emergency_cap_forced_answer']
    summary = {
        'branch': 'experiment/bcplus-native-deepseek50-baseline',
        'benchmark': 'BrowseComp-Plus', 'model': 'deepseek-flash',
        'baseline_policy': 'native v000 Search + GetDocument with documented transport changes',
        'selection_seed': selection['seed'], 'sample_size': n,
        'score_kind': 'conservative project deterministic exact/entity score; not official Qwen3-32B judge',
        'correct': correct, 'accuracy': correct / n, 'wilson_95': wilson(correct, n),
        'statuses': statuses, 'distributions': dist, 'api_latency_seconds': api_latency,
        'peak_api_concurrency': peak,
        'insufficient_evidence_answers': sum(insufficient_evidence_answer(r['model_final_answer']) for r in rows),
        'natural_answer_accuracy': {'correct': sum(r['correct_deterministic'] for r in natural), 'denominator': len(natural)},
        'completed_run_accuracy': {'correct': sum(r['correct_deterministic'] for r in natural + forced),
                                   'denominator': len(natural) + len(forced)},
        'emergency_cap_forced_accuracy': {'correct': sum(r['correct_deterministic'] for r in forced),
                                          'denominator': len(forced)},
        'get_document_adoption': sum(r['summary']['get_document_calls'] >= 1 for r in rows),
        'search_only_answers': sum(bool(r['model_final_answer']) and r['summary']['get_document_calls'] == 0 for r in rows),
        'repeated_search_trajectories': sum(r['summary']['exact_duplicate_queries'] > 0 for r in rows),
        'rounds_gt_12': sum(r['summary']['tool_round_count'] > 12 for r in rows),
        'rounds_gt_25': sum(r['summary']['tool_round_count'] > 25 for r in rows),
        'rounds_gt_50': sum(r['summary']['tool_round_count'] > 50 for r in rows),
        'rounds_gt_100': sum(r['summary']['tool_round_count'] > 100 for r in rows),
        'gold_string_observed_count': len(observed),
        'correct_given_gold_string_observed': sum(r['correct_deterministic'] for r in observed),
        'answers_with_citation': sum(r['diagnostic']['answer_contains_citation'] for r in rows),
        'answers_with_invented_url': sum(bool(r['diagnostic']['invented_urls']) for r in rows),
        'answers_with_invented_explicit_docid': sum(bool(r['diagnostic']['invented_explicit_docids']) for r in rows),
        'cache_hit_tokens': sum(r['summary']['cache_hit_tokens'] for r in rows),
        'cache_input_tokens': sum(r['summary']['cache_input_tokens'] for r in rows),
        'cache_usage_missing_or_inconsistent_records': sum(r['summary']['cache_usage_missing_or_inconsistent_records'] for r in rows),
        'estimated_cost_cny': sum(r['cost']['estimated_cny'] for r in rows),
        'cost_unpriced_responses': sum(r['cost']['unpriced_responses'] for r in rows),
        'billed_amount_known': False,
        'adjudication_queue_count': len(adjudication),
        'sample_replacement': False, 'sdk_retries': 0}
    summary['cache_hit_rate'] = (summary['cache_hit_tokens'] / summary['cache_input_tokens']
                                 if summary['cache_input_tokens'] else None)
    ci = summary['wilson_95']
    batch_manifest = json.loads((run_root / 'BATCH_MANIFEST.json').read_text(encoding='utf-8'))
    start = datetime.fromisoformat(batch_manifest['started_at_utc'])
    stop = datetime.fromisoformat(end['completed_at_utc'])
    summary['total_wall_clock_seconds'] = (stop - start).total_seconds()
    write_json(HERE / 'RESULTS.json', summary)
    head = f"""# BC+ Random50 Comparison Set — native baseline

Branch: {summary['branch']}
Commit: {batch_manifest.get('git_commit', 'see frozen run manifest')}

Model: DeepSeek Flash (`deepseek-flash`)
Benchmark: BrowseComp-Plus
Baseline policy: native v000 Search + GetDocument
Sampling: random frozen 50; seed = {selection['seed']}

Correct: {correct} / 50
Accuracy: {100*correct/n:.1f}% (conservative project score; official judge unavailable)
95% Wilson CI: [{100*ci[0]:.1f}%, {100*ci[1]:.1f}%]

Natural answers: {statuses['natural_answer']} / 50
Emergency-cap-forced answers: {statuses['emergency_cap_forced_answer']} / 50
Run/API failures: {statuses['RUN_FAILED']} / 50
Insufficient-evidence answers: {summary['insufficient_evidence_answers']} / 50 (explicit phrase heuristic)

GetDocument adoption: {summary['get_document_adoption']} / 50
Search calls: {dist['search_calls']['total']} total; median {dist['search_calls']['median']}; p90 {dist['search_calls']['p90']}; max {dist['search_calls']['max']}
GetDocument calls: {dist['get_document_calls']['total']} total; median {dist['get_document_calls']['median']}; p90 {dist['get_document_calls']['p90']}; max {dist['get_document_calls']['max']}
Search-only answers: {summary['search_only_answers']} / 50
Repeated Search trajectories: {summary['repeated_search_trajectories']} / 50
Rounds >12: {summary['rounds_gt_12']} / 50
Rounds >25: {summary['rounds_gt_25']} / 50
Rounds >50: {summary['rounds_gt_50']} / 50
Rounds >100: {summary['rounds_gt_100']} / 50
Gold-string observed: {len(observed)} / 50 (heuristic only)
Correct given observed: {summary['correct_given_gold_string_observed']} / {len(observed)}
Median/p90/max tool rounds: {dist['tool_round_count']['median']} / {dist['tool_round_count']['p90']} / {dist['tool_round_count']['max']}
Total model requests: {dist['api_requests']['total']}
Total prompt/completion tokens: {dist['prompt_tokens']['total']} / {dist['completion_tokens']['total']}
Total wall-clock seconds: {summary['total_wall_clock_seconds']:.1f}
Estimated cost: ¥{summary['estimated_cost_cny']:.4f}; unpriced responses: {summary['cost_unpriced_responses']}

The 50 qids are now the BC+ Random50 Comparison Set and are no longer fresh. Later comparisons must account for model, tools, prompt, termination cap, tokens and cost; a paired system difference alone does not isolate recoverability.
"""
    (HERE / 'RESULTS.md').write_text(head, encoding='utf-8')
    (HERE / 'TOOL_BEHAVIOR.md').write_text('# Tool behavior\n\n' + json.dumps({k: dist[k] for k in fields[:8]}, indent=2) + '\n', encoding='utf-8')
    (HERE / 'COST_AND_LATENCY.md').write_text('# Cost and latency\n\n' + json.dumps({**{k: dist[k] for k in fields[8:]}, 'api_latency_seconds': api_latency}, indent=2) + '\n\nTotal wall-clock seconds: ' + str(summary['total_wall_clock_seconds']) + '\nEstimated cost CNY: ' + str(summary['estimated_cost_cny']) + '\n', encoding='utf-8')
    failure_labels = {
        'run_or_api_failure': statuses['RUN_FAILED'],
        'gold_string_not_observed_heuristic': sum(not r['diagnostic']['gold_answer_string_observed'] and not r['correct_deterministic'] for r in rows),
        'gold_string_observed_but_answer_wrong': sum(r['diagnostic']['gold_answer_string_observed'] and not r['correct_deterministic'] for r in rows),
        'search_repetition': sum(r['summary']['exact_duplicate_queries'] > 0 and not r['correct_deterministic'] for r in rows),
        'document_not_read': sum(r['summary']['get_document_calls'] == 0 and not r['correct_deterministic'] for r in rows),
        'very_long_trajectory_gt_50_rounds': sum(r['summary']['tool_round_count'] > 50 and not r['correct_deterministic'] for r in rows),
        'emergency_cap_reached': sum(r['status'] == 'emergency_cap_forced_answer' and not r['correct_deterministic'] for r in rows),
        'explicit_insufficient_evidence': sum(insufficient_evidence_answer(r['model_final_answer']) and not r['correct_deterministic'] for r in rows),
    }
    (HERE / 'FAILURE_BREAKDOWN.md').write_text('# Failure breakdown\n\nMechanically identifiable, overlapping post-hoc labels:\n\n' + json.dumps(failure_labels, indent=2) + '\n\nCandidate fixation, premature answer, conflicting evidence, and other causal labels require separate qualitative review. These labels do not change accuracy.\n', encoding='utf-8')


if __name__ == '__main__':
    main()
