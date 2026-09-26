import sys,json,sqlite3,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT));TOP=ROOT/'experiments/deferred_recovery'
from transformers import AutoTokenizer
from llm_chat.search_find_agent import SearchFindTools
from llm_chat.search_find_v3b_agent import OrthogonalSearchFindTools
from llm_chat.raw_windows import RawWindowBuilder
class FixedHit:
 def __init__(self,hit,tokenizer):self.hit=hit;self.tokenizer=tokenizer
 def search(self,query,k=5):return [self.hit]
class Spy(RawWindowBuilder):
 def __init__(self,t):super().__init__(t);self.queries=[]
 def search(self,docid,text,url,query):self.queries.append(query);return super().search(docid,text,url,query)
def main():
 out=TOP/'tool_audit/RESULTS.json';assert not out.exists()
 tok=AutoTokenizer.from_pretrained('/data/model/Qwen3-Embedding-8B',local_files_only=True,padding_side='left');db=sqlite3.connect(f"file:{ROOT/'BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite'}?mode=ro",uri=True)
 rows=[]
 for docid,q1,q2 in [('38231','Ding Junhui early life','Ding fifth 147 Players Tour Championship 2013'),('10836','You’re the Worst cast characters','num_seasons num_episodes'),('5266','Dean Dodrill gaming PC storage','animate printing paper')]:
  text,url=db.execute('select text,url from documents where docid=?',(docid,)).fetchone();hit={'docid':docid,'text':text,'url':url,'score':1.0}
  for cls in [SearchFindTools,OrthogonalSearchFindTools]:
   t=cls();t.searcher=FixedHit(hit,tok);t.window_builder=Spy(tok)
   a=t.execute('search',{'query':q1,'k':5});n=len(t.window_builder.queries);b=t.execute('search',{'query':q2,'k':5});delta=len(t.window_builder.queries)-n
   if cls==SearchFindTools:
    assert delta==1 and t.window_builder.queries[-1]==q2
    assert b['results'][0]['previously_discovered'] and b['results'][0]['preview'];assert a['results'][0]['doc_ref']==b['results'][0]['doc_ref']
   else:assert delta==0 and b['results'][0]['status']=='already_discovered' and 'preview' not in b['results'][0]
   rows.append({'implementation':cls.__name__,'docid':docid,'document_sha256':hashlib.sha256(text.encode()).hexdigest(),'old_query':q1,'new_query':q2,'local_search_calls_on_known_doc':delta,'first':a,'second':b,'audit':t.audit_record()})
 db.close();out.write_text(json.dumps({'status':'PASS','scope':'offline integration with real corpus documents, real tokenizer/localizer and a fixed global-hit fixture; tests known-hit semantics, not retriever recall','rows':rows},ensure_ascii=False,indent=2)+'\n');print('PASS: 3 real documents; v3a3/3 relocalizes, v3b3/3 preserves metadata-only')
if __name__=='__main__':main()
