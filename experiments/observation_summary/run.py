"""Paired real-API observation-summary experiment; production files unchanged."""
import sys,json,random,sqlite3,hashlib,shutil
from datetime import datetime,timezone
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from transformers import AutoTokenizer
from openai import OpenAI
from llm_chat.client import Config
from llm_chat.agent import TOOLS,AGENT_PROMPT
from llm_chat.raw_windows import RawWindowBuilder
from llm_chat.observed_agent import ObservedAgentSession
from llm_chat.observations import ObservationStore
from experiments.run_rollout import Recorder,RecordedClient,RecordedTools
from experiments.observation_summary.summary import build_summary,request_with_summary

SOURCE=ROOT/'experiments/observation_state/runs/20260918T034912.334507Z'


def dump(p,value):p.write_text(json.dumps(value,ensure_ascii=False,indent=2))


def main():
    out=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT/'experiments/observation_summary/runs'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True,exist_ok=False)
    cfg=Config.load();tok=AutoTokenizer.from_pretrained('/data/model/Qwen3-Embedding-8B',local_files_only=True)
    tasks=[]
    for t in json.loads((SOURCE/'queries.json').read_text())[:6]:
        views=json.loads((SOURCE/f"qid_{t['qid']}"/'baseline.json').read_text())
        tasks.append(dict(id='qid_'+t['qid'],kind='natural',question=t['question'],seeds=[dict(tool='search',arguments={'query':t['query'],'k':5},result=views)]))
    db=sqlite3.connect(f'file:{ROOT}/BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite?mode=ro',uri=True)
    controls=[]
    for kind in ['full_repeat','partial_overlap','sufficient','need_read']:
        b=RawWindowBuilder(tok);did='67431' if kind=='need_read' else '5266'
        text,url=db.execute('select text,url from documents where docid=?',(did,)).fetchone()
        query='Peter King role in The Constant Gardener' if kind=='need_read' else 'Dean Dodrill gaming PC storage'
        v=b.search(did,text,url,query)
        seed=dict(tool='search',arguments={'query':query,'k':1},result=[v]);seeds=[seed]
        if kind=='full_repeat':
            a=b.open(v['window_ref'],'after');op=dict(tool='open',arguments={'window_ref':v['window_ref'],'direction':'after'},result=a);seeds.extend([op,op])
        elif kind=='partial_overlap':
            a=b.open(v['window_ref'],'around');seeds.append(dict(tool='open',arguments={'window_ref':v['window_ref'],'direction':'around'},result=a))
        else:seeds.append(seed)
        if kind in {'full_repeat','partial_overlap'}:
            question='请审阅上面的既有工具记录，回答 Dean Dodrill 的这台游戏电脑有多大存储空间。再核对最后一条既有工具返回：如果其中有相对于此前工具返回新增的原文，逐字摘录一句；如果没有，明确说明。这里新增仅指此前未返回的文字。'
        elif kind=='sufficient':question='Dean Dodrill 在这篇 PC Gamer 访谈中介绍的游戏电脑有多大存储空间？请根据资料回答并引用。'
        else:question='肯尼亚演员 Peter King（Peter Nzioki）在 The Constant Gardener 中具体饰演哪个角色？请根据资料回答并引用。'
        assert ('Policeman 1' not in v['text']) if kind=='need_read' else ('5TB' in v['text'])
        store=ObservationStore()
        for s in seeds:store.record(s['tool'],s['arguments'],s['result'],b)
        metrics=store.events()[-1]['observations'][0]
        if kind=='full_repeat':assert metrics['new_chars']==0
        if kind=='partial_overlap':assert metrics['new_chars']>0 and metrics['body_overlap_chars']>0
        expected='Policeman 1' if kind=='need_read' else '5TB'
        ref_start=text.index(expected);controls.append(dict(id='control_'+kind,expected=expected,docid=did,reference_span=[ref_start,ref_start+len(expected)],last_seed_metrics=metrics))
        store.close();tasks.append(dict(id='control_'+kind,kind=kind,question=question,seeds=seeds))
    db.close();dump(out/'tasks.json',tasks);dump(out/'controls.offline.json',controls)
    manifest=dict(model=cfg.model,base_url=cfg.base_url,request_options=cfg.request_options(),system=cfg.system_prompt+'\n\n'+AGENT_PROMPT,tools=TOOLS,window='baseline',max_tool_rounds=4,max_tokens=2048,timeout=120,max_retries=0,repeats=2,workers=4,summary_token_cap=1200,source_sha256={})
    for rel in ['experiments/observation_summary/PLAN.md','experiments/observation_summary/run.py','experiments/observation_summary/summary.py','experiments/observation_summary/test_summary.py','llm_chat/observations.py','llm_chat/observed_agent.py','llm_chat/agent.py','llm_chat/raw_windows.py','llm_chat/window_locator.py','llm_chat/window_units.py','llm_chat/client.py','experiments/run_rollout.py','BCPlus/scripts/search_bcplus.py']:
        dest=out/'source'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/rel,dest);manifest['source_sha256'][rel]=hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()
    dump(out/'manifest.json',manifest)
    jobs=[(t,a,r) for t in tasks for a in ['hidden','visible'] for r in [1,2]];random.Random(20260918).shuffle(jobs)
    dump(out/'schedule.json',[dict(task=t['id'],arm=a,repeat=r) for t,a,r in jobs]);print('OUTPUT_DIR='+str(out),flush=True)
    worker=ThreadPoolExecutor(max_workers=1);holder={}
    def search(query,k):
        if 'searcher' not in holder:
            from BCPlus.scripts.search_bcplus import BCPlusSearcher
            holder['searcher']=BCPlusSearcher()
        return holder['searcher'].search(query,k)
    class SearchProxy:
        def search(self,q,k):return worker.submit(search,q,k).result()

    def run(t,arm,rep):
        p=out/f"{t['id']}__{arm}__r{rep}";p.mkdir();rec=Recorder(p)
        class Client(RecordedClient):
            seeded=False;last_sequence=0;store=None
            def create(self,**kw):
                if not self.seeded:
                    for i,s in enumerate(t['seeds']):
                        callid=f'seed_{i}'
                        kw['messages'].extend([{'role':'assistant','content':None,'tool_calls':[{'id':callid,'type':'function','function':{'name':s['tool'],'arguments':json.dumps(s['arguments'])}}]}, {'role':'tool','tool_call_id':callid,'content':json.dumps(s['result'],ensure_ascii=False)}])
                    self.seeded=True
                summary=build_summary(self.store.events(),self.last_sequence,tok)
                rec.emit('observation_summary',visible=arm=='visible',after_sequence=self.last_sequence,through_sequence=self.store.sequence,message=summary)
                self.last_sequence=self.store.sequence
                kw=request_with_summary(kw,summary if arm=='visible' else None);kw['max_tokens']=2048
                return super().create(**kw)
        client=Client(OpenAI(api_key=cfg.api_key,base_url=cfg.base_url,timeout=120,max_retries=0),rec)
        session=ObservedAgentSession(cfg,state_path=p/'state.sqlite',variant='baseline',client=client,max_rounds=4)
        client.store=session.observations;b=RawWindowBuilder(tok);session.tools.window_builder=b;session.tools.searcher=SearchProxy()
        db=sqlite3.connect(f'file:{ROOT}/BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite?mode=ro',uri=True)
        for s in t['seeds']:
            for v in s['result'] if isinstance(s['result'],list) else [s['result']]:
                text,url=db.execute('select text,url from documents where docid=?',(v['docid'],)).fetchone();key=b.register(v['docid'],text,url);assert b._emit(key,v['offset'],v['end_char'])['window_ref']==v['window_ref']
            session.observations.record(s['tool'],s['arguments'],s['result'],b)
        db.close();seed_sequence=session.observations.sequence;session.tools=RecordedTools(rec,session.tools)
        result=dict(task=t['id'],kind=t['kind'],arm=arm,repeat=rep,seed_sequence=seed_sequence)
        try:
            answer=session.ask(t['question']);(p/'answer.md').write_text(answer);result['status']='complete'
        except Exception as e:result.update(status='error',error_type=type(e).__name__,error_detail=str(e).replace(cfg.api_key,'[redacted]'))
        events=session.observations.events();dump(p/'observations.json',events)
        usage={k:sum((e['response'].get('usage') or {}).get(k,0) for e in rec.events if e['kind']=='api_response') for k in ['prompt_tokens','completion_tokens','total_tokens']}
        result.update(usage=usage,forced_final=any(e['kind']=='api_request' and e['request']['tool_choice']=='none' for e in rec.events),observations=session.observations.summary())
        session.close();rec.render();dump(p/'summary.json',result);return result
    results=[]
    try:
        with ThreadPoolExecutor(max_workers=4) as pool:
            for f in as_completed([pool.submit(run,*j) for j in jobs]):
                r=f.result();results.append(r);dump(out/'results.json',results);print('DONE',r['task'],r['arm'],r['repeat'],r['status'],flush=True)
    finally:worker.shutdown()
    print('FINISHED',out,flush=True)


if __name__=='__main__':main()
