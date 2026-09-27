"""Prefix-bounded mechanical reconstruction; never read later Actor/Writer files.
Only whitelist projections enter payloads. Source metadata is separate from model input.
"""
from datetime import datetime
from .common import *
ALLOWED={'search':'Search','find':'Find','open':'Open'}
def claims(s):return [{'claim_id':f'C{i+1}','statement':v['statement']} for i,v in enumerate(s['claims'])]
def delta(current, previous):
 old={x['statement'] for x in previous}
 return [x for x in current if x['statement'] not in old]
def construct(c):
 accessed={}
 def get(path):
  accessed[rel(path)]=sha(path);return read(path)
 path=ROOT/c['snapshot'];snap=get(path);folder=path.parent
 assert snap['state_id']==c['state_id'] and sha(path)==c['snapshot_sha256']
 assert snap['state']['question']==c['belief']['question'] and claims(snap['state'])==c['claims']
 sn=int(path.stem[1:]);previous=get(folder/f'S{sn-1:02}.json') if sn else None
 dc=delta(c['claims'],claims(previous['state'])) if previous else []
 init=get(folder/'S00.json');assert init['transition']=='initial'
 initial_request=get(folder/'calls/actor_1.request.json')
 initial_view=json.loads(initial_request['request']['messages'][1]['content'])
 assert initial_view['Original Question']==c['belief']['question']
 assert initial_view['Current Claims']==[x['statement'] for x in init['state']['claims']]
 events=[];last_state=init['state'];start=initial_request['started_utc'];end=start
 stop=(0,0) if snap['transition']=='initial' else tuple(map(int,snap['transition'].removeprefix('update_').split('_')))
 for step in range(1,stop[0]+1):
  toolpath=folder/f'decision{step}_tool.json';raw=get(toolpath)
  started=get(folder/f'decision{step}_tool_started.json')
  assert started['action']==raw['action'] and raw['error'] is None
  # This tool returned before writer_1. No later Actor request is read for visibility.
  first_request=get(folder/f'calls/writer_{step}_1.request.json')
  tool_end_upper=first_request['started_utc']
  visible=[{k:w[k] for k in ('window_ref','doc_ref','title','url','text')} for w in raw['observations']]
  events.append({'event_index':len(events)+1,'event_type':ALLOWED[raw['action']['tool']],
   'argument':{k:v for k,v in raw['action'].items() if k!='tool'},
   'observed_refs':list(dict.fromkeys([r for w in visible for r in (w['doc_ref'],w['window_ref'])])),
   'claim_delta':[],'source_file':rel(toolpath),'started_utc':started['utc'],'completed_by_utc':tool_end_upper,
   'observations':visible})
  waves=stop[1] if step==stop[0] else len(raw['observations'])
  for wave in range(1,waves+1):
   upath=folder/f'update_{step}_{wave}.json';u=get(upath)
   request=get(folder/f'calls/writer_{step}_{wave}.request.json')
   view=json.loads(request['request']['messages'][1]['content'])
   assert u['round']==step and u['wave']==wave
   assert u['pre_state']==last_state and u['observation']==raw['observations'][wave-1]
   assert view['Original Question']==c['belief']['question']
   assert view['Verified Claims']==[x['statement'] for x in last_state['claims']]
   assert view['Observation']=={k:visible[wave-1][k] for k in ('title','url','text','window_ref','doc_ref')}
   new=delta(claims(u['post_state']),claims(u['pre_state']))
   assert [x['statement'] for x in new]==u['writer']['output']['claims_to_add']
   # All original trajectories append claims, with no removal or renumbering.
   assert claims(u['post_state'])[:len(last_state['claims'])]==claims(last_state)
   assert all(x in c['claims'] for x in new)
   last_state=u['post_state'];end=u['writer']['completed_utc']
   events.append({'event_index':len(events)+1,'event_type':'WriterUpdate',
    'argument':{'window_ref':u['observation']['window_ref']},
    'observed_refs':[u['observation']['doc_ref'],u['observation']['window_ref']],
    'claim_delta':[x['claim_id'] for x in new],'source_file':rel(upath),
    'started_utc':request['started_utc'],'completed_by_utc':end,'observations':[]})
 assert last_state==snap['state']
 checkpoint=len(events)
 assert all(0<e['event_index']<=checkpoint for e in events)
 assert all(start<=e['started_utc']<=e['completed_by_utc']<=end for e in events)
 assert all(events[i]['completed_by_utc']<=events[i+1]['started_utc'] for i in range(len(events)-1))
 recent=events[-4:]
 payload_path=[{'step_offset':e['event_index']-checkpoint,**{k:e[k] for k in ('event_type','argument','observed_refs','claim_delta')}} for e in recent]
 # Arrival ordering is event index; simultaneous batch windows tie-break by original array index.
 # Descending index is the preregistered mechanical most-recent-first tie-break, not relevance.
 candidates=[(e,i,w) for e in recent if e['event_type'] in ('Search','Find','Open') for i,w in enumerate(e['observations'])]
 chosen=sorted(candidates,key=lambda t:(t[0]['event_index'],t[1]),reverse=True)[:2]
 obs=[{'observation_ref':w['window_ref'],'source_ref':w['doc_ref'],'text':w['text']} for _,_,w in chosen]
 contexts={a:{'recent_claim_delta':dc if a!='C0' else [],'recent_events':payload_path if a in ('C1','C2') else [],'recent_observations':obs if a=='C2' else []} for a in ARMS}
 source={'case_id':c['case_id'],'state_id':c['state_id'],'source_run':'experiments/belief_need_budget_locality_repair/acquisition',
  'source_file':c['snapshot'],'source_event_index':checkpoint,'event_index_convention':'initial=0, tools and every Writer response indexed in execution order, including no-change updates',
  'question_hash':digest(c['belief']['question']),'claims_hash':digest(c['claims']),'prefix_start':start,'prefix_end':end,
  'has_previous_checkpoint':previous is not None,'previous_checkpoint':rel(folder/f'S{sn-1:02}.json') if sn else None,
  'has_recent_path':bool(payload_path),'has_recent_observation':bool(obs),
  'context_sources':accessed,'recent_event_indices':[e['event_index'] for e in recent],
  'observation_sources':[{'event_index':e['event_index'],'source_file':e['source_file'],'array_index':i,'text_sha256':digest(w['text'])} for e,i,w in chosen]}
 availability={k:source[k] for k in ('case_id','state_id','has_previous_checkpoint','has_recent_path','has_recent_observation')}
 availability.update(delta_context_available=previous is not None,delta_eligible=bool(previous and dc),path_eligible=bool(payload_path),observation_eligible=bool(obs),delta_count=len(dc),event_count=len(payload_path),observation_count=len(obs))
 # Archive ONLY control projections + provenance, never Writer H/reasoning/need.
 audit_events=[{k:v for k,v in e.items() if k!='observations'} for e in events]
 return contexts,source,availability,audit_events

