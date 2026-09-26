"""Frozen two-decision builder; no semantic routing or evaluation imports."""
import copy,json,os,sys,hashlib,subprocess
from pathlib import Path
from runtime import TOP,ROOT,read,write,digest,sha,now,head,CONFIG,make_item,batch,AUTH
from tools import restore,registry,execute
from llm_chat.search_find_agent import SEARCH_FIND_TOOLS

def catalog(reg):return [{k:d[k] for k in ('doc_ref','title','url')} for d in reg['documents']]
def initial():
 cells={}
 for i,b in enumerate(read(TOP/'bank/RECOVERY_BANK.json')):
  for arm in (['G','H'] if i%2==0 else ['H','G']):
   key=b['case_id']+':'+arm
   cells[key]={'cell':key,'case_id':b['case_id'],'qid':b['qid'],'arm':arm,'question':b['original_question'],
    'claims':copy.deepcopy(b['claims_at_recovery_start']),'hypothesis':b['working_hypothesis'],'need':b['recovery_need'],
    'registry':copy.deepcopy(b['registry']),'catalog':copy.deepcopy(b['historical_document_catalog']),
    'attempts':[],'visible_windows':[],'status':'active','decisions':[],'updates':[]}
 return cells

def actor_view(c,rnd):
 return {'Original Question':c['question'],'Current Claims':[x['statement'] for x in c['claims']],
  'Working Hypothesis':c['hypothesis'],'Current Recovery Need':c['need'],
  'Historical Document Catalog':c['catalog'],'Recent Attempts':c['attempts'],'New Observations':c['visible_windows'],
  'Budget':{'remaining_decisions':2-rnd,'max_actions_this_decision':1},
  'Tool schema':SEARCH_FIND_TOOLS[:1] if c['arm']=='G' else SEARCH_FIND_TOOLS,
  'Response schema':read(TOP/'schemas'/f"actor_{c['arm']}.json")}

def item(c,kind,view):
 prompt=(TOP/'prompts'/('actor.md' if kind.startswith('actor_') else 'writer.md')).read_text()
 chat={'model':CONFIG['model'],'messages':[{'role':'system','content':prompt},{'role':'user','content':json.dumps(view,ensure_ascii=False)}],'stream':False}
 return make_item(c['case_id'],c['qid'],c['arm'],kind,chat,'json_mode_fallback')

def actor_items(cells,rnd):return [item(c,'actor_'+c['arm'],actor_view(c,rnd)) for c in cells.values() if c['status']=='active']

def writer_view(c,w):return {'Original Question':c['question'],'Verified Claims':[x['statement'] for x in c['claims']],
 'Working Hypothesis':c['hypothesis'],'Current Research Gap':c['need'],
 'Observation':{k:w[k] for k in ('title','url','text','window_ref','doc_ref')}}

def check():
 f=read(TOP/'freeze.json')
 for p,h in f['files'].items():assert sha(ROOT/p)==h,p
 assert subprocess.check_output(['git','show','HEAD:experiments/deferred_recovery/freeze.json'])==(TOP/'freeze.json').read_bytes()
 # Heavy corpus/embedding checks occur at pre-call freeze and final integrity; metadata checked at every stage.
 for p,s in f['binary_files'].items():
  st=Path(p).stat();assert (st.st_size,st.st_mtime_ns)==(s['size'],s['mtime_ns']),p
 assert (TOP/'prompts/writer.md').read_bytes()==(ROOT/'experiments/goal_residual_control_v3_1/prompts/state_updater_gap_conditioned.md').read_bytes()

def actors(rnd):
 check();base=TOP/f'r{rnd+1}';cells=initial() if rnd==0 else read(TOP/'r1/post_writer_cells.json')
 reqs=actor_items(cells,rnd)
 if rnd==0:assert reqs==read(base/'requests.json')
 else:
  assert reqs==read(base/'requests.json')
  for name in ('requests.json','continuation_freeze.json'):
   assert subprocess.check_output(['git','show','HEAD:'+str((base/name).relative_to(ROOT))])==(base/name).read_bytes()
 rows=batch(base,'actor',reqs)
 for r in rows:
  c=cells[r['case_id']+':'+r['arm']];c['decisions'].append({'round':rnd,'actor':r,'tool':None,'pre_claims':copy.deepcopy(c['claims'])})
  if r['output'] is None:c['status']='actor_failure'
  elif r['output']['decision']=='stop':c['status']='actor_stop'
 write(base/'post_actor_cells.json',cells)

