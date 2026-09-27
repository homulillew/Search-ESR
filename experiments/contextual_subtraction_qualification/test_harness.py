"""Offline contract, counterfactual gate and input-isolation checks."""
import copy,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from .common import *
from .inputs import *
from .score import aggregate,gate
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.jobs=build_schedule();cls.refs={c['certificate_id']:c for c in read(P/'e0_reference/CERTIFICATES.json')}
 def rows(self):return [{**j,'valid_output':True,'output':{'verdict':self.refs[j['certificate_id']]['gold_verdict'],'missing_or_unsupported':None if self.refs[j['certificate_id']]['gold_verdict']=='SUBTRACTABLE' else 'Frozen missing condition.'}} for j in self.jobs]
 def test_runtime_isolation(self):
  self.assertEqual(len(self.jobs),192);self.assertEqual(self.jobs,read(P/'e1_qualification/SCHEDULE.json'))
  self.assertEqual(len({j['id'] for j in self.jobs}),192)
  for j in self.jobs:
   p=json.loads(j['request']['messages'][1]['content']);keys={'candidate_locator','candidate_verified_claims'}|({'original_question','parent_requirement'} if j['arm']=='Q1' else set())
   self.assertEqual(set(p),keys);self.assertNotIn('max_tokens',j['request']);self.assertNotIn('tools',j['request'])
   self.assertEqual(p['candidate_verified_claims'],self.refs[j['certificate_id']]['candidate_verified_claims'])
 def test_gold_claim_provenance(self):
  ss={s['cell_id']:s for s in read(P/'e0_reference/STATES.json')};inputs=bank()
  self.assertEqual(sum(c['gold_verdict']=='SUBTRACTABLE' for c in self.refs.values()),22)
  for c in self.refs.values():
   claims={x['claim_id']:x for x in ss[c['cell_id']]['claims']}
   self.assertEqual(c['candidate_verified_claims'],[claims[k] for k in c['candidate_claim_ids']]);self.assertIn(c['candidate_locator'],inputs[c['certificate_id']]['parent_requirement']['text'])
   if c['false_full_risk']:self.assertEqual(c['gold_verdict'],'NOT_SUBTRACTABLE')
 def test_literal_context_prompt(self):
  task=(P/'TASK.md').read_text();expected=task.split('# 13. E1 核心 System Prompt\n\n',1)[1].split('\n---',1)[0].strip()+'\n'
  self.assertEqual((P/'prompts/Q1.txt').read_text(),expected)
 def test_schema_rejects_conflict_extra_fields_and_missing(self):
  for v in [{},{'verdict':'YES','missing_or_unsupported':None},{'verdict':'SUBTRACTABLE','missing_or_unsupported':'missing'},{'verdict':'NOT_SUBTRACTABLE','missing_or_unsupported':None},{'verdict':'NOT_SUBTRACTABLE','missing_or_unsupported':' '},{'verdict':'SUBTRACTABLE','missing_or_unsupported':None,'confidence':1}]:self.assertFalse(validate(v))
  self.assertTrue(validate({'verdict':'SUBTRACTABLE','missing_or_unsupported':None}))
 def test_perfect_tie_passes(self):
  m=aggregate(self.rows(),self.refs);self.assertTrue(gate(m)['E1_PASS']);self.assertEqual(m,aggregate(self.rows(),self.refs));self.assertEqual(m['Q1']['subtraction_recall']['denominator'],44)
 def test_euler_one_accept_blocks(self):
  rows=self.rows();r=next(r for r in rows if r['arm']=='Q1' and 'Euler' in self.refs[r['certificate_id']]['case_tags']);r['output']={'verdict':'SUBTRACTABLE','missing_or_unsupported':None};m=aggregate(rows,self.refs)
  self.assertEqual(m['Q1']['Euler_false_acceptance_count'],1);self.assertFalse(gate(m)['E2_eligible'])
 def test_invalid_outputs_not_safe_rejections(self):
  rows=self.rows()
  for r in rows:r['valid_output']=False;r['output']=None
  m=aggregate(rows,self.refs);self.assertEqual(m['Q1']['hard_negative_rejection']['numerator'],0);self.assertIsNone(m['Q1']['subtraction_precision']['value']);self.assertEqual(m['Q1']['planned'],96);self.assertFalse(gate(m)['E1_PASS'])
 def test_joint_claims_not_individual_false_promotions(self):
  b=bank()['A07_CAND1'];self.assertEqual([c['claim_id'] for c in b['candidate_verified_claims']],['C4','C5']);self.assertEqual(self.refs['A07_CAND1']['gold_verdict'],'SUBTRACTABLE')
  self.assertEqual(self.refs['A21_CAND2']['candidate_locator'],self.refs['A21_CAND3']['candidate_locator']);self.assertNotEqual(self.refs['A21_CAND2']['gold_verdict'],self.refs['A21_CAND3']['gold_verdict'])
 def test_transport_preserves_timeout_without_retry(self):
  from . import run
  import httpx
  class Client:
   def __init__(self):self.n=0
   def post(self,*a,**k):self.n+=1;raise httpx.ReadTimeout('synthetic')
  with tempfile.TemporaryDirectory() as d,patch.object(run,'OUT',Path(d)):
   c=Client();batch=run.Batch(c,'test-only',read(P/'CONFIG.json'),'test');j=self.jobs[0];batch.one(j);self.assertEqual(c.n,1)
   self.assertEqual(read(Path(d)/'calls'/f"{j['id']}.result.json")['failure'],'timeout')
   with self.assertRaises(FileExistsError):batch.one(j)
   self.assertEqual(c.n,1)
 def test_model_finish_contract(self):
  from .run import parse
  j=self.jobs[0];body={'model':'deepseek-flash','choices':[{'finish_reason':'stop','message':{'content':'{"verdict":"SUBTRACTABLE","missing_or_unsupported":null}'}}]}
  self.assertTrue(parse(200,json.dumps(body),j)['valid_output']);body['choices'][0]['finish_reason']='length';self.assertFalse(parse(200,json.dumps(body),j)['valid_output'])
if __name__=='__main__':unittest.main()
