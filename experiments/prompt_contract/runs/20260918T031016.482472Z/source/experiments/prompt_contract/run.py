"""Paired seeded-observation trial; only the system reading contract varies."""
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
from experiments.run_batch import SharedTools
from experiments.run_rollout import Recorder,RecordedClient,RecordedTools

CONTRACT='''When a returned document is relevant but the requested detail is not in the current window, consider reading that document further before reformulating the search or concluding that the detail is unavailable. A relevant section heading, table header, or unfinished passage near a window boundary is a reason to inspect the adjacent source text with open. Use search when you need other documents or a different information target. If the visible text already supports the answer, answer without opening merely to satisfy a workflow. Distinguish a detail not seen in the current window from a detail absent from the document.'''
CASES=[
 dict(id='role_gardener',docid='67431',locator_query='Peter King role in The Constant Gardener',question='What character did the Kenyan actor Peter King (Peter Nzioki) play in The Constant Gardener?',group='detail_missing',needle='| 2005 | The Constant Gardener | Policeman 1 |'),
 dict(id='role_estate',docid='67431',locator_query='Peter King role in The Fifth Estate',question='What character did the Kenyan actor Peter King (Peter Nzioki) play in The Fifth Estate?',group='detail_missing',needle='| 2013 | The Fifth Estate | Oscar Kamau Kingara |'),
 dict(id='birth',docid='67431',locator_query='Peter King birth date',question='What birth date does the provided Wikipedia source give for the Kenyan actor Peter King Nzioki?',group='sufficient',needle='birth_date: 25 May 1978'),
 dict(id='riise',docid='23800',locator_query='2005 Champions League final Riise free kick end of extra time',question="What happened to John Arne Riise's free kick at the end of extra time in the 2005 Champions League final?",group='sufficient',needle="John Arne Riise's free kick was blocked"),
 dict(id='poker',docid='85213',locator_query='Gromenkova final opponent 2008 Ladies event',question='Who was Svetlana Gromenkova\'s final opponent in the 2008 WSOP Ladies event?',group='sufficient',needle='Californian poker pro Anh Le'),
 dict(id='full_mismatch',docid='39918',locator_query='early 21st century football final 95th minute free kick player',question='Does the supplied document itself identify a player who took a free kick in the 95th minute of a football final? If so, give the name; otherwise explain what this document establishes.',group='complete_insufficient',needle=None),
]

def main():
 out=ROOT/'experiments/prompt_contract/runs'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 frozen=json.loads((ROOT/'全链路排查报告/Search-Open冻结清单.json').read_text())
 for rel,digest in frozen['files'].items():assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==digest,rel
 cfg=Config.load();tok=AutoTokenizer.from_pretrained('/data/model/Qwen3-Embedding-8B',local_files_only=True,use_fast=True);builder=RawWindowBuilder(tok)
 db=sqlite3.connect(f'file:{ROOT}/BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite?mode=ro',uri=True)
 tasks=[];prepared={}
 for case in CASES:
  t=dict(case);text,url=db.execute('select text,url from documents where docid=?',(t['docid'],)).fetchone();obs=builder.search(t['docid'],text,url,t['locator_query'])
  t['reference_span']=[text.index(t['needle']),text.index(t['needle'])+len(t['needle'])] if t['needle'] else None
  t['source_sha256']=hashlib.sha256(text.encode()).hexdigest();t['initial_ref']=obs['window_ref'];tasks.append(t);prepared[t['id']]=obs
 db.close()
 baseline=cfg.system_prompt+'\n\n'+AGENT_PROMPT
 variant=baseline+'\n\n'+CONTRACT
 manifest=dict(model=cfg.model,base_url=cfg.base_url,request_options=cfg.request_options(),system_prompts=dict(baseline=baseline,reading_contract=variant),tools=TOOLS,max_tool_rounds=4,repeats=3,workers=4,order_seed=918,protocol='Synthetic search history containing one genuine frozen-builder observation. All arms/repeats see identical initial source. No seed search cost/recall claim. Subsequent search is real full-corpus search; open is unchanged. Same real AgentSession loop, 4 tool-eligible rounds + forced final, not a 64-round rollout. Sampling defaults unchanged. No gold in online messages. Only system prompt varies.',frozen_files_verified=True,source_sha256={})
 for rel in ['experiments/prompt_contract/run.py','llm_chat/agent.py','llm_chat/client.py','llm_chat/raw_windows.py','llm_chat/window_locator.py','llm_chat/window_units.py','experiments/run_batch.py','experiments/run_rollout.py','BCPlus/scripts/search_bcplus.py']:
  dest=out/'source'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/rel,dest);manifest['source_sha256'][rel]=hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()
 for name,value in [('manifest.json',manifest),('tasks.offline.json',tasks),('initial_observations.json',prepared)]: (out/name).write_text(json.dumps(value,ensure_ascii=False,indent=2))
 shutil.copy2(ROOT/'experiments/prompt_contract/PLAN.md',out/'PLAN.md')
 print('OUTPUT_DIR='+str(out),flush=True)
 shared=SharedTools()
 def initialize():
  shared.inner=BCPlusTools();shared.inner.window_builder=builder
 shared.worker.submit(initialize).result()
 def run(t,arm,rep):
  path=out/f"{t['id']}__{arm}__r{rep}";path.mkdir();rec=Recorder(path);initial=prepared[t['id']];allowed={initial['window_ref']}
  class SessionTools:
   def execute(self,name,args):
    if name=='open' and args.get('window_ref') not in allowed:raise ValueError('Window reference has not been observed in this session')
    result=shared.execute(name,args)
    for v in result if isinstance(result,list) else [result]:
     if 'window_ref' in v:allowed.add(v['window_ref'])
    return result
   def close(self):pass
  class SeedClient(RecordedClient):
   seeded=False
   def create(self,**kw):
    if not self.seeded:
     # Modify the actual pending list so later turns preserve seeded observation history.
     kw['messages'].extend([{'role':'assistant','content':None,'tool_calls':[{'id':'seed_search','type':'function','function':{'name':'search','arguments':json.dumps({'query':t['locator_query'],'k':1})}}]},{'role':'tool','tool_call_id':'seed_search','content':json.dumps([initial],ensure_ascii=False)}])
     self.seeded=True
    return super().create(**kw)
  client=SeedClient(OpenAI(api_key=cfg.api_key,base_url=cfg.base_url,timeout=cfg.timeout,max_retries=2),rec)
  session=AgentSession(cfg,client=client,tools=RecordedTools(rec,SessionTools()),max_rounds=4);session.messages[0]['content']=manifest['system_prompts'][arm]
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
 jobs=[(t,a,r) for t in tasks for a in ['baseline','reading_contract'] for r in [1,2,3]];random.Random(918).shuffle(jobs)
 (out/'job_order.json').write_text(json.dumps([[t['id'],a,r] for t,a,r in jobs],indent=2));results=[]
 try:
  with ThreadPoolExecutor(max_workers=4) as pool:
   fs=[pool.submit(run,*job) for job in jobs]
   for f in as_completed(fs):
    result=f.result();results.append(result);(out/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2));print('DONE',result,flush=True)
 finally:shared.shutdown()
 for rel,digest in frozen['files'].items():assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==digest,rel
 print('FINISHED',out,flush=True)
if __name__=='__main__':main()
