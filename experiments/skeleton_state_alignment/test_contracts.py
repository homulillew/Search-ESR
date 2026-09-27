"""Offline contract/denominator/failure tests. All fake transport uses tempdirs."""
import copy
import contextlib
import io
import json
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
import httpx
from .common import P, bank, read, runtime_nodes, digest
from .contracts import alignment_errors, selection_errors, project_mask, residual
from .inputs import alignment_input, selection_input, gold_mask
from .prepare import build_schedule
from .run import Batch, parse_response, accounting, authorization
from .score import e1_counts, e1_metrics, e2_metrics, check_gates

F='fully_supported';PART='partially_supported';U='unsupported'
def prediction(nodes,status=U,refs=()):
    return {'requirements':[{'requirement_id':n['requirement_id'],'status':status,'supported_by':list(refs)} for n in nodes]}
def response_for(job,value=None,model='deepseek-flash',finish='stop',usage=None):
    if value is None:value=prediction(json.loads(job['request']['messages'][1]['content'])['Task Skeleton'])
    return json.dumps({'model':model,'choices':[{'finish_reason':finish,'message':{'content':json.dumps(value)}}],'usage':usage})

class InputContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.states=bank();cls.jobs=build_schedule('e1_alignment');cls.nodes=runtime_nodes('261','A1')
        cls.claims=[{'claim_id':'C1','statement':'Example local fact'}]

    def test_cross_product_and_frozen_schedule(self):
        for stage in ('e1_alignment','e2_selection'):
            rows=build_schedule(stage)
            self.assertEqual(len(rows),108);self.assertEqual(len({r['id'] for r in rows}),108)
            self.assertEqual(rows,read(P/stage/'SCHEDULE.json'))
            self.assertEqual({r['case_id'] for r in rows},set(self.states))

    def test_e1_whitelist_ignores_poisoned_metadata(self):
        c=copy.deepcopy(self.states['G03']);base=alignment_input(c,'A1')
        c.update(gold_obligation='LEAK',future_claims=['LEAK'],hypothesis='LEAK',workspace='LEAK',type='LEAK')
        c['claims'][0]['audit_note']='LEAK'
        self.assertEqual(base,alignment_input(c,'A1'))
        self.assertEqual(set(base),{'Original Question','Task Skeleton','Verified Claims'})
        self.assertNotIn('LEAK',json.dumps(base))

    def test_e2_has_no_claims_or_support_refs(self):
        c=self.states['G03'];m=gold_mask('G03')
        for n in m['requirements']:n.update(supported_by=['C1'],reason='LEAK',gold_label='LEAK')
        value=selection_input(c,m)
        self.assertEqual(set(value),{'Original Question','Task Skeleton','Coverage Mask'})
        self.assertTrue(all(set(n)=={'requirement_id','status'} for n in value['Coverage Mask']['requirements']))
        self.assertNotIn('LEAK',json.dumps(value));self.assertNotIn('Verified Claims',value)

    def test_s1_is_deferred_fixed_replicate1(self):
        rows=[r for r in build_schedule('e2_selection') if r['arm']=='S1']
        self.assertEqual(len(rows),54)
        for r in rows:
            self.assertIsNone(r['request']);self.assertIsNone(r['request_sha256'])
            self.assertTrue(r['mask_source'].endswith(f"A1__{r['case_id']}__R1.result.json"))

    def test_provider_shape_never_adds_tools_or_token_cap(self):
        for r in self.jobs:
            q=r['request'];self.assertEqual(set(q),{'model','temperature','stream','response_format','messages'})
            self.assertEqual(q['model'],'deepseek-flash');self.assertEqual(q['temperature'],0)
            self.assertEqual(q['response_format'],{'type':'json_object'});self.assertIn('JSON',q['messages'][0]['content'])

    def test_all_empty_claims_references_unsupported(self):
        gold=read(P/'e1_alignment/GOLD_MASKS.json')
        for row in gold:
            if not self.states[row['case_id']]['claims']:
                self.assertTrue(all(n['status']==U and not n['contributing_claims'] for n in row['requirements'].values()))

    def test_valid_unsupported_and_reordered_ids(self):
        v=prediction(self.nodes);v['requirements'].reverse()
        self.assertFalse(alignment_errors(v,self.nodes,self.claims))
        self.assertEqual([r['requirement_id'] for r in project_mask(v,self.nodes)['requirements']], [n['requirement_id'] for n in self.nodes])
        self.assertEqual(set(residual(v)),{n['requirement_id'] for n in self.nodes})

    def test_duplicate_missing_unknown_ids_rejected(self):
        for mode in ('duplicate','missing','unknown'):
            v=prediction(self.nodes)
            if mode=='duplicate':v['requirements'][-1]=copy.deepcopy(v['requirements'][0])
            if mode=='missing':v['requirements'].pop()
            if mode=='unknown':v['requirements'][0]['requirement_id']='R999'
            self.assertTrue(alignment_errors(v,self.nodes,self.claims))

    def test_status_citation_contract(self):
        for status,refs in [(F,[]),(PART,[]),(U,['C1']),(F,['C999']),(PART,['C1','C1']),('confidence_0.9',[])]:
            self.assertTrue(alignment_errors(prediction(self.nodes,status,refs),self.nodes,self.claims))
        self.assertFalse(alignment_errors(prediction(self.nodes,PART,['C1']),self.nodes,self.claims))

    def test_extra_fields_and_bad_types_rejected(self):
        variants=[]
        v=prediction(self.nodes);v['reasoning']='explanation';variants.append(v)
        v=prediction(self.nodes);v['requirements'][0]['confidence']=.9;variants.append(v)
        v=prediction(self.nodes);v['requirements'][0]['supported_by']=None;variants.append(v)
        v=prediction(self.nodes);v['requirements'][0]['status']={'bad':'type'};variants.append(v)
        for v in variants:self.assertTrue(alignment_errors(v,self.nodes,self.claims))

    def test_selection_contract_does_not_semantically_validate_STOP(self):
        self.assertFalse(selection_errors({'selection':'STOP'},self.nodes))
        for v in ({'selection':['R1']},{'selection':'R1','reason':'x'},{'selection':'R999'},{'selection':None}):
            self.assertTrue(selection_errors(v,self.nodes))

    def test_selection_partitions_no_manufactured_STOP(self):
        rows=read(P/'e2_selection/SELECTION_REFERENCE.json')
        self.assertEqual(len(rows),27);self.assertFalse(any(r['stop_allowed'] for r in rows))
        self.assertEqual([r['case_id'] for r in rows if r['no_admissible_single_id']],['G04','G05'])
        for r in rows:
            ids=sum([r[k] for k in ('acceptable_active_ids','invalid_supported_ids','blocked_or_downstream_ids','other_invalid_ids')],[])
            expected=[n['requirement_id'] for n in runtime_nodes(str(r['qid']),'A1')]
            self.assertEqual(sorted(ids),sorted(expected));self.assertEqual(len(set(ids)),len(ids))