def prepare_context():
 contexts={a:{} for a in ARMS};sources=[];availability=[];audit=[]
 for c in bank().values():
  cc,s,av,ee=construct(c)
  for a in ARMS:contexts[a][c['case_id']]=cc[a]
  sources.append(s);availability.append(av)
  audit.append({'case_id':c['case_id'],'checkpoint_index':s['source_event_index'],'checkpoint_utc':s['prefix_end'],'events':ee,'status':'PASS'})
 for a in ARMS:write(P/f'e0_context/CONTEXT_{a}.json',contexts[a])
 write(P/'e0_context/SOURCE_MAP.json',sources);write(P/'e0_context/AVAILABILITY.json',availability)
 write(P/'analysis/PREFIX_LEAKAGE_AUDIT.json',{'status':'PASS','cases':audit,'future_result_files_read':0,
  'actor_visibility':'Exact bounded observations appended to historical actor_view visible_windows before Writer waves, per acquisition/run.py. Intermediate snapshots have no contemporaneous Actor API call; no future Actor request used as proof. Text is the available Actor-view buffer, not a claim that a separate Actor call consumed it at each checkpoint.',
  'simultaneous_window_tie_break':'descending original observation array index within each completed tool return; no semantic selection'})
 subsets={k:[a['case_id'] for a in availability if a[k]] for k in ('has_previous_checkpoint','delta_eligible','path_eligible','observation_eligible')}
 write(P/'analysis/CONTEXT_AVAILABILITY.json',{'counts':{k:len(v) for k,v in subsets.items()},'subsets':subsets,'all_states':27})
 write(P/'e0_context/REPORT.md','# Mechanical context reconstruction\n\n'+json.dumps({k:len(v) for k,v in subsets.items()},indent=2)+'\n\nAll 27 exact historical states retained. Recent path includes every completed Writer update, even unchanged claims. A path containing only Writer updates has no eligible Search/Find/Open observation. Within a single tool batch, descending array index is a deterministic recency tie-break. No semantic relevance selection.\n\nExact bounded text comes from the historical tool return and actor_view buffer projection before writers, without reading a later Actor request. Intermediate Writer checkpoints have no contemporaneous Actor call; this limitation is disclosed, not represented as model-consumed text at each checkpoint.\n')
if __name__=='__main__':prepare_context()
