"""Twelve independent trajectories, frozen three-slot horizon, zero retries."""
import copy
from concurrent.futures import ThreadPoolExecutor,as_completed
from dataclasses import asdict
import os
import sqlite3
import threading
import time
from .common import *
from experiments.recoverable_loop_clean.micro_recovery.prepare import restore
from .transport import Transport,TrajectoryPort
from llm_chat.recoverable_loop.engine import RecoverableLoop
from llm_chat.recoverable_loop.replay import replay_log


class SearchProxy:
    """Thread-local DB/tokenizer; unchanged BCPlusSearcher.search serialized on GPU."""
    def __init__(self,shared,lock):
        self.index=shared.index;self.docids=shared.docids;self.device=shared.device;self.model=shared.model
        self.tokenizer=copy.deepcopy(shared.tokenizer);self.lock=lock
        self.db=sqlite3.connect(f"file:{ROOT/'BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite'}?mode=ro",uri=True)
    def search(self,query,k=5):
        from BCPlus.scripts.search_bcplus import BCPlusSearcher
        with self.lock:return BCPlusSearcher.search(self,query,k)
    def close(self):self.db.close()


def check_freeze():
    f=read(BASE/'FREEZE.json')
    assert subprocess.check_output(['git','show','HEAD:'+str((BASE/'FREEZE.json').relative_to(ROOT))],cwd=ROOT)==(BASE/'FREEZE.json').read_bytes()
    for name,h in f['files'].items():
        assert sha(ROOT/name)==h,('freeze changed',name)
        assert subprocess.check_output(['git','show','HEAD:'+name],cwd=ROOT)==(ROOT/name).read_bytes()
    for name,info in f['external_source_files'].items():
        assert sha(ROOT/name)==info['sha256']
        assert (ROOT/name).read_bytes()==(ROOT/info['committed_snapshot']).read_bytes()
    for name,meta in f['binary_files'].items():
        st=Path(name).stat();assert {'size':st.st_size,'mtime_ns':st.st_mtime_ns}==meta,name
    return f


def run():
    check_freeze();config=read(BASE/'CONFIG.json');out=BASE/'run001';out.mkdir(exist_ok=False)
    start=time.monotonic();save(out/'STARTED.json',{'utc':now(),'head':head(),'config':config})
    os.environ['BCPLUS_DEVICE']='cuda:0'
    import faiss
    import torch
    faiss.omp_set_num_threads(1);torch.set_num_threads(2)
    from BCPlus.scripts.search_bcplus import BCPlusSearcher
    print('Loading unchanged BCPlusSearcher on GPU0',flush=True)
    shared=BCPlusSearcher();lock=threading.Lock()
    print('BCPlusSearcher ready',flush=True)
    transport=Transport(config,out);rows=[]
    def one(job):
        directory=out/'trajectories'/job['trajectory_id'];directory.mkdir(parents=True,exist_ok=False)
        packet=read(BASE/'prefixes'/(job['cell_id']+'.json'));proxy=None;loop=None;outcomes=[];status='active';error=None
        began=time.monotonic()
        try:
            proxy=SearchProxy(shared,lock);state,bridge=restore(packet,proxy.tokenizer,proxy)
            expected=read(BASE/'INITIAL_REQUESTS.json')[job['cell_id']]
            port=TrajectoryPort(transport,directory,packet['forced_first'],expected)
            loop=RecoverableLoop(state,bridge,port,directory/'trace.jsonl')
            for slot in range(1,config['horizon']+1):
                result=loop.step();outcomes.append({'slot':slot,**result});save(directory/f'slot{slot}.json',outcomes[-1])
                print('STEP',job['trajectory_id'],slot,result,flush=True)
                if result.get('failure'):status='step_failure';break
                if result.get('closure',{}).get('status')=='READY':
                    save(directory/'final.json',loop.finalize());status='ready_finalized';break
            if status=='active':status='horizon_exhausted'
        except Exception as exc:
            status='runtime_failure';error={'type':type(exc).__name__,'message':str(exc)[:1600]}
        finally:
            if loop:
                loop.close();save(directory/'FINAL_STATE.json',asdict(loop.state))
                try:assert replay_log(directory/'trace.jsonl')[0]==loop.state
                except Exception as exc:status='replay_failure';error={'type':type(exc).__name__,'message':str(exc)}
            if proxy:proxy.close()
        row={**job,'status':status,'error':error,'outcomes':outcomes,'elapsed_seconds':time.monotonic()-began,'completed_utc':now()}
        save(directory/'RESULT.json',row);print('DONE',job['trajectory_id'],status,flush=True);return row
    try:
        with ThreadPoolExecutor(max_workers=config['concurrency']) as pool:
            for f in as_completed([pool.submit(one,j) for j in read(BASE/'SCHEDULE.json')]):rows.append(f.result())
        save(out/'RESULTS.json',sorted(rows,key=lambda r:r['trajectory_id']))
    finally:
        transport.close();shared.close()
        save(out/'COMPLETED.json',{'utc':now(),'head':head(),'wall_seconds':time.monotonic()-start,'trajectories':len(rows)})

if __name__=='__main__':run()
