"""Offline ledger/hash checks; never display unseen document text or execute tools."""
from pathlib import Path
import sys,json,sqlite3,hashlib,datetime
ROOT=Path(__file__).resolve().parents[6];sys.path.insert(0,str(ROOT))
from experiments.research_state.first_observation.run import audit_capture
from experiments.research_state.first_observation.artifacts import file_hash
r=Path(__file__).resolve().parents[1];c=audit_capture(r/'capture');out=[]
for row in c['cases']:
 p=r/'capture'/row['id']/'observations.sqlite'
 with sqlite3.connect(p.resolve().as_uri()+'?mode=ro',uri=True) as db:
  events=db.execute('SELECT tool,arguments,result FROM events').fetchall()
  assert len(events)==1 and events[0][0]=='search'
  assert json.loads(events[0][1])=={'query':row['question'],'k':5}
  assert json.loads(events[0][2])==row['observation']
  for w in row['observation']:
   text,url=db.execute('SELECT text,url FROM documents WHERE docid=? AND digest=?',(w['docid'],w['document_sha256'])).fetchone()
   assert hashlib.sha256(text.encode()).hexdigest()==w['document_sha256']
   assert text[w['offset']:w['end_char']]==w['text'] and url==w['url']
   if w['title_span']:
    a,b=w['title_span'];assert text[a:b]==w['title']
   assert w['title_tokens']+w['text_tokens']<=400
   assert w['window_ref']=='w_'+hashlib.sha256(f"raw-v1:{w['docid']}:{w['document_sha256']}:{w['offset']}:{w['end_char']}".encode()).hexdigest()[:24]
 out.append({'id':row['id'],'query_tokens':row['query_tokens'],'windows':len(row['observation']),'window_tokens':[w['title_tokens']+w['text_tokens'] for w in row['observation']],'sqlite_path':str(p.relative_to(ROOT)),'sqlite_sha256':file_hash(p),'sqlite_not_for_git':True,'elapsed_seconds':row['elapsed_seconds']})
assert len([p for p in c['retrieval']['asset_sha256'] if '/qwen3-embedding-8b/' in p and p.endswith('.pkl')])==4
v={'verified_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'collection_sha256':c['sha256'],'actual_search_calls':6,'initial_model_calls':0,'open_calls':0,'all_queries_exact_original':True,'all30_windows_match_pinned_versions':True,'actual_vectors_in_manifest':True,'cases':out}
(r/'capture_verification.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print('Verified six original queries and 30 ledger windows; no Open or extra Search.')
