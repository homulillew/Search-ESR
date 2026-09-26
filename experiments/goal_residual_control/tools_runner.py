"""Restore observed handles and execute the unchanged Orthogonal tools."""
import copy,json,sqlite3,os
from pathlib import Path
from common import ROOT,TOP,read,write,digest,now

def create_searcher():
    os.environ['BCPLUS_DEVICE']='cuda:1'
    from BCPlus.scripts.search_bcplus import BCPlusSearcher
    return BCPlusSearcher()

def restore(state,searcher):
    from llm_chat.search_find_v3b_agent import OrthogonalSearchFindTools
    from llm_chat.raw_windows import Window,RawWindowBuilder
    tools=OrthogonalSearchFindTools();tools.searcher=searcher
    tools.window_builder=RawWindowBuilder(searcher.tokenizer)
    sources=read(TOP/'bank/SOURCE_WINDOWS.json');ws=state['available_workspace']
    db=sqlite3.connect(f"{(ROOT/'BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite').as_uri()}?mode=ro",uri=True)
    for d in ws['known_documents']:
        text,url=db.execute('select text,url from documents where docid=?',(d['docid'],)).fetchone()
        key=tools._windows().register(d['docid'],text,url)
        assert tools.handles.document(key)[0]==d['doc_ref']
    for w in ws['observed_windows']:
        s=sources[w['source_id']];key=tools.handles.resolve_document(w['doc_ref'])
        assert key==(s['docid'],s['document_sha256'])
        assert tools.window_builder.documents[key]['text'][s['offset']:s['offset']+len(w['text'])]==w['text']
        raw='restored_'+w['window_ref']
        tools._windows().windows[raw]=Window(s['docid'],key[1],s['offset'],s['offset']+len(w['text']))
        assert tools.handles.window(raw)[0]==w['window_ref']
        tools.discovery_previews.setdefault(w['doc_ref'],w['window_ref'])
    db.close();return tools

def workspace(tools):
    snap=tools.handles.snapshot();docs=[];windows=[]
    for d in snap['documents']:
        key=tools.handles.resolve_document(d['doc_ref']);raw=tools.window_builder.documents[key]
        docs.append({'doc_ref':d['doc_ref'],'docid':key[0],'title':raw['title'],'url':raw['url']})
    for w in snap['windows']:
        span=tools.window_builder.windows[w['source_window_ref']];key=(span.docid,span.digest)
        dref=tools.handles.document(key)[0];doc=tools.window_builder.documents[key]
        windows.append({'window_ref':w['window_ref'],'doc_ref':dref,'title':doc['title'],'url':doc['url'],
          'text':doc['text'][span.start:span.end]})
    return {'known_documents':docs,'observed_windows':windows}

def observations(tools,action,result):
    name=action['tool']
    if name=='search':refs=[x['preview_ref'] for x in result.get('results',[]) if 'preview_ref' in x]
    elif name=='find':refs=[x['window_ref'] for x in result.get('matches',[])]
    else:refs=[result['window_ref']] if result.get('text') else []
    ws=workspace(tools);allw={w['window_ref']:w for w in ws['observed_windows']}
    return [copy.deepcopy(allw[r]) for r in refs]

def execute_batch(tools,out):
    record={'decision':out,'started_utc':now(),'actions':[],'error':None,'pre_handles':tools.handles.snapshot()}
    if not out:return {**record,'error':'upstream_model_failure'}
    if out['decision']=='stop':return record
    docs={x['doc_ref'] for x in record['pre_handles']['documents']};wins={x['window_ref'] for x in record['pre_handles']['windows']}
    for a in out['actions']:
        if a['tool']=='find' and a['doc_ref'] not in docs:record['error']='unknown_prebatch_document';return record
        if a['tool']=='open' and a['window_ref'] not in wins:record['error']='unknown_prebatch_window';return record
    for a in out['actions']:
        event={'action':a,'started_utc':now(),'result':None,'observations':[],'error':None}
        try:
            event['result']=tools.execute(a['tool'],{k:v for k,v in a.items() if k!='tool'})
            event['observations']=observations(tools,a,event['result']);event['audit']=copy.deepcopy(tools.audit_record())
        except Exception as exc:event['error']=type(exc).__name__+': '+str(exc)[:500]
        event['finished_utc']=now();record['actions'].append(event)
    record['post_handles']=tools.handles.snapshot();record['finished_utc']=now()
    return record

def run_one_step(base,states,outputs):
    base=Path(base);assert not (base/'tool_events.jsonl').exists()
    searcher=create_searcher();results=[]
    try:
        with (base/'tool_events.jsonl').open('w') as log:
            for out in outputs:
                state=states[out['case_id']];tools=restore(state,searcher)
                rec={'case_id':out['case_id'],'qid':out['qid'],'arm':out['arm']}
                log.write(json.dumps({'kind':'start',**rec,'output_hash':digest(out)},ensure_ascii=False)+'\n');log.flush()
                rec.update(execute_batch(tools,out['output']));results.append(rec)
                log.write(json.dumps({'kind':'result',**rec},ensure_ascii=False)+'\n');log.flush()
                tools.close();print(out['case_id'],out['arm'],len(rec['actions']),rec['error'],flush=True)
    finally:searcher.close()
    write(base/'outputs.json',results)

if __name__=='__main__':
    import sys
    states={s['case_id']:s for s in read(TOP/'bank/SNAPSHOTS.json')}
    run_one_step(TOP/'one_step_acquisition',states,read(TOP/'research_decision/outputs.json'))
