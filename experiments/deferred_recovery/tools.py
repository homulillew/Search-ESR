"""Mechanical restore/execute only. No semantic source routing."""
import copy,hashlib,json,sqlite3,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from llm_chat.search_find_agent import SearchFindTools
from llm_chat.raw_windows import RawWindowBuilder,Window

def restore(registry,searcher):
 t=SearchFindTools();t.searcher=searcher;t.window_builder=RawWindowBuilder(searcher.tokenizer)
 db=sqlite3.connect(f"file:{ROOT/'BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite'}?mode=ro",uri=True)
 for d in registry['documents']:
  txt,url=db.execute('select text,url from documents where docid=?',(d['docid'],)).fetchone()
  key=t.window_builder.register(d['docid'],txt,url);assert key[1]==d['document_sha256'];assert t.handles.document(key)[0]==d['doc_ref']
 for w in registry['windows']:
  key=t.handles.resolve_document(w['doc_ref']);doc=t.window_builder.documents[key]
  assert doc['text'][w['offset']:w['offset']+len(w['text'])]==w['text']
  # Preserve original canonical source ref if previously emitted; otherwise restored private identity.
  raw=w.get('source_window_ref','restored_'+w['window_ref']);t.window_builder.windows[raw]=Window(key[0],key[1],w['offset'],w['offset']+len(w['text']))
  assert t.handles.window(raw)[0]==w['window_ref']
 db.close();return t

def registry(t):
 s=t.handles.snapshot();ds=[];ws=[]
 for d in s['documents']:
  k=t.handles.resolve_document(d['doc_ref']);src=t.window_builder.documents[k]
  ds.append({**d,'title':src['title'],'url':src['url']})
 for w in s['windows']:
  span=t.window_builder.windows[w['source_window_ref']];k=(span.docid,span.digest);src=t.window_builder.documents[k];txt=src['text'][span.start:span.end]
  ws.append({**w,'doc_ref':t.handles.document(k)[0],'title':src['title'],'url':src['url'],'text':txt,'offset':span.start,'text_sha256':hashlib.sha256(txt.encode()).hexdigest()})
 return {'documents':ds,'windows':ws}

def execute(t,action):
 start=time.monotonic();r={'action':action,'result':None,'observations':[],'audit':None,'error':None}
 try:
  r['result']=t.execute(action['tool'],{k:v for k,v in action.items() if k!='tool'});r['audit']=copy.deepcopy(t.audit_record());out=r['result']
  refs=([x['preview_ref'] for x in out.get('results',[])] if action['tool']=='search' else [x['window_ref'] for x in out.get('matches',[])] if action['tool']=='find' else [out['window_ref']] if out.get('text') else [])
  ws={w['window_ref']:w for w in registry(t)['windows']};r['observations']=[ws[w] for w in refs]
 except Exception as e:r['error']={'category':'tool failure','type':type(e).__name__,'message':str(e)[:1000]}
 r['elapsed_seconds']=time.monotonic()-start;return r
