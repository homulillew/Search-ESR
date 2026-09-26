"""Frozen runtime: no offline labels/reference evidence imports or semantic routing."""
import copy,json,os,sys,subprocess
from pathlib import Path
from runtime import TOP,ROOT,read,write,digest,sha,now,head,CONFIG,make_item,batch,AUTH
from experiments.deferred_recovery.tools import restore,registry,execute
from llm_chat.search_find_agent import SEARCH_FIND_TOOLS

def initial():
 cells={}
 for x in read(TOP/'bank/RUNTIME_INPUTS.json'):
  c=copy.deepcopy(x);c.update(status='active',decisions=[],updates=[],visible_windows=[],catalog=[],claims_version=0,hypothesis_version=int(c['hypothesis'] is not None));cells[c['case_id']+':'+c['arm']]=c
 return cells

def actor_view(c,rnd):
 v={'Original Question':c['question'],'Current Claims':[x['statement'] for x in c['claims']],
 'Working Hypothesis':c['hypothesis'],'Historical Document Catalog':c['catalog'],'Recent Attempts':c['attempts'],
 'New Observations':c['visible_windows'],'Budget':{'remaining_decisions':c['horizon']-rnd,'max_actions_this_decision':1},
 'Tool schema':SEARCH_FIND_TOOLS,'Response schema':read(TOP/'schemas/actor_H.json')}
 if c['arm']=='V':v.update({'Candidate':c['candidate'],'Constraint to Verify':c['constraint']})
 return v

def item(c,kind,view):
 prompt=TOP/'prompts'/('writer.md' if kind=='state_updater' else 'verification_actor.md' if c['arm']=='V' else 'discovery_actor.md')
 chat={'model':CONFIG['model'],'messages':[{'role':'system','content':prompt.read_text()},{'role':'user','content':json.dumps(view,ensure_ascii=False)}],'stream':False}
 return make_item(c['case_id'],c['qid'],c['arm'],kind,chat,'json_mode_fallback')

def actor_items(cells,rnd):
 # Stable hash interleaving avoids submitting an entire polarity/cohort first.
 return sorted([item(c,'actor_H',actor_view(c,rnd)) for c in cells.values() if c['status']=='active' and rnd<c['horizon']],key=lambda it:digest(['bcplus-verification-order',rnd,it['case_id']]))

def writer_view(c,w):return {'Original Question':c['question'],'Verified Claims':[x['statement'] for x in c['claims']],
 'Working Hypothesis':c['hypothesis'],'Current Research Gap':c['need'],
 'Observation':{k:w[k] for k in ('title','url','text','window_ref','doc_ref')}}

def check():
 f=read(TOP/'freeze.json')
 for p,h in f['files'].items():assert sha(ROOT/p)==h,p
 assert subprocess.check_output(['git','show','HEAD:experiments/bcplus_verification/freeze.json'])==(TOP/'freeze.json').read_bytes()
 for p,s in f['binary_files'].items():
  st=Path(p).stat();assert (st.st_size,st.st_mtime_ns)==(s['size'],s['mtime_ns']),p
 assert (TOP/'prompts/writer.md').read_bytes()==(ROOT/'experiments/goal_residual_control_v3_1/prompts/state_updater_gap_conditioned.md').read_bytes()

def prepare():
 write(TOP/'INITIAL_REQUESTS.json',actor_items(initial(),0))

