"""Frozen adaptive construction for controlled transitions and three-round loops."""
import copy,sys
from common import *
from tools_runner import create_searcher,restore,execute_batch,workspace

def journal_batch(base,tag,items):
    path=base/(tag+'_events.jsonl');assert not path.exists(),f'already attempted {path}'
    write(base/(tag+'_requests.json'),items);results={}
    with client() as c,path.open('w') as log:
        with ThreadPoolExecutor(max_workers=4) as pool:
            fs=[]
            for it in items:
                log.write(json.dumps({'kind':'request_started','time':now(),'item':it},ensure_ascii=False)+'\n');log.flush()
                fs.append(pool.submit(call,c,it))
            for f in as_completed(fs):
                ev,res=f.result();results[res['case_id'],res['arm']]=res
                log.write(json.dumps({'kind':'completed','event':ev,'result':res},ensure_ascii=False)+'\n');log.flush()
                print(tag,res['case_id'],res['arm'],'ok' if res['output'] else res['error']['type'],flush=True)
    ordered=[results[x['case_id'],x['arm']] for x in items];write(base/(tag+'_outputs.json'),ordered)
    return ordered

def update_view(state,obs):
    return {**goal_view(state),'Working Hypothesis':state['working_hypothesis'],
       'Observation':{k:v for k,v in obs.items() if k in ('title','url','text','window_ref','doc_ref')}}

def apply_update(state,output,obs,origin):
    before=digest({'claims':claims(state),'hypothesis':state['working_hypothesis']})
    for text in output['claims_to_add']:
        state['verified_claims'].append({'statement':text,'support_refs':[obs.get('window_ref',obs.get('source_id'))],
          'source_text_hashes':[hashlib.sha256(obs['text'].encode()).hexdigest()],
          'first_seen_time':[origin],'admission':'unrepaired online proposal; support judged offline'})
    h=output['hypothesis_update']
    if h['action']=='set':state['working_hypothesis']=h['statement']
    elif h['action']=='clear':state['working_hypothesis']=None
    return before!=digest({'claims':claims(state),'hypothesis':state['working_hypothesis']})

def freeze(which):
    base=TOP/which;assert not (base/'freeze.json').exists()
    extra={'phase':which,'max_decisions':1 if which=='transition_replan' else 3,
      'max_actions_per_decision':2,'updater':'one call per actual source window, max 2 claims; sequential within each trajectory',
      'failure':'no retry; invalid updater/goal/actor terminates dependent branch as failed; other arms continue',
      'dynamic_requests':'exact context builder below committed before calls; every constructed request journaled before submission'}
    if which=='transition_replan':
        extra['transition_order']=[t['transition_id'] for t in read(TOP/'bank/TRANSITIONS.json')]
        extra['arms']=['R0','R1','R2','R3']
    else:
        extra['selection']=read(base/'selection.json');extra['arms']=['L0','L1','L2']
        extra['stop']='L2 immediate resolved goal review; all Actor stops independently scored; horizon censoring is not a stop'
    freeze_stage(base,[],extra)
    f=read(base/'freeze.json');f['files'].update({str(p.relative_to(ROOT)):sha(p) for p in [Path(__file__),TOP/'tools_runner.py',TOP/'bank/SNAPSHOTS.json',TOP/'bank/TRANSITIONS.json',TOP/'bank/SOURCE_WINDOWS.json']})
    if which=='three_round_loop':f['files'][str((base/'selection.json').relative_to(ROOT))]=sha(base/'selection.json')
    write(base/'freeze.json',f)
    (base/'PROTOCOL.md').write_text('# '+which+'\n\n'+json.dumps(extra,ensure_ascii=False,indent=2)+'\n\nSee root PROTOCOL and REVIEW_RUBRIC. Oracle state is used only in R2 and offline review. Adaptive hypotheses/claims/residuals are never manually repaired.\n')

def gate(base):
    f=read(base/'freeze.json')
    assert all(sha(ROOT/p)==h for p,h in f['files'].items())
    assert subprocess.check_output(['git','show',f'HEAD:{(base/"freeze.json").relative_to(ROOT)}'],cwd=ROOT)==(base/'freeze.json').read_bytes()
    assert not (base/'run_started.json').exists(),'no duplicate adaptive run'
    write(base/'run_started.json',{'head':head(),'started_utc':now(),'freeze_sha256':sha(base/'freeze.json')})

