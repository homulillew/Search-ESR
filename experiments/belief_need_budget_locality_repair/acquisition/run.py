"""Frozen historical Actor/U1 discovery trajectories; no new Need prompt imports."""
import copy,json,os,sys,threading,time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from transport import P,ROOT,C,rd,save,sha,dg,head,now,check_freeze,Transport
sys.path.insert(0,str(ROOT))
from experiments.deferred_recovery.tools import restore,registry,execute
from experiments.evidence_scope_localization.runtime import LockedModel,SearchProxy
from llm_chat.search_find_agent import SEARCH_FIND_TOOLS
from experiments.bcplus_verification.runtime import validate_object
BASE=P/'acquisition';LEGACY=ROOT/'experiments/bcplus_verification'
ACTOR_SCHEMA=rd(LEGACY/'schemas/actor_H.json');WRITER_SCHEMA=rd(ROOT/'experiments/goal_residual_control/harness_v2/UPDATER_RESPONSE_SCHEMA.json')
def make_request(view,writer=False):
 prompt=LEGACY/'prompts'/('writer.md' if writer else 'discovery_actor.md')
 # Exact historical model/prompt/JSON transport options. No completion cap.
 return {'model':C['model'],'messages':[{'role':'system','content':prompt.read_text()},{'role':'user','content':json.dumps(view,ensure_ascii=False)}],'stream':False,'response_format':{'type':'json_object'}}
def actor_view(c,step):
 return {'Original Question':c['question'],'Current Claims':[x['statement'] for x in c['claims']],'Working Hypothesis':c['hypothesis'],'Historical Document Catalog':[{k:d[k] for k in ['doc_ref','title','url']} for d in c['registry']['documents']],'Recent Attempts':c['attempts'],'New Observations':c['visible_windows'],'Budget':{'remaining_decisions':3-step,'max_actions_this_decision':1},'Tool schema':SEARCH_FIND_TOOLS,'Response schema':ACTOR_SCHEMA}
def state(c):return {'question':c['question'],'claims':copy.deepcopy(c['claims']),'hypothesis':c['hypothesis']}
def initial(row):return {**row,'claims':[],'hypothesis':None,'need':'','registry':{'documents':[],'windows':[]},'visible_windows':[],'attempts':[],'decisions':[],'updates':[],'status':'active'}
def freeze():
 qs=rd(BASE/'QUESTIONS.json');save(BASE/'INITIAL_REQUESTS.json',[{'case_id':x['case_id'],'request':make_request(actor_view(initial(x),0))} for x in qs])
 deps=[BASE/'run.py',BASE/'prepare.py',BASE/'QUESTIONS.json',BASE/'SELECTION.json',BASE/'EXCLUDED_QIDS.json',BASE/'INITIAL_REQUESTS.json',P/'CONFIG.json',P/'transport.py',P/'PROTOCOL.md',LEGACY/'prompts/discovery_actor.md',LEGACY/'prompts/writer.md',LEGACY/'schemas/actor_H.json',ROOT/'experiments/goal_residual_control/harness_v2/UPDATER_RESPONSE_SCHEMA.json',ROOT/'experiments/deferred_recovery/tools.py',ROOT/'experiments/evidence_scope_localization/runtime.py',ROOT/'experiments/bcplus_verification/runtime.py',ROOT/'llm_chat/search_find_agent.py',ROOT/'llm_chat/agent.py',ROOT/'llm_chat/raw_windows.py',ROOT/'BCPlus/scripts/search_bcplus.py']
 binaries=rd(ROOT/'experiments/evidence_scope_localization/r1/FREEZE.json')['binary_files'];current={p:{'size':Path(p).stat().st_size,'mtime_ns':Path(p).stat().st_mtime_ns} for p in binaries}
 save(BASE/'FREEZE.json',{'head':head(),'utc':now(),'files':{str(p.relative_to(ROOT)):sha(p) for p in deps},'binary_files':current,'model':C['model'],'budget':'omit max_tokens, exact historical request fields','actor_horizon':3,'qids':16,'dev_qids':6,'confirmation_qids':10,'max_retries':0,'parallel_trajectories':8,'gpu':'cuda:1','mechanical_parallelization':'isolated tokenizer/db/handles per trajectory; shared unchanged embedding forward serialized by lock; HTTP and other independent work overlap','writer':'exact historical U1, max2 claims per actual observation, stop trajectory on failure','state_selection':'Archive all states now; selection/labels only after QCH commit, before any B0/B1/B2 semantic experiment.'})
