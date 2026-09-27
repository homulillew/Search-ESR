"""Mechanical accounting and compact review packets. No semantic scores inferred."""
from collections import Counter
import math
import statistics
from .common import *


def quantile(values,p):
    if not values:return None
    xs=sorted(values);pos=(len(xs)-1)*p;i=int(pos);f=pos-i
    return xs[i]*(1-f)+xs[min(i+1,len(xs)-1)]*f


def analyze():
    run=BASE/'run001';dest=BASE/'analysis';dest.mkdir(exist_ok=False)
    rows=[read(p) for p in sorted(run.glob('trajectories/*/calls/*.result.json'))]
    attempted=[r for r in rows if r['attempted']]
    complete=[r for r in attempted if r['accounting']['complete']]
    sums={k:sum(r['accounting']['tokens'][k] for r in complete) for k in ['input','output','total','hit','miss']}
    reason=sum(r['accounting']['tokens'].get('reasoning') or 0 for r in complete)
    latencies=[r['elapsed_seconds'] for r in attempted]
    summaries=[];packets=[];counts=Counter()
    for path in sorted(run.glob('trajectories/*/trace.jsonl')):
        lines=[json.loads(l) for l in path.open()]
        initial=lines[0]['state'];snapshot={k:initial[k] for k in ['Q','R','C','H']};events=[]
        traj=path.parent.name;step=0;blocks=[];block={'pre_state':json.loads(canonical(snapshot)),'events':[]}
        for e in lines[1:]:
            p=json.loads(e['payload_json']);event={'kind':e['kind'],**p};events.append(event)
            if e['kind'] in ('role_request','role_response','role_failure','step_failure','claim_committed','hypotheses_updated','closure_feedback','closure_ready','tool_observation','grounding_decision','final_answer','hypothesis_update_failed','hypothesis_update_skipped'):
                block['events'].append(event)
            if e['kind'] in ('hypothesis_update_failed','hypothesis_update_skipped'):counts[e['kind']]+=1
            if e['kind']=='claim_committed':snapshot['C'].append(p['claim']);counts['new_C']+=1
            if e['kind']=='hypotheses_updated':snapshot['H']=p['after']
            if e['kind']=='step_outcome':
                step+=1;block['slot']=step;block['outcome']=p;blocks.append(block)
                counts[p['feedback']]+=1
                decision=p.get('decision') or {};counts['decision_'+str(decision.get('decision'))]+=1
                if decision.get('action'):counts['tool_'+decision['action']['tool']]+=1
                block={'pre_state':json.loads(canonical(snapshot)),'events':[]}
        packet={'trajectory_id':traj,'initial_state':initial,'steps':blocks,'tail':block['events']}
        save(dest/'review_packets'/(traj+'.json'),packet)
        brief=[]
        for b in blocks:
            p=b['outcome'];d=p.get('decision') or {};claims=[e['claim'] for e in b['events'] if e['kind']=='claim_committed']
            hs=[e for e in b['events'] if e['kind']=='hypotheses_updated'];closures=[e for e in b['events'] if e['kind'] in ('closure_feedback','closure_ready')]
            brief.append({'slot':b['slot'],'decision':d,'feedback':p['feedback'],'gain_reasons':p['gain_reasons'],'failure':p['failure'],
                          'claims':claims,'H_after':hs[-1]['after'] if hs else [],'closure':closures,
                          'opportunities':p['new_source_opportunities'],'auxiliary_failures':p.get('auxiliary_failures',[]),'hypothesis_outcome':p.get('hypothesis_outcome'),'acquisition_outcome':p.get('acquisition_outcome'),'claim_outcome':p.get('claim_outcome')})
        summaries.append({'trajectory_id':traj,'status':read(path.parent/'RESULT.json')['status'],'steps':brief})
    accounting={'calls_attempted':len(attempted),'calls_not_sent':len(rows)-len(attempted),'failed_requests':sum(bool(r['error']) for r in attempted),
        'roles':dict(Counter(r['role'] for r in attempted)),'tokens_complete_records':sums,'reasoning_tokens_reported':reason,
        'cache_hit_rate':sums['hit']/sums['input'] if sums['input'] else None,
        'usage_complete_records':len(complete),'usage_missing_or_inconsistent':len(attempted)-len(complete),
        'usage_issues':[{'id':r['id'],'issues':r['accounting']['issues']} for r in attempted if not r['accounting']['complete']],
        'latency_seconds':{'min':min(latencies) if latencies else None,'p50':quantile(latencies,.5),'p90':quantile(latencies,.9),'p95':quantile(latencies,.95),'max':max(latencies) if latencies else None},
        'transport':read(run/'TRANSPORT_SUMMARY.json'),'completion':read(run/'COMPLETED.json'),
        'runtime_counts_unreviewed':dict(counts),'model_quality_scores':'Pending separate semantic review. Gain != useful evidence.'}
    save(dest/'ACCOUNTING.json',accounting);save(dest/'REVIEW_SUMMARY.json',summaries)
    print(json.dumps(accounting,ensure_ascii=False,indent=2))

if __name__=='__main__':analyze()
