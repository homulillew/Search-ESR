"""Only frozen Q/one parent/current evidence; no H, Gold residual or future data."""
from .common import *
def build_schedule():
 parents={p['case_id']:p['parent'] for p in read(P/'e0_reference/PARENT_REQUIREMENTS.json')}
 support={p['case_id']:p for p in read(P/'e0_reference/SUPPORT_REFERENCE.json')};jobs=[]
 for s in read(P/'e0_reference/STATES.json'):
  cid=s['case_id'];g=support[cid]
  for arm in ('R0','R1','R2'):
   payload={'Original Question':s['question'],'Parent Requirement':parents[cid]}
   if arm in ('R0','R1'):payload['Current Verified Claims']=s['claims'] if arm=='R0' else g['gold_contributing_claims']
   else:
    payload['Prior Alignment']={k:g['model_packet'][k] for k in ('status','supported_by')};payload['Supporting Claims']=g['model_packet_claims']
   request={'model':'deepseek-flash','temperature':0,'stream':False,'response_format':{'type':'json_object'},
    'messages':[{'role':'system','content':(P/'prompts/residualizer.txt').read_text()},{'role':'user','content':json.dumps(payload,ensure_ascii=False)}]}
   for rep in (1,2):
    jobs.append({'id':f'{arm}__{cid}__R{rep}','stage':'e1_residualization','case_id':cid,'state_id':s['state_id'],'qid':s['qid'],
      'arm':arm,'replicate':rep,'request':request,'request_sha256':digest(request)})
 return sorted(jobs,key=lambda j:digest(['state-conditioned-residualization-v1',j['id']]))
def validate(value,job):
 p=json.loads(job['request']['messages'][1]['content'])
 if not isinstance(value,dict) or set(value)!={'parent_requirement_id','mode','used_claims','local_residual'}:return False
 if value['parent_requirement_id']!=p['Parent Requirement']['requirement_id'] or value['mode'] not in ('residual','probe'):return False
 ids=value['used_claims'];allowed={c['claim_id'] for c in p.get('Current Verified Claims',p.get('Supporting Claims',[]))}
 if not isinstance(ids,list) or any(not isinstance(i,str) for i in ids) or len(set(ids))!=len(ids) or not set(ids)<=allowed:return False
 return isinstance(value['local_residual'],str) and bool(value['local_residual'].strip())
