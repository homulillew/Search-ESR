"""Mechanical M4 relation/scope accounting with frozen semantic scores."""

import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
FIELDS = ('Evidence relation', 'Current leading candidate', 'Did the candidate change?',
          'What remains unresolved', 'Best next scope')


def parse(content):
    fields = {}
    for label in FIELDS:
        match = re.search(rf'(?im)^\s*{re.escape(label)}\s*:\s*(.*)$', content or '')
        fields[label] = match.group(1).strip() if match else ''
    relation = re.search(r'\b(supports|refutes|inconclusive|irrelevant)\b',
                         fields['Evidence relation'], re.I)
    scope = re.search(r'\b(corpus|document|window|stop)\b',
                      fields['Best next scope'], re.I)
    changed = re.search(r'\b(yes|no)\b', fields['Did the candidate change?'], re.I)
    fields['parsed_relation'] = relation.group(1).lower() if relation else None
    fields['parsed_scope'] = scope.group(1).lower() if scope else None
    fields['parsed_candidate_changed'] = changed.group(1).lower() if changed else None
    return fields


def main():
    cases = json.loads((HERE / 'cases.json').read_text())['cases']
    rubric = json.loads((HERE / 'EVALUATION_RULES.json').read_text())
    assert rubric['samples_per_case_arm_model'] == 1
    freeze = json.loads((HERE / 'freeze.json').read_text())
    models = freeze['model_order']
    events = [json.loads(x) for x in (HERE / 'events.jsonl').open()]
    responses = {x['cell']: x for x in events if x['kind'] == 'api_response'}
    errors = {x['cell']: x for x in events if x['kind'] == 'api_error'}
    score_path = HERE / 'semantic_scores.json'
    scores = json.loads(score_path.read_text()) if score_path.exists() else {}
    rows = []
    for case in cases:
        for arm in ('E0', 'E1'):
            for model in models:
                cell = f"{case['case_id']}:{arm}:{model}"
                event = responses.get(cell)
                if event:
                    choice = (event['response'].get('choices') or [{}])[0]
                    content = (choice.get('message') or {}).get('content') or ''
                    parsed = parse(content)
                    score = scores.get(cell, {}) if arm == 'E1' else {}
                    row = {'cell': cell, 'case_id': case['case_id'], 'arm': arm,
                           'model': model, 'expected_relation': case['expected_relation'],
                           'content': content, 'finish_reason': choice.get('finish_reason'),
                           **parsed,
                           'relation_accurate': parsed['parsed_relation'] == case['expected_relation']
                                                if arm == 'E1' else None,
                           'stop_calibrated': parsed['parsed_scope'] not in (None, 'stop')
                                              if arm == 'E1' else None,
                           'belief_update_correct': score.get('belief_update_correct'),
                           'unsupported_override': score.get('unsupported_override')}
                else:
                    row = {'cell': cell, 'case_id': case['case_id'], 'arm': arm,
                           'model': model, 'expected_relation': case['expected_relation'],
                           'error': errors.get(cell, {}).get('error_type', 'missing_response'),
                           'parsed_relation': None, 'parsed_scope': None,
                           'relation_accurate': None, 'stop_calibrated': None,
                           'belief_update_correct': None, 'unsupported_override': None}
                rows.append(row)
    e1_cells = {r['cell'] for r in rows if r['arm'] == 'E1' and 'content' in r}
    if set(scores) - e1_cells:
        raise ValueError('semantic scores include absent or non-E1 cells')
    for cell, score in scores.items():
        if score.get('belief_update_correct') not in (True, False) \
                or score.get('unsupported_override') not in (True, False) \
                or not score.get('reason'):
            raise ValueError(f'incomplete semantic score: {cell}')
    aggregates = {}
    for model in models:
        group = [r for r in rows if r['model'] == model and r['arm'] == 'E1']
        aggregates[model] = {
            'e1_responses': sum('content' in r for r in group),
            'e1_relation_accurate': sum(r['relation_accurate'] is True for r in group),
            'e1_belief_update_correct': sum(r['belief_update_correct'] is True for r in group),
            'e1_semantic_scored': sum(r['cell'] in scores for r in group),
            'e1_unsupported_overrides': sum(r['unsupported_override'] is True for r in group),
            'e1_stop_calibrated': sum(r['stop_calibrated'] is True for r in group),
        }
    paired = []
    for case in cases:
        for arm in ('E0', 'E1'):
            item = {'case_id': case['case_id'], 'arm': arm,
                    'expected_relation': case['expected_relation'] if arm == 'E1' else None}
            for model, label in zip(models, ('qwen', 'atria')):
                row = next(r for r in rows if r['cell'] == f"{case['case_id']}:{arm}:{model}")
                item[f'{label}_relation'] = row['parsed_relation']
                item[f'{label}_scope'] = row['parsed_scope']
                item[f'{label}_error'] = row.get('error')
            paired.append(item)
    result = {'rows': rows, 'paired': paired, 'aggregates': aggregates,
              'metric_note': 'E1 exact four-way relation; E0 descriptive; all E1 snippets are partial for full-question stop calibration'}
    (HERE / 'mechanical_summary.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'paired': paired, 'aggregates': aggregates}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
