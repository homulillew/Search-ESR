"""Select unseen BC+ questions before retrieval, never pass gold to the API."""
import sys,json,hashlib,random,shutil
from pathlib import Path
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from openai import OpenAI
from llm_chat.agent import TOOLS,AGENT_PROMPT
from llm_chat.client import Config
from llm_chat.raw_windows import RawWindowBuilder
from experiments.structural_boundary.candidate import TableEntryWindowBuilder
from transformers import AutoTokenizer
out=ROOT/'experiments/observation_state/runs'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
excluded={'186','311','776','324','546','517','1094'}
rows=[{'qid':str(r['query_id']),'question':r['query']} for line in (ROOT/'BCPlus/data/bcplus/qa.jsonl').read_text().splitlines() if str((r:=json.loads(line))['query_id']) not in excluded]
random.Random(919).shuffle(rows);tasks=rows[:12]
(out/'tasks.json').write_text(json.dumps(tasks,ensure_ascii=False,indent=2));(out/'protocol.json').write_text(json.dumps(dict(seed=919,excluded=sorted(excluded),count=12,scope='New BC+ questions selected before any rollout result; first API search query only, top5 documents; no gold sent. Compare same queries/docs and raw structural boundaries, not final QA accuracy.'),indent=2));shutil.copy2(__file__,out/'prepare_new.py')
print('OUTPUT_DIR='+str(out),flush=True)
cfg=Config.load()
def query(t):
 p=out/('qid_'+t['qid']);p.mkdir()
 request=dict(model=cfg.model,messages=[{'role':'system','content':cfg.system_prompt+'\n\n'+AGENT_PROMPT},{'role':'user','content':t['question']}],tools=TOOLS,tool_choice='auto',stream=False,**cfg.request_options())
 (p/'initial_request.json').write_text(json.dumps(request,ensure_ascii=False,indent=2))
 with OpenAI(api_key=cfg.api_key,base_url=cfg.base_url,timeout=cfg.timeout,max_retries=2) as client:response=client.chat.completions.create(**request)
 (p/'initial_response.json').write_text(response.model_dump_json(indent=2))
 calls=response.choices[0].message.tool_calls or []
 call=next((c for c in calls if c.function.name=='search'),None)
 if call is None:return dict(**t,status='no_search',query=None)
 args=json.loads(call.function.arguments)
 return dict(**t,status='search',query=args['query'],original_k=args.get('k',5),selected_call_id=call.id)
with ThreadPoolExecutor(max_workers=4) as pool:queries=list(pool.map(query,tasks))
(out/'queries.json').write_text(json.dumps(queries,ensure_ascii=False,indent=2))
from BCPlus.scripts.search_bcplus import BCPlusSearcher
searcher=BCPlusSearcher();tok=AutoTokenizer.from_pretrained('/data/model/Qwen3-Embedding-8B',local_files_only=True)
b=RawWindowBuilder(tok);c=TableEntryWindowBuilder(tok);observations=[]
for t in queries:
 if t['query'] is None:continue
 results=searcher.search(t['query'],5)
 old=[];new=[]
 for hit in results:
  did=str(hit['docid']);a=b.search(did,hit['text'],hit['url'],t['query']);z=c.search(did,hit['text'],hit['url'],t['query']);repair=c.last_repair
  assert z['text']==hit['text'][z['offset']:z['end_char']]
  assert z['text_tokens']+z['title_tokens']<=400
  old.append(dict(a,score=hit['score']));new.append(dict(z,score=hit['score']))
  observations.append(dict(qid=t['qid'],query=t['query'],docid=did,baseline=a,candidate=z,repair=repair,has_table=bool(c.documents[(did,z['document_sha256'])]['tables']),has_list=any(l.lstrip().startswith(('- ','* ','1. ')) for l in hit['text'].splitlines()),chars=len(hit['text'])))
 (out/('qid_'+t['qid'])/'baseline.json').write_text(json.dumps(old,ensure_ascii=False,indent=2));(out/('qid_'+t['qid'])/'candidate.json').write_text(json.dumps(new,ensure_ascii=False,indent=2));print('RETRIEVED',t['qid'],len(results),flush=True)
(out/'observations.json').write_text(json.dumps(observations,ensure_ascii=False,indent=2))
print('FINISHED',out,flush=True)
