import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from .common import *
from .source_units import *
from .prepare import request_for,preflight
from .run import parse_response,Batch
from .evaluate import gate
class Contracts(unittest.TestCase):
 def test_verbatim_offset_coverage(self):
  q='Dr. A. B. has 13.53 percent. Next clause; Third clause? Last question?'
  u=split_units(q)
  self.assertEqual(u[0]['text'],'Dr. A. B. has 13.53 percent.')
  self.assertEqual(len(u),4)
  for x in u:self.assertEqual(q[x['start']:x['end']],x['text'])
 def test_bullet_not_semantic_node(self):
  q='Clues: - Two authors. One other paper. - Six tables. One value 13.53.'
  self.assertEqual(len(split_units(q)),3)
 def test_unicode_whitespace_exact(self):
  self.assertTrue(span_check({'unit':'Q1','text':'cafe\u0301  x'},[{'unit':'Q1','text':'café\nx'}])['valid'])
  self.assertFalse(span_check({'unit':'Q1','text':'coffee x'},[{'unit':'Q1','text':'café x'}])['valid'])
 def test_duplicate_occurrence(self):
  u=[{'unit':'Q1','text':'x then x'}]
  self.assertFalse(span_check({'unit':'Q1','text':'x'},u)['valid'])
  self.assertTrue(span_check({'unit':'Q1','text':'x','occurrence':2},u)['valid'])
  self.assertFalse(span_check({'unit':'Q1','text':'x','occurrence':True},u)['valid'])
 def test_schema_limits_and_prose(self):
  node={'source_spans':[{'unit':'Q1','text':'x'}]};u=[{'unit':'Q1','text':'x'}]
  self.assertTrue(validate({'requirements':[node]*12},'D2',u)['valid'])
  self.assertFalse(validate({'requirements':[node]*13},'D2',u)['valid'])
  self.assertFalse(validate({'requirements':[{**node,'requirement':'x'}]},'D2',u)['valid'])
  self.assertFalse(validate({'requirements':[{'source_spans':[]}]},'D2',u)['valid'])
 def test_contract_and_isolation(self):
  for stage in STAGES:
   cases=bank(stage);jobs=read(P/stage/'SCHEDULE.json')
   self.assertEqual(preflight(jobs,cases,read(P/'CONFIG.json'),stage,False)['status'],'PASS')
   for q,c in cases.items():
    self.assertEqual(len({request_for(c,a)['messages'][1]['content'] for a in ARMS}),1)
    self.assertEqual(set(json.loads(request_for(c,'D2')['messages'][1]['content'])),{'Original Question','Addressable Source Units'})
 def test_length_retains_usage(self):
  job=read(P/STAGES[0]/'SCHEDULE.json')[0];c=bank(STAGES[0])[job['qid']]
  raw={'model':'deepseek-flash','usage':{'completion_tokens':65536},'choices':[{'finish_reason':'length','message':{'content':'{}'}}]}
  r=parse_response(200,json.dumps(raw),job,c)
  self.assertEqual(r['failure'],'length');self.assertEqual(r['usage'],raw['usage']);self.assertFalse(r['valid_output'])
 def test_model_mismatch(self):
  job=read(P/STAGES[0]/'SCHEDULE.json')[0];c=bank(STAGES[0])[job['qid']]
  raw={'model':'other','choices':[{'finish_reason':'stop','message':{'content':'{}'}}]}
  self.assertEqual(parse_response(200,json.dumps(raw),job,c)['failure'],'model_mismatch')
 def test_timeout_not_retried(self):
  import httpx
  class Client:
   n=0
   def post(self,*a,**kw):self.n+=1;raise httpx.ReadTimeout('synthetic offline timeout')
  client=Client();job=read(P/STAGES[0]/'SCHEDULE.json')[0]
  with tempfile.TemporaryDirectory() as d:
   b=Batch(client,'dummy',read(P/'CONFIG.json'),bank(STAGES[0]),Path(d),'offline');b.run([job])
   r=read(Path(d)/'calls'/f"{job['id']}.result.json")
   self.assertEqual(client.n,1);self.assertEqual(r['failure'],'timeout');self.assertIsNone(r['usage'])
 def test_contract_failure_halts_unsent(self):
  class Response:status_code=400;text='{"error":{"message":"synthetic"}}'
  class Client:
   n=0
   def post(self,*a,**kw):self.n+=1;return Response()
  client=Client();jobs=read(P/STAGES[0]/'SCHEDULE.json')[:3]
  with tempfile.TemporaryDirectory() as d:
   b=Batch(client,'dummy',read(P/'CONFIG.json'),bank(STAGES[0]),Path(d),'offline');b.run(jobs)
   self.assertEqual(client.n,1)
   self.assertEqual(len(list((Path(d)/'calls').glob('*.result.json'))),3)
 def test_no_overwrite(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'x.json';write(p,{})
   with self.assertRaises(FileExistsError):write(p,{})
 def test_gate_tie_and_critical_coverage(self):
  a=dict(strict=1,critical_coverage=1,material_coverage=1,structural_corruption=0,invented=0,dependency=1,severe_broad=0,mechanical=1,both_strict=1)
  self.assertTrue(gate({'D0':a,'D2':a},STAGES[0])['pass'])
  self.assertFalse(gate({'D0':a,'D2':a},STAGES[1])['pass'])
  self.assertFalse(gate({'D0':a,'D2':{**a,'critical_coverage':.99}},STAGES[0])['pass'])
if __name__=='__main__':unittest.main()
