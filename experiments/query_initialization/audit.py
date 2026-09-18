"""Audit plans, frozen raw-window contracts, and descriptive initialization metrics."""
import sys,json,hashlib,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from experiments.query_initialization.initializer import validate


def main():
    p=Path(sys.argv[1]).resolve();tasks={t['qid']:t for t in json.loads((p/'tasks.json').read_text())};manifest=json.loads((p/'manifest.json').read_text());reports=[];pool={}
    db=sqlite3.connect(f'file:{ROOT}/BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite?mode=ro',uri=True);cache={}
    for d in sorted(p.iterdir()):
        if not (d/'summary.json').exists():continue
        s=json.loads((d/'summary.json').read_text());obs=json.loads((d/'observations.json').read_text());trace=[json.loads(l) for l in (d/'events.jsonl').read_text().splitlines()];bundle=json.loads((d/'bundle.json').read_text())
        plan=json.loads((d/'plan.json').read_text()) if (d/'plan.json').exists() else None
        if plan and s['arm']!='A' and plan['status'] in {'valid','underfilled','no_direction'}:
            clean={'directions':[{k:x[k] for k in ['goal','source_clues','query']} for x in plan['directions']]}
            assert not validate(clean,tasks[s['qid']]['question'],2 if s['arm']=='C' else 1)
        finalized=next((e['seq'] for e in trace if e['kind']=='plan_finalized'),None)
        searches=[e for e in trace if e['kind']=='search_result'];starts=[e for e in trace if e['kind']=='search_start']
        assert all(finalized is not None and e['seq']>finalized for e in starts)
        assert not starts or max(e['seq'] for e in trace if e['kind']=='api_request')<min(e['seq'] for e in starts)
        assert [e['result'] for e in searches]==[e['result'] for e in obs]==[b['result'] for b in bundle['directions']]
        chars=tokens=0;docids=[];refs=[];fallbacks=0
        for e in searches:
            k=3 if s['arm']=='C' else 6;assert e['arguments']['k']==k and len(e['result'])<=k
            for v in e['result']:
                did=v['docid']
                if did not in cache:cache[did]=db.execute('select text,url from documents where docid=?',(did,)).fetchone()
                text,url=cache[did];assert hashlib.sha256(text.encode()).hexdigest()==v['document_sha256']
                assert v['text']==text[v['offset']:v['end_char']] and v['url']==url
                if v['title_span']:
                    a,z=v['title_span'];assert v['title']==text[a:z]
                assert v['text_tokens']+v['title_tokens']<=400
                assert v['has_more_before']==(v['offset']>0) and v['has_more_after']==(v['end_char']<len(text))
                tokens+=v['text_tokens']+v['title_tokens'];chars+=len(v['text']);docids.append(did);refs.append(v['window_ref']);fallbacks+=v['status']=='prefix_fallback'
                key=(s['qid'],did);entry=pool.setdefault(key,dict(qid=s['qid'],docid=did,title=v['title'],url=url,windows={},sessions=[]))
                entry['windows'][v['window_ref']]=v;entry['sessions'].append(dict(session=d.name,direction=e['direction'],rank=e['result'].index(v)+1))
        assert tokens<=2400
        metrics=[m for e in obs for m in e['observations']]
        row=dict(session=d.name,**s,raw_checks_passed=True,returned_windows=len(refs),distinct_documents=len(set(docids)),distinct_windows=len(set(refs)),window_tokens=tokens,body_chars=chars,overlap_chars=sum(m['body_overlap_chars'] for m in metrics),prefix_fallbacks=fallbacks,search_calls=len(starts))
        if len(searches)==2:
            ds1={v['docid'] for v in searches[0]['result']};ds2={v['docid'] for v in searches[1]['result']}
            row['second_direction_new_documents']=sorted(ds2-ds1)
        reports.append(row)
    aggregates={}
    for arm in ['A','B','C']:
        rs=[r for r in reports if r['arm']==arm]
        aggregates[arm]=dict(attempts=len(rs),complete=sum(r['status']=='complete' for r in rs),first_valid=sum(r.get('initial_valid',False) for r in rs),repairs=sum(max(0,r['api_requests']-1) for r in rs),
            statuses={st:sum(r['status']==st for r in rs) for st in sorted({r['status'] for r in rs})},
            plan_statuses={st:sum(r.get('plan_status','missing')==st for r in rs) for st in sorted({r.get('plan_status','missing') for r in rs})},
            search_calls=sum(r['search_calls'] for r in rs),returned_windows=sum(r['returned_windows'] for r in rs),window_tokens=sum(r['window_tokens'] for r in rs),fallbacks=sum(r['prefix_fallbacks'] for r in rs),
            distinct_docs_sum=sum(r['distinct_documents'] for r in rs),api_requests=sum(r['api_requests'] for r in rs),usage={k:sum(r['usage'][k] for r in rs) for k in ['prompt_tokens','completion_tokens','total_tokens']})
    (p/'audit.json').write_text(json.dumps(dict(aggregates=aggregates,sessions=reports),ensure_ascii=False,indent=2))
    pools=[]
    for entry in pool.values():entry['windows']=list(entry['windows'].values());pools.append(entry)
    (p/'review_pool.json').write_text(json.dumps(pools,ensure_ascii=False,indent=2))
    print(json.dumps(dict(sessions=len(reports),unique_question_documents=len(pool),aggregates=aggregates),ensure_ascii=False,indent=2))


if __name__=='__main__':main()
