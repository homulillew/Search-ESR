"""At most one orthogonal objective and one query for each actual NoGain."""
from .common import *
from .bootstrap_runtime import request,seal,load_rows

def probes():
 metrics=read(P/'e2_bootstrap/METRICS.json');states={s['case_id']:s for s in read(P/'e0_reference/STATES.json')};parents={s['case_id']:s['parent'] for s in read(P/'e0_reference/PARENT_REQUIREMENTS.json')}
 rs=[r for r in metrics['rows'] if r['arm']=='P1' and r['real_no_gain']];assert {r['case_id'] for r in rs}=={'G10','G20'}
 reasons={'G10':'The fixed parent includes the same university for undergraduate and graduate degrees; initial probe focused on the promotion and omitted this source-anchored relation.','G20':'The parent requires a release-date interval between base game and DLC. Publisher/store release records and the base-game date facet remain untried; initial probe asks for DLC identity generically.'}
 jobs=[];elig=[];regs={}
 for r in rs:
  cid=r['case_id'];s=states[cid];ret=read(P/'e2_bootstrap/retrieval'/f"{r['id']}.json");source=read(P/'e1_residualization/calls'/f'R0__{cid}__R1.result.json');q=read(P/'e2_bootstrap/calls'/f"{r['id']}.result.json")
  eligible={'case_id':cid,'P1_real_no_gain':True,'oracle_accessibility':'accessible','untried_facet':reasons[cid],'source_review_id':r['review_id']};elig.append(eligible);regs[cid]=ret['registry']
  payload={'Original Question':s['question'],'Parent Requirement':parents[cid],'Previous probe objective':source['output']['local_residual'],'Previous query':q['output']['query'],'Mechanical result summary':{'returned documents':[{k:v[k] for k in ['doc_ref','title']} for v in ret['tool']['result']['results']],'any new claim admitted':'no','new binding found':'no'}}
  req=request(payload,'orthogonal_probe');jobs.append({'id':f'P1__{cid}__R2_PROBE','stage':'e2b_escalation','case_id':cid,'state_id':s['state_id'],'qid':s['qid'],'arm':'P1','replicate':2,'request':req,'request_sha256':digest(req),'field':'probe','blocked_reason':None})
 write(P/'e2b_escalation/ELIGIBILITY.json',{'eligible':elig,'excluded':'All other accessible P1 states either gained or have no actual Search (G08/G11 source failures). No semantic/source failure relabeled NoGain.','maximum_additional_probes_per_state':1,'maximum_additional_model_calls':4,'maximum_additional_searches':2})
 write(P/'e2b_escalation/probe_generation/SCHEDULE.json',jobs);write(P/'e2b_escalation/RETRIEVAL_REGISTRIES.json',regs)
 seal('e2b_escalation/probe_generation',[P/'escalation_prepare.py',P/'e2b_escalation/ELIGIBILITY.json',P/'e2_bootstrap/METRICS.json',P/'e2_bootstrap/review/JUDGMENTS.json',P/'e2b_escalation/RETRIEVAL_REGISTRIES.json'])
 print('2 eligible states,2 frozen probe requests')
def queries():
 states={s['case_id']:s for s in read(P/'e0_reference/STATES.json')};jobs=[]
 for r in load_rows('e2b_escalation/probe_generation'):
  cid=r['case_id'];req=request({'Original Question':states[cid]['question'],'Research Objective':r['output']['probe']}) if r['valid_output'] else None
  jobs.append({'id':f'P1__{cid}__R2','stage':'e2b_escalation','case_id':cid,'state_id':states[cid]['state_id'],'qid':states[cid]['qid'],'arm':'P1','replicate':2,'request':req,'request_sha256':digest(req),'field':'query','blocked_reason':None if req else 'invalid_orthogonal_probe'})
 write(P/'e2b_escalation/SCHEDULE.json',jobs)
 seal('e2b_escalation',[P/'escalation_prepare.py',P/'e2b_escalation/ELIGIBILITY.json',P/'e2b_escalation/RETRIEVAL_REGISTRIES.json',*[p for p in (P/'e2b_escalation/probe_generation/calls').glob('*.result.json')]])
 print('2 frozen dependent query slots')
if __name__=='__main__':
 import sys
 globals()[sys.argv[1]]()