def g4():
    base=TOP/'transition_replan';gate(base)
    bank={s['case_id']:s for s in read(TOP/'bank/SNAPSHOTS.json')};sources=read(TOP/'bank/SOURCE_WINDOWS.json')
    trans=read(TOP/'bank/TRANSITIONS.json');states={};failures={};update_records=[]
    for t in trans:
        s=copy.deepcopy(bank[t['pre_snapshot']]);s['available_workspace']=copy.deepcopy(bank[t['post_snapshot']]['available_workspace'])
        states[t['transition_id']]=s
    for wave in range(max(len(t['observation_source_refs']) for t in trans)):
        items=[];obsmap={};premap={}
        for t in trans:
            tid=t['transition_id']
            if tid in failures or wave>=len(t['observation_source_refs']):continue
            ref=t['observation_source_refs'][wave];src=sources[ref]
            w=next(w for w in bank[t['post_snapshot']]['available_workspace']['observed_windows'] if w['source_id']==ref)
            obsmap[tid]=w;premap[tid]=copy.deepcopy(states[tid])
            items.append(item(tid,t['qid'],'updater','state_updater',update_view(states[tid],w)))
        outputs=journal_batch(base,f'updater_{wave}',items)
        for x in outputs:
            tid=x['case_id'];obs=obsmap[tid]
            if x['output'] is None:failures[tid]=x['error']
            else:apply_update(states[tid],x['output'],obs,{'stage':'G4','transition_id':tid,'wave':wave})
            update_records.append({'transition_id':tid,'qid':x['qid'],'wave':wave,'pre_state':premap[tid],
              'observation':obs,'proposal':x,'post_state':copy.deepcopy(states[tid])})
    write(base/'state_updates.json',update_records);write(base/'online_post_states.json',states);write(base/'updater_failures.json',failures)
    items=[]
    for t in trans:
        tid=t['transition_id'];items.append(item(tid,t['qid'],'oracle','goal_reviewer',goal_view(bank[t['post_snapshot']])))
        if tid not in failures:items.append(item(tid,t['qid'],'online','goal_reviewer',goal_view(states[tid])))
    goals=journal_batch(base,'reviewer',items);gm={(x['case_id'],x['arm']):x for x in goals}
    items=[];actor_states={};inherited=[]
    for i,t in enumerate(trans):
        tid=t['transition_id'];order=['R0','R1','R2','R3'];order=order[i%4:]+order[:i%4]
        for arm in order:
            if arm!='R2' and tid in failures:inherited.append({'case_id':tid,'arm':arm,'reason':'updater_failure'});continue
            state=copy.deepcopy(bank[t['post_snapshot']] if arm=='R2' else states[tid]);res=None
            # Common attempt context and all observed source windows are identical.
            state['attempts']=recent(bank[t['post_snapshot']])
            if arm in ('R2','R3'):
                res=gm[tid,'oracle' if arm=='R2' else 'online']['output']
                if res is None:inherited.append({'case_id':tid,'arm':arm,'reason':'goal_failure'});continue
            actor_states[tid+':'+arm]=state
            items.append(item(tid,t['qid'],arm,'research_actor',actor_view(state,res,t['historical_active_gap'] if arm=='R0' else None)))
    actors=journal_batch(base,'actor',items);write(base/'actor_states.json',actor_states);write(base/'inherited_failures.json',inherited)
    searcher=create_searcher();results=[]
    try:
        with (base/'tool_events.jsonl').open('w') as log:
            for x in actors:
                tools=restore(actor_states[x['case_id']+':'+x['arm']],searcher)
                key={k:x[k] for k in ('case_id','qid','arm')};log.write(json.dumps({'kind':'start',**key})+'\n');log.flush()
                rec={**key,**execute_batch(tools,x['output'])};results.append(rec)
                log.write(json.dumps({'kind':'result',**rec},ensure_ascii=False)+'\n');log.flush();tools.close()
                print('G4 tools',x['case_id'],x['arm'],len(rec['actions']),flush=True)
    finally:searcher.close()
    write(base/'tool_outputs.json',results)

