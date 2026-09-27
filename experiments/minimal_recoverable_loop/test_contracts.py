"""Offline adversarial invariant checks; fixtures are never study evidence."""
import copy
import unittest
from unittest.mock import patch
from .contracts import *
from .requests import request,writer_jobs,compile_admissions
from .run import parse

class Boundaries(unittest.TestCase):
    def setUp(self):
        self.s=MinimalLoopState('Who had no children as of2019?',[
            {'requirement_id':'R1','text':'Identify the person as of2019.'}])
        self.src={'source_id':'S1','source_observation':{'title':'Example','url':'https://example.test',
                  'text':'The2019 source says Alice was married without children.'},
                  'historical_refs':{'doc_ref':'D1','window_ref':'W1'}}
        self.s.register_source(self.src)
        self.c={'source_id':'S1','statement':'The2019 source says Alice was married without children.',
                'supporting_excerpt':'The2019 source says Alice was married without children.'}
        self.a={'focus_requirement_id':'R1','strategy':'VERIFY_RELATION','focus_hypothesis_ids':[],
                'one_useful_gap':'Identify the relevant relationship.','probe':'Find evidence for the relationship.',
                'action':{'type':'SEARCH','query':'Alice2019','source_ref':None,'pattern':None},'expected_gain':'NEW_CLAIM'}

    def test_actor_and_h_cannot_mutate_authoritative_inputs(self):
        original=self.s.view();view=self.s.view();view['Q']='changed';view['R'].clear();view['C'].append(self.c)
        self.assertEqual(self.s.view(),original)
        for field in ('C','R','Q','claims_to_add','STOP','closed_requirements'):
            out=copy.deepcopy(self.a);out[field]='attack'
            with self.assertRaises(ValueError):self.s.record_actor(out)
        with self.assertRaises(ValueError):self.s.hypothesis_operations({'operations':[],'C':[self.c]})
        self.assertEqual(self.s.view()['C'],[])

    def test_admission_requires_actual_excerpt_and_component_result(self):
        for c,v in [({**self.c,'supporting_excerpt':'Invented quotation.'},{'verdict':'ADMIT','error_tags':[]}),
                    ({**self.c,'source_id':'S2'},{'verdict':'ADMIT','error_tags':[]}),
                    (self.c,{'verdict':'REJECT','error_tags':['other']}),
                    (self.c,{'verdict':'ADMIT','error_tags':['unsupported_inference']})]:
            self.assertIsNone(self.s.admit(c,v,str([c,v])))
        self.assertEqual(self.s.admit(self.c,{'verdict':'ADMIT','error_tags':[]},'valid'),'C1')
        with self.assertRaises(ValueError):self.s.admit(self.c,{'verdict':'ADMIT','error_tags':[]},'valid')
        self.assertEqual(len(self.s.view()['C']),1)

    def test_renamed_query_does_not_reset_family(self):
        for query in ('Alice2019','2019Alice'):
            a=copy.deepcopy(self.a);a['action']['query']=query;before=self.s.view()
            tok=self.s.record_actor(a);self.assertFalse(self.s.finish_acquisition(tok,before)['gain'])
        self.assertTrue(self.s.view()['TraceView']['strategy_shift_required'])
        with self.assertRaisesRegex(ValueError,'POLICY_VIOLATION'):self.s.record_actor(self.a)
        a=copy.deepcopy(self.a);a['strategy']='LOCATE_SOURCE';self.s.record_actor(a)

    def test_pending_source_gain_only_once(self):
        before=self.s.view();t=self.s.record_actor(self.a)
        self.assertTrue(self.s.finish_acquisition(t,before,source_refs_seen=['S1'],followups=['S1'])['gain'])
        before=self.s.view();t=self.s.record_actor(self.a)
        self.assertFalse(self.s.finish_acquisition(t,before,source_refs_seen=['S1'],followups=['S1'])['gain'])

    def test_h_dedup_and_transactional_capacity(self):
        for statement in ('Euler may be the person','The person could be Euler','Perhaps Euler is relevant'):
            self.s.hypothesis_operations({'operations':[{'type':'ADD','hypothesis_id':None,'statement':statement,'status':'active','basis_refs':['S1']}]})
        self.assertEqual(len(self.s.view()['H']),1);self.assertEqual(self.s.view()['C'],[])
        old=self.s.view()
        ops=[{'type':'ADD','hypothesis_id':None,'statement':f'Candidate name{i}','status':'active','basis_refs':['S1']} for i in range(7)]
        with self.assertRaises(ValueError):self.s.hypothesis_operations({'operations':ops})
        self.assertEqual(self.s.view(),old)

    def test_closure_authority_and_staleness(self):
        self.s.record_actor({'action':{'type':'REQUEST_CLOSURE_AUDIT'}})
        with self.assertRaises(ValueError):self.s.answer_input()
        self.assertNotIn('H',self.s.closure_input());self.assertNotIn('TraceView',self.s.closure_input())
        self.s.record_closure({'requirements':[{'requirement_id':'R1','status':'OPEN','supporting_claim_ids':[],'missing':'A relation is missing.'}],'overall':'CONTINUE'})
        with self.assertRaises(ValueError):self.s.answer_input()
        self.s.admit(self.c,{'verdict':'ADMIT','error_tags':[]},'one')
        self.s.record_closure({'overall':'READY_TO_ANSWER'})
        self.assertNotIn('H',self.s.answer_input())
        self.s.register_source({'source_id':'S2','source_observation':{'title':'Conflict','url':'https://example.test/2','text':'A conflicting observation.'}})
        self.s.admit({'source_id':'S2','statement':'A conflicting observation.','supporting_excerpt':'A conflicting observation.'},{'verdict':'ADMIT','error_tags':[]},'two')
        with self.assertRaises(ValueError):self.s.answer_input()
        with self.assertRaises(ValueError):self.s.record_closure({'overall':'READY_TO_ANSWER'})

    def test_only_actual_tool_routes(self):
        self.assertEqual(tool_action(self.a),('search',{'query':'Alice2019','k':5}))
        a=copy.deepcopy(self.a);a['action']={'type':'FIND','query':'marriage','source_ref':'D1','pattern':None}
        self.assertTrue(validate_actor(a,self.s.view()));self.assertEqual(tool_action(a)[1]['doc_ref'],'D1')
        a['action']['source_ref']='D999';self.assertFalse(validate_actor(a,self.s.view()))
        a['action']={'type':'OPEN','query':None,'source_ref':'W1','pattern':'after'}
        self.assertTrue(validate_actor(a,self.s.view()));self.assertEqual(tool_action(a)[1]['direction'],'after')

    def test_frozen_writer_excludes_h_and_hidden_labels(self):
        js=writer_jobs();self.assertEqual(len(js),106)
        import json
        for j in js:
            payload=json.loads(j['request']['messages'][1]['content'])
            self.assertEqual(set(payload),{'original_question','relevant_requirement','source_id','source_observation'})
            self.assertEqual(j['request']['temperature'],0)
            self.assertNotIn('tools',j['request'])

    def test_parse_does_not_use_reasoning_or_repair_schema(self):
        import json
        j={'phase':'writer','request':{'model':'deepseek-flash'}}
        raw={'model':'deepseek-flash','choices':[{'finish_reason':'stop','message':{'content':'bad JSON','reasoning_content':'{"candidate_claims":[],"followup_source_refs":[]}'}}]}
        self.assertFalse(parse(200,json.dumps(raw),j)['valid_output'])
        raw['choices'][0]['message']['content']='{"candidate_claims":[],"followup_source_refs":[]}'
        self.assertTrue(parse(200,json.dumps(raw),j)['valid_output'])
        raw['choices'][0]['finish_reason']='length';self.assertFalse(parse(200,json.dumps(raw),j)['valid_output'])

    def test_excerpt_locality_not_full_claimset(self):
        import json
        from .common import P,read
        b=read(P/'e0_reference/ADMISSION_BANK.json')[0]
        candidate={'source_id':b['source_id'],'statement':'Example candidate for compiler test.',
                   'supporting_excerpt':b['source_observation']['text'][:50]}
        w={'id':'W_S001_r1','valid_output':True,'source_id':b['source_id'],'replicate':1,
           'output':{'candidate_claims':[candidate,{**candidate,'supporting_excerpt':'not present xyz'}],'followup_source_refs':[]}}
        js,ledger=compile_admissions([w]);self.assertEqual(len(js),1);self.assertEqual(len(ledger),2)
        payload=json.loads(js[0]['request']['messages'][1]['content'])
        self.assertEqual(set(payload),{'candidate_claim','exact_supporting_excerpt','source_metadata'})
        self.assertEqual(payload['exact_supporting_excerpt'],candidate['supporting_excerpt'])
        self.assertNotIn('Q',payload);self.assertNotIn('R',payload);self.assertNotIn('H',payload)

    def test_split_claim_recall_requires_complete_witness(self):
        from .score import covered_slots
        proofs=[{'replicate':1,'atom_id':'compound','sufficient_candidate_sets':[['C1','C2'],['C3']]},
                {'replicate':2,'atom_id':'compound','sufficient_candidate_sets':[['C4','C5']]}]
        self.assertEqual(covered_slots(proofs,{'C1'}),set())
        self.assertEqual(covered_slots(proofs,{'C1','C2'}),{(1,'compound')})
        self.assertEqual(covered_slots(proofs,{'C3','C4'}),{(1,'compound')})
        self.assertEqual(covered_slots(proofs,{'C1','C2','C3','C4','C5'}),{(1,'compound'),(2,'compound')})

    def test_cache_accounting_excludes_unknown_and_inconsistent_usage(self):
        from .run import accounting
        def row(tokens,hit,miss):
            return {'attempted':True,'valid_output':True,'usage':{'prompt_tokens':tokens,
                    'completion_tokens':5,'total_tokens':tokens+5,
                    'completion_tokens_details':{'reasoning_tokens':2},
                    'prompt_cache_hit_tokens':hit,'prompt_cache_miss_tokens':miss}}
        # 80/100 and 0/900 aggregate to 8%, not the mean of rates (40%).
        out=accounting([row(100,80,20),row(900,0,900),row(100,100,100),
                        {'attempted':True,'valid_output':False,'usage':None}])
        self.assertEqual(out['cache_hit_rate_reported_tokens']['value'],.08)
        self.assertEqual(out['cache_rate_eligible_calls'],2)
        self.assertEqual(out['cache_rate_excluded_attempts'],2)

if __name__=='__main__':unittest.main()
