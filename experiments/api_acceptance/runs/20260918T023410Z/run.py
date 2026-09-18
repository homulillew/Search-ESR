import sys,json,hashlib,shutil,time
from pathlib import Path
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor,as_completed
ROOT=Path('/data/WSH/Search-ESR');sys.path.insert(0,str(ROOT))
from llm_chat.agent import AgentSession,TOOLS,AGENT_PROMPT
from llm_chat.client import Config
from experiments.run_batch import SharedTools
from experiments.run_rollout import Recorder,RecordedClient,RecordedTools
from openai import OpenAI
out=Path('/tmp/search-esr-api-acceptance-disambiguated')/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ');out.mkdir()
cfg=Config.load()
frozen=json.loads((ROOT/'全链路排查报告/Search-Open冻结清单.json').read_text())
for rel,digest in frozen['files'].items():assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==digest,rel
alltasks=json.loads((ROOT/'experiments/local_support/runs/20260917T184725.353925Z/tasks.offline.json').read_text())
ids=['local_04','local_14']
tasks=[t for t in alltasks if t['id'] in ids]
for t in tasks:
 t['query']={'local_04':'Peter King Nzioki Kenyan actor birth date','local_14':'What-a-Mess cartoon Afghan hound dog formal name'}[t['id']]
(out/'tasks.offline.json').write_text(json.dumps(tasks,ensure_ascii=False,indent=2))
manifest=dict(model=cfg.model,base_url=cfg.base_url,request_options=cfg.request_options(),system_prompt=cfg.system_prompt+'\n\n'+AGENT_PROMPT,tools=TOOLS,max_tool_rounds=64,repeats=2,workers=4,protocol='Real AgentSession and real full-corpus search/open. Two disambiguated follow-up queries twice each; added after observing ambiguous original queries, separate diagnostic sample. No seeded tool history, no forced Open, no reference spans/docids sent to model. Current prompts unchanged. Manual evidence grounding review and mechanical tool/ref checks; not a superiority test. SDK defaults including retries=2 and no added sampling/max_tokens overrides.',frozen_manifest_verified=True,source_sha256={})
for rel in ['llm_chat/agent.py','llm_chat/client.py','llm_chat/raw_windows.py','llm_chat/window_locator.py','llm_chat/window_units.py','experiments/run_rollout.py','experiments/run_batch.py','BCPlus/scripts/search_bcplus.py']:
 p=out/'source'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/rel,p);manifest['source_sha256'][rel]=hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()
shutil.copy2(__file__,out/'run.py');(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
(out/'PLAN.md').write_text('''# 预设验收方案
2个事后消歧局部问题，每题2次独立真实Agent会话，不与原样本混算；真实全库检索，当前系统提示词及工具描述不变，64轮上限。不得把全库未检索到文档的问题归因于窗口。
机械验收：调用参数是否合法、Open是否引用当前会话已返回窗口、原文区间一致性、返回引用是否存在、是否正常结束、是否预算耗尽。语义验收：逐例核查核心回答是否由实际观察支持、是否混淆角色/事件/年份、是否把局部未见写成全库不存在、是否重复读取无新增内容。
Open次数不是成功指标；没有Open样本时增加明确的续读接口探针并分开统计，不能由探针证明模型自主读取。相关信息已充分时直接回答合法。
这是接口验收及坏例发现，不是新旧方案因果对照；样本非独立泛化测试。完整SDK请求响应、工具轨迹和最终回答均保存，不记录密钥。
''')
print('OUTPUT_DIR='+str(out),flush=True)
shared=SharedTools()
def run(t,rep):
 p=out/(t['id']+f'_r{rep}');p.mkdir();r=Recorder(p)
 client=RecordedClient(OpenAI(api_key=cfg.api_key,base_url=cfg.base_url,timeout=cfg.timeout,max_retries=2),r)
 session=AgentSession(cfg,client=client,tools=RecordedTools(r,shared),max_rounds=64)
 result=dict(task=t['id'],repeat=rep,query=t['query'])
 try:
  answer=session.ask(t['query']);(p/'answer.md').write_text(answer);result['status']='complete'
 except Exception as e:result.update(status='error',error_type=type(e).__name__)
 finally:session.close();r.render()
 counts={};usage={}
 for e in r.events:
  if e['kind']=='tool_start':counts[e['name']]=counts.get(e['name'],0)+1
  if e['kind']=='api_response':
   for k in ['prompt_tokens','completion_tokens','total_tokens']:usage[k]=usage.get(k,0)+(e['response'].get('usage') or {}).get(k,0)
 result.update(tool_calls=counts,usage=usage);(p/'summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));return result
results=[]
try:
 with ThreadPoolExecutor(max_workers=4) as pool:
  fs=[pool.submit(run,t,rep) for rep in (1,2) for t in tasks]
  for f in as_completed(fs):
   result=f.result();results.append(result);(out/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2));print('DONE',result,flush=True)
finally:shared.shutdown()
print('FINISHED',out,flush=True)
