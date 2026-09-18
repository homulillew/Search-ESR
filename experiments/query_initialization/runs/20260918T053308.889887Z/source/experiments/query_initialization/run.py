"""A/B/C initialization probes, shared local retrieval, complete SDK traces."""
import argparse,hashlib,json,random,re,shutil,sys,time
from pathlib import Path
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor,as_completed
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from openai import OpenAI
from transformers import AutoTokenizer
from llm_chat.client import Config
from llm_chat.observations import ObservationStore
from llm_chat.observed_agent import ObservedTools
from llm_chat.raw_windows import RawWindowBuilder
from experiments.run_rollout import Recorder,RecordedClient
from experiments.query_initialization.initializer import generate


def dump(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2))


def exclusion_inventory():
    found={};known='186 311 776 324 546 517 1094 580 905 1034 593 177 387 729 496 49 645 1224 802'.split()
    for q in known:found.setdefault(q,set()).add('design_known_questions')
    def walk(value,source):
        if isinstance(value,dict):
            for k,v in value.items():
                if k in {'qid','query_id'} and str(v).isdigit():found.setdefault(str(v),set()).add(source)
                elif k=='qids' and isinstance(v,list):
                    for q in v:
                        if str(q).isdigit():found.setdefault(str(q),set()).add(source)
                elif isinstance(v,(dict,list)):walk(v,source)
        elif isinstance(value,list):
            for v in value:walk(v,source)
    for p in (ROOT/'experiments').rglob('*.json'):
        if 'source' in p.parts or 'final_source' in p.parts or p.stat().st_size>5_000_000:continue
        if p.name not in {'tasks.json','input.json','batch.json','summary.json','queries.json','tasks.offline.json'}:continue
        try:walk(json.loads(p.read_text()),str(p.relative_to(ROOT)))
        except (ValueError,UnicodeError):continue
    return {q:sorted(v) for q,v in sorted(found.items(),key=lambda kv:int(kv[0]))}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--phase',choices=['dev','holdout'],required=True);ap.add_argument('--dev-run',type=Path);args=ap.parse_args()
    cfg=Config.load();out=ROOT/'experiments/query_initialization/runs'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    inventory=exclusion_inventory();dump(out/'exclusions.json',inventory)
    rows=[dict(qid=str(r['query_id']),question=r['query']) for line in (ROOT/'BCPlus/data/bcplus/qa.jsonl').open() if (r:=json.loads(line))]
    if args.phase=='dev':
        order=['1034','645','905','387'];tasks=[next(t for t in rows if t['qid']==q) for q in order];repeats=1
    else:
        if not args.dev_run:raise ValueError('--dev-run required before holdout')
        review=json.loads((args.dev_run/'dev_review.json').read_text());assert review['proceed_to_holdout'] is True
        prior=json.loads((args.dev_run/'manifest.json').read_text())
        for name in ['experiments/query_initialization/initializer.py','experiments/query_initialization/INITIALIZER_PROMPT.md']:
            assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==prior['source_sha256'][name],name
        candidates=[t for t in rows if t['qid'] not in inventory];random.Random(20260919).shuffle(candidates);tasks=candidates[:20];assert len(tasks)==20;repeats=2
    dump(out/'tasks.json',tasks)
    manifest=dict(version='query_init_v001',phase=args.phase,model=cfg.model,base_url=cfg.base_url,request_options=cfg.request_options(),max_tokens=1536,timeout=120,sdk_retries=0,repair_limit=1,repeats=repeats,workers=4,selection_seed=20260919,schedule_seed=20260920,window='baseline',slots=dict(A=[6],B=[6],C=[3,3]),source_sha256={},dev_run=str(args.dev_run) if args.dev_run else None)
    paths=['experiments/query_initialization/initializer.py','experiments/query_initialization/run.py','experiments/query_initialization/test_initializer.py','experiments/query_initialization/INITIALIZER_PROMPT.md','全链路排查报告/Query初始化节点设计与实验方案.md','llm_chat/agent.py','llm_chat/client.py','llm_chat/raw_windows.py','llm_chat/window_locator.py','llm_chat/window_units.py','llm_chat/observations.py','llm_chat/observed_agent.py','experiments/run_rollout.py','BCPlus/scripts/search_bcplus.py','BCPlus/indexes/bcplus-qwen3-8b/metadata.json']
    for name in paths:
        dest=out/'source'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,dest);manifest['source_sha256'][name]=hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
    dump(out/'manifest.json',manifest)
    jobs=[(t,a,r) for t in tasks for a in ['A','B','C'] for r in range(1,repeats+1)];random.Random(20260920).shuffle(jobs)
    dump(out/'schedule.json',[dict(qid=t['qid'],arm=a,repeat=r) for t,a,r in jobs]);print('OUTPUT_DIR='+str(out),flush=True)
    tok=AutoTokenizer.from_pretrained('/data/model/Qwen3-Embedding-8B',local_files_only=True)
    worker=ThreadPoolExecutor(max_workers=1);holder={}
    def search(q,k):
        if 'searcher' not in holder:
            from BCPlus.scripts.search_bcplus import BCPlusSearcher
            holder['searcher']=BCPlusSearcher()
        return holder['searcher'].search(q,k)
    class Proxy:
        def search(self,q,k):return worker.submit(search,q,k).result()

    def run(t,arm,rep):
        p=out/f"qid_{t['qid']}__{arm}__r{rep}";p.mkdir();rec=Recorder(p)
        client=RecordedClient(OpenAI(api_key=cfg.api_key,base_url=cfg.base_url,timeout=120,max_retries=0),rec)
        store=ObservationStore(p/'observations.sqlite');tool=ObservedTools(store);tool.window_builder=RawWindowBuilder(tok);tool.searcher=Proxy()
        result=dict(qid=t['qid'],arm=arm,repeat=rep);bundles=[];start=time.monotonic()
        try:
            plan=generate(client,cfg,t['question'],arm);dump(p/'plan.json',plan);rec.emit('plan_finalized',plan=plan)
            result.update(plan_status=plan['status'],initial_valid=plan['initial_valid'],repairs=plan['repairs'],directions=len(plan['directions']))
            errors=[]
            for i,d in enumerate(plan['directions'],1):
                arguments=dict(query=d['query'],k=3 if arm=='C' else 6);rec.emit('search_start',direction=i,arguments=arguments);stamp=time.monotonic()
                try:
                    views=tool.execute('search',arguments);elapsed=time.monotonic()-stamp
                    rec.emit('search_result',direction=i,arguments=arguments,result=views,elapsed_seconds=elapsed)
                    bundles.append(dict(direction=i,query=d['query'],result=views,elapsed_seconds=elapsed))
                except Exception as e:
                    detail=str(e).replace(cfg.api_key,'[redacted]');errors.append(dict(direction=i,type=type(e).__name__,detail=detail));rec.emit('search_error',direction=i,error_type=type(e).__name__,detail=detail)
            result.update(status='partial' if errors else 'complete' if plan['directions'] else plan['status'],search_errors=errors)
        except Exception as e:
            result.update(status='error',error_type=type(e).__name__,error_detail=str(e).replace(cfg.api_key,'[redacted]'))
        finally:
            dump(p/'observations.json',store.events());dump(p/'bundle.json',dict(question=t['question'],origin='initialization_harness',directions=bundles))
            result.update(observations=store.summary(),elapsed_seconds=time.monotonic()-start)
            result['usage']={k:sum((e['response'].get('usage') or {}).get(k,0) for e in rec.events if e['kind']=='api_response') for k in ['prompt_tokens','completion_tokens','total_tokens']}
            result['api_requests']=sum(e['kind']=='api_request' for e in rec.events)
            dump(p/'summary.json',result);tool.close();store.close();client.close();rec.render()
        return result
    results=[]
    try:
        with ThreadPoolExecutor(max_workers=4) as pool:
            for f in as_completed([pool.submit(run,*j) for j in jobs]):
                r=f.result();results.append(r);dump(out/'results.json',results);print('DONE',r['qid'],r['arm'],r['repeat'],r['status'],flush=True)
    finally:worker.shutdown()
    print('FINISHED',out,flush=True)


if __name__=='__main__':main()
