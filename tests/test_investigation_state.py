"""Offline unit/fault-injection tests. Synthetic prefixes are not BC+ results."""
import contextlib
from copy import deepcopy
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from experiments.research_state.need_review.checkpoint import extract_checkpoint, digest, canonical_json
from experiments.research_state.investigation_state import packet as p
from experiments.research_state.investigation_state import run as r
from experiments.research_state.investigation_state import report
from experiments.research_state.investigation_state.storage import loads, read, write, sealed, safe_path, read_journal

QUESTION = 'Identify a person born in the 1970s who joined Institute Z.'
TOOLS = [{'type':'function','function':{'name':'search','description':'Search the test corpus.',
          'parameters':{'type':'object','properties':{'query':{'type':'string'}},
                        'required':['query'],'additionalProperties':False}}}]
SOURCE = 'Ada joined Institute Z in 1999. Bo was a nurse. Ada was an artist.'


def checkpoint(root, case_id='case_one', texts=None, arguments=None, scores=None, windows=None):
    texts = texts or [SOURCE, SOURCE]
    arguments = arguments or ['same query'] * len(texts)
    scores = scores or [0.9-i/10 for i in range(len(texts))]
    messages = [{'role':'system','content':'Prior system instructions.'}, {'role':'user','content':QUESTION}]
    events = []
    def event(kind, **fields):
        events.append(dict(seq=len(events)+1, kind=kind, **fields))
    for i, value in enumerate(texts):
        event('api_request',request={'model':'captured','stream':False,'messages':deepcopy(messages),'tools':TOOLS,
                                     'extra_body':{'enable_thinking':False}})
        call = {'id':f'c{i}','type':'function','function':{'name':'search','arguments':json.dumps({'query':arguments[i]})}}
        assistant = {'role':'assistant','content':'Candidate A and 1975 are guesses.', 'tool_calls':[call]}
        event('api_response',response={'message':assistant})
        event('tool_start',name='search')
        result = [{'docid':'d1','text':value,'url':'https://example.test/a','score':scores[i]}]
        if windows is not None:
            result[0].update(window_ref=windows[i], offset=0, end_char=len(value))
        event('tool_result',name='search',result=result)
        messages += [assistant,{'role':'tool','tool_call_id':f'c{i}','content':json.dumps(result)}]
    event('api_request',request={'model':'captured','stream':False,'messages':messages,'tools':TOOLS,
                                'tool_choice':'auto','extra_body':{'enable_thinking':False}})
    path=Path(root)/f'{case_id}.jsonl'
    path.write_text(''.join(canonical_json(e)+'\n' for e in events))
    return extract_checkpoint(path,len(events),checkpoint_id=case_id,source_commit='a'*40,tool_version='synthetic')


def fixture():
    return {'notebook':[
        {'kind':'given_constraint','text':'The birth decade is a target constraint, not proof for Candidate A.',
         'basis':[{'ref':'question','quote':'born in the 1970s'}]},
        {'kind':'observed_finding','text':'Ada joined Institute Z in 1999.',
         'basis':[{'ref':'event:4:doc:d1','quote':'Ada joined Institute Z in 1999.'}]},
        {'kind':'hypothesis','text':'The 1975 binding is provisional.',
         'basis':[{'message_index':2,'quote':'1975 are guesses.'}]}],
        'task':{'intent':'verify','question':'What evidence establishes the target person and birth decade?',
                'decision_effect':'Use actual evidence to retain or revise the candidate, not to relax the decade.',
                'basis':[{'ref':'question','quote':'born in the 1970s'}]}}


def bundle_for(root, count=1):
    cases, packets = [], {}
    for i in range(count):
        key=f'case_{i}'
        cp=checkpoint(root,key)
        fi=fixture()
        packets[key]=p.build_packet(cp,fi)
        cases.append({'case_id':key,'fixture':fi})
    return sealed({'schema_version':'investigation_bundle_v1','selection':{'cases':cases},'packets':packets},'bundle_sha256')


def profile():
    return {'model':'test-model','base_url':'https://example.test/v1','timeout_seconds':120,
            'request_options':{'max_tokens':8192},'max_request_utf8_bytes':2000000}


