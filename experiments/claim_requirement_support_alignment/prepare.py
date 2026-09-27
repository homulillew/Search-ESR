"""Offline preparation. Exact user-supplied system prompts; no model calls."""
import re
from .common import *

def main():
 task=(P/'TASK.md').read_text()
 for arm,section in [('S0',17),('S1',19),('RESIDUAL',28)]:
  block=re.search(r'# '+str(section)+r'\.[\s\S]*?```text\n([\s\S]*?)```',task).group(1)
  write(P/f'prompts/{arm}.txt',block)
 write(P/'prompts/D0_ADAPTER.txt','For this raw-Claims diagnostic only, first internally identify which supplied Claims qualify as substantive support under the evidence rules above. Treat only that internally identified support as eligible for subtraction. Do not output the assignment; return only the required residual JSON.\n')
 previous=read(ROOT/'experiments/state_conditioned_residualization/CONFIG.json')
 cfg={k:previous[k] for k in ['provider','endpoint','base_url','model','temperature','max_retries','max_workers','replicates','max_tokens_policy','response_format','timeout_seconds','timeout_semantics','halt_http_statuses','credential_source','tool_calls','horizon']}
 cfg.update(planned_E1=96,conditional_E2_maximum=192,permission='TASK20: new explicit E1 approval after actual request freeze/commit/estimate. TASK29: separate E2 approval only after scored E1 entry gate.',cache_metric='sum prompt_cache_hit_tokens / sum prompt_tokens; report hit/miss and missing-usage counts, never assume missing usage means zero cost',resumption_policy='No overwrite, retry, automatic resume or replacement. Incomplete attempts remain failures.')
 write(P/'CONFIG.json',cfg)
 write(P/'GATES.json',{'E1_S1':{'support_precision_min':0.95,'support_recall_min':0.90,'hard_negative_false_promotion_max':0.05,'support_scope_correctness_min':0.90,'relation_argument_corruption_max':0.03,'candidate_branch_mixing_max':0.02,'false_full_support_hazard_count_max':0,'schema_validity_min':0.95},'comparative':{'metric':'hard_negative_false_promotion','near_zero_both_max':0.05,'near_zero_rule':'S1 <= S0','otherwise_rule':'S1 < S0','S0_required_to_pass':False},'E2_entry':{'required':'All E1_S1 thresholds except support_recall_min; sealed complete review and deterministic replay; fresh separate authorization. Comparative result does not override absolute safety.','recall_only_failure':'Diagnostic E2 allowed under TASK24 Case C and TASK25, not declared S1 PASS.','unsafe_failure':'STOP; no E2 calls.'},'E2_D3':{'strict_min':0.90,'false_subtraction_max':0.03,'false_full_support_count_max':0},'E2_D2':{'strict_min':0.85,'D3_minus_D2_strict_max':0.10,'false_subtraction_max':0.05,'false_full_support_count_max':0,'supported_content_leakage_max':0.05,'state_discrimination_min':0.80,'schema_validity_min':0.95},'empty_denominator':'null; cannot satisfy a gate','ambiguity':'all cells primary, nonambiguous sensitivity cannot replace primary gate','stop_after_E2':True})
 from .inputs import build_schedule
 jobs=build_schedule();write(P/'e1_support_alignment/SCHEDULE.json',jobs)
 chars=sum(sum(len(m['content']) for m in j['request']['messages']) for j in jobs)
 write(P/'CALL_ESTIMATE.json',{'status':'AWAITING_FRESH_E1_AUTHORIZATION','E1':{'parent_state_cells':24,'unique_qids':9,'arms':2,'replicates':2,'actual_requests':len(jobs),'message_characters':chars,'input_tokens_rough_range':[chars//5,chars//3],'token_estimate_method':'English character heuristic only, excludes framing; provider tokenizer unknown; no preflight API call','completion_limit':'max_tokens omitted as requested; completion consumption not bounded by this estimate','paid_attempt_limit':96},'E2':{'conditional_request_maximum':192,'actual_requests_frozen':0,'authorization':'separate after E1 scored/sealed and entry gate passed'},'monetary_estimate':None,'monetary_note':'No current provider price was assumed. This is a call-count estimate, not a spending cap.','calls_made':0})
 write(P/'e1_support_alignment/STATUS.json',{'status':'PREPARED_NOT_RUN','planned':96,'attempted':0,'authorization':'pending new explicit user approval after freeze/commit'})
 write(P/'e2_downstream_residual/STATUS.json',{'status':'NOT_ENTERED','reason':'E1 not run; entry gate unassessed; separate authorization required','conditional_maximum':192,'actual_requests':0})
 write(P/'analysis/STATE_DISCRIMINATION.json',{'status':'PREREGISTERED_NOT_MEASURED','primary_pairs':[{'before':'A05','after':'A07','qid':'228','parent':'R2'},{'before':'A16','after':'A17','qid':'637','parent':'R3'}],'secondary_invariance_pairs':[['A06','A08'],['A09','A11']],'primary_denominator_per_arm':4,'unit':'pair × matched replicate; both residuals strict and correct support-dependent semantic change; lexical change alone is insufficient'})
 print(json.dumps({'E1_actual_requests':len(jobs),'message_characters':chars,'calls_made':0},indent=2))
if __name__=='__main__':main()
