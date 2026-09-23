"""Mechanical M1 parsing and paired scope/target accounting.

Need and source-type semantic agreement require separate blinded review of
the verbatim outputs; this script does not pretend string overlap is meaning.
"""

import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
FIELDS = ['Current unresolved need', 'Expected source type', 'Best scope',
          'Target document/window', 'Reason']


def parse(text):
    fields = {}
    for label in FIELDS:
        pattern = rf'(?im)^\s*(?:\*\*)?{re.escape(label)}(?:\*\*)?\s*:\s*(.*)$'
        match = re.search(pattern, text or '')
        fields[label] = match.group(1).strip() if match else ''
    scope = re.search(r'\b(corpus|document|window|stop)\b',
                      fields['Best scope'], re.I)
    target = re.search(r'\b(D[1-9][0-9]*|W[1-9][0-9]*|none)\b',
                       fields['Target document/window'], re.I)
    fields['parsed_scope'] = scope.group(1).lower() if scope else None
    fields['parsed_target'] = target.group(1) if target else None
    return fields


def main():
    events = [json.loads(line) for line in (HERE/'events.jsonl').open()]
    annotation = json.loads((STUDY/'PREFIX_ONLY_ANNOTATIONS.json').read_text())
    labels = {(r['qid'],r['seq']):r for r in annotation['rows']}
    responses = {e['cell']:e for e in events if e['kind']=='api_response'}
    errors = {e['cell']:e for e in events if e['kind']=='api_error'}
    rows = []
    for q,seq in labels:
        label=labels[(q,seq)]
        for model in ('qwen3.7-flash','Atria-Dawn-Preview'):
            cell=f'{q}:{seq}:{model}'
            response=responses.get(cell)
            if response:
                raw=response['response']; choice=(raw.get('choices') or [{}])[0]
                content=(choice.get('message') or {}).get('content') or ''
                parsed=parse(content)
                scope=parsed['parsed_scope'];target=parsed['parsed_target']
                row={'cell':cell,'qid':q,'seq':seq,'model':model,
                     'finish_reason':choice.get('finish_reason'), 'content':content,
                     **parsed,
                     'scope_compatible':scope in label['acceptable_scopes'] if scope else False,
                     'target_compatible':target in label['plausible_document_refs']
                         if scope=='document' else None,
                     'over_search':scope=='corpus' and 'corpus' not in label['acceptable_scopes'],
                     'premature_local':scope in {'document','window'} and label['acceptable_scopes']==['corpus'],
                     'need_agreement':None,'source_type_agreement':None}
            else:
                row={'cell':cell,'qid':q,'seq':seq,'model':model,
                     'error':errors.get(cell,{}).get('error_type','missing_response'),
                     'scope_compatible':False,'need_agreement':None,'source_type_agreement':None}
            rows.append(row)
    aggregates={model:{'responses':sum('content' in r for r in rows if r['model']==model),
                       'scope_compatible':sum(r['scope_compatible'] for r in rows if r['model']==model),
                       'document_plans':sum(r.get('parsed_scope')=='document' for r in rows if r['model']==model),
                       'over_search':sum(r.get('over_search',False) for r in rows if r['model']==model),
                       'premature_local':sum(r.get('premature_local',False) for r in rows if r['model']==model)}
                for model in ('qwen3.7-flash','Atria-Dawn-Preview')}
    paired=[]
    for q,seq in labels:
        a,b=[next(r for r in rows if r['cell']==f'{q}:{seq}:{model}')
             for model in ('qwen3.7-flash','Atria-Dawn-Preview')]
        paired.append({'qid':q,'seq':seq,'acceptable_scopes':labels[(q,seq)]['acceptable_scopes'],
                       'qwen_scope':a.get('parsed_scope'),'atria_scope':b.get('parsed_scope'),
                       'qwen_compatible':a['scope_compatible'],
                       'atria_compatible':b['scope_compatible']})
    doc={'completed_cells':len(responses),'error_cells':list(errors),
         'rows':rows,'paired':paired,'aggregates':aggregates,
         'semantic_scoring':'need_agreement/source_type_agreement require independent review'}
    (HERE/'mechanical_summary.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'completed_cells':len(responses),'errors':len(errors),
                      'aggregates':aggregates,'paired':paired},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
