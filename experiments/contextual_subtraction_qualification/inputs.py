"""No Gold/category/hidden Claims/IDs leak into verifier requests."""
from .common import *
def bank():
 ss={s['cell_id']:s for s in read(P/'e0_reference/STATES.json')};ps={r['cell_id']:r for r in read(P/'e0_reference/PARENTS.json')};out={}
 for c in read(P/'e0_reference/CERTIFICATES.json'):
  cell=c['cell_id'];s=ss[cell]
  out[c['certificate_id']]={'original_question':s['question'],'parent_requirement':{'requirement_id':s['parent_requirement_id'],'text':'\n'.join(x['text'] for x in ps[cell]['parent']['source_spans'])},'candidate_locator':c['candidate_locator'],'candidate_verified_claims':c['candidate_verified_claims']}
 return out
def request(arm,payload):
 cfg=read(P/'CONFIG.json');body=payload if arm=='Q1' else {k:payload[k] for k in ('candidate_locator','candidate_verified_claims')}
 return {'model':cfg['model'],'temperature':cfg['temperature'],'response_format':cfg['response_format'],'messages':[{'role':'system','content':(P/f'prompts/{arm}.txt').read_text()},{'role':'user','content':json.dumps(body,ensure_ascii=False,indent=2)}]}
def build_schedule():
 inputs=bank();out=[]
 for i,c in enumerate(read(P/'e0_reference/CERTIFICATES.json')):
  for rep in (1,2):
   for arm in (('Q0','Q1') if (i+rep)%2 else ('Q1','Q0')):
    req=request(arm,inputs[c['certificate_id']]);out.append({'id':f"E1_{c['certificate_id']}_{arm}_r{rep}",'stage':'E1','certificate_id':c['certificate_id'],'cell_id':c['cell_id'],'case_id':c['case_id'],'qid':c['qid'],'arm':arm,'replicate':rep,'request':req,'request_sha256':digest(req)})
 return out
def validate(value,job=None):
 if not isinstance(value,dict) or set(value)!={'verdict','missing_or_unsupported'}:return False
 if value['verdict']=='SUBTRACTABLE':return value['missing_or_unsupported'] is None
 return value['verdict']=='NOT_SUBTRACTABLE' and isinstance(value['missing_or_unsupported'],str) and bool(value['missing_or_unsupported'].strip())
