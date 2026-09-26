"""Read-only restore audit using local tokenizer, no model or tool execution."""
from types import SimpleNamespace
from runtime import *
from tools_runner import restore,workspace

def run():
    from transformers import AutoTokenizer
    searcher=SimpleNamespace(tokenizer=AutoTokenizer.from_pretrained('/data/model/Qwen3-Embedding-8B',local_files_only=True,padding_side='left'))
    rows=[]
    for state in read(TOP/'bank/SNAPSHOTS.json'):
        tools=restore(state,searcher);after=workspace(tools);before=state['available_workspace']
        assert [(x['doc_ref'],x['docid']) for x in after['known_documents']]==[(x['doc_ref'],x['docid']) for x in before['known_documents']]
        assert [(x['window_ref'],x['doc_ref'],x['text']) for x in after['observed_windows']]==[(x['window_ref'],x['doc_ref'],x['text']) for x in before['observed_windows']]
        rows.append({'case_id':state['case_id'],'documents':len(after['known_documents']),'windows':len(after['observed_windows']),'exact_text_and_handles':True})
        tools.close()
    print(json.dumps({'all_pass':True,'snapshots':len(rows),'model_calls':0,'tool_calls':0}))
    return rows

if __name__=='__main__':run()
