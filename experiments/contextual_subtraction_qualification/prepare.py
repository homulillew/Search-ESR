"""Construct literal Q1 prompt and balanced192-call E1 schedule without network."""
from .common import *
Q0='''You are deciding whether the supplied Verified Claims establish a candidate
semantic condition that may be treated as solved.

You receive a Candidate Locator and a set of current Verified Claims.
For this standalone-fragment diagnostic, treat the Candidate Locator as the
condition to verify. No full Parent Requirement or Original Question is supplied.

Use only the supplied Verified Claims. Do not use outside knowledge or hypotheses.
Multiple Claims may jointly establish the condition; a single Claim does not
need to contain it all in one sentence.

Return SUBTRACTABLE only when the supplied Claims, taken together, establish
the condition stated in the Candidate Locator strongly enough to treat it as solved.
Otherwise return NOT_SUBTRACTABLE and briefly state the most important missing
or unsupported content. Do not propose a search query.

Return JSON only:
{
  "verdict": "SUBTRACTABLE",
  "missing_or_unsupported": null
}
or
{
  "verdict": "NOT_SUBTRACTABLE",
  "missing_or_unsupported": "..."
}
'''
def main():
 task=(P/'TASK.md').read_text();q1=task.split('# 13. E1 核心 System Prompt\n\n',1)[1].split('\n---',1)[0].strip()+'\n'
 write(P/'prompts/Q1.txt',q1);write(P/'prompts/Q0.txt',Q0)
 cfg=read(OLD/'CONFIG.json');keys=['provider','endpoint','base_url','model','temperature','max_retries','max_workers','replicates','max_tokens_policy','response_format','timeout_seconds','timeout_semantics','halt_http_statuses','credential_source','tool_calls','horizon','cache_metric','resumption_policy'];cfg={k:cfg[k] for k in keys}
 cfg.update(planned_E1=192,E1_replicates={'Q0':2,'Q1':2},E1_authorization_basis='Current user TASK directs E1 mechanism test and calls; no new E1 confirmation gate. Prior96-call authorization is not reused.',E2_authorization='New separate authorization only after E1 PASS per current TASK21.',E3='Conditional on E2 PASS; no E3 execution in E1 authorization.')
 write(P/'CONFIG.json',cfg)
 write(P/'GATES.json',{'E1_Q1':{'subtraction_precision_min':0.97,'subtraction_recall_min':0.90,'binding_missing_false_acceptance_max':0.03,'qualifier_incomplete_false_acceptance_max':0.05,'Euler_false_acceptance_count_max':0,'book_article_false_acceptance_count_max':0,'false_full_risk_acceptance_count_max':0,'schema_validity_min':0.95},'E1_comparative':{'precision':'Q1 >= Q0','recall':'Q1 >= Q0 - 0.05','both_must_pass':True,'strict_improvement_required':False},'E2_entry':'All E1 absolute and comparative criteria PASS; separately authorized after concrete dependent stage preparation. No recall-only exception in this task.','null_denominator':'not estimable; cannot pass a gate','E2':{'support_precision_min':0.95,'support_recall_min':0.90,'binding_context_false_promotion_max':0.02,'false_full_hazard_count_max':0,'candidate_proposal_recall_min':0.95,'schema_validity_min':0.95,'comparative':['Cascade precision >= historical S1 precision','Cascade recall >= historical S0 recall']},'E3_gold':{'strict_min':0.90,'false_subtraction_max':0.03,'false_full_support_count_max':0},'E3_model':{'strict_min':0.85,'Gold_minus_Model_strict_max':0.10,'false_subtraction_max':0.05,'false_full_support_count_max':0,'state_discrimination_min':0.80},'ambiguity':'All48 certificates primary; exclusion sensitivity cannot replace primary gate.'})
 from .inputs import build_schedule
 jobs=build_schedule();assert len(jobs)==192;write(P/'e1_qualification/SCHEDULE.json',jobs)
 chars=sum(len(m['content']) for j in jobs for m in j['request']['messages'])
 write(P/'CALL_ESTIMATE.json',{'stage':'E1','certificates':48,'arms':2,'replicates_each':2,'actual_requests':len(jobs),'message_characters':chars,'approximate_input_tokens_by_characters':[chars//5,chars//3],'estimate_caveat':'English-character heuristic, excludes framing/output; omit max_tokens. Not a currency or spending cap.','E2_E3_actual_requests':0,'maximum_concurrency':8,'retries':0})
 write(P/'e2_cascade/STATUS.json',{'status':'NOT_ENTERED','condition':'E1 PASS then separate authorization','actual_requests':0})
 write(P/'e3_residual/STATUS.json',{'status':'NOT_ENTERED','condition':'E2 PASS and stage request freeze','actual_requests':0})
 print(read(P/'CALL_ESTIMATE.json'))
if __name__=='__main__':main()
