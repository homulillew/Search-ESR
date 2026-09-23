"""Mechanical S2 versus scoped-Search comparison."""

from collections import Counter, defaultdict
import json

from run_scoped import CASES, HERE, STATE, checkpoint


def analyze():
    events=[json.loads(x) for x in (HERE/'events.jsonl').open()]
    by_cell=defaultdict(list)
    for e in events:
        if e.get('cell'):by_cell[e['cell']].append(e)
    rows=[]
    state=json.loads((STATE/'mechanical_summary.json').read_text())
    wanted={(c['qid'],c['seq']) for c in CASES}
    for r in state['rows']:
        if r['arm']=='S2' and (r['qid'],r['seq']) in wanted:
            rows.append({**r,'source':'reused_state_S2'})
    for cell,parts in by_cell.items():
        start=next((x for x in parts if x['kind']=='cell_start'),None)
        end=next((x for x in parts if x['kind']=='cell_end'),None)
        if start is None or end is None:continue
        qid,seq,_=cell.split(':')
        _,prior,_=checkpoint(qid,int(seq))
        seen={x['window_ref'] for x in [x['audit']['handles'] for x in prior if x['kind']=='tool_internal'][-1]['windows']}
        calls=[x for x in parts if x['kind']=='tool_start']
        results={(x['decision'],x['call_index']):x['result'] for x in parts if x['kind']=='tool_result'}
        local=[];corpus=[];new_docs=old_hits=no_gain=local_new=local_no_match=raw_chars=0
        for x in calls:
            d,i=x['decision'],x['call_index']
            n=x['name'];args=x['arguments'];r=results.get((d,i),{})
            if n=='search' and args.get('scope')=='document':
                local.append((d,i))
                if r.get('status')=='no_match':local_no_match+=1
                for m in r.get('matches',[]):
                    raw_chars+=len(m.get('text',''))
                    if m.get('window_ref') not in seen:local_new+=1
                    seen.add(m.get('window_ref'))
            elif n=='search' and args.get('scope')=='corpus':
                corpus.append((d,i))
                hits=r.get('results',[])
                old=0;raw=0
                for h in hits:
                    if h.get('status')=='already_discovered':old+=1;old_hits+=1
                    else:new_docs+=1
                    if 'preview' in h:raw+=1;raw_chars+=len(h['preview']);seen.add(h.get('preview_ref'))
                if hits and old>len(hits)/2 and raw==0:no_gain+=1
            elif n=='open':
                raw_chars+=len(r.get('text',''));seen.add(r.get('window_ref'))
        rows.append({
            'cell':cell,'qid':qid,'seq':int(seq),'arm':'SC','source':'new_scoped_call',
            'status':end['status'],'decisions':len([x for x in parts if x['kind']=='api_response']),
            'actions':[(x['name'],x['arguments'].get('scope')) for x in calls],
            'local_any':bool(local),'local_before_next_corpus':bool(local) and (not corpus or local[0]<corpus[0]),
            'local_within_1':any(d<=1 for d,_ in local),
            'local_within_2':any(d<=2 for d,_ in local),
            'local_within_3':any(d<=3 for d,_ in local),
            'local_new_windows':local_new,'local_no_match':local_no_match,
            'local_calls':len(local),'corpus_calls':len(corpus),
            'no_gain_searches':no_gain,'new_documents':new_docs,'old_document_hits':old_hits,
            'raw_chars':raw_chars,'prompt_tokens':end['prompt_tokens'],
            'total_tokens':end['total_tokens'],'elapsed_seconds':end['elapsed_seconds'],
            'undeclared_tool_calls':sum(x['kind']=='undeclared_tool_call' for x in parts),
            'invalid_tool_arguments':sum(x['kind']=='invalid_tool_arguments' for x in parts),
            'tool_errors':sum(x['kind']=='tool_error' for x in parts),
        })
    rows.sort(key=lambda r:(int(r['qid']),r['seq'],r['arm']))
    agg={}
    for arm in ('S2','SC'):
        group=[r for r in rows if r['arm']==arm]
        count=Counter()
        if arm=='S2':
            mappings={'local_any':'find_any','local_before_next_corpus':'find_before_next_search',
                      'local_within_1':'find_within_1','local_within_2':'find_within_2',
                      'local_within_3':'find_within_3','local_new_windows':'find_new_windows'}
        else:mappings={}
        keys=('local_any','local_before_next_corpus','local_within_1','local_within_2',
              'local_within_3','local_new_windows','local_no_match','local_calls',
              'corpus_calls','no_gain_searches','new_documents','old_document_hits',
              'raw_chars','prompt_tokens','total_tokens','undeclared_tool_calls',
              'invalid_tool_arguments','tool_errors')
        for r in group:
            for k in keys:count[k]+=r.get(mappings.get(k,k),0)
        agg[arm]={'n':len(group),'status':dict(Counter(r['status'] for r in group)),**dict(count)}
    output={'expected_cells':8,'completed_cells':len(rows),'rows':rows,'aggregate':agg}
    (HERE/'mechanical_summary.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    print('completed',len(rows),'/8')
    for arm,val in agg.items():print(arm,val)


if __name__=='__main__':analyze()
