"""Paired structural-window trial with frozen production prompts/tools."""
import hashlib,json,random,shutil,sqlite3,sys
from pathlib import Path
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor,as_completed
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from transformers import AutoTokenizer
from openai import OpenAI
from llm_chat.agent import AgentSession,BCPlusTools,AGENT_PROMPT,TOOLS
from llm_chat.client import Config
from llm_chat.raw_windows import RawWindowBuilder
from experiments.structural_boundary.candidate import TableEntryWindowBuilder
from experiments.prompt_contract.run import CASES
from experiments.run_rollout import Recorder,RecordedClient,RecordedTools

def main():
 out=ROOT/'experiments/structural_boundary/api_runs'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 frozen=json.loads((ROOT/'全链路排查报告/Search-Open冻结清单.json').read_text())
 for rel,digest in frozen['files'].items():assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==digest,rel
 cfg=Config.load();tok=AutoTokenizer.from_pretrained('/data/model/Qwen3-Embedding-8B',local_files_only=True,use_fast=True)
 builders={'baseline':RawWindowBuilder(tok),'table_entry':TableEntryWindowBuilder(tok)}
 db=sqlite3.connect(f'file:{ROOT}/BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite?mode=ro',uri=True)
 tasks=[];prepared={};repairs={}
 for case in CASES:
  t=dict(case);text,url=db.execute('select text,url from documents where docid=?',(t['docid'],)).fetchone()
  prepared[t['id']]={arm:b.search(t['docid'],text,url,t['locator_query']) for arm,b in builders.items()};repairs[t['id']]=builders['table_entry'].last_repair
  t['reference_span']=[text.index(t['needle']),text.index(t['needle'])+len(t['needle'])] if t['needle'] else None
  t['source_sha256']=hashlib.sha256(text.encode()).hexdigest();tasks.append(t)
 db.close()
 system=cfg.system_prompt+'\n\n'+AGENT_PROMPT
 manifest=dict(model=cfg.model,base_url=cfg.base_url,request_options=cfg.request_options(),system_prompts={arm:system for arm in builders},tools=TOOLS,max_tool_rounds=4,repeats=3,workers=4,order_seed=918,protocol='One fixed document per task with synthetic search history. Only structural window algorithm differs; same real API, frozen original system/tools, unchanged retrieval and Open. Later search uses arm-specific windows. Four subsequent tool-eligible rounds plus forced final. Defaults unchanged. Gold remains offline.',source_sha256={})
 for rel in ['experiments/structural_boundary/run_api.py','experiments/structural_boundary/candidate.py','experiments/structural_boundary/PLAN.md','experiments/prompt_contract/run.py','llm_chat/agent.py','llm_chat/client.py','llm_chat/raw_windows.py','llm_chat/window_locator.py','llm_chat/window_units.py','experiments/run_rollout.py','BCPlus/scripts/search_bcplus.py']:
  dest=out/'source'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/rel,dest);manifest['source_sha256'][rel]=hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()
 for name,value in [('manifest.json',manifest),('tasks.offline.json',tasks),('initial_observations.json',prepared),('repairs.json',repairs)]: (out/name).write_text(json.dumps(value,ensure_ascii=False,indent=2))
 print('OUTPUT_DIR='+str(out),flush=True)
 worker=ThreadPoolExecutor(max_workers=1);inners={arm:BCPlusTools() for arm in builders}
 for arm,b in builders.items():inners[arm].window_builder=b
 def execute(arm,name,args):
  if name=='search' and inners[arm].searcher is None:
   from BCPlus.scripts.search_bcplus import BCPlusSearcher
   searcher=BCPlusSearcher()
   for inner in inners.values():inner.searcher=searcher
  return inners[arm].execute(name,args)
 def run(t,arm,rep):
  path=out/f"{t['id']}__{arm}__r{rep}";path.mkdir();rec=Recorder(path);initial=prepared[t['id']][arm];allowed={initial['window_ref']}
  class SessionTools:
   def execute(self,name,args):
    if name=='open' and args.get('window_ref') not in allowed:raise ValueError('Window reference has not been observed in this session')
    result=worker.submit(execute,arm,name,args).result()
    for v in result if isinstance(result,list) else [result]:
     if 'window_ref' in v:allowed.add(v['window_ref'])
    return result
   def close(self):pass
  class SeedClient(RecordedClient):
   seeded=False
   def create(self,**kw):
    if not self.seeded:
     kw['messages'].extend([{'role':'assistant','content':None,'tool_calls':[{'id':'seed_search','type':'function','function':{'name':'search','arguments':json.dumps({'query':t['locator_query'],'k':1})}}]},{'role':'tool','tool_call_id':'seed_search','content':json.dumps([initial],ensure_ascii=False)}]);self.seeded=True
    return super().create(**kw)
  client=SeedClient(OpenAI(api_key=cfg.api_key,base_url=cfg.base_url,timeout=cfg.timeout,max_retries=2),rec)
  session=AgentSession(cfg,client=client,tools=RecordedTools(rec,SessionTools()),max_rounds=4)
  rec.emit('seeded_observation',result=initial,synthetic_search_history=True)
  result=dict(task=t['id'],group=t['group'],arm=arm,repeat=rep)
  try:
   answer=session.ask(t['question']);(path/'answer.md').write_text(answer);result['status']='complete'
  except Exception as e:result.update(status='error',error_type=type(e).__name__)
  finally:session.close();rec.render()
  counts={};usage={};forced=False
  for e in rec.events:
   if e['kind']=='tool_start':counts[e['name']]=counts.get(e['name'],0)+1
   if e['kind']=='api_request' and e['request']['tool_choice']=='none':forced=True
   if e['kind']=='api_response':
    for k in ['prompt_tokens','completion_tokens','total_tokens']:usage[k]=usage.get(k,0)+(e['response'].get('usage') or {}).get(k,0)
  result.update(tool_calls=counts,usage=usage,forced_final=forced);(path/'summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));return result
 jobs=[(t,a,r) for t in tasks for a in builders for r in [1,2,3]];random.Random(918).shuffle(jobs)
 (out/'job_order.json').write_text(json.dumps([[t['id'],a,r] for t,a,r in jobs],indent=2));results=[]
 try:
  with ThreadPoolExecutor(max_workers=4) as pool:
   for f in as_completed([pool.submit(run,*job) for job in jobs]):
    result=f.result();results.append(result);(out/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2));print('DONE',result,flush=True)
 finally:
  for inner in inners.values():worker.submit(inner.close).result()
  worker.shutdown()
 for rel,digest in frozen['files'].items():assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==digest,rel
 print('FINISHED',out,flush=True)
if __name__=='__main__':main()