def response(calls=1, content='I will check the relationship.', finish='tool_calls', usage=None):
    message={'role':'assistant','content':content}
    if calls:
        message['tool_calls']=[{'id':f'new{i}','type':'function','function':{'name':'search','arguments':'{"query":"same query"}'}} for i in range(calls)]
    return {'choices':[{'index':0,'finish_reason':finish,'message':message}],
            'usage': usage if usage is not None else {'prompt_tokens':10,'completion_tokens':3,'total_tokens':13},
            'model':'test-model'}


class APITimeoutError(Exception):
    pass


class FakeClient:
    def __init__(self, outputs=None, mutate=False):
        self.requests=[]
        self.outputs=outputs
        self.mutate=mutate
        self.chat=SimpleNamespace(completions=self)
    def create(self, **request):
        self.requests.append(deepcopy(request))
        if self.mutate:
            request['messages'].clear()
            request['tools'].clear()
        output=self.outputs[len(self.requests)-1] if self.outputs is not None else response(calls=2)
        if isinstance(output, BaseException):
            raise output
        return deepcopy(output)


class PacketTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.cp=checkpoint(self.root)
        self.fi=fixture()
        self.packet=p.build_packet(self.cp,self.fi)

    def test_lossless_flat_typed_inventory(self):
        a,b=p.render(self.packet,'flat'),p.render(self.packet,'typed')
        self.assertEqual(p.unpack(a),p.unpack(b))
        originals=sorted([x for x in p.unpack(b) if 'message_index' in x],key=lambda x:x['message_index'])
        self.assertEqual([x['value'] for x in originals],self.cp['request']['messages'])

    def test_no_input_mutation_or_alias(self):
        old=deepcopy(self.cp)
        packet=p.build_packet(self.cp,self.fi)
        packet['items'][0]['value']['content']='changed'
        self.assertEqual(self.cp,old)

    def test_quotes_must_be_exact_and_source_bound(self):
        for change in ('quote','ref'):
            fi=fixture();fi['notebook'][1]['basis'][0][change]='not in the prefix'
            with self.subTest(change=change),self.assertRaises(ValueError):p.build_packet(self.cp,fi)

    def test_question_not_observed_fact(self):
        self.fi['notebook'][0]['kind']='observed_finding'
        with self.assertRaises(ValueError):p.build_packet(self.cp,self.fi)

    def test_assistant_not_observed_fact(self):
        self.fi['notebook'][2]['kind']='observed_finding'
        with self.assertRaises(ValueError):p.build_packet(self.cp,self.fi)

    def test_schema_membership_is_not_entailment(self):
        self.fi['notebook'][1]['text']='Bo joined Institute Z in 1999.'
        packet=p.build_packet(self.cp,self.fi)
        self.assertIn('Bo joined',next(x for x in packet['items'] if x['id']=='n1')['value']['text'])

    def test_task_null_allowed_not_completion(self):
        self.fi['task']=None
        packet=p.build_packet(self.cp,self.fi)
        self.assertIsNone(next(x['value'] for x in packet['items'] if x['id']=='task'))
        self.assertNotIn('done',packet)

    def test_no_query_or_completion_field_in_task(self):
        for field in ('query','candidate','done','final_answer'):
            fi=fixture();fi['task'][field]='bad'
            with self.subTest(field=field),self.assertRaises(ValueError):p.build_packet(self.cp,fi)

    def test_resealed_item_tampering_rejected(self):
        changed=deepcopy(self.packet);changed['items'][1]['value']['content']='altered question'
        changed=sealed(changed,'packet_sha256')
        with self.assertRaises(ValueError):p.validate_packet(changed)

    def test_hidden_checkpoint_metadata_not_rendered(self):
        cp=deepcopy(self.cp);cp['hidden_gold']='NEVER SEND THIS'
        cp=sealed(cp,'checkpoint_sha256')
        view=p.render(p.build_packet(cp,self.fi),'typed')
        self.assertNotIn('NEVER SEND THIS',canonical_json(view))
        self.assertNotIn('checkpoint_id',view)

    def test_duplicate_queries_linked_without_deletion(self):
        self.assertEqual(self.packet['attempt_index']['same_exact_arguments'],[['a0','a1']])
        self.assertEqual(len([x for x in self.packet['items'] if x['kind']=='attempts']),2)

    def test_scores_do_not_make_source_content_novel(self):
        self.assertEqual(self.packet['attempt_index']['same_ordered_visible_source_content'],[['a0','a1']])

    def test_different_windows_of_same_document_are_not_merged(self):
        cp=checkpoint(self.root,texts=[SOURCE,'A different window.'])
        packet=p.build_packet(cp,self.fi)
        self.assertEqual(packet['attempt_index']['same_ordered_visible_source_content'],[['a0'],['a1']])

    def test_no_fuzzy_query_equivalence(self):
        cp=checkpoint(self.root,arguments=['same query','Same query'])
        packet=p.build_packet(cp,self.fi)
        self.assertEqual(packet['attempt_index']['same_exact_arguments'],[['a0'],['a1']])

    def test_linked_adds_only_derived_index(self):
        a,b=p.render(self.packet,'typed'),p.render(self.packet,'linked')
        index=b.pop('attempt_index')
        self.assertEqual(a,b)
        self.assertEqual(index,self.packet['attempt_index'])

    def test_proposed_repeat_is_a_diagnostic_not_a_rejection(self):
        raw=response()
        diagnostic=p.proposed_repeats(self.packet,raw['choices'][0]['message']['tool_calls'])
        self.assertEqual(diagnostic[0]['exact_previous_attempts'],['a0','a1'])
        self.assertEqual(diagnostic[0]['semantic_quality'],'not_evaluated')
        self.assertTrue(r.compact_classification(raw,r.request_for(self.packet,'typed',profile(),'Prompt'))['protocol_compatible'])

    def test_current_window_refs_roundtrip_after_grouping(self):
        cp=checkpoint(self.root,windows=['window_zero','window_one'])
        fi=fixture();fi['notebook'][1]['basis'][0]['ref']='window_zero'
        packet=p.build_packet(cp,fi)
        restored=p.unpack(p.render(packet,'typed'))
        self.assertEqual(p.resolve(cp,'window_one')['text'],SOURCE)
        self.assertEqual(next(x for x in restored if x['id']=='m3')['value'],cp['request']['messages'][3])

    def test_repeated_immutable_ref_with_different_scores_is_valid(self):
        cp=checkpoint(self.root,windows=['window_zero','window_zero'])
        fi=fixture();fi['notebook'][1]['basis'][0]['ref']='window_zero'
        packet=p.build_packet(cp,fi)
        self.assertEqual(packet['attempt_index']['same_ordered_visible_source_content'],[['a0','a1']])

    def test_same_ref_cannot_identify_conflicting_source_content(self):
        cp=checkpoint(self.root,texts=[SOURCE,'Contradictory text'],windows=['window_zero','window_zero'])
        fi=fixture();fi['notebook'][1]['basis'][0]['ref']='window_zero'
        with self.assertRaises(ValueError):p.build_packet(cp,fi)

    def test_invalid_basis_shapes(self):
        for value in ([],None,[{'ref':'question','quote':'born','extra':1}],
                      [{'message_index':True,'quote':'x'}],[{'message_index':999,'quote':'x'}]):
            fi=fixture();fi['notebook'][2]['basis']=value
            with self.subTest(value=value),self.assertRaises(ValueError):p.build_packet(self.cp,fi)

    def test_duplicates_in_view_rejected(self):
        view=p.render(self.packet,'flat');view['items'].append(view['items'][0])
        with self.assertRaises(ValueError):p.unpack(view)


class PlanTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.bundle=bundle_for(self.root,3)

    def test_three_cases_two_views_two_repeats_is_twelve_calls(self):
        plan=r.build_plan(self.bundle,profile(),'Prompt')
        self.assertEqual(plan['planned_model_calls'],12)
        self.assertEqual(plan['planned_tool_executions'],0)
        self.assertEqual(plan,r.build_plan(self.bundle,profile(),'Prompt'))

    def test_only_user_view_differs_in_layout_pair(self):
        packet=self.bundle['packets']['case_0']
        a=r.request_for(packet,'flat',profile(),'Prompt');b=r.request_for(packet,'typed',profile(),'Prompt')
        self.assertEqual(a['messages'][0],b['messages'][0])
        self.assertEqual({k:v for k,v in a.items() if k!='messages'},{k:v for k,v in b.items() if k!='messages'})
        self.assertEqual(p.unpack(loads(a['messages'][1]['content'])),p.unpack(loads(b['messages'][1]['content'])))

    def test_group_display_order_survives_serialization(self):
        request=r.request_for(self.bundle['packets']['case_0'],'typed',profile(),'Prompt')
        view=loads(request['messages'][1]['content'])
        self.assertEqual(list(view['groups']),list(p.GROUP_ORDER))

    def test_historical_provider_options_not_inherited(self):
        request=r.request_for(self.bundle['packets']['case_0'],'typed',profile(),'Prompt')
        self.assertNotIn('extra_body',request)
        self.assertEqual(request['model'],'test-model')
        self.assertEqual(request['max_tokens'],8192)

    def test_profile_rejects_credentials_and_ambiguous_options(self):
        for options in ({'max_tokens':True},{'max_tokens':1,'max_completion_tokens':2},
                        {'max_tokens':10,'extra_body':{'enable_thinking':False}},
                        {'max_tokens':10,'api_key':'secret'},{'max_tokens':10,'temperature':float('inf')}):
            pro=profile();pro['request_options']=options
            with self.subTest(options=options),self.assertRaises(ValueError):r.validate_profile(pro)

    def test_profile_endpoint_and_timeout_guards(self):
        for url in ('https://secret@example.test/v1','https://example.test/v1?key=secret',
                    'https://example.test/v1/responses','https://example.test/v1/', 'ftp://example.test/v1'):
            pro=profile();pro['base_url']=url
            with self.subTest(url=url),self.assertRaises(ValueError):r.validate_profile(pro)
        for value in (0,-1,True,float('nan')):
            pro=profile();pro['timeout_seconds']=value
            with self.subTest(value=value),self.assertRaises(ValueError):r.validate_profile(pro)

    def test_no_silent_input_truncation(self):
        pro=profile();pro['max_request_utf8_bytes']=20
        with self.assertRaises(ValueError):r.build_plan(self.bundle,pro,'Prompt')

    def test_formal_requires_attestation_and_delivery_pilot(self):
        with self.assertRaises(ValueError):r.build_plan(self.bundle,profile(),'Prompt',purpose='formal')

    def test_formal_acceptance_is_not_semantic_selection(self):
        review={'bundle_sha256':self.bundle['bundle_sha256'],'reviewer':'fixture auditor',
                'prefix_only':True,'quotes_and_claim_scope_checked':True,'task_is_not_a_gold_answer_hint':True}
        acceptance={'bundle_sha256':self.bundle['bundle_sha256'],'profile_sha256':digest(profile()),
                    'comparison':'layout','code_sha256':r.code_hashes(),'runtime_versions':r.runtime_versions(),'prompt_sha256':digest('Prompt'),
                    'mechanically_clean':True}
        plan=r.build_plan(self.bundle,profile(),'Prompt',purpose='formal',fixture_review=review,acceptance=acceptance)
        self.assertEqual(plan['planned_model_calls'],12)
        self.assertNotIn('semantic_score',plan)

    def test_resealed_schedule_tamper_rejected(self):
        plan=r.build_plan(self.bundle,profile(),'Prompt')
        plan['schedule'][0]['view']='linked';plan=sealed(plan,'plan_sha256')
        with self.assertRaises(ValueError):r.validate_plan(plan,self.bundle)

    def test_code_drift_rejected(self):
        plan=r.build_plan(self.bundle,profile(),'Prompt')
        with patch.object(r,'code_hashes',return_value={'changed':'x'}),self.assertRaises(ValueError):
            r.validate_plan(plan,self.bundle)

    def test_runtime_drift_invalidates_sealed_plan(self):
        plan=r.build_plan(self.bundle,profile(),'Prompt')
        with patch.object(r,'runtime_versions',return_value={'python':'changed'}),self.assertRaises(ValueError):
            r.validate_plan(plan,self.bundle)

    def test_attempt_linkage_is_separate_pair(self):
        plan=r.build_plan(self.bundle,profile(),'Prompt',comparison='attempt_linkage')
        self.assertEqual({row['view'] for row in plan['schedule']},{'typed','linked'})
        self.assertEqual(plan['planned_model_calls'],12)


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.bundle=bundle_for(self.root)
        self.plan=r.build_plan(self.bundle,profile(),'Prompt',repeats=1)
        self.out=self.root/'run'

    def execute(self,outputs=None,mutate=False):
        self.client=FakeClient(outputs,mutate)
        return r.execute(self.plan,self.bundle,self.out,self.client)

    def test_mock_complete_batch_and_all_calls_preserved(self):
        summary=self.execute(mutate=True)
        self.assertEqual(len(self.client.requests),2)
        self.assertTrue(summary['mechanically_clean'])
        self.assertTrue(summary['cost_accounting_complete'])
        self.assertEqual(summary['reported_token_lower_bounds']['total_tokens'],26)
        _,rows=report.audit(self.out)
        self.assertTrue(all(len(x['classification']['tool_calls'])==2 for x in rows))
        self.assertTrue(all(len(q['messages'])==2 for q in self.client.requests))

    def test_three_case_full_mock_schedule_twelve_calls(self):
        bundle=bundle_for(self.root,3)
        plan=r.build_plan(bundle,profile(),'Prompt',repeats=2)
        client=FakeClient(mutate=True)
        summary=r.execute(plan,bundle,self.out,client)
        self.assertEqual(len(client.requests),12)
        self.assertEqual(summary['scheduled_branches'],12)
        self.assertEqual(summary['reviewer_calls'],0)
        self.assertEqual(summary['tool_executions'],0)
        self.assertTrue(summary['mechanically_clean'])
        exported=self.root/'review';report.export(self.out,exported)
        self.assertEqual(len((exported/'cards.jsonl').read_text().splitlines()),12)

    def test_no_overwrite_of_run_directory(self):
        self.execute()
        with self.assertRaises(FileExistsError):r.execute(self.plan,self.bundle,self.out,FakeClient())

    def test_api_timeout_keeps_denominator_unknown_cost(self):
        summary=self.execute([APITimeoutError('secret-do-not-log'),response()])
        self.assertEqual(summary['scheduled_branches'],2)
        self.assertEqual(summary['logical_requests_attempted'],2)
        self.assertEqual(summary['responses_received'],1)
        self.assertEqual(summary['unknown_usage_calls'],1)
        self.assertFalse(summary['cost_accounting_complete'])
        self.assertNotIn('secret-do-not-log',''.join(x.read_text() for x in (self.out/'branches').rglob('*.json*')))

    def test_reasoning_only_response_is_not_delivered_review_or_answer(self):
        raw=response(0,None,'length');raw['choices'][0]['message']['reasoning_content']='private computation'
        summary=self.execute([raw,response()])
        self.assertFalse(summary['mechanically_clean'])
        _,rows=report.audit(self.out)
        self.assertEqual(rows[0]['classification']['response_kind'],'protocol_error')
        export=self.root/'review';report.export(self.out,export)
        self.assertNotIn('private computation',(export/'cards.jsonl').read_text())
        self.assertIn('private computation',(self.out/'branches'/self.plan['schedule'][0]['sample_id']/'events.jsonl').read_text())

    def test_tool_calls_with_stop_retained_but_not_normalized(self):
        summary=self.execute([response(finish='stop'),response()])
        self.assertFalse(summary['mechanically_clean'])
        _,rows=report.audit(self.out)
        self.assertEqual(rows[0]['classification']['response_kind'],'tool_calls')
        self.assertIn('tool_calls_with_stop',rows[0]['classification']['compatibility_markers'])

    def test_partial_usage_preserved_without_imputation(self):
        raw=response(usage={'prompt_tokens':10})
        summary=self.execute([raw,response()])
        self.assertFalse(summary['cost_accounting_complete'])
        self.assertEqual(summary['reported_token_lower_bounds']['prompt_tokens'],20)
        self.assertEqual(summary['reported_token_lower_bounds']['total_tokens'],13)

    def test_inconsistent_usage_not_complete(self):
        raw=response(usage={'prompt_tokens':2,'completion_tokens':1,'total_tokens':99})
        summary=self.execute([raw,response()])
        self.assertEqual(summary['responses_inconsistent_usage'],1)
        self.assertFalse(summary['cost_accounting_complete'])

    def test_interrupt_keeps_unrun_branches(self):
        with self.assertRaises(KeyboardInterrupt):self.execute([KeyboardInterrupt(),response()])
        summary=read(self.out/'summary.json')
        self.assertEqual(summary['statuses'],{'interrupted':1,'not_run':1})
        self.assertEqual(summary['unknown_usage_calls'],1)
        exported=self.root/'review';report.export(self.out,exported)
        self.assertEqual(len((exported/'cards.jsonl').read_text().splitlines()),2)

    def test_local_adapter_error_is_harness_not_model_failure(self):
        with self.assertRaises(TypeError):self.execute([TypeError('bad adapter'),response()])
        summary=read(self.out/'summary.json')
        self.assertEqual(summary['statuses'],{'harness_error':1,'not_run':1})

    def test_truncated_journal_preserves_prefix_and_marks_error(self):
        self.execute()
        branch=self.out/'branches'/self.plan['schedule'][0]['sample_id']
        with (branch/'events.jsonl').open('ab') as stream:stream.write(b'{"seq":')
        summary,_=report.audit(self.out)
        self.assertEqual(summary['responses_received'],2)
        self.assertEqual(summary['branches_with_audit_errors'],1)
        self.assertFalse(summary['mechanically_clean'])

    def test_actual_request_tampering_detected(self):
        self.execute()
        path=self.out/'branches'/self.plan['schedule'][0]['sample_id']/'events.jsonl'
        events=[loads(line) for line in path.read_text().splitlines()]
        events[0]['request']['messages'][0]['content']='changed'
        path.write_text(''.join(canonical_json(e)+'\n' for e in events))
        summary,rows=report.audit(self.out)
        self.assertIn('actual_request_differs_from_frozen_view',rows[0]['errors'])
        self.assertFalse(summary['mechanically_clean'])

    def test_stored_response_tampering_detected(self):
        self.execute()
        path=self.out/'branches'/self.plan['schedule'][0]['sample_id']/'result.json'
        record=read(path);record['response']['choices'][0]['message']['content']='changed'
        write(path,record)
        summary,_=report.audit(self.out)
        self.assertEqual(summary['branches_with_audit_errors'],1)

    def test_source_snapshot_tampering_detected(self):
        self.execute()
        path=self.out/'source'/next(iter(self.plan['code_sha256']))
        path.write_text('tampered')
        summary,_=report.audit(self.out)
        self.assertTrue(summary['global_errors'])

    def test_response_recovered_from_journal_without_semantic_success(self):
        self.execute()
        path=self.out/'branches'/self.plan['schedule'][0]['sample_id']/'result.json'
        record=read(path);record['response']=None;record['status']='interrupted';write(path,record)
        _,rows=report.audit(self.out)
        self.assertTrue(rows[0]['response_recovered_from_journal'])
        self.assertFalse(rows[0]['semantic_eligible'])

    def test_mock_pilot_cannot_authorize_formal(self):
        self.execute()
        with self.assertRaises(ValueError):report.pilot_acceptance(self.out)

    def test_live_client_timeout_drift_rejected_before_calls(self):
        client=FakeClient();client.base_url=profile()['base_url'];client.max_retries=0;client.timeout=999
        with self.assertRaises(ValueError):r.execute(self.plan,self.bundle,self.out,client,mode='live')
        self.assertEqual(client.requests,[])
        self.assertFalse(self.out.exists())

    def test_execution_mode_tampering_rejected(self):
        self.execute()
        path=self.out/'execution.json';value=read(path);value['mode']='live';write(path,value)
        with self.assertRaises(ValueError):report.pilot_acceptance(self.out)

    def test_spurious_harness_event_does_not_pass_as_completed(self):
        self.execute()
        path=self.out/'branches'/self.plan['schedule'][0]['sample_id']/'events.jsonl'
        with path.open('a') as stream:stream.write('{"seq":3,"kind":"harness_error","error_type":"Bad"}\n')
        summary,rows=report.audit(self.out)
        self.assertFalse(summary['mechanically_clean'])
        self.assertIn('completed_event_sequence_mismatch',rows[0]['errors'])

    def test_export_preserves_denominators_and_empty_labels(self):
        self.execute();out=self.root/'review';report.export(self.out,out)
        cards=[loads(x) for x in (out/'cards.jsonl').read_text().splitlines()]
        self.assertEqual(len(cards),2)
        self.assertTrue(all(value is None for card in cards for value in card['labels'].values()))
        self.assertNotIn('view',cards[0])
        with self.assertRaises(FileExistsError):report.export(self.out,out)


