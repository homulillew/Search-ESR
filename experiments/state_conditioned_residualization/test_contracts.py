import unittest,json
from .inputs import build_schedule,validate
from .run import parse
from .common import read,P
class ContractTests(unittest.TestCase):
 def setUp(self):
  self.j=build_schedule()[0];p=json.loads(self.j['request']['messages'][1]['content']);self.v={'parent_requirement_id':p['Parent Requirement']['requirement_id'],'mode':'probe','used_claims':[],'local_residual':'Establish an unresolved relation.'}
 def test_parent_cannot_be_changed(self):
  self.assertTrue(validate(self.v,self.j));self.v['parent_requirement_id']='R999';self.assertFalse(validate(self.v,self.j))
 def test_foreign_claim_and_extra_fields_rejected(self):
  self.v['used_claims']=['C999'];self.assertFalse(validate(self.v,self.j));self.v['used_claims']=[];self.v['confidence']=1;self.assertFalse(validate(self.v,self.j))
 def test_length_retains_usage_never_repairs_content(self):
  raw={'model':'deepseek-flash','usage':{'completion_tokens':65536},'choices':[{'finish_reason':'length','message':{'content':json.dumps(self.v)}}]}
  r=parse(200,json.dumps(raw),self.j);self.assertEqual(r['failure'],'length');self.assertIsNone(r['output']);self.assertEqual(r['usage']['completion_tokens'],65536)
 def test_arm_boundaries(self):
  jobs=build_schedule();self.assertEqual(len(jobs),114)
  for j in jobs:
   p=json.loads(j['request']['messages'][1]['content']);self.assertNotIn('Hypothesis',p);self.assertNotIn('tools',j['request'])
   self.assertEqual(set(p),{'Original Question','Parent Requirement','Prior Alignment','Supporting Claims'} if j['arm']=='R2' else {'Original Question','Parent Requirement','Current Verified Claims'})
 def test_frozen_error_not_repaired(self):
  g=next(s for s in read(P/'e0_reference/SUPPORT_REFERENCE.json') if s['case_id']=='G14')
  self.assertEqual(g['gold_status'],'unsupported');self.assertEqual(g['model_packet']['status'],'partially_supported');self.assertEqual(g['model_packet']['supported_by'],['C1'])
if __name__=='__main__':unittest.main()
