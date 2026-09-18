"""Mechanical checks and descriptive paired metrics, without model-based grading."""
import sys,json,hashlib,re,copy,random
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from transformers import AutoTokenizer
from experiments.observation_summary.summary import build_summary,PREFIX


def main():
    p=Path(sys.argv[1]).resolve();tok=AutoTokenizer.from_pretrained('/data/model/Qwen3-Embedding-8B',local_files_only=True)
    manifest=json.loads((p/'manifest.json').read_text());tasks={t['id']:t for t in json.loads((p/'tasks.json').read_text())}
    controls={t['id']:t for t in json.loads((p/'controls.offline.json').read_text())}
    reports=[];reviews=[];source_cache={}
    import sqlite3
    db=sqlite3.connect(f'file:{ROOT}/BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite?mode=ro',uri=True)
    for d in sorted(p.iterdir()):
        if not (d/'summary.json').exists():continue
        s=json.loads((d/'summary.json').read_text());obs=json.loads((d/'observations.json').read_text());trace=[json.loads(l) for l in (d/'events.jsonl').read_text().splitlines()]
        request_tools={};previous_seq=0;summary_tokens=[];injected_tokens=[];summary_message=None
        for e in trace:
            if e['kind']=='observation_summary':
                subset=[dict(v,active=True) for v in obs if v['sequence']<=e['through_sequence']]
                expected=build_summary(subset,e['after_sequence'],tok)
                assert expected==e['message'] and e['after_sequence']==previous_seq
                previous_seq=e['through_sequence'];summary_message=expected
                if expected:summary_tokens.append(len(tok.encode(expected['content'],add_special_tokens=False)))
            if e['kind']=='api_request':
                r=e['request'];assert r['messages'][0]['content']==manifest['system'] and r['tools']==manifest['tools']
                assert r['max_tokens']==2048 and r['model']==manifest['model']
                injected=[m for m in r['messages'] if isinstance(m.get('content'),str) and m['content'].startswith(PREFIX)]
                assert injected==([summary_message] if s['arm']=='visible' and summary_message else [])
                if injected:injected_tokens.append(len(tok.encode(injected[0]['content'],add_special_tokens=False)))
                for m in r['messages']:
                    if m['role']=='tool':request_tools[m['tool_call_id']]=json.loads(m['content'])
        assert list(request_tools.values())==[e['result'] for e in obs]
        windows=[];refs=set()
        for e in obs:
            for v in e['result'] if isinstance(e['result'],list) else [e['result']]:
                if 'window_ref' not in v:continue
                did=v['docid']
                if did not in source_cache:source_cache[did]=db.execute('select text from documents where docid=?',(did,)).fetchone()[0]
                text=source_cache[did];assert hashlib.sha256(text.encode()).hexdigest()==v['document_sha256']
                assert text[v['offset']:v['end_char']]==v['text']
                if v['parent_window_ref']:assert v['parent_window_ref'] in refs
                refs.add(v['window_ref']);windows.append(v)
        after=[e for e in obs if e['sequence']>s['seed_sequence']]
        searches=[e for e in after if e['tool']=='search'];opens=[e for e in after if e['tool']=='open']
        zero=lambda e:sum(v['new_chars'] for v in e['observations'])==0
        streak=0;max_streak=0;pairs=0
        for e in after:
            if e['tool']=='search' and zero(e):
                streak+=1;max_streak=max(max_streak,streak);pairs+=streak>=2
            else:streak=0
        metrics=[m for e in after for m in e['observations']]
        body_total=sum(m['body_overlap_chars']+sum(z-a for a,z in m['body_new_spans']) for m in metrics)
        row=dict(session=d.name,task=s['task'],kind=s['kind'],arm=s['arm'],repeat=s['repeat'],status=s['status'],error_type=s.get('error_type'),
            search=len(searches),open=len(opens),zero_new_search=sum(zero(e) for e in searches),zero_search_pairs=pairs,max_zero_search_streak=max_streak,
            returned_windows=len(metrics),repeat_windows=sum(m['repeated_window'] for m in metrics),body_chars=body_total,
            body_overlap_chars=sum(m['body_overlap_chars'] for m in metrics),new_source_chars=sum(m['new_chars'] for m in metrics),
            forced_final=s['forced_final'],usage=s['usage'],summary_tokens_injected=sum(injected_tokens),max_summary_tokens=max(summary_tokens,default=0),
            tool_errors=sum(e['kind']=='tool_error' for e in trace),raw_and_payload_checks_passed=True)
        if (d/'answer.md').exists():
            answer=(d/'answer.md').read_text();cited=re.findall(r'w_[0-9a-f]{24}',answer)
            row.update(citations=len(cited),invalid_citations=[x for x in cited if x not in refs])
            if s['task'] in controls:
                c=controls[s['task']];a,z=c['reference_span']
                row['reference_observed']=any(v['docid']==c['docid'] and v['offset']<=a and v['end_char']>=z for v in windows)
                row['answer_contains_expected_literal']=c['expected'].replace(' ','').lower() in answer.replace(' ','').lower()
                reviews.append(dict(session=d.name,kind=s['kind'],answer=answer,expected=c['expected'],reference_observed=row['reference_observed']))
        reports.append(row)
    def aggregate(rows):
        result=dict(sessions=len(rows),completed=sum(r['status']=='complete' for r in rows),errors=[dict(session=r['session'],error_type=r['error_type']) for r in rows if r['status']!='complete'])
        for key in ['search','open','zero_new_search','zero_search_pairs','returned_windows','repeat_windows','body_chars','body_overlap_chars','new_source_chars','summary_tokens_injected','tool_errors']:
            result[key]=sum(r[key] for r in rows)
        result['forced_final']=sum(r['forced_final'] for r in rows)
        result['usage']={k:sum(r['usage'][k] for r in rows) for k in ['prompt_tokens','completion_tokens','total_tokens']}
        result['zero_new_search_rate']=result['zero_new_search']/result['search'] if result['search'] else None
        result['body_overlap_rate']=result['body_overlap_chars']/result['body_chars'] if result['body_chars'] else None
        return result
    agg={}
    for scope in ['natural','controls']:
        for arm in ['hidden','visible']:
            rows=[r for r in reports if (r['kind']=='natural')==(scope=='natural') and r['arm']==arm]
            agg[scope+'_'+arm]=aggregate(rows)
    pairs=[]
    for t in tasks:
        for rep in [1,2]:
            pair=[r for r in reports if r['task']==t and r['repeat']==rep]
            if len(pair)==2:
                a=next(r for r in pair if r['arm']=='hidden');b=next(r for r in pair if r['arm']=='visible')
                pairs.append(dict(task=t,kind=a['kind'],repeat=rep,both_complete=a['status']==b['status']=='complete',hidden=a,visible=b))
    complete_natural=[q for q in pairs if q['kind']=='natural' and q['both_complete']]
    agg['complete_natural_pairs']={arm:aggregate([q[arm] for q in complete_natural]) for arm in ['hidden','visible']}
    (p/'audit.json').write_text(json.dumps(dict(sessions=reports,aggregates=agg,pairs=pairs),ensure_ascii=False,indent=2))
    random.Random(2209).shuffle(reviews);key={};blind=[]
    for i,r in enumerate(reviews,1):
        label=f'R{i:02}';key[label]=r['session'];blind.append(dict(id=label,**{k:v for k,v in r.items() if k!='session'}))
    (p/'review_blinded.json').write_text(json.dumps(blind,ensure_ascii=False,indent=2));(p/'review_key.json').write_text(json.dumps(key,indent=2))
    print(json.dumps(agg,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