class MetricContracts(unittest.TestCase):
    def gold(self):
        return {'requirements':{'R1':{'status':F,'acceptable_full_support_groups':[['C1','C2'],['C4']],
          'acceptable_partial_support_groups':[],'contributing_claims':['C1','C2','C4']},
         'R2':{'status':PART,'acceptable_full_support_groups':[],'acceptable_partial_support_groups':[['C3']],
          'contributing_claims':['C3']}}}
    def row(self,refs=('C4',),second=PART):
        return {'case_id':'test','arm':'A0','valid_output':True,'output':{'requirements':[
          {'requirement_id':'R1','status':F,'supported_by':list(refs)},
          {'requirement_id':'R2','status':second,'supported_by':['C3'] if second!=U else []}]}}

    def test_alternative_proof_and_superset_not_exact_match(self):
        for refs in (['C1','C2'],['C4'],['C1','C2','C999']):
            c=e1_counts(self.row(refs),self.gold());self.assertEqual(c['full_sufficient'],1)
        c=e1_counts(self.row(['C4','C999']),self.gold())
        self.assertEqual(c['cited'],3);self.assertEqual(c['contributing_cited'],2)

    def test_no_cross_candidate_frankenstein_proof(self):
        g=self.gold();g['requirements']['R1']['acceptable_full_support_groups']=[['C1','C2'],['C3','C4']]
        self.assertEqual(e1_counts(self.row(['C1','C4']),g)['full_sufficient'],0)

    def test_false_supported_uses_all_gold_residual_denominator(self):
        row=self.row(second=F);m=e1_metrics([row],{('test','A0'):self.gold()})
        self.assertEqual(m['false_supported_rate'],{'numerator':1,'denominator':1,'value':1.0})
        self.assertEqual(m['fully_supported_precision']['value'],.5)
        self.assertEqual(m['residual_recall']['value'],0)

    def test_failure_is_not_synthesized_unsupported(self):
        row={'case_id':'test','arm':'A0','valid_output':False,'output':None}
        m=e1_metrics([row],{('test','A0'):self.gold()})
        self.assertEqual(m['node_status_accuracy']['denominator'],2)
        self.assertEqual(m['node_status_accuracy']['value'],0);self.assertEqual(m['residual_recall']['value'],0)
        self.assertEqual(m['false_unresolved_rate']['numerator'],0)
        self.assertEqual(m['counts']['missing_on_gold_full'],1);self.assertIsNone(m['support_precision']['value'])

    def test_schema_invalid_whole_output_no_success_credit(self):
        row=self.row();row['valid_output']=False
        self.assertEqual(e1_counts(row,self.gold())['status_correct'],0)

    def test_partial_needs_substantive_proof_not_name(self):
        row=self.row();row['output']['requirements'][1]['supported_by']=['C999']
        self.assertEqual(e1_counts(row,self.gold())['partial_valid'],0)

    def test_gate_boundaries_and_NA_fail(self):
        rules=read(P/'GATES.json')['A0']
        values={k:{'value':lim} for k,(_,lim) in rules.items()}
        self.assertTrue(check_gates(values,rules)['pass'])
        values['support_precision']['value']=None;self.assertFalse(check_gates(values,rules)['pass'])
        values['support_precision']['value']=.899;self.assertFalse(check_gates(values,rules)['pass'])

    def test_e2_different_acceptable_IDs_valid_and_STOP_false(self):
        jobs=build_schedule('e2_selection');base=next(j for j in jobs if j['arm']=='S0' and j['case_id']=='G01')
        refs={r['case_id']:r for r in read(P/'e2_selection/SELECTION_REFERENCE.json')}
        rows=[{**base,'id':f't{i}','valid_output':True,'output':{'selection':v}} for i,v in enumerate(['R2','R5'])]
        with patch('experiments.skeleton_state_alignment.score.schedule',return_value=[{**base,'id':r['id']} for r in rows]):
            m=e2_metrics(rows,refs)
        self.assertEqual(m['valid_selection']['value'],1)
        self.assertEqual(m['stability']['compatible_different_valid_IDs'],1)
        rows[0]['output']['selection']='STOP'
        with patch('experiments.skeleton_state_alignment.score.schedule',return_value=[{**base,'id':r['id']} for r in rows]):m=e2_metrics(rows,refs)
        self.assertEqual(m['false_stop']['value'],.5);self.assertIsNone(m['missed_stop']['value'])

    def test_complete_e1_metric_pipeline_with_exact_reference_fixture(self):
        from .score import calculate_stage
        gold={(g['case_id'],g['skeleton_arm']):g for g in read(P/'e1_alignment/GOLD_MASKS.json')}
        rows=[]
        for j in build_schedule('e1_alignment'):
            nodes=[]
            for rid,v in gold[j['case_id'],j['arm']]['requirements'].items():
                groups=v['acceptable_full_support_groups'] or v['acceptable_partial_support_groups']
                nodes.append({'requirement_id':rid,'status':v['status'],'supported_by':groups[0] if groups else []})
            rows.append({**j,'valid_output':True,'output':{'requirements':nodes}})
        with patch('experiments.skeleton_state_alignment.score.load_rows',return_value=rows):m=calculate_stage('e1_alignment')
        self.assertTrue(m['joint_gate_pass']);self.assertEqual(m['arms']['A0']['metrics']['counts']['nodes'],322)
        self.assertEqual(m['arms']['A1']['metrics']['counts']['nodes'],264)
        self.assertEqual(m['monotonic_progress']['frozen_eligible_pairs'],15)

    def test_complete_e2_pipeline_preserves_structural_impossibility(self):
        from .score import calculate_stage
        refs={r['case_id']:r for r in read(P/'e2_selection/SELECTION_REFERENCE.json')}
        jobs=build_schedule('e2_selection');rows=[]
        for j in jobs:
            accepted=refs[j['case_id']]['acceptable_active_ids']
            rows.append({**j,'valid_output':True,'output':{'selection':accepted[0] if accepted else 'R2'}})
        with patch('experiments.skeleton_state_alignment.score.load_rows',return_value=rows),patch('experiments.skeleton_state_alignment.score.schedule',return_value=jobs):
            m=calculate_stage('e2_selection')
        self.assertTrue(m['joint_gate_pass']);self.assertAlmostEqual(m['arms']['S0']['metrics']['valid_selection']['value'],25/27)
        self.assertEqual(m['arms']['S0']['metrics']['valid_selection']['denominator'],54)

    def test_failed_e1_gate_cannot_materialize_e2(self):
        from .prepare import materialize_e2
        failed={'joint_gate_pass':False}
        with patch('experiments.skeleton_state_alignment.run.audit'),patch('experiments.skeleton_state_alignment.score.assert_review_sealed'),patch('experiments.skeleton_state_alignment.prepare.read',return_value=failed),patch('experiments.skeleton_state_alignment.score.calculate_stage',return_value=failed),patch('experiments.skeleton_state_alignment.prepare.write') as writer:
            with self.assertRaises(AssertionError):materialize_e2()
            writer.assert_not_called()

