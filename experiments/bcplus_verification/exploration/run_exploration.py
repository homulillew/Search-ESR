"""Single registered exploration; no semantic evaluator/labels imported by runtime."""
import copy,json,os,sys
from pathlib import Path
E=Path(__file__).resolve().parent;P=E.parent
sys.path.insert(0,str(P))
import run as primary
from runtime import read,write,sha,digest,head,now,batch,AUTH
from experiments.deferred_recovery.tools import restore,registry,execute

def actor(c):
 it=primary.item(c,'actor_H',primary.actor_view(c,1))
 it['request']['messages'][0]['content']+=(E/'PROMPT_ADDITION.md').read_text()
 it['request_sha256']=digest(it['request']);return it

def run():
 primary.check();f=read(E/'freeze.json')
 for path,h in f['files'].items():assert sha(primary.ROOT/path)==h,path
 import subprocess
 assert subprocess.check_output(['git','show','HEAD:experiments/bcplus_verification/exploration/freeze.json'])==(E/'freeze.json').read_bytes()
 assert not (E/'RUN_STARTED.json').exists(),'No repeated exploration'
 write(E/'RUN_STARTED.json',{'head':head(),'utc':now(),'max_api_calls':24})
 cells=read(E/'INPUTS.json');reqs=read(E/'REQUESTS.json');assert reqs==[actor(c) for c in cells.values()]
 n=len(reqs);rows=batch(E,'actor',reqs);searcher=None
 try:
  active=[]
  for r in rows:
   c=cells[r['case_id']+':V'];c['decisions'].append({'round':1,'actor':r,'tool':None,'pre_claims':copy.deepcopy(c['claims']),'pre_hypothesis':c['hypothesis']})
   c['status']='actor_failure' if r['output'] is None else 'actor_stop' if r['output']['decision']=='stop' else 'active'
   if c['status']=='active':active.append(c)
  write(E/'post_actor_cells.json',cells)
  if AUTH.failure:raise RuntimeError('Authentication failure')
  if active:
   os.environ['BCPLUS_DEVICE']='cuda:1'
   from BCPlus.scripts.search_bcplus import BCPlusSearcher
   searcher=BCPlusSearcher()
  for c in active:
   t=None;a=c['decisions'][-1]['actor']['output']['actions'][0]
   try:
    t=restore(c['registry'],searcher);out=execute(t,a);c['registry']=registry(t)
   except Exception as e:out={'action':a,'observations':[],'result':None,'audit':None,'error':{'type':type(e).__name__,'message':str(e)[:1000]},'elapsed_seconds':None}
   finally:
    if t:t.close()
   c['decisions'][-1]['tool']=out
   if out['error']:c['status']='tool_failure'
   else:
    seen={x['doc_ref'] for x in c['catalog']};c['catalog'].extend({k:d[k] for k in ('doc_ref','title','url')} for d in c['registry']['documents'] if d['doc_ref'] not in seen)
    c['attempts'].append({'action':a,'status':out['result']['status'],'returned_windows':[w['window_ref'] for w in out['observations']]})
    for w in out['observations']:
     if w['window_ref'] not in {v['window_ref'] for v in c['visible_windows']}:c['visible_windows'].append({k:w[k] for k in ('window_ref','doc_ref','title','url','text')})
   write(E/'post_tool_cells.json',cells);print('tool',c['case_id'],a,flush=True)
  for wave in range(5):
   items=[];obs={};pre={}
   for c in active:
    ws=c['decisions'][-1]['tool']['observations']
    if c['status']!='active' or wave>=len(ws):continue
    w=ws[wave];key=c['case_id']+':V';obs[key]=w;pre[key]={'claims':copy.deepcopy(c['claims']),'hypothesis':c['hypothesis']};items.append(primary.item(c,'state_updater',primary.writer_view(c,w)))
   if not items:continue
   assert n+len(items)<=24;n+=len(items);write(E/f'writer{wave}_requests.json',items)
   for r in batch(E,f'writer{wave}',items):
    key=r['case_id']+':V';c=cells[key];w=obs[key]
    if r['output'] is None:c['status']='writer_failure'
    else:
     o=r['output']
     for text in o['claims_to_add']:
      c['claims'].append({'statement':text,'support_refs':[w['window_ref']],'source_text_hashes':[w['text_sha256']],'first_seen_time':[{'round':1,'wave':wave}],'admission':'unrepaired U1; exploration reviewed offline'});c['claims_version']+=1
     h=o['hypothesis_update'];old=c['hypothesis']
     if h['action']=='set':c['hypothesis']=h['statement']
     elif h['action']=='clear':c['hypothesis']=None
     if old!=c['hypothesis']:c['hypothesis_version']+=1
    c['updates'].append({'round':1,'wave':wave,'need':c['need'],'observation':w,'pre_state':pre[key],'proposal':r,'post_state':{'claims':copy.deepcopy(c['claims']),'hypothesis':c['hypothesis']}})
   write(E/'writer_checkpoint.json',cells)
   if AUTH.failure:raise RuntimeError('Authentication failure')
  for c in active:
   if c['status']=='active':c['status']='budget_exhausted'
  write(E/'RESULTS.json',cells);write(E/'RUN_COMPLETED.json',{'head':head(),'utc':now(),'api_calls':n,'units':4})
 finally:
  if searcher:searcher.close()
if __name__=='__main__':run()
