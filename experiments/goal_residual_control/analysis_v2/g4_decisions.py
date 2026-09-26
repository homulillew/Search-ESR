from progress import *
b=TOP/'transition_replan_v2';outs=read(b/'actor_outputs.json');states=read(b/'actor_states.json');k=read(b/'ONLINE_KNOWLEDGE_REVIEW.json');rows=[];packets=[]
for i,x in enumerate(sorted(outs,key=lambda x:digest(['G4-decision',x['request_sha256'],x['arm']])),1):
 key=x['case_id']+':'+x['arm'];s=states[key];o=x['output'];gold=k['closure'][key];stop=o is not None and o['decision']=='stop';sha=x['request_sha256'][:10]
 packets.append({'packet_id':f'S{i:03}','qid':x['qid'],'question':s['question'],'claims':[c['statement'] for c in s['verified_claims']],'hypothesis':s['working_hypothesis'],'workspace':s['available_workspace'],'decision':o,'error':x['error']})
 lock=sha=='526b2f72b5';over=sha in ['526b2f72b5','96698d0570','a393373d4f','de8778469a','f5d3cc2810','587bb6f257']
 rows.append({'packet_id':f'S{i:03}','case_id':x['case_id'],'qid':x['qid'],'arm':x['arm'],'request_sha256':x['request_sha256'],'valid':o is not None,'gold_resolved':gold,'correct_stop':stop and gold,'premature_stop':stop and not gold,'late_stop':bool(o and not stop and gold),'goal_drift':False if o else None,'hypothesis_lock':lock,'stale_gap_continuation':lock,'hypothesis_overcommit':over,'residual_reducing':bool(o and not stop and not gold and not lock),'strict_correct_stop':stop and gold and x['qid']!='435','strict_premature_stop':stop and (not gold or x['qid']=='435'),'reason':'Continues Heart birth-name lookup despite cleared hypothesis and observed timing contradiction.' if lock else 'Treats unsupported temporal join as count to confirm at the May feature.' if sha=='587bb6f257' else 'Calls Rangers already identified despite unresolved original club/season constraints; requested founding relation is still useful.' if over else 'Original-goal-directed exploration or source checking; candidate name alone is not verified identity.' if o and not stop else 'STOP evaluated against independently supported current Claims, not oracle truth transplanted to online state.' if stop else 'Strict schema failure; no repair or tools.'})
write(b/'DECISION_REVIEW_PACKETS.json',packets);write(b/'decision_reviews.json',rows)
metrics={}
for a in ['R0','R1','R2','R3']:
 rr=[r for r in rows if r['arm']==a];metrics[a]={'planned':20,'resolved':sum(r['gold_resolved'] for r in rr),'open':sum(not r['gold_resolved'] for r in rr),**{k:sum(r[k] is True for r in rr) for k in ['valid','correct_stop','premature_stop','late_stop','goal_drift','hypothesis_lock','stale_gap_continuation','hypothesis_overcommit','residual_reducing','strict_correct_stop','strict_premature_stop']}}
write(b/'decision_metrics.json',metrics)
# Reviewer fidelity is reviewed on source-grounded claims; hypotheses were absent.
gr=[]
for x in read(b/'reviewer_outputs.json'):
 key=x['case_id']+(':'+('R2' if x['arm']=='oracle' else 'R3'));gold=k['closure'][key];o=x['output'];badjoin=x['case_id']=='T19' and x['arm']=='online'
 gr.append({'case_id':x['case_id'],'arm':x['arm'],'gold_resolved':gold,'output':o,'closure_correct':bool(o and o['resolved']==gold),'premature':bool(o and o['resolved'] and not gold),'unsupported_state_propagation':badjoin,'new_goal_drift':False,'residual_fidelity':'false temporal premise inherited from updater' if badjoin else 'identity prematurely closed' if o and o['resolved'] and not gold else 'open requirements retained or supported closure','notes':'T09 online wording calls the game identified despite remaining developer/single-player/shareware checks; closure stays open.' if x['case_id']=='T09' and x['arm']=='online' else 'T07 keeps birth-name uncertainty but does not emphasize incumbent timing exclusion.' if x['case_id']=='T07' else ''})
write(b/'goal_reviews.json',gr)
print(json.dumps(metrics,indent=2))