class StorageAndPreparationTests(unittest.TestCase):
    def test_strict_json_rejects_duplicate_and_nonfinite(self):
        for raw in ('{"x":1,"x":2}','{"x":NaN}','{"x":1e999}'):
            with self.subTest(raw=raw),self.assertRaises(ValueError):loads(raw)

    def test_relative_path_and_symlink_escape(self):
        with tempfile.TemporaryDirectory() as root,tempfile.TemporaryDirectory() as other:
            for relative in ('../escape','/absolute'):
                with self.assertRaises(ValueError):safe_path(Path(root),relative)
            (Path(root)/'outside').symlink_to(other,target_is_directory=True)
            with self.assertRaises(ValueError):safe_path(Path(root),'outside/file')

    def test_sequence_damage_stops_recovery(self):
        with tempfile.TemporaryDirectory() as root:
            path=Path(root)/'events.jsonl';path.write_text('{"seq":1,"kind":"request"}\n{"seq":3,"kind":"response"}\n{"seq":2,"kind":"response"}\n')
            rows,errors=read_journal(path)
            self.assertEqual(len(rows),1);self.assertTrue(errors)

    def test_prepare_checks_blob_and_never_overwrites(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);cp=checkpoint(root)
            cp_path=root/'archived.json';write(cp_path,cp)
            selection={'schema_version':'investigation_selection_v1','archive_commit':'b'*40,
                       'cases':[{'case_id':cp['checkpoint_id'],'checkpoint_path':'archived.json',
                                 'checkpoint_blob_sha':r.blob_sha(cp_path.read_bytes()),'fixture':fixture()}]}
            select_path=root/'selection.json';write(select_path,selection)
            out=root/'prepared';r.prepare(select_path,root,out)
            bundle=r.load_bundle(out/'bundle.json')
            self.assertEqual(len(bundle['packets']),1)
            with self.assertRaises(FileExistsError):r.prepare(select_path,root,out)
            cp_path.write_text(cp_path.read_text()+' ')
            with self.assertRaises(ValueError):r.prepare(select_path,root,root/'other')

    def test_builtin_selection_is_complete(self):
        data=read(r.PACKAGE/'fixtures.json')
        self.assertEqual(len(data['cases']),3)
        self.assertEqual(data['archive_commit'],'396592c3ed371a6be260ca0a40434d1f6afc821f')
        self.assertTrue(all(len(x['checkpoint_blob_sha'])==40 for x in data['cases']))

    @unittest.skipUnless((r.ROOT/'experiments/research_state/need_review/runs/e01_atria4096_20260920/checkpoints/qid_517_s21.json').exists(),
                         'Full archived real checkpoints unavailable in this checkout; Codex must run prepare before paid calls.')
    def test_builtin_real_checkpoints_and_quotes(self):
        with tempfile.TemporaryDirectory() as root:
            result=r.prepare(r.PACKAGE/'fixtures.json',r.ROOT,Path(root)/'prepared')
            self.assertEqual(len(result['cases']),3)
            bundle=r.load_bundle(Path(root)/'prepared'/'bundle.json')
            cp=bundle['packets']['qid_776_s53']['checkpoint']
            ref=next(x for x in cp['references'] if x['ref']=='event:16:doc:34541')
            observation=json.loads(cp['request']['messages'][ref['message_index']]['content'])[int(ref['path'][1:])]
            self.assertIn('title: Nineteenth Century Periodicals: 1880-1899',observation['text'])
            self.assertIn('American Anthropologist (1888-present)',observation['text'])
            self.assertNotIn('1940',observation['text'])


if __name__=='__main__':unittest.main()
