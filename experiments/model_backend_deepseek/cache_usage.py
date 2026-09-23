"""Extract and aggregate DeepSeek's response-reported prompt cache usage."""

import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
MODEL = 'deepseek-flash'
STAGE_FILES = {
    'M0': HERE / 'protocol_events.jsonl',
    'M1': HERE / 'planning_probe/events.jsonl',
    'M2': HERE / 'natural_action_probe/events.jsonl',
    'M3': HERE / 'orthogonal_partial/events.jsonl',
    'M4': HERE / 'evidence_update/events.jsonl',
    'M5': HERE / 'deepseek_native/events.jsonl',
}


def extract(raw):
    usage = raw.get('usage') or {}
    hit = usage.get('prompt_cache_hit_tokens')
    miss = usage.get('prompt_cache_miss_tokens')
    prompt = usage.get('prompt_tokens')
    result = {'prompt_tokens': prompt, 'prompt_cache_hit_tokens': hit,
              'prompt_cache_miss_tokens': miss,
              'reported_cached_tokens': (usage.get('prompt_tokens_details') or {}).get('cached_tokens')}
    if not all(isinstance(x, int) and not isinstance(x, bool) and x >= 0
               for x in (hit, miss)):
        result.update(status='missing_hit_or_miss', hit_rate=None)
    elif prompt is not None and prompt != hit + miss:
        result.update(status='inconsistent_prompt_total', hit_rate=None)
    else:
        result.update(status='reported', hit_rate=hit / (hit + miss) if hit + miss else None)
    return result


def summarize(stages=None):
    selected = stages or list(STAGE_FILES)
    by_stage = {}
    for stage in selected:
        path = STAGE_FILES[stage]
        if not path.exists():
            continue
        responses = []
        errors = 0
        for line in path.open():
            event = json.loads(line)
            if event.get('kind') in ('response', 'api_response'):
                raw = event.get('response') or {}
                if raw.get('model') != MODEL:
                    continue
                cache = extract(raw)
                responses.append({'cell': event.get('cell') or event.get('label'),
                                  'cache': cache})
            elif event.get('kind') == 'api_error':
                cell = event.get('cell', '')
                if cell.endswith(':' + MODEL) or stage == 'M0':
                    errors += 1
        reported = [r['cache'] for r in responses if r['cache']['status'] == 'reported']
        hit = sum(r['prompt_cache_hit_tokens'] for r in reported)
        miss = sum(r['prompt_cache_miss_tokens'] for r in reported)
        by_stage[stage] = {'responses': len(responses), 'api_errors': errors,
                           'usage_reported': len(reported),
                           'usage_unavailable': len(responses) - len(reported),
                           'prompt_cache_hit_tokens': hit,
                           'prompt_cache_miss_tokens': miss,
                           'weighted_hit_rate': hit / (hit + miss) if hit + miss else None,
                           'per_response': responses}
    hit = sum(x['prompt_cache_hit_tokens'] for x in by_stage.values())
    miss = sum(x['prompt_cache_miss_tokens'] for x in by_stage.values())
    return {'model': MODEL,
            'definition': 'sum(hit tokens) / sum(hit tokens + miss tokens) over responses with consistent reported usage',
            'stages': by_stage,
            'all_stages': {'responses': sum(x['responses'] for x in by_stage.values()),
                           'api_errors': sum(x['api_errors'] for x in by_stage.values()),
                           'usage_reported': sum(x['usage_reported'] for x in by_stage.values()),
                           'usage_unavailable': sum(x['usage_unavailable'] for x in by_stage.values()),
                           'prompt_cache_hit_tokens': hit,
                           'prompt_cache_miss_tokens': miss,
                           'weighted_hit_rate': hit / (hit + miss) if hit + miss else None}}


if __name__ == '__main__':
    selected = sys.argv[1:] or None
    summary = summarize(selected)
    (HERE / 'CACHE_USAGE.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(summary['all_stages'], ensure_ascii=False))