def g5():
    base=TOP/'three_round_loop';gate(base)
    bank={s['case_id']:s for s in read(TOP/'bank/SNAPSHOTS.json')};selection=read(base/'selection.json')
    searcher=create_searcher();cells={};order=[]
    for i,x in enumerate(selection):
        arms=['L0','L1','L2'];arms=arms[i%3:]+arms[:i%3]
        for arm in arms:
            key=x['qid']+':'+arm;s=copy.deepcopy(bank[x['snapshot_id']]);s['attempts']=recent(s)
            cells[key]={'cell':key,'qid':x['qid'],'arm':arm,'seed_snapshot':x['snapshot_id'],'state':s,
              'persistent_gap':s['historical_active_gap'],'residual':None,'residual_dirty':True,'status':'active','decisions':[],
              'updates':[],'goal_reviews':[],'tools':restore(s,searcher)};order.append(key)
    def save():
        write(base/'checkpoint.json',{k:{kk:vv for kk,vv in v.items() if kk!='tools'} for k,v in cells.items()})
    log=(base/'trajectories.jsonl').open('w')
    def emit(kind,**kw):log.write(json.dumps({'kind':kind,'time':now(),**kw},ensure_ascii=False)+'\n');log.flush()
    try:
        for rnd in range(3):
            items=[]
            for key in order:
                c=cells[key]
                if c['status']=='active' and c['arm']=='L2' and c['residual_dirty']:
                    items.append(item(key,c['qid'],c['arm'],'goal_reviewer',goal_view(c['state'])))
            goals=journal_batch(base,f'round{rnd}_reviewer',items)
            for x in goals:
                c=cells[x['case_id']];c['goal_reviews'].append({'round':rnd,'state':copy.deepcopy(c['state']),'result':x})
                c['residual']=x['output'];c['residual_dirty']=False
                if x['output'] is None:c['status']='reviewer_failure'
                elif x['output']['resolved']:c['status']='goal_stop';emit('goal_stop',cell=c['cell'],round=rnd,state=c['state'])
            items=[];prestates={}
            for key in order:
                c=cells[key]
                if c['status']!='active':continue
                prestates[key]=copy.deepcopy(c['state'])
                view=actor_view(c['state'],c['residual'] if c['arm']=='L2' else None,
                    c['persistent_gap'] if c['arm']=='L0' else None,3-rnd)
                items.append(item(key,c['qid'],c['arm'],'research_actor',view))
            actors=journal_batch(base,f'round{rnd}_actor',items);pending={}
            for x in actors:
                c=cells[x['case_id']];emit('tool_start',cell=c['cell'],round=rnd,output=x['output'])
                rec=execute_batch(c['tools'],x['output']);rec.update(round=rnd,actor=x,pre_state=prestates[c['cell']])
                c['decisions'].append(rec);emit('decision',cell=c['cell'],record=rec)
                if x['output'] is None:c['status']='actor_failure';continue
                if rec['error'] or any(a['error'] for a in rec['actions']):c['status']='tool_failure';continue
                if x['output']['decision']=='stop':c['status']='actor_stop';continue
                if c['arm']=='L0':c['persistent_gap']=x['output']['gap']
                c['state']['attempts'].extend([a['action']|{'result_status':a['result'].get('status'),'returned_windows':[w['window_ref'] for w in a['observations']]} for a in rec['actions']])
                c['state']['available_workspace']=workspace(c['tools'])
                pending[c['cell']]=[w for a in rec['actions'] for w in a['observations']]
            save()
            for wave in range(max((len(v) for v in pending.values()),default=0)):
                items=[];before={};obsmap={}
                for key in order:
                    c=cells[key]
                    if c['status']!='active' or wave>=len(pending.get(key,[])):continue
                    w=pending[key][wave];obsmap[key]=w;before[key]=copy.deepcopy(c['state'])
                    items.append(item(key,c['qid'],c['arm'],'state_updater',update_view(c['state'],w)))
                updates=journal_batch(base,f'round{rnd}_updater{wave}',items)
                for x in updates:
                    c=cells[x['case_id']];obs=obsmap[c['cell']]
                    if x['output'] is None:c['status']='updater_failure'
                    else:c['residual_dirty'] |= apply_update(c['state'],x['output'],obs,{'stage':'G5','round':rnd,'wave':wave})
                    rec={'round':rnd,'wave':wave,'pre_state':before[c['cell']],'observation':obs,'proposal':x,'post_state':copy.deepcopy(c['state'])}
                    c['updates'].append(rec);emit('state_update',cell=c['cell'],record=rec)
                save()
        # Review mutations after the final tool budget too: correct stopping is
        # observable without permitting a fourth Actor decision.
        items=[item(key,cells[key]['qid'],'L2','goal_reviewer',goal_view(cells[key]['state'])) for key in order
          if cells[key]['status']=='active' and cells[key]['arm']=='L2' and cells[key]['residual_dirty']]
        goals=journal_batch(base,'final_reviewer',items)
        for x in goals:
            c=cells[x['case_id']];c['goal_reviews'].append({'round':3,'state':copy.deepcopy(c['state']),'result':x});c['residual']=x['output'];c['residual_dirty']=False
            if x['output'] is None:c['status']='reviewer_failure'
            elif x['output']['resolved']:c['status']='goal_stop'
        for c in cells.values():
            if c['status']=='active':c['status']='horizon_exhausted'
        save();write(base/'results.json',{k:{kk:vv for kk,vv in v.items() if kk!='tools'} for k,v in cells.items()})
    finally:
        log.close()
        for c in cells.values():c['tools'].close()
        searcher.close()

if __name__=='__main__':
    if sys.argv[1]=='freeze':freeze(sys.argv[2])
    elif sys.argv[1]=='g4':g4()
    elif sys.argv[1]=='g5':g5()
