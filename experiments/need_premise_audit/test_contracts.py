"""Network-free tests of references, failure preservation and stage boundaries."""
import copy
import json
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import patch
import httpx

from .common import P, bank, digest, read
from .run import Batch, parse_response, validate_output
from .score import gate

C = {'claims': [{'id':'C1','statement':'X exists.'}]}
V1 = {'target':'Whether X did R','subject':{'description':'X','status':'grounded','basis_refs':['C1']},
      'required_background':[{'statement':'X exists','status':'supported','basis_refs':['C1']}],'decision':'keep'}

class Contracts(unittest.TestCase):
    def test_illegal_refs_rejected_in_every_slot(self):
        for ref in ('H','memory','C99','C01','https://example.org','Source title'):
            with self.subTest(ref=ref):
                value=copy.deepcopy(V1);value['subject']['basis_refs']=[ref]
                self.assertFalse(validate_output(value,'V1',C))
                value=copy.deepcopy(V1);value['required_background'][0]['basis_refs']=[ref]
                self.assertFalse(validate_output(value,'V1',C))
                self.assertFalse(validate_output({'decision':'revise','issue':'bad','basis_refs':[ref]},'V0',C))

    def test_schema_is_not_entailment(self):
        self.assertTrue(validate_output(V1,'V1',C))
        value=copy.deepcopy(V1);value['required_background'][0]['statement']='X performed an unverified event'
        self.assertTrue(validate_output(value,'V1',C))  # Semantic review must catch the false anchor.
        value['need']='unrequested repair'
        self.assertFalse(validate_output(value,'V1',C))

    def test_parse_preserves_schema_invalid_json(self):
        value=copy.deepcopy(V1);value['subject']['basis_refs']=['H']
        body=json.dumps({'model':'deepseek-flash','choices':[{'finish_reason':'stop','message':{'content':json.dumps(value)}}]})
        r=parse_response(200,body,{'arm':'V1','request':{'model':'deepseek-flash'}},C)
        self.assertTrue(r['valid_json']);self.assertFalse(r['valid_output']);self.assertEqual(r['output'],value)

    def test_length_retained(self):
        body=json.dumps({'model':'deepseek-flash','usage':{'completion_tokens':65535},
                         'choices':[{'finish_reason':'length','message':{'content':''}}]})
        r=parse_response(200,body,{'arm':'V1','request':{'model':'deepseek-flash'}},C)
        self.assertEqual(r['failure'],'length');self.assertEqual(r['usage']['completion_tokens'],65535)

    def test_replicates_identical_and_candidates_exact(self):
        jobs=read(P/'e1_checker/SCHEDULE.json'); candidates=bank()
        self.assertEqual(len(jobs),88)
        for cid in candidates:
            for arm in ('V0','V1'):
                pair=[j for j in jobs if j['candidate_id']==cid and j['arm']==arm]
                self.assertEqual(len(pair),2);self.assertEqual(pair[0]['request'],pair[1]['request'])
                self.assertEqual(json.loads(pair[0]['request']['messages'][1]['content'])['Candidate Need'],candidates[cid]['candidate_need'])
                self.assertFalse(set(pair[0]['request'])&{'tools','max_tokens','max_completion_tokens'})

    def test_billing_halt_and_transport_no_retry(self):
        seed=read(P/'e1_checker/SCHEDULE.json')[0]; config=read(P/'CONFIG.json')
        jobs=[{**seed,'id':'test'+str(i)} for i in range(3)]
        for status in (402,'timeout'):
            sent=[]
            def handler(request):
                sent.append(request)
                if status=='timeout':raise httpx.ReadTimeout('test',request=request)
                return httpx.Response(status,json={'error':{'message':'test'}})
            with tempfile.TemporaryDirectory() as directory, patch.object(socket.socket,'connect',side_effect=AssertionError('No real network')):
                with httpx.Client(transport=httpx.MockTransport(handler)) as client:
                    Batch(client,'fake-test-only',config,bank(),Path(directory),'test-head').run(jobs)
                results=[read(f) for f in (Path(directory)/'calls').glob('*.result.json')]
                self.assertEqual(len(results),3);self.assertTrue(all(not r['valid_output'] for r in results))
                self.assertEqual(len(sent),1 if status==402 else 3)

    def test_conjunctive_gate_boundaries(self):
        base={'n':44,'invalid_n':22,'control_n':22,'invalid_detected':19,'controls_kept':19,
              'all_binding_correct':38,'distinction_correct':38,'replicate_agree':18,'replicate_pairs':22,
              'valid_output':42,'balanced_accuracy':19/22}
        good={'V0':copy.deepcopy(base),'V1':copy.deepcopy(base)}
        self.assertEqual(gate(good)['status'],'PASS_TO_E2');self.assertFalse(gate(good)['opens_E3'])
        for k in ('invalid_detected','controls_kept','all_binding_correct','distinction_correct','replicate_agree','valid_output'):
            m=copy.deepcopy(good);m['V1'][k]-=1
            self.assertEqual(gate(m)['status'],'STOP_E1',k)
        m=copy.deepcopy(good);m['V0']['balanced_accuracy']=1
        self.assertEqual(gate(m)['status'],'STOP_E1')

if __name__=='__main__':
    unittest.main()