def run():
 check();assert not (TOP/'RUN_STARTED.json').exists(),'No duplicate run/retry'
 write(TOP/'RUN_STARTED.json',{'head':head(),'utc':now(),'max_retries':0})
 cells=initial();searcher=None
 try:
  for rnd in range(3):
   check();base=TOP/f'round{rnd+1}';base.mkdir(exist_ok=False)
   reqs=actor_items(cells,rnd)
   if rnd==0:assert reqs==read(TOP/'INITIAL_REQUESTS.json')
   write(base/'requests.json',reqs)
   write(base/'REQUEST_FREEZE.json',{'head':head(),'utc':now(),'requests_sha256':sha(base/'requests.json'),'builder_sha256':sha(TOP/'run.py'),'previous_checkpoint_sha256':sha(TOP/f'round{rnd}/post_writer_cells.json') if rnd else None,'all_nonterminal_with_budget_continue':True})
   rows=batch(base,'actor',reqs)
   for r in rows:
    c=cells[r['case_id']+':'+r['arm']];c['decisions'].append({'round':rnd,'actor':r,'tool':None,'pre_claims':copy.deepcopy(c['claims']),'pre_hypothesis':c['hypothesis']})
    if r['output'] is None:c['status']='actor_failure'
    elif r['output']['decision']=='stop':c['status']='actor_stop'
    elif c['arm']=='D':c['need']=r['output']['gap']
   write(base/'post_actor_cells.json',cells)
   if AUTH.failure:raise RuntimeError('Auth failure; no more submissions')
   active=[c for c in cells.values() if c['status']=='active' and rnd<c['horizon']]
   if active and searcher is None:
    os.environ['BCPLUS_DEVICE']='cuda:1'
    from BCPlus.scripts.search_bcplus import BCPlusSearcher
    searcher=BCPlusSearcher()
   with (base/'tool_events.jsonl').open('x') as log:
    for c in active:
     d=c['decisions'][-1];a=d['actor']['output']['actions'][0]
     log.write(json.dumps({'kind':'started','case_id':c['case_id'],'action':a,'utc':now()})+'\n');log.flush()
     t=None
     try:
      t=restore(c['registry'],searcher);r=execute(t,a);c['registry']=registry(t)
     except Exception as e:r={'action':a,'result':None,'observations':[],'audit':None,'error':{'category':'tool failure','type':type(e).__name__,'message':str(e)[:1000]},'elapsed_seconds':None}
     finally:
      if t is not None:t.close()
     d['tool']=r
     seen={x['doc_ref'] for x in c['catalog']};c['catalog'].extend({k:x[k] for k in ('doc_ref','title','url')} for x in c['registry']['documents'] if x['doc_ref'] not in seen)
     if r['error']:c['status']='tool_failure'
     else:
      c['attempts'].append({'action':a,'status':r['result']['status'],'returned_windows':[w['window_ref'] for w in r['observations']]})
      for w in r['observations']:
       if w['window_ref'] not in {v['window_ref'] for v in c['visible_windows']}:
        c['visible_windows'].append({k:w[k] for k in ('window_ref','doc_ref','title','url','text')})
     log.write(json.dumps({'kind':'completed','case_id':c['case_id'],'record':r,'utc':now()},ensure_ascii=False)+'\n');log.flush()
     print('tool',rnd+1,c['case_id'],a['tool'],r['error'],flush=True);write(base/'tool_checkpoint.json',cells)
   write(base/'post_tool_cells.json',cells)
   maxw=max((len(c['decisions'][-1]['tool']['observations']) for c in active if c['status']=='active'),default=0)
   for wave in range(maxw):
    items=[];obs={};pre={}
    for c in active:
     if c['status']!='active':continue
     ws=c['decisions'][-1]['tool']['observations']
     if wave>=len(ws):continue
     w=ws[wave];key=c['case_id']+':'+c['arm'];obs[key]=w;pre[key]={'claims':copy.deepcopy(c['claims']),'hypothesis':c['hypothesis']}
     items.append(item(c,'state_updater',writer_view(c,w)))
    items=sorted(items,key=lambda it:digest(['bcplus-writer-order',rnd,wave,it['case_id']]))
    write(base/f'writer{wave}_requests.json',items)
    for r in batch(base,f'writer{wave}',items):
     key=r['case_id']+':'+r['arm'];c=cells[key];w=obs[key]
     if r['output'] is None:c['status']='writer_failure'
     else:
      o=r['output']
      for text in o['claims_to_add']:
       c['claims'].append({'statement':text,'support_refs':[w['window_ref']],'source_text_hashes':[w['text_sha256']],'first_seen_time':[{'round':rnd,'wave':wave}],'admission':'unrepaired U1; reviewed offline'});c['claims_version']+=1
      h=o['hypothesis_update'];old=c['hypothesis']
      if h['action']=='set':c['hypothesis']=h['statement']
      elif h['action']=='clear':c['hypothesis']=None
      if old!=c['hypothesis']:c['hypothesis_version']+=1
     c['updates'].append({'round':rnd,'wave':wave,'need':c['need'],'observation':w,'pre_state':pre[key],'proposal':r,'post_state':{'claims':copy.deepcopy(c['claims']),'hypothesis':c['hypothesis']}})
    write(base/'writer_checkpoint.json',cells)
    if AUTH.failure:raise RuntimeError('Auth failure; no more submissions')
   for c in active:
    if c['status']=='active' and rnd+1>=c['horizon']:c['status']='budget_exhausted'
   write(base/'post_writer_cells.json',cells)
  write(TOP/'RESULTS.json',cells);write(TOP/'RUN_COMPLETED.json',{'utc':now(),'head':head(),'cells':len(cells)})
 finally:
  if searcher is not None:searcher.close()

if __name__=='__main__':globals()[sys.argv[1]]()
