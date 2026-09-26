import copy,json,unittest
from run import initial,actor_view,item,TOP,ROOT
from runtime import validate_object,schema
from jsonschema import Draft202012Validator
class Contracts(unittest.TestCase):
 def test_initial_projection(self):
  cs=initial()
  for cid in sorted({c['case_id'] for c in cs.values()}):
   g=actor_view(cs[cid+':G'],0);h=actor_view(cs[cid+':H'],0)
   for k in g:
    if k not in ['Tool schema','Response schema']:self.assertEqual(g[k],h[k])
   self.assertEqual(g['New Observations'],[]);self.assertEqual(g['Recent Attempts'],[])
   self.assertTrue(all(set(d)=={'doc_ref','title','url'} for d in g['Historical Document Catalog']))
   s=json.dumps(g);self.assertNotIn('private_recovery_truth',s);self.assertNotIn('historical_support',s)
 def test_one_action(self):
  a={'decision':'act','gap':'test','actions':[{'tool':'search','query':'q','k':5}]*2}
  with self.assertRaises(Exception):Draft202012Validator(schema('actor_G')).validate(a)
 def test_global_find_rejected(self):
  with self.assertRaises(Exception):Draft202012Validator(schema('actor_G')).validate({'decision':'act','gap':'x','actions':[{'tool':'find','doc_ref':'D1','query':'x'}]})
 def test_hidden_window_rejected(self):
  with self.assertRaisesRegex(ValueError,'window_not_visible'):validate_object({'decision':'act','gap':'x','actions':[{'tool':'open','window_ref':'W1','direction':'around'}]},'actor_H',{'known_documents':[],'observed_windows':[]})
 def test_exact_writer(self):self.assertEqual((TOP/'prompts/writer.md').read_bytes(),(ROOT/'experiments/goal_residual_control_v3_1/prompts/state_updater_gap_conditioned.md').read_bytes())
 def test_wrong_k_rejected(self):
  with self.assertRaises(Exception):Draft202012Validator(schema('actor_G')).validate({'decision':'act','gap':'x','actions':[{'tool':'search','query':'x','k':10}]})
 def test_no_claim_deletion(self):
  bank=json.loads((TOP/'bank/RECOVERY_BANK.json').read_text());cs=initial()
  for b in bank:self.assertEqual(cs[b['case_id']+':G']['claims'],b['claims_at_recovery_start'])
if __name__=='__main__':unittest.main()
