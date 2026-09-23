"""Mechanical S0/S1/S2 summaries; semantic usefulness requires separate review."""

from collections import Counter, defaultdict
import json

from run_state import CASES, HERE, ORTH, checkpoint


def analyze():
    events = [json.loads(x) for x in (HERE / 'events.jsonl').open()]
    by_cell = defaultdict(list)
    for e in events:
        if e.get('cell'):
            by_cell[e['cell']].append(e)
    rows = []
    orth = json.loads((ORTH / 'mechanical_summary.json').read_text())
    wanted = {(c['qid'], c['seq']) for c in CASES}
    for r in orth['rows']:
        if r['arm'] == 'P1' and (r['qid'], r['seq']) in wanted:
            rows.append({**r, 'arm': 'S0', 'source': 'reused_orthogonal_P1'})
    for cell, parts in by_cell.items():
        start = next((x for x in parts if x['kind']=='cell_start'), None)
        end = next((x for x in parts if x['kind']=='cell_end'), None)
        if start is None or end is None: continue
        qid, seq, arm = cell.split(':')
        _, prior, _ = checkpoint(qid, int(seq))
        seen = {x['window_ref'] for x in [x['audit']['handles'] for x in prior if x['kind']=='tool_internal'][-1]['windows']}
        calls = [(x['decision'],x['call_index'],x['name']) for x in parts if x['kind']=='tool_start']
        results = {(x['decision'],x['call_index']):x['result'] for x in parts if x['kind']=='tool_result'}
        find_decisions = [d for d,_,n in calls if n=='find']
        first_find = next((i for i,(_,_,n) in enumerate(calls) if n=='find'), None)
        first_search = next((i for i,(_,_,n) in enumerate(calls) if n=='search'), None)
        no_gain = []
        old_hits = new_docs = find_new = old_new_search = raw_chars = 0
        for d,i,n in calls:
            result = results.get((d,i),{})
            if n=='search':
                hits = result.get('results',[])
                old = 0; new_raw = 0
                for hit in hits:
                    if hit.get('status')=='already_discovered': old += 1; old_hits += 1
                    else: new_docs += 1
                    if 'preview' in hit:
                        new_raw += 1; raw_chars += len(hit['preview'])
                        if hit.get('status')=='already_discovered' and hit.get('preview_ref') not in seen:
                            old_new_search += 1
                        seen.add(hit.get('preview_ref'))
                if hits and old > len(hits)/2 and not new_raw: no_gain.append((d,i))
            elif n=='find':
                for hit in result.get('matches',[]):
                    raw_chars += len(hit.get('text',''))
                    if hit.get('window_ref') not in seen: find_new += 1
                    seen.add(hit.get('window_ref'))
            elif n=='open':
                raw_chars += len(result.get('text',''))
                seen.add(result.get('window_ref'))
        rows.append({
            'cell':cell, 'qid':qid, 'seq':int(seq), 'arm':arm, 'source':'new_state_call',
            'status':end['status'], 'decisions':len([x for x in parts if x['kind']=='api_response']),
            'actions':[n for _,_,n in calls],
            'find_any':bool(find_decisions),
            'find_before_next_search':first_find is not None and (first_search is None or first_find < first_search),
            'find_within_1':any(d<=1 for d in find_decisions),
            'find_within_2':any(d<=2 for d in find_decisions),
            'find_within_3':any(d<=3 for d in find_decisions),
            'find_new_windows':find_new, 'no_gain_searches':len(no_gain),
            'find_within_2_after_no_gain':any(any(d < fd <= d+2 for fd in find_decisions) for d,_ in no_gain),
            'search_again_after_no_gain':any(any((sd,si)>(d,i) and n=='search' for sd,si,n in calls) for d,i in no_gain),
            'new_documents':new_docs, 'old_document_hits':old_hits,
            'old_document_new_search_windows':old_new_search,
            'raw_chars':raw_chars, 'prompt_tokens':end['prompt_tokens'],
            'total_tokens':end['total_tokens'], 'elapsed_seconds':end['elapsed_seconds'],
            'undeclared_tool_calls':sum(x['kind']=='undeclared_tool_call' for x in parts),
            'tool_errors':sum(x['kind']=='tool_error' for x in parts),
        })
    rows.sort(key=lambda r:(int(r['qid']),r['seq'],r['arm']))
    aggregate = {}
    for arm in ('S0','S1','S2'):
        group = [r for r in rows if r['arm']==arm]
        sums = Counter()
        for r in group:
            for key in ('find_any','find_before_next_search','find_within_1','find_within_2',
                        'find_within_3','find_new_windows','no_gain_searches',
                        'find_within_2_after_no_gain','search_again_after_no_gain',
                        'new_documents','old_document_hits','old_document_new_search_windows',
                        'raw_chars','prompt_tokens','total_tokens','undeclared_tool_calls','tool_errors'):
                sums[key] += r.get(key,0)
        aggregate[arm] = {'n':len(group),'status':dict(Counter(r['status'] for r in group)),**dict(sums)}
    output = {'expected_cells':12,'completed_cells':len(rows),'rows':rows,'aggregate':aggregate}
    (HERE / 'mechanical_summary.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    print('completed',len(rows),'/12')
    for arm, val in aggregate.items(): print(arm,val)


if __name__=='__main__': analyze()
