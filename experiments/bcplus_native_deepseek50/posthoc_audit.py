"""Read-only audit of the completed restart; does not change online data or scores."""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

from .evaluate import estimate_cost, percentile
from .runner import HERE, ROOT, read_json, sha, write_json


def observed_documents(events):
    for event in events:
        if event['kind'] != 'tool_result':
            continue
        result = event['result']
        for item in result if isinstance(result, list) else [result]:
            if isinstance(item, dict):
                yield item


def answer_urls(answer):
    urls = set()
    for raw in re.findall(r'https?://[^\s<>]+', answer):
        value = raw.rstrip('.,;]>:')
        while value.endswith(')') and value.count(')') > value.count('('):
            value = value[:-1]
        urls.add(value)
    return urls


def url_key(value):
    parts = urlsplit(value)
    return parts.netloc.lower(), unquote(parts.path).rstrip('/')


def load_events(directory):
    return [json.loads(line) for line in (directory / 'events.jsonl').open(encoding='utf-8')]


def main():
    selection = read_json('SELECTION_FREEZE.json')
    config = read_json('RUN_CONFIG.json')
    model = read_json('MODEL_FREEZE.json')
    end = json.loads((HERE / 'runs/BATCH_END.json').read_text(encoding='utf-8'))
    batch = HERE / 'runs' / end['batch_id']
    qids = selection['selected_qids']
    assert len(qids) == len(set(qids)) == 50
    assert {p.name.removeprefix('qid_') for p in batch.glob('qid_*')} == set(qids)
    assert sha(ROOT / 'BCPlus/data/bcplus/qa.jsonl') == selection['dataset_sha256']
    assert sha(HERE / 'ONLINE_INPUTS.json') == selection['selected_questions_sha256']
    for name, expected in config['source_sha256'].items():
        path = ROOT / name if name.startswith('BCPlus/') else HERE / name
        assert sha(path) == expected, name
    usage_complete = usage_bad = 0
    request_count = response_count = tool_errors = api_errors = 0
    response_models = Counter()
    unsupported = []
    citations = []
    all_tool_latency = {'search': [], 'get_document': []}
    for qid in qids:
        directory = batch / f'qid_{qid}'
        manifest = json.loads((directory / 'manifest.json').read_text(encoding='utf-8'))
        inp = json.loads((directory / 'input.json').read_text(encoding='utf-8'))
        summary = json.loads((directory / 'summary.json').read_text(encoding='utf-8'))
        assert set(inp) == {'qid', 'question'} and inp['qid'] == qid
        assert manifest['sdk_max_retries'] == 0 and manifest['max_tool_rounds'] == 200
        assert manifest['model'] == model['model'] and manifest['request_options'] == {
            'temperature': 0, 'extra_body': model['thinking_extra_body']}
        assert summary['status'] in {'natural_answer', 'emergency_cap_forced_answer', 'RUN_FAILED'}
        events = load_events(directory)
        answer = (directory / 'answer.md').read_text(encoding='utf-8')
        docs = list(observed_documents(events))
        observed_urls = {url_key(d['url']) for d in docs if d.get('url')}
        urls = answer_urls(answer)
        unmatched = sorted(u for u in urls if url_key(u) not in observed_urls)
        citations.append({'qid': qid, 'answer_url_count': len(urls),
                          'url_matches_observed': len(urls) - len(unmatched),
                          'unmatched_urls': unmatched})
        for event in events:
            kind = event['kind']
            if kind == 'api_request':
                request_count += 1
                req = event['request']
                if (req['model'] != model['model'] or req['temperature'] != 0
                        or req['extra_body'] != model['thinking_extra_body']
                        or req['tool_choice'] not in {'auto', 'none'}):
                    unsupported.append({'qid': qid, 'seq': event['seq'], 'kind': 'request_mismatch'})
            elif kind == 'api_response':
                response_count += 1
                response_models[event['response'].get('model')] += 1
                usage = event['response'].get('usage') or {}
                hit, miss, inp_tokens = (usage.get('prompt_cache_hit_tokens'),
                                         usage.get('prompt_cache_miss_tokens'), usage.get('prompt_tokens'))
                if all(isinstance(x, int) for x in (hit, miss, inp_tokens)) and hit + miss == inp_tokens:
                    usage_complete += 1
                else:
                    usage_bad += 1
            elif kind == 'tool_error':
                tool_errors += 1
            elif kind == 'api_error':
                api_errors += 1
            elif kind == 'tool_result' and event['name'] in all_tool_latency:
                all_tool_latency[event['name']].append(event['elapsed_seconds'])
    latency = {name: {'count': len(vals), 'median': percentile(vals, 50),
                      'p90': percentile(vals, 90), 'p95': percentile(vals, 95), 'max': max(vals)}
               for name, vals in all_tool_latency.items()}
    old_dir = HERE / 'runs' / read_json('RESTART_FREEZE.json')['aborted_batch_id']
    old = json.loads((old_dir / 'ABORTED.json').read_text(encoding='utf-8'))
    old_events = [event for directory in old_dir.glob('qid_*')
                  for event in load_events(directory)]
    old_cost = estimate_cost(old_events)
    integrity = {
        'formal_batch_id': end['batch_id'], 'formal_qid_count': len(qids),
        'formal_api_requests': request_count, 'formal_api_responses': response_count,
        'response_model_counts': response_models,
        'thinking_enabled_all_requests': not unsupported,
        'request_mismatches': unsupported,
        'source_hashes_match_freeze': True, 'dataset_and_selection_hashes_match': True,
        'gold_absent_from_online_input_fields': True,
        'sdk_retries': 0, 'formal_api_errors': api_errors, 'formal_tool_errors': tool_errors,
        'cache_usage_complete_records': usage_complete,
        'cache_usage_missing_or_inconsistent_records': usage_bad,
        'tool_latency_seconds': latency,
        'aborted_batch_id': old['batch_id'],
        'aborted_recorded_api_requests': old['recorded_api_requests'],
        'aborted_recorded_api_responses': old['recorded_api_responses'],
        'aborted_estimated_cost_cny': old_cost['estimated_cny'],
        'aborted_cost_unpriced_responses': old_cost['unpriced_responses'],
        'aborted_excluded_from_primary': True,
    }
    write_json(HERE / 'INTEGRITY_AUDIT.json', integrity)
    citation_summary = {
        'method': 'Extract full visible HTTP(S) URLs, trim enclosing Markdown punctuation, compare normalized host and decoded path to observed tool-result URL metadata. Exact query/fragment not required.',
        'formal_answer_count': len(citations),
        'answers_with_at_least_one_url': sum(c['answer_url_count'] > 0 for c in citations),
        'answers_with_unmatched_url': sum(bool(c['unmatched_urls']) for c in citations),
        'unmatched_url_count': sum(len(c['unmatched_urls']) for c in citations),
        'unmatched': [c for c in citations if c['unmatched_urls']],
        'note': 'Unmatched means the exact normalized citation URL was not observed as tool metadata; it does not by itself prove fabrication. This supersedes the first-pass regex count in RESULTS.json.'}
    write_json(HERE / 'CITATION_AUDIT.json', citation_summary)
    files = []
    for path in (HERE / 'runs/BATCH_MANIFEST.json', HERE / 'runs/BATCH_END.json'):
        files.append({'path': str(path.relative_to(ROOT)), 'bytes': path.stat().st_size,
                      'sha256': sha(path)})
    for directory in (old_dir, batch):
        for path in sorted(directory.rglob('*')):
            if path.is_file():
                files.append({'path': str(path.relative_to(ROOT)), 'bytes': path.stat().st_size,
                              'sha256': sha(path)})
    write_json(HERE / 'RUN_ARCHIVE_MANIFEST.json', {
        'batch_ids': [old_dir.name, batch.name],
        'raw_file_count': len(files), 'raw_total_bytes': sum(f['bytes'] for f in files),
        'files': files})


if __name__ == '__main__':
    main()
