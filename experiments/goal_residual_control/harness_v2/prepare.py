"""Append-only freezes and exact G2 request-object comparison."""
import copy,sys
from runtime import *

def g2():
    base=TOP/'research_decision_v2';old_items=read(TOP/'research_decision/REQUESTS.json')
    appendix=(HERE/'actor_contract.md').read_text();items=[];audit=[]
    for old_it in old_items:
        it=copy.deepcopy(old_it);it['request']['messages'][0]['content']+=appendix
        it['request_sha256']=digest(it['request']);items.append(it)
        stripped=copy.deepcopy(it['request']);stripped['messages'][0]['content']=stripped['messages'][0]['content'][:-len(appendix)]
        assert stripped==old_it['request']
        assert it['request']['messages'][1:]==old_it['request']['messages'][1:]
        audit.append({'case_id':it['case_id'],'arm':it['arm'],'old_request_sha256':old_it['request_sha256'],
          'new_request_sha256':it['request_sha256'],'user_messages_equal':True,'api_fields_equal':True,
          'old_system_is_exact_prefix':True,'only_difference':'appended explicit response contract/examples'})
    write(base/'REQUEST_DIFF_AUDIT.json',{'pairs':audit,'all_equal_except_contract':True,'contract_sha256':sha(HERE/'actor_contract.md'),
      'reused_G1_sha256':sha(TOP/'goal_review/outputs.json'),'same_order':True,'old_validity_immutable':'75/120'})
    old_paths=subprocess.check_output(['git','ls-tree','-r','--name-only','f53a43c','--','experiments/goal_residual_control'],cwd=ROOT,text=True).splitlines()
    write(HERE/'HISTORICAL_ARTIFACT_HASHES.json',{p:sha(ROOT/p) for p in old_paths})
    write(base/'PREFLIGHT.json',{'engineering_commit':'4346276','maintained_full_offline_suite':'python -m pytest -q tests',
      'offline_result':'427 passed, 2 dependency deprecation warnings; 22.63 seconds',
      'new_contract_tests':31,'model_calls_before_freeze':0,'object_comparison_pairs':120,
      'auth_fix_ancestor':'8021aca19a1ee5201730e40b338012c65ecd51cf','new_merge_or_cherry_pick':None})
    (base/'PROTOCOL.md').write_text('# G2v2\n\n40 unchanged snapshots × A0/A1/A2; 120 single calls in the original order. Same user messages, old G1 residuals, model/config and four-worker policy. Only an explicit system serialization contract is appended. k is required in the response, with unchanged Search semantics. Zero retries; ≥80% valid permits G3–G5. Old G2 remains 75/120. See REQUEST_DIFF_AUDIT, PREFLIGHT and ../harness_v2/PROTOCOL_AMENDMENT.md.\n')
    freeze_stage(base,items,{'phase':'G2v2','request_diff_audit_sha256':sha(base/'REQUEST_DIFF_AUDIT.json'),
      'old_requests_sha256':sha(TOP/'research_decision/REQUESTS.json'),'G1_outputs_sha256':sha(TOP/'goal_review/outputs.json'),
      'horizon':1,'planned':120,'engineering_target':.90,'ideal':.95,'execution_minimum':.80,
      'planned_followups':['G3v2','G4v2','G5v2'],'no_effect_gate':True})

if __name__=='__main__':{'g2':g2}[sys.argv[1]]()
