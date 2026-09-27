"""Frozen evaluation-only known-source diagnostic. No model requests or repair."""
import os,time
from concurrent.futures import ThreadPoolExecutor,as_completed
from .common import *
from .bootstrap_runtime import audit
D=P/'analysis/oracle_diagnostic'
def freeze():
 refs={r['case_id']:r for r in read(P/'e0_reference/ACCESSIBILITY_REFERENCE.json')['rows']}
 qs={'G10':'Alka Marwaha associate professor University of Delhi The Secret World of Vipassana and Mathematics', 'G20':'Europa Universalis IV Rights of Man release date 11 October 2016'}
 rows=[{'case_id':cid,'query':q,'known_docid':refs[cid]['source']['docid'],'known_source_sha256':refs[cid]['source']['document_sha256']} for cid,q in qs.items()]
 assert all(r['real_no_gain'] for r in read(P/'e2b_escalation/METRICS.json')['rows'])
 write(D/'SCHEDULE.json',rows)
 write(D/'FREEZE.json',{'head_before_seal':git('rev-parse','HEAD'),'purpose':'Evaluation-only: known-source anchor queries test access upper bound; cannot rescue P0/P1/E2B evidence or enter any model input. Known-document preview uses same query/localizer independently of ranking.','max_searches':2,'max_known_document_previews':2,'model_calls':0,'max_retries':0,'files':{rel(p):sha(p) for p in [P/'oracle_diagnostic.py',D/'SCHEDULE.json',P/'e2_bootstrap/BACKEND.json',P/'e2b_escalation/METRICS.json',P/'e0_reference/ACCESSIBILITY_REFERENCE.json']}})
def run():
 head=audit('e2b_escalation');committed(D/'FREEZE.json')
 for p,h in read(D/'FREEZE.json')['files'].items():assert sha(ROOT/p)==h,p;committed(ROOT/p)
 write(D/'RUN.json',{'head':head,'freeze_sha256':sha(D/'FREEZE.json')});os.environ['BCPLUS_DEVICE']='cuda:1'
 import faiss;faiss.omp_set_num_threads(1)
 from BCPlus.scripts.search_bcplus import BCPlusSearcher
 from experiments.evidence_scope_localization.runtime import LockedModel,SearchProxy
 from experiments.deferred_recovery.tools import restore,registry,execute
 from llm_chat.raw_windows import RawWindowBuilder
 shared=BCPlusSearcher();shared.model=LockedModel(shared.model)
 def one(j):
  proxy=SearchProxy(shared);t=restore({'documents':[],'windows':[]},proxy);r={**j,'tool':None,'known_document_preview':None,'error':None}
  try:
   write(D/(j['case_id']+'.attempt.json'),{'query':j['query'],'k':5});r['tool']=execute(t,{'tool':'search','query':j['query'],'k':5});r['registry']=registry(t)
   txt,url=proxy.db.execute('select text,url from documents where docid=?',(j['known_docid'],)).fetchone();assert hashlib.sha256(txt.encode()).hexdigest()==j['known_source_sha256']
   builder=RawWindowBuilder(proxy.tokenizer);r['known_document_preview']=builder.search(j['known_docid'],txt,url,j['query'])
  except Exception as e:r['error']={'type':type(e).__name__,'message':str(e)[:500]}
  finally:t.close();proxy.close()
  write(D/(j['case_id']+'.json'),r);return r
 try:
  with ThreadPoolExecutor(max_workers=2) as pool:rows=[f.result() for f in as_completed([pool.submit(one,j) for j in read(D/'SCHEDULE.json')])]
 finally:shared.close()
 write(D/'COMPLETED.json',{'searches':2,'known_source_previews':2,'model_calls':0,'errors':sum(bool(r['error']) or bool(r['tool']['error']) for r in rows)})
if __name__=='__main__':
 import sys
 globals()[sys.argv[1]]()
