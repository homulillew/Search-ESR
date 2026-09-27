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
  self.jobs=read(P/'e1_context/SCHEDULE.json');self.cases=bank();self.cfg=read(P/'CONFIG.json');self.j=self.jobs[0];self.c=self.cases[self.j['case_id']]
 def test_all_schedule(self):self.assertEqual(preflight(self.jobs,self.cases,self.cfg)['scheduled'],216)
 def test_schema_single_field(self):
  self.assertTrue(validate_output({'obligation':'Identify the event.'},self.c))
  for v in ({'obligation':''},{'obligation':'x','reason':'y'},{'obligation':None},{'need':'x'},['x']):self.assertFalse(validate_output(v,self.c))
 def test_no_gold_or_H_leakage(self):
  for field in ('Gold Obligation','Gold Gap','Historical Need','Working Hypothesis','arm'):
   jobs=copy.deepcopy(self.jobs);j=next(x for x in jobs if x['arm']=='C0');payload=json.loads(j['request']['messages'][1]['content']);payload[field]='prohibited';j['request']['messages'][1]['content']=json.dumps(payload)
   with self.assertRaises(AssertionError):preflight(jobs,self.cases,self.cfg)
 def test_preflight_mutations(self):
  for mutate in (lambda j:j[0]['request'].update(max_tokens=8),lambda j:j[0]['request'].update(model='other'),lambda j:j.append(j[0]),lambda j:j.pop(),lambda j:j[0]['request']['messages'][0].update(content='Return an object')):
   jobs=copy.deepcopy(self.jobs);mutate(jobs)
   with self.assertRaises(AssertionError):preflight(jobs,self.cases,self.cfg)
 def test_literal_guard_before_transport(self):
  j=copy.deepcopy(self.j);j['request']['messages'][0]['content']='Return an object';j['request']['messages'][1]['content']='{}'
  class NoSend:
   def post(self,*a,**kw):raise AssertionError('NETWORK MUST NOT BE REACHED')
  with tempfile.TemporaryDirectory() as d,patch('experiments.obligation_context_sufficiency.run.request_for',return_value=j['request']):
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

class ContextContracts(unittest.TestCase):
 def test_exact_QC(self):
  from .context import construct,claims
  for c in bank().values():
   construct(c);s=read(ROOT/c['snapshot'])['state']
   self.assertEqual(c['belief']['question'],s['question']);self.assertEqual(c['claims'],claims(s))
   bad=copy.deepcopy(c);bad['belief']['question']+=' fabricated'
   with self.assertRaises(AssertionError):construct(bad)
 def test_previous_checkpoint_delta(self):
  from .context import construct,claims
  for c in bank().values():
   cc,s,_,_=construct(c);previous=read(ROOT/s['previous_checkpoint'])['state'] if s['previous_checkpoint'] else None
   expected=[v for v in c['claims'] if v['statement'] not in {x['statement'] for x in claims(previous)}] if previous else []
   self.assertEqual(cc['CDELTA']['recent_claim_delta'],expected)
 def test_future_index_and_time(self):
  from .context import construct
  for c in bank().values():
   cc,s,_,events=construct(c)
   for e in events:
    self.assertLessEqual(e['event_index'],s['source_event_index']);self.assertLessEqual(e['completed_by_utc'],s['prefix_end'])
   # No future Writer/Actor files in the read log, nor aggregate RESULT files.
   import re
   transition=read(ROOT/c['snapshot'])['transition']
   cap=(0,0) if transition=='initial' else tuple(map(int,transition.removeprefix('update_').split('_')))
   for path in s['context_sources']:
    self.assertNotIn('RESULT',path)
    m=re.search(r'(?:writer_|update_)(\d+)_(\d+)',path)
    if m:self.assertLessEqual(tuple(map(int,m.groups())),cap)
    m=re.search(r'actor_(\d+)',path)
    if m:self.assertEqual(m.group(1),'1')
 def test_last_four_events(self):
  from .context import construct
  for c in bank().values():
   cc,s,_,events=construct(c)
   self.assertEqual(s['recent_event_indices'],[e['event_index'] for e in events[-4:]])
   self.assertEqual([x['event_type'] for x in cc['C1']['recent_events']],[e['event_type'] for e in events[-4:]])
 def test_recent_observations_exact_and_matched(self):
  from .context import construct
  for c in bank().values():
   cc,s,_,_=construct(c);obs=cc['C2']['recent_observations'];self.assertLessEqual(len(obs),2)
   for o,src in zip(obs,s['observation_sources']):
    raw=read(ROOT/src['source_file'])['observations'][src['array_index']]
    self.assertEqual(o,{'observation_ref':raw['window_ref'],'source_ref':raw['doc_ref'],'text':raw['text']})
    self.assertIn(src['event_index'],s['recent_event_indices'])
 def test_no_H_gold_review_projections(self):
  from .context import construct
  forbidden={'hypothesis','Working Hypothesis','gold_obligation','gold_gap','reason','reasoning','rationale','error_labels','arm','need','reference_status'}
  def check(v):
   if isinstance(v,dict):
    self.assertFalse(set(v)&forbidden)
    for x in v.values():check(x)
   if isinstance(v,list):
    for x in v:check(x)
  for c in bank().values():
   contexts,*_=construct(c)
   for a in ARMS:
    check(input_for(c,a));self.assertEqual(input_for(c,a)['Recent Context'],contexts[a])
   self.assertEqual(contexts['C0'],dict(recent_claim_delta=[],recent_events=[],recent_observations=[]))
   self.assertEqual(contexts['CDELTA']['recent_claim_delta'],contexts['C2']['recent_claim_delta'])
   self.assertEqual(contexts['C1']['recent_events'],contexts['C2']['recent_events'])

if __name__=='__main__':unittest.main()