def run():
 f=check_freeze(BASE/'FREEZE.json')
 for p,v in f['binary_files'].items():assert (Path(p).stat().st_size,Path(p).stat().st_mtime_ns)==(v['size'],v['mtime_ns'])
 assert rd(P/'e0/PREFLIGHT_VERDICT.json')['passed'],'Need transport preflight must pass before acquisition'
 save(BASE/'STARTED.json',{'head':head(),'utc':now(),'gpu':'cuda:1'});os.environ['BCPLUS_DEVICE']='cuda:1'
 import faiss;faiss.omp_set_num_threads(1)
 from BCPlus.scripts.search_bcplus import BCPlusSearcher
 shared=BCPlusSearcher();shared.model=LockedModel(shared.model);t=Transport();done=[];start=time.monotonic();initials={r['case_id']:r['request'] for r in rd(BASE/'INITIAL_REQUESTS.json')}
 def one(row):
  c=initial(row);cid=c['case_id'];outdir=BASE/'trajectories'/cid;outdir.mkdir(parents=True,exist_ok=False);proxy=None;tool=None;snapshots=[{'state_id':cid+'_S00','transition':'initial','state':state(c)}];save(outdir/'S00.json',snapshots[0]);toolcount=0
  try:
   proxy=SearchProxy(shared);tool=restore(c['registry'],proxy)
   for step in range(3):
    req=make_request(actor_view(c,step))
    if step==0:assert req==initials[cid]
    a=t.call(outdir/'calls',f'actor_{step+1}',req,ACTOR_SCHEMA);d={'step':step+1,'actor':a,'pre_state':state(c),'tool':None};c['decisions'].append(d)
    if a['output'] is None:c['status']='actor_failure';break
    validate_object(a['output'],'actor_H',{'known_documents':c['registry']['documents'],'observed_windows':c['visible_windows']})
    if a['output']['decision']=='stop':c['status']='actor_stop';break
    c['need']=a['output']['gap'];action=a['output']['actions'][0];d['tool_started_utc']=now();save(outdir/f'decision{step+1}_tool_started.json',{'action':action,'utc':now()})
    obs=execute(tool,action);toolcount+=1;d['tool']=obs;d['tool_completed_utc']=now();c['registry']=registry(tool);save(outdir/f'decision{step+1}_tool.json',obs)
    print('TOOL',cid,step+1,action['tool'],len(obs['observations']),obs['error'],flush=True)
    if obs['error']:c['status']='tool_failure';break
    c['attempts'].append({'action':action,'status':obs['result']['status'],'returned_windows':[w['window_ref'] for w in obs['observations']]})
    for w in obs['observations']:
     if w['window_ref'] not in {x['window_ref'] for x in c['visible_windows']}:c['visible_windows'].append({k:w[k] for k in ['window_ref','doc_ref','title','url','text']})
    for wave,w in enumerate(obs['observations']):
     before=state(c);view={'Original Question':c['question'],'Verified Claims':[x['statement'] for x in c['claims']],'Working Hypothesis':c['hypothesis'],'Current Research Gap':c['need'],'Observation':{k:w[k] for k in ['title','url','text','window_ref','doc_ref']}}
     wr=t.call(outdir/'calls',f'writer_{step+1}_{wave+1}',make_request(view,True),WRITER_SCHEMA)
     if wr['output'] is None:c['status']='writer_failure'
     else:
      validate_object(wr['output'],'state_updater');o=wr['output']
      for text in o['claims_to_add']:c['claims'].append({'statement':text,'support_refs':[w['window_ref']],'source_text_hashes':[w['text_sha256']],'source_observation_path':str((outdir/f'decision{step+1}_tool.json').relative_to(ROOT)),'source_observation_index':wave,'writer_request_id':f'writer_{step+1}_{wave+1}','admission':'unrepaired frozen U1; offline support review required'})
      h=o['hypothesis_update']
      if h['action']=='set':c['hypothesis']=h['statement']
      elif h['action']=='clear':c['hypothesis']=None
     update={'round':step+1,'wave':wave+1,'need':c['need'],'observation':w,'writer':wr,'pre_state':before,'post_state':state(c)};c['updates'].append(update);save(outdir/f'update_{step+1}_{wave+1}.json',update)
     if wr['output'] is None:break
     if dg(before)!=dg(state(c)):
      snap={'state_id':f'{cid}_S{len(snapshots):02}','transition':f'update_{step+1}_{wave+1}','state':state(c)};snapshots.append(snap);save(outdir/f"S{len(snapshots)-1:02}.json",snap)
    if c['status']!='active':break
   if c['status']=='active':c['status']='budget_exhausted'
  except Exception as e:c['status']='runtime_failure';c['runtime_error']={'type':type(e).__name__,'message':str(e)[:1200]}
  finally:
   if tool is not None:tool.close()
   if proxy is not None:proxy.close()
  c['snapshots']=snapshots;c['completed_utc']=now();c['tool_calls']=toolcount;save(outdir/'RESULT.json',c);print('ACQUIRED',cid,c['qid'],c['status'],'states',len(snapshots),flush=True);return c
 try:
  with ThreadPoolExecutor(max_workers=8) as pool:
   for fu in as_completed([pool.submit(one,x) for x in rd(BASE/'QUESTIONS.json')]):done.append(fu.result())
  save(BASE/'RESULTS.json',sorted(done,key=lambda c:c['case_id']));save(BASE/'ALL_QCH.json',[{'case_id':c['case_id'],'qid':c['qid'],'split':c['split'],**s} for c in sorted(done,key=lambda c:c['case_id']) for s in c['snapshots']])
 finally:t.close();shared.close();save(BASE/'COMPLETED.json',{'utc':now(),'calls':t.count,'http_peak':t.peak,'tool_calls':sum(c['tool_calls'] for c in done),'wall_seconds':time.monotonic()-start})
if __name__=='__main__':globals()[sys.argv[1]]()
