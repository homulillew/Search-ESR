"""Pure request construction: no credentials, transport, hypotheses or Gold in E1."""
from .common import *

def bank():
 states=read(P/'e0_reference/STATES.json');parents={r['cell_id']:r for r in read(P/'e0_reference/PARENTS.json')}
 return {s['cell_id']:{'original_question':s['question'],'parent_requirement':{'requirement_id':s['parent_requirement_id'],'text':'\n'.join(t['text'] for t in parents[s['cell_id']]['parent']['source_spans'])},'current_verified_claims':s['claims']} for s in states}

def request(system,payload):
 cfg=read(P/'CONFIG.json')
 return {'model':cfg['model'],'temperature':cfg['temperature'],'response_format':cfg['response_format'],'messages':[{'role':'system','content':system},{'role':'user','content':json.dumps(payload,ensure_ascii=False,indent=2)}]}

def build_schedule():
 inputs=bank();states=read(P/'e0_reference/STATES.json');out=[]
 for s in states:
  for rep in (1,2):
   # Balance arm order across cells and replicates; no adaptive order.
   arms=('S0','S1') if (int(s['cell_id'][1:])+rep)%2==0 else ('S1','S0')
   for arm in arms:
    body=request((P/f'prompts/{arm}.txt').read_text(),inputs[s['cell_id']])
    out.append({'id':f"E1_{s['cell_id']}_{arm}_r{rep}",'stage':'E1','cell_id':s['cell_id'],'case_id':s['case_id'],'qid':s['qid'],'parent_requirement_id':s['parent_requirement_id'],'arm':arm,'replicate':rep,'request':body,'request_sha256':digest(body)})
 return out

def validate(value,job):
 if not isinstance(value,dict):return False
 payload=json.loads(job['request']['messages'][1]['content'])
 ids={c['claim_id'] for c in payload['current_verified_claims']};r=payload['parent_requirement']['text']
 if job['arm']=='S0':
  cs=value.get('support_claim_ids')
  return set(value)=={'support_claim_ids'} and isinstance(cs,list) and all(isinstance(c,str) and c in ids for c in cs) and len(cs)==len(set(cs))
 if job['arm']!='S1' or set(value)!={'claims'} or not isinstance(value['claims'],list):return False
 seen=[]
 for c in value['claims']:
  if not isinstance(c,dict) or set(c)!={'claim_id','role','supported_requirement_fragments'}:return False
  if not isinstance(c['claim_id'],str) or c['claim_id'] not in ids or c['role'] not in ROLES:return False
  fs=c['supported_requirement_fragments']
  if not isinstance(fs,list) or not all(isinstance(f,str) and f.strip() and f in r for f in fs):return False
  if len(fs)!=len(set(fs)) or bool(fs)!=(c['role']=='SUBSTANTIVE_SUPPORT'):return False
  seen.append(c['claim_id'])
 return len(seen)==len(ids) and set(seen)==ids

def support_ids(value,arm):
 return set(value['support_claim_ids']) if arm=='S0' else {c['claim_id'] for c in value['claims'] if c['role']=='SUBSTANTIVE_SUPPORT'}

def e2_payload(cell,arm,assignment=None):
 """Requires matched replicate assignment from caller. Never exports scope fragments."""
 b=bank()[cell];claims=b['current_verified_claims'];payload={'parent_requirement':b['parent_requirement']}
 if arm=='D0':return {**payload,'raw_current_verified_claims':claims}
 if arm=='D1':
  assert isinstance(assignment,dict) and 'support_claim_ids' in assignment
  picked=set(assignment['support_claim_ids']);assert picked<={c['claim_id'] for c in claims}
  return {**payload,'SUBSTANTIVE SUPPORT':[c for c in claims if c['claim_id'] in picked]}
 if arm=='D2':
  assert isinstance(assignment,dict) and 'claims' in assignment
  roles={c['claim_id']:c['role'] for c in assignment['claims']}
 elif arm=='D3':
  g=next(g for g in read(P/'e0_reference/CLAIM_ROLE_REFERENCE.json') if g['cell_id']==cell)
  roles={k:v['epistemic_role'] for k,v in g['claims'].items()}
 else:raise ValueError(arm)
 assert set(roles)=={c['claim_id'] for c in claims} and all(v in ROLES for v in roles.values())
 return {**payload,**{role.replace('_',' '):[c for c in claims if roles[c['claim_id']]==role] for role in ROLES[:3]}}

def validate_residual(value):
 if not isinstance(value,dict) or set(value)!={'status','residual'}:return False
 return (value['status']=='FULLY_SUPPORTED' and value['residual'] is None) or (value['status']=='UNRESOLVED' and isinstance(value['residual'],str) and bool(value['residual'].strip()))
