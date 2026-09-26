"""Deterministic historical selection; never loads new model outputs."""
import copy, json, sys
from runtime import *
OLD=ROOT/'experiments/goal_residual_control'

def canary():
    old=read(ROOT/'experiments/goal_residual_control_v3/structured_output_preflight/HISTORICAL_REQUESTS.json')
    items=[]
    for r in old:
        it=make_item(r['id'],r['qid'],'canary',r['kind'],r['old_request'],'responses_structured')
        it['historical']={k:r[k] for k in ['source_path','source_line','old_request_sha256','old_output_sha256','selection_stratum','categories']}
        assert it['request']['input']==r['old_request']['messages']
        items.append(it)
    freeze(TOP/'structured_transport_canary',items,{'selection':'reuse 24 previously frozen but never called v3 requests; 12 Actor, 8 Updater, 4 Goal',
      'decision_rule':'use responses_structured if all 24 return structurally valid objects; otherwise json_mode_fallback for all nodes. Harness violations reported separately, not a schema redesign trigger.',
      'no_tools':True,'canary_only_once':True})

def bank():
    base=TOP/'admission_replay';assert not (base/'BANK.json').exists()
    cells=read(OLD/'three_round_loop_v2/results.json');labels=read(OLD/'analysis_v2/UPDATER_LABELS.json')
    archived={}
    for p in sorted((OLD/'three_round_loop_v2').glob('*updater*_events.jsonl')):
        for line_no,line in enumerate(p.open(),1):
            e=json.loads(line)
            if e['kind']=='completed':
                r=e['result'];archived[r['case_id'],r['request_sha256']]={'source_file':str(p.relative_to(ROOT)),'source_line':line_no,'event':e}
    rows=[]
    for key,c in cells.items():
        for i,u in enumerate(c['updates']):
            d=next(d for d in c['decisions'] if d['round']==u['round']);a=d['actor'];assert a['output']['decision']=='act'
            r=u['proposal'];e=archived[key,r['request_sha256']];chat=e['event']['event']['request']
            # The old analysis digest uses compact separators.
            uid=hashlib.sha256(json.dumps([r['request_sha256'],r['output']],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()[:16]
            lab=labels.get(uid,{})
            out=r['output'];tags=[k for k,v in lab.items() if v is True]
            cl=lab.get('claims',[])
            if any(x.get('incidental') for x in cl):tags.append('incidental')
            if any(x.get('source_supported') and not x.get('incidental') for x in cl):tags.append('useful_positive')
            if any(x.get('material_qualifier_omission') for x in cl):tags.append('qualifier_omission')
            if out and not out['claims_to_add'] and out['hypothesis_update']['action']=='keep':tags.append('no_change')
            if out and len(out['claims_to_add'])==2:tags.append('multi_fact_page')
            if any(x.get('source_supported') and x.get('incidental') for x in cl):tags.append('supported_irrelevant')
            view=json.loads(chat['messages'][1]['content'])
            assert chat['messages'][0]['content']==(TOP/'prompts/state_updater_v2_control.md').read_text()
            assert view['Verified Claims']==[x['statement'] for x in u['pre_state']['verified_claims']]
            assert view['Observation']['text']==u['observation']['text']
            matches=[{'action_index':ai,'action':act['action'],'audit':act.get('audit')} for ai,act in enumerate(d['actions']) if any(w==u['observation'] for w in act['observations'])]
            assert matches
            pid=digest(['v3.1-bank',key,u['round'],u['wave'],r['request_sha256']])[:16]
            rows.append({'packet_id':pid,'qid':c['qid'],'cell':key,'round':u['round'],'wave':u['wave'],'update_index':i,
              'historical_review_id':uid,'selection_tags':sorted(set(tags)),'source_file':e['source_file'],'source_line':e['source_line'],
              'pre_state':u['pre_state'],'observation':u['observation'],'actor':a,'current_actor_gap':a['output']['gap'],
              'producing_actions':matches,'old_request':chat,'old_request_sha256':r['request_sha256'],'U0':r,
              'observation_sha256':digest(u['observation']),'pre_state_sha256':digest(u['pre_state'])})
    priority=['missed_discriminative_admission','qualifier_omission','missed_material_rejection','correct_material_rejection',
      'contradicted_hypothesis_set','spurious_hypothesis_clear','weak_hypothesis_replacement','weak_hypothesis_set',
      'unresolved_source_conflict','source_conflict_retained','incidental','useful_positive','no_change','multi_fact_page','supported_irrelevant']
    selected=[]
    for qid in sorted({r['qid'] for r in rows},key=int):
        pool=sorted([r for r in rows if r['qid']==qid],key=lambda r:digest(['admission-20260926-v3.1',r['packet_id']]))
        pick=[]
        for tag in priority:
            if len(pick)>=6:break
            if any(tag in r['selection_tags'] for r in pick):continue
            eligible=[r for r in pool if r not in pick and tag in r['selection_tags']]
            if eligible:pick.append(eligible[0])
        pick.extend([r for r in pool if r not in pick][:6-len(pick)])
        selected.extend(pick)
    write(base/'BANK.json',selected)
    write(base/'U0_ARCHIVED.json',[{'packet_id':r['packet_id'],**r['U0']} for r in selected])
    write(base/'SELECTION.json',{'seed':'admission-20260926-v3.1','priority':priority,'target_per_qid':6,
      'actual_per_qid':{q:sum(r['qid']==q for r in selected) for q in sorted({r['qid'] for r in rows},key=int)},
      'available_per_qid':{q:sum(r['qid']==q for r in rows) for q in sorted({r['qid'] for r in rows},key=int)},
      'rule':'within qid greedily cover first unmet stratum by seeded hash; fill to min(6,available). No redistribution or duplicated packets.',
      'candidate_or_final_relation':'semantic coverage characterized during pre-call atom review, not post-output selection'})
    packets=[{'packet_id':r['packet_id'],'qid':r['qid'],'question':r['pre_state']['question'],
      'claims_before':[c['statement'] for c in r['pre_state']['verified_claims']],
      'hypothesis_before':r['pre_state']['working_hypothesis'],'gap':r['current_actor_gap'],'observation':r['observation']} for r in selected]
    write(base/'PREFIX_REVIEW_PACKETS.json',packets)
    print('Selected',len(selected),'of',len(rows),'labels matched',sum(bool(r['selection_tags']) for r in rows))

if __name__=='__main__':globals()[sys.argv[1]]()