class TransportContracts(unittest.TestCase):
    def setUp(self):self.jobs=build_schedule('e1_alignment');self.config=read(P/'CONFIG.json')
    def test_wrong_model_and_truncation_preserve_usage(self):
        usage={'prompt_tokens':3,'completion_tokens':7,'total_tokens':10}
        for model,finish,expected in [('wrong','stop','model_mismatch'),('deepseek-flash','length','length')]:
            v=parse_response(200,response_for(self.jobs[0],model=model,finish=finish,usage=usage),self.jobs[0])
            self.assertFalse(v['valid_output']);self.assertEqual(v['failure'],expected);self.assertEqual(v['usage'],usage)

    def test_timeout_one_attempt_no_retry(self):
        count=[]
        def handler(req):count.append(1);raise httpx.ReadTimeout('offline timeout fixture',request=req)
        with tempfile.TemporaryDirectory() as d, httpx.Client(transport=httpx.MockTransport(handler)) as client,contextlib.redirect_stdout(io.StringIO()):
            batch=Batch(client,'FAKE_TEST_KEY',self.config,Path(d),'test');batch.one(self.jobs[0])
            row=read(Path(d)/'calls'/f"{self.jobs[0]['id']}.result.json")
            self.assertEqual(len(count),1);self.assertEqual(row['failure'],'timeout');self.assertTrue(row['attempted'])

    def test_contract_error_canary_halts_all_remaining(self):
        count=[]
        def handler(req):count.append(1);return httpx.Response(400,json={'error':{'message':'offline contract fixture'}})
        with tempfile.TemporaryDirectory() as d, httpx.Client(transport=httpx.MockTransport(handler)) as client,contextlib.redirect_stdout(io.StringIO()):
            batch=Batch(client,'FAKE_TEST_KEY',self.config,Path(d),'test');batch.run(self.jobs[:12])
            rows=[read(p) for p in (Path(d)/'calls').glob('*.result.json')]
            self.assertEqual(len(count),1);self.assertEqual(len(rows),12)
            self.assertEqual(sum(r['attempted'] for r in rows),1)

    def test_peak_concurrency_at_most_eight_and_no_secret_archived(self):
        active=0;peak=0;lock=threading.Lock()
        def handler(req):
            nonlocal active,peak
            with lock:active+=1;peak=max(peak,active)
            value=json.loads(req.content);nodes=json.loads(value['messages'][1]['content'])['Task Skeleton']
            time.sleep(.015)
            with lock:active-=1
            return httpx.Response(200,text=response_for(self.jobs[0],prediction(nodes)))
        with tempfile.TemporaryDirectory() as d, httpx.Client(transport=httpx.MockTransport(handler)) as client,contextlib.redirect_stdout(io.StringIO()):
            batch=Batch(client,'FAKE_TEST_KEY',self.config,Path(d),'test');batch.run(self.jobs[:18])
            self.assertGreater(peak,1);self.assertLessEqual(peak,8);self.assertEqual(batch.peak,peak)
            self.assertTrue(all('FAKE_TEST_KEY' not in p.read_text() for p in Path(d).rglob('*.json')))

    def test_exclusive_result_paths_prevent_replacement(self):
        count=[]
        def handler(req):count.append(1);return httpx.Response(200,text=response_for(self.jobs[0]))
        with tempfile.TemporaryDirectory() as d, httpx.Client(transport=httpx.MockTransport(handler)) as client,contextlib.redirect_stdout(io.StringIO()):
            batch=Batch(client,'FAKE_TEST_KEY',self.config,Path(d),'test');batch.one(self.jobs[0])
            with self.assertRaises(FileExistsError):batch.one(self.jobs[0])
            self.assertEqual(len(count),1)

    def test_blocked_dependent_mask_never_sent(self):
        row={**self.jobs[0],'request':None,'request_sha256':None,'blocked_reason':'invalid_A1_replicate1_mask'}
        with tempfile.TemporaryDirectory() as d:
            batch=Batch(None,'FAKE_TEST_KEY',self.config,Path(d),'test');batch.one(row)
            r=read(Path(d)/'calls'/f"{row['id']}.result.json")
            self.assertFalse(r['attempted']);self.assertEqual(r['failure'],'invalid_A1_replicate1_mask')

    def test_cache_weighting_reasoning_not_double_counted(self):
        rows=[]
        for inp,out,hit in [(100,20,10),(300,40,270)]:
            rows.append({'attempted':True,'valid_output':True,'http_status':200,'elapsed_seconds':2,'failure':None,
              'usage':{'prompt_tokens':inp,'completion_tokens':out,'total_tokens':inp+out,
              'completion_tokens_details':{'reasoning_tokens':out-2},'prompt_cache_hit_tokens':hit,'prompt_cache_miss_tokens':inp-hit}})
        a=accounting(rows);self.assertEqual(a['cache_weighted_rate'],.7)
        self.assertEqual(a['reported_partial_totals']['total'],460);self.assertEqual(a['reported_partial_totals']['reasoning'],56)
        rows.append({'attempted':True,'valid_output':False,'failure':'timeout','usage':None})
        self.assertFalse(accounting(rows)['accounting_complete'])

    def test_no_inherited_paid_authorization(self):
        with tempfile.TemporaryDirectory() as d,patch('experiments.skeleton_state_alignment.run.P',Path(d)):
            with self.assertRaises(PermissionError):authorization('e1_alignment')

if __name__=='__main__':unittest.main()
