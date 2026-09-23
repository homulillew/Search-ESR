"""Mechanical same-prefix M2 planning-to-action accounting."""

import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent


def main():
    frozen = json.loads((HERE / 'freeze.json').read_text())
    m1 = json.loads((STUDY / 'planning_probe/mechanical_summary.json').read_text())
    planning = {r['cell']: r for r in m1['rows']}
    events = [json.loads(line) for line in (HERE / 'events.jsonl').open()]
    responses = {e['cell']: e for e in events if e['kind'] == 'api_response'}
    errors = {e['cell']: e for e in events if e['kind'] == 'api_error'}
    rows = []
    for qid, seq in frozen['selection']:
        for model in (frozen['qwen_model'], frozen['atria_model']):
            cell = f'{qid}:{seq}:{model}'
            event = responses.get(cell)
            planned = planning[cell].get('parsed_scope')
            if event:
                name = event['action']
                action_scope = {'search': 'corpus', 'find': 'document',
                                'open': 'window', 'stop': 'stop'}.get(name)
                calls = event.get('parsed_calls') or []
                target = (calls[0]['arguments'].get('doc_ref') if name == 'find'
                          else calls[0]['arguments'].get('window_ref') if name == 'open'
                          else None)
                row = {'qid': qid, 'seq': seq, 'model': model, 'cell': cell,
                       'planning_scope': planned, 'action': name,
                       'action_scope': action_scope, 'target_ref': target,
                       'validation': event['validation'],
                       'raw_finish_reason': event['raw_finish_reason'],
                       'scope_realized': planned == 'document' and name == 'find',
                       'policy_realization_failure': planned == 'document' and name == 'search'}
            else:
                row = {'qid': qid, 'seq': seq, 'model': model, 'cell': cell,
                       'planning_scope': planned, 'action': 'api_error',
                       'action_scope': None, 'target_ref': None,
                       'validation': errors.get(cell, {}).get('error_type', 'missing'),
                       'scope_realized': False, 'policy_realization_failure': False}
            rows.append(row)
    aggregates = {}
    for model in (frozen['qwen_model'], frozen['atria_model']):
        group = [r for r in rows if r['model'] == model]
        doc_plans = [r for r in group if r['planning_scope'] == 'document']
        aggregates[model] = {
            'cells': len(group), 'actions': dict(Counter(r['action'] for r in group)),
            'document_plan_count': len(doc_plans),
            'document_scope_realized': sum(r['scope_realized'] for r in doc_plans),
            'document_to_search_failures': sum(r['policy_realization_failure'] for r in doc_plans),
        }
    paired = []
    for qid, seq in frozen['selection']:
        q, a = (next(r for r in rows if r['cell'] == f'{qid}:{seq}:{model}')
                for model in (frozen['qwen_model'], frozen['atria_model']))
        paired.append({'qid': qid, 'seq': seq,
                       'qwen_planning_scope': q['planning_scope'], 'qwen_action': q['action'],
                       'atria_planning_scope': a['planning_scope'], 'atria_action': a['action']})
    result = {'selection_rule': frozen['selection_rule'], 'rows': rows,
              'paired': paired, 'aggregates': aggregates,
              'scope_realization_denominator': 'M1 document plans among M2 selected cells',
              'policy_realization_failure': 'M1 document plan followed by single valid search'}
    (HERE / 'mechanical_summary.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'paired': paired, 'aggregates': aggregates}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
