from runtime import *
def main():
 base=TOP/'p1_progress';assert not (base/'freeze.json').exists()
 primary=rd(TOP/'bank/PRIMARY.json');challenge=rd(TOP/'bank/CHALLENGE.json')
 items=[item(c,a,r) for c in primary+challenge for a in ['R','B'] for r in [1,2]]
 full=set(rd(TOP/'bank/SELECTION.json')['full_sensitivity'])
 items.extend(item(c,'FULL',r) for c in primary if c['case_id'] in full for r in [1,2])
 items.sort(key=lambda x:dg(['dynamic-progress-order-20260926',x['id']]))
 assert len(items)==216
 wr(base/'requests.json',items)
 labels=rd(TOP/'bank/CHALLENGE_LABELS.json');old=rd(ROOT/'experiments/frontier_generation/f1_state_sufficiency/frontier_outputs.json')
 direct=[]
 for o in old:
  if o['arm']!='S':continue
  cid='C'+o['case_id'][1:];out=o['output'];gold=labels[cid]['gold_resolved'];stop=out is not None and out['decision']=='stop'
  direct.append({'case_id':cid,'historical_id':o['id'],'qid':o['qid'],'replicate':o['replicate'],'gold_resolved':gold,'resolved':stop if out else None,'correct_completion':out is not None and stop==gold,'false_closure':not gold and stop,'original_output':out})
 wr(base/'historical_direct_completion.json',direct)
 historical=subprocess.check_output(['git','ls-tree','-r','--name-only','fafe06019326cef35aa40f6e6092bbb5c725306f'],cwd=ROOT,text=True).splitlines()
 hist={p:sha(ROOT/p) for p in historical if (ROOT/p).is_file()}
 wr(TOP/'historical_baseline_hashes.json',hist)
 paths=[p for p in TOP.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
 pins=['experiments/model_backend_deepseek/provider.json','experiments/goal_residual_control/prompts/goal_reviewer.md','experiments/goal_residual_control/harness_v2/GOAL_RESPONSE_SCHEMA.json','experiments/goal_residual_control_v3_1/prompts/state_updater_gap_conditioned.md','experiments/frontier_generation/f1_state_sufficiency/frontier_outputs.json']
 paths += [ROOT/p for p in pins]
 wr(base/'freeze.json',{'created_utc':now(),'construction_head':head(),'base_head':'fafe06019326cef35aa40f6e6092bbb5c725306f','execution_head_policy':'Inputs and freeze must be committed; request journals exact execution HEAD.','provider':CONFIG,'sample_count':216,'primary':96,'challenge':96,'FULL':24,'replicates':2,'horizon':1,'tool_calls':0,'writer_calls':0,'max_retries':0,'best_of':0,'workers':4,'timeout_seconds':240,'failure_policy':'All planned slots counted; no repair/resample/overwrite; auth latch.','file_hashes':{str(p.relative_to(ROOT)):sha(p) for p in sorted(set(paths))},'request_hashes':{i['id']:i['request_sha256'] for i in items},'historical_tracked_count':len(hist),'historical_direct_completion':{'correct':sum(d['correct_completion'] for d in direct),'total':len(direct)},'gate':{'B_false_closure_max':4,'B_unresolved_denominator':42,'B_valid_presence_min':36,'B_precision_min':0.9,'B_correct_closure_min':6,'B_resolved_denominator':6,'challenge_accuracy_gain_min':0.1},'binary_policy':'No binary retrieval access; immutable historical corpus/index manifest remains authoritative; verify if P4 reached.'})
 print('Frozen',len(items),'requests;',len(hist),'historical files; Direct completion',sum(d['correct_completion'] for d in direct),'/48')
if __name__=='__main__':main()
