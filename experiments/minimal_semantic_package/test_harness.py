"""Offline tests for costly-call guards, semantic scope and scoring hazards."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from .common import P, read
from .inputs import verifier_schedule, references, validate, auditor_job
from .run import parse
from .score import aggregate, gate, combine

class HarnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.jobs=verifier_schedule()
        cls.refs=references()

    def job(self,cid,rep=1):
        return next(j for j in self.jobs if j['certificate_id']==cid and j['replicate']==rep)

    def result(self,job,output):
        return {**{k:job[k] for k in ('id','certificate_id','replicate','request_sha256')},
                'valid_output':validate(output,job),'output':output}

    def perfect(self):
        out=[]
        for job in self.jobs:
            ref=self.refs[job['certificate_id']]
            yes=ref['gold_support']=='SUPPORTED'
            v=self.result(job,{'verdict':ref['gold_support'],
                 'supporting_claim_ids':ref['minimal_sufficient_claim_sets'][0] if yes else [],
                 'uncovered_target_unit_ids':[] if yes else ref['material_gap_anchor_unit_ids']})
            a={'valid_output':True,'output':{'uncovered_target_unit_ids':[]}} if yes else None
            out.append({'verifier':v,'auditor':a})
        return out

    def test_exact_source_spans_and_unchanged_claims(self):
        for p in read(P/'e0_reference/UNITS.json'):
            previous=0
            for u in p['units']:
                self.assertEqual(p['parent_text'][u['start']:u['end']],u['text'])
                self.assertFalse(p['parent_text'][previous:u['start']].strip())
                previous=u['end']
            self.assertFalse(p['parent_text'][previous:].strip())
        historical={r['certificate_id']:r for r in read(P/'e0_reference/HISTORICAL_CERTIFICATES.json')}
        for cid,r in self.refs.items():
            self.assertEqual(r['candidate_verified_claims'],historical[cid]['candidate_verified_claims'])

    def test_same_parent_locator_has_one_evidence_independent_package(self):
        grouped={}
        for c in self.refs.values():
            key=(c['parent_id'],c['candidate_locator'])
            grouped.setdefault(key,set()).add(c['package_id'])
        self.assertEqual(len(grouped),34)
        self.assertTrue(all(len(s)==1 for s in grouped.values()))
        self.assertEqual(self.refs['A13_CAND1']['package_id'],self.refs['A14_CAND1']['package_id'])

    def test_payload_has_no_gold_parent_question_locator_or_siblings(self):
        packages={p['package_id']:p for p in read(P/'e0_reference/GOLD_PACKAGES.json')}
        for j in self.jobs:
            payload=json.loads(j['request']['messages'][1]['content'])
            self.assertEqual(set(payload),{'target_semantics','interpretive_context','verified_claims'})
            pkg=packages[j['package_id']]
            self.assertEqual([u['unit_id'] for u in payload['target_semantics']],pkg['target_unit_ids'])
            self.assertEqual([u['unit_id'] for u in payload['interpretive_context']],pkg['interpretive_context_unit_ids'])

    def test_clinical_country_sibling_and_euler_governing_relation(self):
        clinical=json.loads(self.job('A17_CAND1')['request']['messages'][1]['content'])
        target=' '.join(u['text'] for u in clinical['target_semantics'])
        self.assertIn('The first case',target)
        self.assertNotIn('country',target)
        euler=json.loads(self.job('A15_CAND1')['request']['messages'][1]['content'])
        self.assertIn('Additionally, it references',[u['text'] for u in euler['target_semantics']])

    def test_syntax_and_context_ids_cannot_masquerade_as_target_gaps(self):
        job=self.job('A17_CAND3')
        self.assertFalse(validate({'verdict':'OPEN','supporting_claim_ids':[],'uncovered_target_unit_ids':['U6']},job))
        self.assertFalse(validate({'verdict':'SUPPORTED','supporting_claim_ids':[],'uncovered_target_unit_ids':[]},job))
        self.assertFalse(validate({'verdict':'SUPPORTED','supporting_claim_ids':['C7','C7'],'uncovered_target_unit_ids':[]},job))
        self.assertFalse(validate({'verdict':'SUPPORTED','supporting_claim_ids':['C999'],'uncovered_target_unit_ids':[]},job))

    def test_auditor_sees_only_actual_cited_subset(self):
        job=self.job('A03_CAND1')
        v=self.result(job,{'verdict':'SUPPORTED','supporting_claim_ids':['C2','C5'],'uncovered_target_unit_ids':[]})
        a=auditor_job(job,v)
        payload=json.loads(a['request']['messages'][1]['content'])
        self.assertEqual([c['claim_id'] for c in payload['verified_claims']],['C2','C5'])
        self.assertNotIn('verdict',payload)
        self.assertNotIn('reasoning',payload)
        opened=self.result(job,{'verdict':'OPEN','supporting_claim_ids':[],'uncovered_target_unit_ids':['U1']})
        self.assertIsNone(auditor_job(job,opened))

    def test_perfect_reference_and_mandatory_euler_stop(self):
        records=self.perfect()
        self.assertTrue(gate(aggregate(records,self.refs),complete=True)['E1_PASS'])
        item=next(r for r in records if r['verifier']['certificate_id']=='A15_CAND1')
        item['verifier']['output']={'verdict':'SUPPORTED','supporting_claim_ids':['C1'],'uncovered_target_unit_ids':[]}
        item['auditor']={'valid_output':True,'output':{'uncovered_target_unit_ids':[]}}
        scored=aggregate(records,self.refs)
        self.assertEqual(scored['Euler_false_support_count'],1)
        self.assertFalse(gate(scored,complete=True)['E1_PASS'])

    def test_wrong_witness_not_counted_as_true_support(self):
        job=self.job('A03_CAND1')
        v=self.result(job,{'verdict':'SUPPORTED','supporting_claim_ids':['C2'],'uncovered_target_unit_ids':[]})
        scored=aggregate([{'verifier':v,'auditor':{'valid_output':True,'output':{'uncovered_target_unit_ids':[]}}}],self.refs)
        self.assertEqual((scored['TP'],scored['FP'],scored['missed_positives']),(0,1,1))
        self.assertEqual(scored['verifier_only_verdict_precision']['value'],1)

    def test_audit_rescue_false_open_and_failure_are_distinct(self):
        bad=self.job('A15_CAND1');good=self.job('A17_CAND1')
        records=[]
        for j in (bad,good):
            claim=self.refs[j['certificate_id']]['candidate_claim_ids'][0]
            v=self.result(j,{'verdict':'SUPPORTED','supporting_claim_ids':[claim],'uncovered_target_unit_ids':[]})
            records.append({'verifier':v,'auditor':{'valid_output':True,'output':{'uncovered_target_unit_ids':['U1']}}})
        scored=aggregate(records,self.refs)
        self.assertEqual(scored['uncovered_audit_rescue']['numerator'],1)
        self.assertEqual(scored['auditor_introduced_false_open'],1)
        records[0]['auditor']={'valid_output':False,'output':None}
        self.assertEqual(aggregate(records,self.refs)['uncovered_audit_rescue']['numerator'],0)
        self.assertFalse(combine(records[0]['verifier'],None)['valid_chain'])

    def test_failures_and_pending_batches_cannot_pass(self):
        records=self.perfect()
        for r in records:
            r['verifier']['valid_output']=False
        m=aggregate(records,self.refs)
        self.assertEqual(m['planned'],96)
        self.assertEqual(m['missed_positives'],42)
        self.assertIsNone(m['support_precision']['value'])
        self.assertFalse(gate(m,complete=True)['E1_PASS'])
        self.assertEqual(gate(aggregate(self.perfect(),self.refs),complete=False)['status'],'PENDING')

    def test_response_contract_and_reasoning_exclusion(self):
        job=self.job('A17_CAND1')
        out={'verdict':'SUPPORTED','supporting_claim_ids':['C7'],'uncovered_target_unit_ids':[]}
        response={'model':job['request']['model'],'choices':[{'finish_reason':'stop','message':{'content':json.dumps(out),'reasoning_content':'UNTRUSTED_REASONING'}}]}
        parsed=parse(200,json.dumps(response),job)
        self.assertTrue(parsed['valid_output'])
        self.assertNotIn('UNTRUSTED_REASONING',json.dumps(parsed))
        response['choices'][0]['finish_reason']='length'
        self.assertFalse(parse(200,json.dumps(response),job)['valid_output'])

    def test_literal_task_prompt_and_required_provider_configuration(self):
        from .prepare import literal_prompt
        for phase,section in [('verifier',10),('auditor',11)]:
            self.assertEqual((P/f'prompts/{phase}.txt').read_text(),literal_prompt(section))
        config=read(P/'CONFIG.json')
        self.assertEqual((config['model'],config['temperature'],config['max_retries']),('deepseek-flash',0,0))
        self.assertLessEqual(config['max_workers'],8)
        for job in self.jobs:
            self.assertEqual(job['request']['messages'][0]['content'],literal_prompt(10))
            self.assertNotIn('tools',job['request'])

    def test_timeout_preserved_once_without_secret_or_retry(self):
        import httpx
        from .run import Batch
        from unittest.mock import Mock
        client=Mock()
        client.post.side_effect=httpx.ReadTimeout('sensitive remote exception text')
        config=read(P/'CONFIG.json')
        with tempfile.TemporaryDirectory() as folder,patch('experiments.minimal_semantic_package.run.OUT',Path(folder)):
            job=self.jobs[0]
            batch=Batch(client,'SECRET_SENTINEL',config,'verifier','synthetic-test-head')
            batch.one(job)
            self.assertEqual(client.post.call_count,1)
            output=read(Path(folder)/'verifier/calls'/f"{job['id']}.result.json")
            self.assertEqual(output['failure'],'timeout')
            self.assertTrue(output['attempted'])
            contents=''.join(p.read_text() for p in Path(folder).rglob('*.json'))
            self.assertNotIn('SECRET_SENTINEL',contents)
            self.assertNotIn('sensitive remote exception text',contents)

    def test_fresh_authorization_is_required_before_credentials_or_http(self):
        if not (P/'e1_gold_support/VERIFIER_FREEZE.json').exists():
            self.skipTest('run this gate again after the freeze is committed')
        from .run import execute
        with patch('experiments.minimal_semantic_package.run.credential') as key,patch('httpx.Client') as client:
            with self.assertRaisesRegex(PermissionError,'NEW explicit user authorization'):
                execute('verifier')
            key.assert_not_called()
            client.assert_not_called()

if __name__=='__main__':
    unittest.main()
