"""New-question short trajectories with durable observations in both arms."""
import sys,json,random,sqlite3,hashlib,shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from llm_chat.client import Config
from llm_chat.agent import TOOLS,AGENT_PROMPT
from llm_chat.observed_agent import ObservedAgentSession
from llm_chat.raw_windows import RawWindowBuilder
from llm_chat.structural_windows import TableEntryWindowBuilder
from experiments.run_rollout import Recorder,RecordedClient
from transformers import AutoTokenizer
from openai import OpenAI
source=Path(sys.argv[1]).resolve();out=source/'live';out.mkdir();cfg=Config.load();tok=AutoTokenizer.from_pretrained('/data/model/Qwen3-Embedding-8B',local_files_only=True)
tasks=json.loads((source/'queries.json').read_text())[:6]
manifest=dict(scope='First six preselected new BC+ questions, 2 window arms, no outcome selection, one repeat. Seed first real query and its top5 returned windows. Four subsequent tool rounds plus forced final; not full BC+ accuracy evaluation. ObservationStore enabled in both arms and invisible to model. Subsequent searches real. No gold provided.',model=cfg.model,base_url=cfg.base_url,request_options=cfg.request_options(),system=cfg.system_prompt+'\n\n'+AGENT_PROMPT,tools=TOOLS,source_sha256={})
for rel in ['experiments/observation_state/run_live.py','llm_chat/observations.py','llm_chat/observed_agent.py','llm_chat/structural_windows.py','llm_chat/agent.py','llm_chat/raw_windows.py','llm_chat/window_locator.py','llm_chat/window_units.py']:
 dest=out/'source'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/rel,dest);manifest['source_sha256'][rel]=hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2));(out/'tasks.json').write_text(json.dumps(tasks,ensure_ascii=False,indent=2));print('OUTPUT_DIR='+str(out),flush=True)
worker=ThreadPoolExecutor(max_workers=1);holder={}
def search(q,k):
 if 'searcher' not in holder:
  from BCPlus.scripts.search_bcplus import BCPlusSearcher
  holder['searcher']=BCPlusSearcher()
 return holder['searcher'].search(q,k)
class SearchProxy:
 def search(self,q,k):return worker.submit(search,q,k).result()

def run(t,arm):
 p=out/f'qid_{t["qid"]}__{arm}';p.mkdir();rec=Recorder(p)
 initial=json.loads((source/('qid_'+t['qid'])/('baseline.json' if arm=='baseline' else 'candidate.json')).read_text())
 class SeedClient(RecordedClient):
  seeded=False
  def create(self,**kw):
   if not self.seeded:
    kw['messages'].extend([{'role':'assistant','content':None,'tool_calls':[{'id':'seed_search','type':'function','function':{'name':'search','arguments':json.dumps({'query':t['query'],'k':5})}}]},{'role':'tool','tool_call_id':'seed_search','content':json.dumps(initial,ensure_ascii=False)}]);self.seeded=True
   return super().create(**kw)
 client=SeedClient(OpenAI(api_key=cfg.api_key,base_url=cfg.base_url,timeout=cfg.timeout,max_retries=2),rec)
 session=ObservedAgentSession(cfg,state_path=p/'observations.sqlite',variant=arm,client=client,max_rounds=4)
 b=RawWindowBuilder(tok) if arm=='baseline' else TableEntryWindowBuilder(tok);session.tools.window_builder=b;session.tools.searcher=SearchProxy()
 db=sqlite3.connect(f'file:{ROOT}/BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite?mode=ro',uri=True)
 for v in initial:
  text,url=db.execute('select text,url from documents where docid=?',(v['docid'],)).fetchone();key=b.register(v['docid'],text,url);assert b._emit(key,v['offset'],v['end_char'])['window_ref']==v['window_ref']
 db.close();session.observations.record('seed_search',{'query':t['query'],'k':5},initial,b);rec.emit('seeded_observation',result=initial)
 result=dict(qid=t['qid'],arm=arm)
 try:
  answer=session.ask(t['question']);(p/'answer.md').write_text(answer);result['status']='complete'
 except Exception as e:result.update(status='error',error_type=type(e).__name__)
 events=session.observations.events();(p/'observations.json').write_text(json.dumps(events,ensure_ascii=False,indent=2));result['observations']=session.observations.summary()
 calls={};usage={};forced=False
 for e in events:
  if e['tool']!='seed_search':calls[e['tool']]=calls.get(e['tool'],0)+1
 for e in rec.events:
  if e['kind']=='api_request' and e['request']['tool_choice']=='none':forced=True
  if e['kind']=='api_response':
   for k in ['prompt_tokens','completion_tokens','total_tokens']:usage[k]=usage.get(k,0)+(e['response'].get('usage') or {}).get(k,0)
 result.update(tool_calls=calls,usage=usage,forced_final=forced)
 refs=[v for e in events if e['active'] for v in (e['result'] if isinstance(e['result'],list) else [e['result']]) if 'window_ref' in v]
 probe=next((v for v in refs if v['has_more_after']),refs[0]) if refs else None
 expected=b.open(probe['window_ref'],'after') if probe else None
 session.close();rec.render()
 if result['status']=='complete' and probe:
  # New store + builder, pinned source lookup; no API or retrieval call for recovery.
  resumed=ObservedAgentSession(cfg,state_path=p/'observations.sqlite',client=OpenAI(api_key=cfg.api_key,base_url=cfg.base_url,timeout=cfg.timeout),max_rounds=4)
  resumed.tools.window_builder=RawWindowBuilder(tok) if arm=='baseline' else TableEntryWindowBuilder(tok)
  actual=resumed.tools.execute('open',{'window_ref':probe['window_ref'],'direction':'after'})
  assert actual==expected
  (p/'recovery.json').write_text(json.dumps(dict(ref=probe['window_ref'],matches_before_restart=True,result=actual,summary=resumed.observations.summary()),ensure_ascii=False,indent=2));resumed.close();result['recovery_passed']=True
 (p/'summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));return result
jobs=[(t,a) for t in tasks for a in ['baseline','table_entry']];random.Random(919).shuffle(jobs);results=[]
try:
 with ThreadPoolExecutor(max_workers=4) as pool:
  for f in as_completed([pool.submit(run,*job) for job in jobs]):
   r=f.result();results.append(r);(out/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2));print('DONE',r,flush=True)
finally:worker.shutdown()
print('FINISHED',out,flush=True)
