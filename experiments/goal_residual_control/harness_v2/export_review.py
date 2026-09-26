"""Arm-hidden review packets; production inputs never consume these files."""
from runtime import *

def bank():return {s['case_id']:s for s in read(TOP/'bank/SNAPSHOTS.json')}
def g2():
    base=TOP/'research_decision_v2';states=bank();truth=read(TOP/'bank/PRIVATE_TRUTH.json')['snapshots']
    rows=[]
    for line in (base/'actor_events.jsonl').open():
        e=json.loads(line)
        if e['kind']=='completed':rows.append(e['result'])
    keys=sorted(read(base/'REQUESTS.json'),key=lambda x:digest(['G2v2',x['case_id'],x['arm']]))
    mapping={f'B{i:03}':{'case_id':x['case_id'],'arm':x['arm']} for i,x in enumerate(keys,1)}
    rows={(x['case_id'],x['arm']):x for x in rows};packets=[]
    for pid,key in mapping.items():
        cid=key['case_id'];x=rows.get((cid,key['arm']))
        if not x:continue
        s=states[cid];packets.append({'packet_id':pid,'qid':s['qid'],'question':s['question'],
          'verified_claims':claims(s),'working_hypothesis':s['working_hypothesis'],'gold_residual':truth[cid],
          'workspace':old.public_workspace(s['available_workspace']),'decision':x['output'],'error':x['error']})
    write(base/'REVIEW_PACKETS.json',packets);write(base/'PRIVATE_PACKET_MAP.json',mapping)

def progress(stage):
    base=TOP/stage;states=bank();truth=read(TOP/'bank/PRIVATE_TRUTH.json')['snapshots']
    if stage=='one_step_acquisition_v2':
        rows=read(base/'outputs.json');state_for=lambda x:states[x['case_id']];truth_for=lambda x:truth[x['case_id']]
    elif stage=='transition_replan_v2':
        rows=read(base/'tool_outputs.json');ast=read(base/'actor_states.json');ts={t['transition_id']:t for t in read(TOP/'bank/TRANSITIONS.json')}
        state_for=lambda x:ast[x['case_id']+':'+x['arm']];truth_for=lambda x:truth[ts[x['case_id']]['post_snapshot']]
    else:raise ValueError(stage)
    mapping={};packets=[];catalog={};pool=read(TOP/'bank/PRIVATE_TRUTH.json')['known_source_sets'];hist=read(TOP/'bank/HISTORICAL_SOURCE_SETS.json')['historical_fact_source_sets']
    for i,x in enumerate(sorted(rows,key=lambda x:digest([stage,x['case_id'],x['arm']])),1):
        pid=f'E{i:03}';state=state_for(x);observations=[]
        mapping[pid]={'case_id':x['case_id'],'qid':x['qid'],'arm':x['arm'],'actions':[]}
        for ai,a in enumerate(x['actions']):
            ids=[];docids={d['doc_ref']:d['docid'] for d in a.get('audit',{}).get('handles',{}).get('documents',[])}
            for w in a['observations']:
                sid=digest([x['qid'],w['url'],w['text']])[:16]
                did=docids.get(w['doc_ref']);known=set(pool[x['qid']]['verified_fact_source_docids'])|set(hist.get(x['qid'],[]))
                catalog.setdefault(sid,{'evidence_id':sid,'qid':x['qid'],'question':state['question'],
                  'title':w['title'],'url':w['url'],'text':w['text'],'docid':did,'in_primary_pool':did in known,
                  'text_sha256':hashlib.sha256(w['text'].encode()).hexdigest()})
                observations.append({'evidence_id':sid,**w});ids.append(sid)
            mapping[pid]['actions'].append({'action_index':ai,'action':a['action'],'evidence_ids':ids,'error':a['error']})
        packets.append({'packet_id':pid,'qid':x['qid'],'question':state['question'],'verified_claims':claims(state),
          'gold_residual_rubric':truth_for(x),'gold_note':'frozen oracle reference; online state adequacy requires independent review' if stage=='transition_replan_v2' else 'frozen current state',
          'selected_gap':x['decision']['gap'] if x['decision'] else None,'decision':x['decision']['decision'] if x['decision'] else None,
          'observations':observations,'error':x['error']})
    write(base/'REVIEW_PACKETS.json',packets);write(base/'PRIVATE_PACKET_MAP.json',mapping)
    write(base/'EVIDENCE_CATALOG.json',sorted(catalog.values(),key=lambda x:(x['qid'],x['evidence_id'])))
    print(stage,'packets',len(packets),'unique windows',len(catalog))

if __name__=='__main__':g2() if sys.argv[1]=='g2' else progress(sys.argv[1])
