"""Offline tests: malformed contracts never make a network request."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import httpx
from .common import *
from .prepare import preflight, credential
from .run import Batch, validate_output, parse_response
class Contracts(unittest.TestCase):
 def setUp(self):
  self.jobs=read(P/'e1_gap/SCHEDULE.json');self.cases=bank();self.cfg=read(P/'CONFIG.json');self.j=self.jobs[0];self.c=self.cases[self.j['case_id']]
 def test_all_schedule(self):self.assertEqual(preflight(self.jobs,self.cases,self.cfg)['scheduled'],108)
 def test_schema_refs_null(self):
  v={'supported_by':[],'missing':'identity','evidence_needed':'identity record'};self.assertTrue(validate_output(v,self.c))
  for change in ({'supported_by':['H']},{'supported_by':['C999']},{'missing':None},{'reason':'x'}):self.assertFalse(validate_output({**v,**change},self.c))
  self.assertTrue(validate_output({'supported_by':[],'missing':None,'evidence_needed':None},self.c))
 def test_preflight_mutations(self):
  for mutate in (lambda j:j[0]['request'].update(max_tokens=8),lambda j:j[0]['request'].update(model='other'),lambda j:j.append(j[0]),lambda j:j.pop(),lambda j:j[0]['request']['messages'][0].update(content='Return an object')):
   jobs=copy.deepcopy(self.jobs);mutate(jobs)
   with self.assertRaises(AssertionError):preflight(jobs,self.cases,self.cfg)
 def test_literal_guard_before_transport(self):
  j=copy.deepcopy(self.j);j['request']['messages'][0]['content']='Return an object';j['request']['messages'][1]['content']='{}'
  class NoSend:
   def post(self,*a,**kw):raise AssertionError('NETWORK MUST NOT BE REACHED')
  with tempfile.TemporaryDirectory() as d,patch('experiments.evidence_gap_gold_obligation.run.request_for',return_value=j['request']):
   with self.assertRaisesRegex(ValueError,'JSON literal'):Batch(NoSend(),'test-secret',self.cfg,self.cases,Path(d),'offline').one(j)
 def test_timeout_retained_and_exclusive(self):
  class Timeout:
   n=0
   def post(self,*a,**kw):self.n+=1;raise httpx.ReadTimeout('offline')
  client=Timeout()
  with tempfile.TemporaryDirectory() as d:
   b=Batch(client,'test-secret',self.cfg,self.cases,Path(d),'offline');b.one(self.j)
   r=read(Path(d)/'calls'/f"{self.j['id']}.result.json");self.assertEqual(r['failure'],'timeout');self.assertEqual(client.n,1)
   with self.assertRaises(FileExistsError):b.one(self.j)
   self.assertEqual(client.n,1)
   self.assertNotIn('test-secret',''.join(p.read_text() for p in Path(d).rglob('*.json')))
 def test_400_halts_following(self):
  class Rejected:
   n=0
   def post(self,*a,**kw):self.n+=1;return httpx.Response(400,text='{"error":"offline contract rejection"}')
  client=Rejected()
  with tempfile.TemporaryDirectory() as d:
   b=Batch(client,'test-secret',self.cfg,self.cases,Path(d),'offline');b.one(self.jobs[0]);b.one(self.jobs[1]);self.assertEqual(client.n,1)
   self.assertFalse(read(Path(d)/'calls'/f"{self.jobs[1]['id']}.result.json")['attempted'])
 def test_auth_fails_closed(self):
  with patch.dict('os.environ',{},clear=True),patch('dotenv.dotenv_values',return_value={}):
   with self.assertRaises(ValueError):credential()
 def test_length_unknown_usage(self):
  r=parse_response(200,json.dumps({'model':'deepseek-flash','choices':[{'finish_reason':'length','message':{'content':''}}]}),self.j,self.c)
  self.assertEqual(r['failure'],'length');self.assertIsNone(r['usage'])
if __name__=='__main__':unittest.main()
