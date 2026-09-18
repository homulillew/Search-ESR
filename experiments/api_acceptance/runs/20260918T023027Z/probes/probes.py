import sys,json,sqlite3,shutil
from pathlib import Path
ROOT=Path('/data/WSH/Search-ESR');sys.path.insert(0,str(ROOT))
from llm_chat.agent import AgentSession,BCPlusTools
from llm_chat.client import Config
from llm_chat.raw_windows import RawWindowBuilder
from experiments.run_rollout import Recorder,RecordedClient,RecordedTools
from transformers import AutoTokenizer
from openai import OpenAI
p=Path(sys.argv[1])/'probes';p.mkdir(exist_ok=True);shutil.copy2(__file__,p/'probes.py')
cfg=Config.load();tok=AutoTokenizer.from_pretrained('/data/model/Qwen3-Embedding-8B',local_files_only=True)
db=sqlite3.connect(f'file:{ROOT}/BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite?mode=ro',uri=True)
CASES=[('before','23800','2005 Champions League final Riise free kick end of extra time','请继续读取刚才返回片段之前紧邻的原文，并摘录新增内容中的一句话。只读当前文档。'),('after','67431','Peter King role in The Constant Gardener','请继续读取刚才返回片段之后紧邻的原文，并摘录新增内容中的一句话。只读当前文档。'),('around','67431','Peter King role in The Constant Gardener','请扩大刚才的片段，同时保留原有内容，补充周围上下文，并摘录新增内容中的一句话。只读当前文档。'),('complete','39918','early 21st century football final 95th minute free kick player','检查刚才返回的这份文档是否还有下文。有就继续读，没有就说明边界。只读当前文档。')]
for name,did,q,instruction in CASES:
 d=p/name;d.mkdir(exist_ok=True);rec=Recorder(d);inner=BCPlusTools();inner.window_builder=RawWindowBuilder(tok)
 text,url=db.execute('select text,url from documents where docid=?',(did,)).fetchone();initial=inner.window_builder.search(did,text,url,q)
 client=RecordedClient(OpenAI(api_key=cfg.api_key,base_url=cfg.base_url,timeout=cfg.timeout,max_retries=2),rec)
 session=AgentSession(cfg,client=client,tools=RecordedTools(rec,inner),max_rounds=64)
 # Deliberately seeded boundary test, not an autonomous retrieval rollout.
 session.messages += [{'role':'user','content':q},{'role':'assistant','content':None,'tool_calls':[{'id':'seed_search','type':'function','function':{'name':'search','arguments':json.dumps({'query':q,'k':1})}}]},{'role':'tool','tool_call_id':'seed_search','content':json.dumps([initial],ensure_ascii=False)}]
 rec.emit('seeded_observation',note='Synthetic prior search history; real builder output. No API search or score claimed.',result=initial)
 try:
  answer=session.ask(instruction);(d/'answer.md').write_text(answer);status='complete'
 except Exception as e:status=type(e).__name__
 finally:session.close();rec.render()
 (d/'summary.json').write_text(json.dumps(dict(status=status,probe=name,instruction=instruction,initial=initial),ensure_ascii=False,indent=2))
 print('PROBE_DONE',name,status,flush=True)