def tools(rnd):
 check();base=TOP/f'r{rnd+1}';cells=read(base/'post_actor_cells.json');ev=base/'tool_events.jsonl';assert not ev.exists()
 os.environ['BCPLUS_DEVICE']='cuda:1'
 from BCPlus.scripts.search_bcplus import BCPlusSearcher
 s=BCPlusSearcher()
 try:
  with ev.open('x') as log:
   for key,c in cells.items():
    if c['status']!='active':continue
    d=c['decisions'][-1];a=d['actor']['output']['actions'][0]
    log.write(json.dumps({'kind':'started','cell':key,'action':a,'utc':now()})+'\n');log.flush()
    t=restore(c['registry'],s);r=execute(t,a);d['tool']=r;c['registry']=registry(t)
    # New docs appear normally. Keep existing observed catalog metadata unchanged.
    seen={x['doc_ref'] for x in c['catalog']};c['catalog'].extend(x for x in catalog(c['registry']) if x['doc_ref'] not in seen)
    if r['error']:c['status']='tool_failure'
    else:
     c['attempts'].append({'action':a,'status':r['result']['status'],'returned_windows':[w['window_ref'] for w in r['observations']]})
     for w in r['observations']:
      if w['window_ref'] not in {v['window_ref'] for v in c['visible_windows']}:
       c['visible_windows'].append({k:w[k] for k in ('window_ref','doc_ref','title','url','text')})
    log.write(json.dumps({'kind':'completed','cell':key,'record':r,'utc':now()},ensure_ascii=False)+'\n');log.flush();t.close()
    print('tools',rnd,key,a['tool'],r['error'],flush=True)
    write(base/'tool_checkpoint.json',cells)
 finally:s.close()
 write(base/'post_tool_cells.json',cells)

def writers(rnd):
 check();base=TOP/f'r{rnd+1}';cells=read(base/'post_tool_cells.json');assert not (base/'writer_started.json').exists()
 write(base/'writer_started.json',{'head':head(),'utc':now()})
 maxw=max((len(c['decisions'][-1]['tool']['observations']) for c in cells.values() if c['status']=='active'),default=0)
 for wave in range(maxw):
  items=[];ob={};pre={}
  for key,c in cells.items():
   if c['status']!='active':continue
   obs=c['decisions'][-1]['tool']['observations']
   if wave>=len(obs):continue
   w=obs[wave];ob[key]=w;pre[key]={'claims':copy.deepcopy(c['claims']),'hypothesis':c['hypothesis']}
   items.append(item(c,'state_updater',writer_view(c,w)))
  rows=batch(base,f'writer{wave}',items)
  for r in rows:
   key=r['case_id']+':'+r['arm'];c=cells[key];w=ob[key]
   if r['output'] is None:c['status']='writer_failure'
   else:
    o=r['output']
    for txt in o['claims_to_add']:
     c['claims'].append({'statement':txt,'support_refs':[w['window_ref']],'source_text_hashes':[w['text_sha256']],
       'first_seen_time':[{'round':rnd,'wave':wave}],'admission':'unrepaired online U1 proposal; semantic support evaluated offline'})
    h=o['hypothesis_update']
    if h['action']=='set':c['hypothesis']=h['statement']
    elif h['action']=='clear':c['hypothesis']=None
   c['updates'].append({'round':rnd,'wave':wave,'observation':w,'pre_state':pre[key],'proposal':r,'post_state':{'claims':copy.deepcopy(c['claims']),'hypothesis':c['hypothesis']}})
  write(base/'writer_checkpoint.json',cells)
  if AUTH.failure:raise RuntimeError('authentication rejected; stop submissions')
 write(base/'post_writer_cells.json',cells)

def continuation():
 check();base=TOP/'r2';assert not (base/'requests.json').exists()
 cells=read(TOP/'r1/post_writer_cells.json');write(base/'requests.json',actor_items(cells,1))
 write(base/'continuation_freeze.json',{'head':head(),'utc':now(),'r1_cells_sha256':sha(TOP/'r1/post_writer_cells.json'),
  'requests_sha256':sha(base/'requests.json'),'all_nonterminal_continue':True,'no_gold_stopping':True,'planned':len(actor_items(cells,1))})

if __name__=='__main__':
 if sys.argv[1]=='continuation':continuation()
 else:globals()[sys.argv[1]](int(sys.argv[2]))
