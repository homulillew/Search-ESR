"""Offline safety/measurement checks; synthetic outputs never become experiment results."""
import copy,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from .common import *
from .inputs import *
from .score import aggregate,gate

class HarnessTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.jobs=build_schedule();cls.refs={g['cell_id']:g for g in read(P/'e0_reference/CLAIM_ROLE_REFERENCE.json')}
 def job(self,cell='A07',arm='S1'):
  return next(j for j in self.jobs if j['cell_id']==cell and j['arm']==arm)
 def gold_output(self,cell):
  return {'claims':[{'claim_id':k,'role':v['epistemic_role'],'supported_requirement_fragments':v['supported_requirement_fragments']} for k,v in self.refs[cell]['claims'].items()]}
 def rows(self):
  rows=[]
  for j in self.jobs:
   g=self.refs[j['cell_id']];output={'support_claim_ids':g['gold_support_claim_ids']} if j['arm']=='S0' else self.gold_output(j['cell_id'])
   rows.append({**j,'output':output,'valid_output':True,'judgment':{'scope_correct_claim_ids':g['gold_support_claim_ids'] if j['arm']=='S1' else [],'relation_argument_corruption':False,'candidate_branch_mixing':False,'false_full_support_hazard':False if j['arm']=='S1' else None,'error_tags':[],'reason':'Synthetic fixture only.','ambiguous_reference':False}})
  return rows
 def test_schedule_and_gold_contract(self):
  self.assertEqual(self.jobs,read(P/'e1_support_alignment/SCHEDULE.json'));self.assertEqual(len(self.jobs),96)
  self.assertEqual(len({j['id'] for j in self.jobs}),96)
  for j in self.jobs:
   self.assertNotIn('max_tokens',j['request']);self.assertNotIn('tools',j['request']);self.assertEqual(j['request']['temperature'],0)
   value=self.gold_output(j['cell_id']) if j['arm']=='S1' else {'support_claim_ids':self.refs[j['cell_id']]['gold_support_claim_ids']}
   self.assertTrue(validate(value,j));self.assertEqual(digest(j['request']),j['request_sha256'])
  for cell in self.refs:
   self.assertEqual(len({j['request']['messages'][1]['content'] for j in self.jobs if j['cell_id']==cell}),1)
 def test_binary_bad_ids_duplicates_extra_fields(self):
  j=self.job(arm='S0')
  for v in [{'support_claim_ids':['C99']},{'support_claim_ids':['C1','C1']},{'support_claim_ids':[],'reason':'x'},[],{'support_claim_ids':[{}]}]:self.assertFalse(validate(v,j))
 def test_typed_missing_duplicate_unknown_role_and_fragments(self):
  j=self.job();good=self.gold_output('A07');bad=[]
  a=copy.deepcopy(good);a['claims'].pop();bad.append(a)
  a=copy.deepcopy(good);a['claims'][0]=a['claims'][1];bad.append(a)
  a=copy.deepcopy(good);a['claims'][0]['claim_id']='C99';bad.append(a)
  a=copy.deepcopy(good);a['claims'][0]['role']='SUPPORT';bad.append(a)
  a=copy.deepcopy(good);a['claims'][0]['supported_requirement_fragments']=['This person'];bad.append(a)
  a=copy.deepcopy(good);a['claims'][-1]['supported_requirement_fragments']=['paraphrased marriage'];bad.append(a)
  a=copy.deepcopy(good);a['claims'][-1]['supported_requirement_fragments']=[];bad.append(a)
  for a in bad:self.assertFalse(validate(a,j))
 def test_exact_span_does_not_prove_scope(self):
  j=self.job('A17');v=self.gold_output('A17');v['claims'][6]['supported_requirement_fragments']=[bank()['A17']['parent_requirement']['text']]
  self.assertTrue(validate(v,j)) # Semantic overreach requires independent review.
  rows=self.rows();r=next(r for r in rows if r['id']==j['id']);r['output']=v;r['judgment']['scope_correct_claim_ids']=[];r['judgment']['false_full_support_hazard']=True
  m=aggregate(rows,self.refs);self.assertEqual(m['S1']['false_full_support_hazard_count'],1);self.assertFalse(gate(m)['E2_safety_entry_pass'])
 def test_synthetic_perfect_replay_and_nearzero(self):
  m=aggregate(self.rows(),self.refs);self.assertEqual(m,aggregate(self.rows(),self.refs));g=gate(m)
  self.assertTrue(g['S1_primary_pass']);self.assertTrue(g['E2_safety_entry_pass']);self.assertFalse(g['E2_authorized'])
  self.assertEqual(m['S1']['support_recall']['denominator'],36);self.assertEqual(m['S1']['hard_negative_false_promotion']['denominator'],128)
  m['S1']['support_recall']['value']=.85;self.assertFalse(gate(m)['S1_primary_pass']);self.assertTrue(gate(m)['E2_safety_entry_pass'])
 def test_empty_denominator_and_invalid_negative(self):
  rows=self.rows()
  for r in rows:r['valid_output']=False;r['output']=None;r['judgment']['scope_correct_claim_ids']=[]
  m=aggregate(rows,self.refs);self.assertIsNone(m['S1']['support_precision']['value']);self.assertEqual(m['S1']['exact_state_support_set']['numerator'],0);self.assertEqual(m['S1']['support_recall']['value'],0);self.assertFalse(gate(m)['E2_safety_entry_pass'])
 def test_e2_scope_never_exported_and_origin_isolated(self):
  model=self.gold_output('A17');model['claims'][6]['supported_requirement_fragments']=['DO NOT LEAK THIS EVALUATION STRING']
  packet=e2_payload('A17','D2',model);s=json.dumps(packet)
  self.assertNotIn('supported_requirement_fragments',s);self.assertNotIn('DO NOT LEAK',s);self.assertNotIn('original_question',packet)
  self.assertEqual(set(packet),{'parent_requirement','SUBSTANTIVE SUPPORT','BINDING CONTEXT','BACKGROUND'})
  self.assertEqual([c['claim_id'] for c in packet['SUBSTANTIVE SUPPORT']],['C7'])
  self.assertEqual(e2_payload('A17','D1',{'support_claim_ids':[]})['SUBSTANTIVE SUPPORT'],[])
  self.assertEqual(set(e2_payload('A17','D0')),{'parent_requirement','raw_current_verified_claims'})
  self.assertNotIn('supported_requirement_fragments',json.dumps(e2_payload('A17','D3')))
 def test_parse_rejects_finish_and_model_mismatch(self):
  from .run import parse
  j=self.job();body={'model':'deepseek-flash','usage':{'prompt_tokens':123},'choices':[{'finish_reason':'stop','message':{'content':json.dumps(self.gold_output('A07')),'reasoning_content':'not for review'}}]}
  self.assertTrue(parse(200,json.dumps(body),j)['valid_output'])
  body['choices'][0]['finish_reason']='length';self.assertEqual(parse(200,json.dumps(body),j)['failure'],'length')
  body['choices'][0]['finish_reason']='stop';body['model']='different';self.assertEqual(parse(200,json.dumps(body),j)['failure'],'model_mismatch')
 def test_authorization_required_without_network(self):
  from . import run
  with tempfile.TemporaryDirectory() as d,patch.object(run,'P',Path(d)):
   with self.assertRaises(PermissionError):run.authorization()
 def test_single_attempt_and_raw_retention(self):
  from . import run
  import httpx
  class FakeClient:
   def __init__(self):self.calls=0
   def post(self,*args,**kwargs):self.calls+=1;raise httpx.ReadTimeout('synthetic timeout')
  with tempfile.TemporaryDirectory() as d,patch.object(run,'OUT',Path(d)):
   client=FakeClient();batch=run.Batch(client,'not-a-real-key',read(P/'CONFIG.json'),'test-only');j=self.jobs[0];batch.one(j)
   self.assertEqual(client.calls,1);self.assertEqual(read(Path(d)/'calls'/f"{j['id']}.result.json")['failure'],'timeout')
   self.assertTrue((Path(d)/'calls'/f"{j['id']}.attempt.json").exists())
   with self.assertRaises(FileExistsError):batch.one(j)
   self.assertEqual(client.calls,1)

if __name__=='__main__':unittest.main()
