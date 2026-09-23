"""Combine completed alias cells while preserving the interrupted attempt separately."""

from collections import Counter,defaultdict
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
STATE=HERE.parent/'verification_state'
ORIGINAL=HERE/'events.jsonl'
RESUME=HERE/'events_resume.jsonl'


def analyze():
    original=[json.loads(x) for x in ORIGINAL.open()]
    resumed=[json.loads(x) for x in RESUME.open()]
    completed_original={e['cell'] for e in original if e['kind']=='cell_end'}
    completed_resume={e['cell'] for e in resumed if e['kind']=='cell_end'}
    assert completed_original=={'546:9:AL','1094:69:AL'}
    assert completed_resume=={'1094:77:AL','1094:93:AL'}
    selected=[e for e in original if e.get('cell') in completed_original]
    selected.extend(e for e in resumed if e.get('cell') in completed_resume)
    by_cell=defaultdict(list)
    for e in selected:by_cell[e['cell']].append(e)
    rows=[]
    for cell,parts in by_cell.items():
        end=next(e for e in parts if e['kind']=='cell_end')
        starts=[e for e in parts if e['kind']=='cell_start']
        assert len(starts)==1
        calls=[e for e in parts if e['kind']=='tool_start']
        results={(e['decision'],e['call_index']):e['result'] for e in parts if e['kind']=='tool_result'}
        locals_=[e for e in calls if e['name']=='search_document']
        searches=[e for e in calls if e['name']=='search']
        new_windows=local_no_match=old_hits=new_docs=0
        for e in calls:
            r=results.get((e['decision'],e['call_index']),{})
            if e['name']=='search_document':
                if r.get('status')=='no_match':local_no_match+=1
                new_windows+=len(r.get('matches',[]))
            if e['name']=='search':
                for hit in r.get('results',[]):
                    if hit.get('status')=='already_discovered':old_hits+=1
                    else:new_docs+=1
        first_local=next((i for i,e in enumerate(calls) if e['name']=='search_document'),None)
        first_search=next((i for i,e in enumerate(calls) if e['name']=='search'),None)
        qid,seq,_=cell.split(':')
        rows.append({
            'cell':cell,'qid':qid,'seq':int(seq),'status':end['status'],
            'actions':[e['name'] for e in calls],
            'local_any':bool(locals_),
            'local_before_next_search':first_local is not None and (first_search is None or first_local<first_search),
            'local_calls':len(locals_),'local_returns':new_windows,
            'local_no_match':local_no_match,'search_calls':len(searches),
            'old_document_hits':old_hits,'new_documents':new_docs,
            'undeclared_tool_calls':sum(e['kind']=='undeclared_tool_call' for e in parts),
            'invalid_tool_arguments':sum(e['kind']=='invalid_tool_arguments' for e in parts),
            'prompt_tokens':end['prompt_tokens'],'total_tokens':end['total_tokens'],
            'elapsed_seconds':end['elapsed_seconds'],
            'event_file':'original' if cell in completed_original else 'resume',
        })
    rows.sort(key=lambda r:(int(r['qid']),r['seq']))
    sums=Counter()
    for r in rows:
        for key in ('local_any','local_before_next_search','local_calls','local_returns',
                    'local_no_match','search_calls','old_document_hits','new_documents',
                    'undeclared_tool_calls','invalid_tool_arguments','prompt_tokens','total_tokens'):
            sums[key]+=r[key]
    state=json.loads((STATE/'mechanical_summary.json').read_text())
    s2=[r for r in state['rows'] if r['arm']=='S2']
    output={
        'completed_cells':len(rows),'interrupted_attempts':1,
        'interrupted_cell':'1094:77:AL',
        'rows':rows,'aggregate':{'n':len(rows),'status':dict(Counter(r['status'] for r in rows)),**dict(sums)},
        's2_reference':{
            'n':len(s2),'find_cells':sum(r['find_any'] for r in s2),
            'find_new_windows':sum(r['find_new_windows'] for r in s2),
            'prompt_tokens':sum(r['prompt_tokens'] for r in s2),
        },
    }
    (HERE/'mechanical_summary.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    print('completed',len(rows),'/4; interrupted attempt retained')
    print(output['aggregate'])
    for r in rows:print(r['cell'],r['status'],r['actions'])


if __name__=='__main__':analyze()
