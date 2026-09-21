"""Offline contracts and fault injection. Synthetic text is not a BC+ result."""
import json
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

from experiments.research_state.first_observation import contracts as c
from experiments.research_state.first_observation import artifacts as io
from experiments.research_state.first_observation import run as r

TOOLS = [
    {'type': 'function', 'function': {'name': 'search', 'parameters': {'type': 'object',
      'properties': {'query': {'type': 'string'}, 'k': {'type': 'integer', 'minimum': 1, 'maximum': 10}},
      'required': ['query'], 'additionalProperties': False}}},
    {'type': 'function', 'function': {'name': 'open', 'parameters': {'type': 'object',
      'properties': {'window_ref': {'type': 'string'}, 'direction': {'type': 'string', 'enum': ['before','after','around']}},
      'required': ['window_ref','direction'], 'additionalProperties': False}}}]
PROFILE = {'model': 'offline-model', 'base_url': 'https://example.test/v1', 'timeout_seconds': 30,
           'request_options': {'max_tokens': 1024}, 'max_request_utf8_bytes': 200000,
           'allow_tool_calls_with_stop': False}


def window(body='Person A visited Place B in 2001.', ref='w1'):
    return {'window_ref': ref, 'docid': '1', 'url': 'https://source.test/item',
            'document_sha256': 'a'*64, 'text': body, 'title': 'Title-only information',
            'offset': 5, 'end_char': 5+len(body), 'text_tokens': 12, 'title_tokens': 3}


def response(content=None, calls=None, finish='stop', **extra):
    return {'choices': [{'finish_reason': finish, 'message': {'role': 'assistant',
            'content': content, 'tool_calls': calls, **extra}}],
            'usage': {'prompt_tokens': 10, 'completion_tokens': 2, 'total_tokens': 12}}


def tool(name='search', args=None, id='call_1'):
    return {'id': id, 'type': 'function', 'function': {'name': name,
            'arguments': json.dumps({'query': 'new probe'} if args is None else args)}}


def good_note():
    return response(json.dumps({'notes': [{'statement': 'The source describes a visit.',
                     'source_ref': 'w1', 'quote': 'visited Place B'}]}))


class Backend:
    mode, tools = 'mock', TOOLS
    def __init__(self): self.calls = []
    def passport(self): return {'synthetic': True}
    def count_query(self, query): return len(query)
    def check_unchanged(self): pass
    def search(self, query, k, folder):
        self.calls.append({'query': query, 'k': k})
        return [window()]


class SimulatedAPIError(Exception):
    pass


class Client:
    def __init__(self, outputs=None, mutate=False):
        self.chat = SimpleNamespace(completions=self)
        self.requests, self.outputs, self.mutate = [], outputs, mutate
    def create(self, **request):
        self.requests.append(deepcopy(request))
        if self.mutate:
            request['messages'][0]['content'] = 'SDK mutation'
        index = len(self.requests)-1
        result = self.outputs[index] if self.outputs is not None else (
            response(calls=[tool(), tool(id='call_2')], finish='tool_calls') if 'tools' in request else good_note())
        if isinstance(result, BaseException): raise result
        return deepcopy(result)


class Contracts(unittest.TestCase):
    def test_json_strict(self):
        for raw in ['{"a":1,"a":2}', '{"a":NaN}', '{} trailing']:
            with self.subTest(raw=raw), self.assertRaises(ValueError): c.loads(raw)

    def test_seal(self):
        value=c.seal({'a':1}); c.verify(value); value['a']=2
        with self.assertRaises(ValueError): c.verify(value)

    def test_note_and_offsets(self):
        out=c.note_result(good_note(), [window()])
        self.assertEqual(out['status'], 'ok')
        self.assertEqual(out['quote_locations'][0]['absolute_starts'], [14])

    def test_empty_valid(self):
        self.assertEqual(c.note_result(response('{"notes":[]}'), [])['status'], 'empty')

    def test_quote_repeated_positions_not_invented(self):
        out=c.note_result(response('{"notes":[{"statement":"Repeated word","source_ref":"w1","quote":"hi"}]}'), [window('hi hi')])
        self.assertEqual(out['quote_locations'][0]['relative_starts'], [0,3])

    def test_note_failures(self):
        cases=[response(None, finish='length', reasoning_content='valid-looking JSON'),
               response('{"notes":[]}', finish='length'), response('```json\n{"notes":[]}\n```'),
               response('{"notes":[],"candidate":"A"}'), response('{"notes":[],"notes":[]}'),
               response('{"notes":[]}', calls=[tool()]), response('{"notes":[]}', refusal='no')]
        for value in cases:
            with self.subTest(value=value): self.assertEqual(c.note_result(value,[window()])['status'],'invalid')

    def test_note_quote_visibility(self):
        for change in [{'source_ref':'unseen'}, {'quote':'Title-only information'}, {'quote':'hidden full text'}, {'statement':''}]:
            value=c.loads(good_note()['choices'][0]['message']['content']); value['notes'][0].update(change)
            self.assertEqual(c.note_result(response(json.dumps(value)),[window()])['status'],'invalid')

    def test_no_entailment_claim(self):
        value=c.loads(good_note()['choices'][0]['message']['content'])
        value['notes'][0]['statement']='An unsupported answer identity.'
        self.assertEqual(c.note_result(response(json.dumps(value)),[window()])['status'],'ok')

    def test_note_limit_duplicate_and_batch_atomicity(self):
        note=c.loads(good_note()['choices'][0]['message']['content'])['notes'][0]
        for notes in [[note,note], [dict(note,statement=str(i)) for i in range(4)], [note,dict(note,source_ref='unseen')]]:
            result=c.note_result(response(json.dumps({'notes':notes})),[window()])
            self.assertEqual(result['status'],'invalid'); self.assertIsNone(result['notes'])

    def test_actor_full_batch_and_open(self):
        calls=[tool(), tool('open',{'window_ref':'w1','direction':'around'}, 'call_2')]
        self.assertEqual(c.actor_result(response(calls=calls,finish='tool_calls'),[window()])['calls'],calls)

    def test_actor_stop_is_opt_in(self):
        raw=response(calls=[tool()])
        self.assertEqual(c.actor_result(raw,[window()])['status'],'invalid')
        self.assertEqual(c.actor_result(raw,[window()],True)['status'],'ok')
        self.assertEqual(raw['choices'][0]['finish_reason'],'stop')

    def test_actor_invalid_calls(self):
        invalid=[tool('get_document'), tool('open',{'window_ref':'unseen','direction':'after'}),
                 tool(args={'query':'x','k':True}), tool(args={'query':'x','extra':1}), tool(args={})]
        for call in invalid:
            self.assertEqual(c.actor_result(response(calls=[call],finish='tool_calls'),[window()])['status'],'invalid')
        self.assertEqual(c.actor_result(response(calls=[tool(),tool()],finish='tool_calls'),[window()])['status'],'invalid')

    def test_actor_refusal_final_and_truncation(self):
        self.assertEqual(c.actor_result(response('Answer'),[window()])['kind'],'final_text')
        self.assertEqual(c.actor_result(response(refusal='no'),[window()])['kind'],'refusal')
        self.assertEqual(c.actor_result(response(None,finish='length'),[window()])['status'],'invalid')

    def test_window_ranges_and_budget(self):
        for changes in [{'end_char':99},{'text_tokens':401},{'document_sha256':'bad'}]:
            with self.assertRaises(ValueError): c.windows([{**window(),**changes}])

    def test_profile_guards(self):
        for changes in [{'base_url':'https://name:secret@example.test/v1'}, {'timeout_seconds':float('nan')},
                        {'request_options':{'max_tokens':1,'extra_body':{'enable_thinking':False}}},
                        {'request_options':{'max_tokens':True}}, {'allow_tool_calls_with_stop':'true'}]:
            with self.assertRaises(ValueError): c.profile({**PROFILE,**changes})

    def test_cost_unknown_and_inconsistent(self):
        self.assertFalse(c.usage(None)['complete'])
        self.assertFalse(c.usage({'usage':{'prompt_tokens':True}})['complete'])
        self.assertTrue(c.usage({'usage':{'prompt_tokens':2,'completion_tokens':1,'total_tokens':99}})['inconsistent'])
        self.assertEqual(c.usage({'usage':{'prompt_tokens':2}})['known'],{'prompt_tokens':2})


class Pipeline(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name)
        self.dataset=self.root/'qa.jsonl'
        self.dataset.write_text('\n'.join(json.dumps({'query_id':i,'query':q,'answer':'NEVER_SEND_GOLD'})
            for i,q in [(1,'  Original\nquestion?  '),(2,'Other question?')]),encoding='utf-8')
        self.selection=r.select(self.dataset,['1','2'])
        self.backend=Backend()
        self.collection=r.collect(self.selection,self.backend,self.root/'capture')

    def tearDown(self): self.tmp.cleanup()

    def note_run(self, outputs=None):
        plan=r.make_plan(self.collection,PROFILE,'notes')
        client=Client(outputs,mutate=True)
        summary=r.execute(plan,client,self.root/'notes',api_error_types=(SimulatedAPIError,))
        return summary,client,r.note_outputs(self.root/'notes')

    def test_raw_query_exact_no_normalization_or_gold(self):
        self.assertEqual(self.backend.calls[0]['query'],'  Original\nquestion?  ')
        self.assertNotIn('NEVER_SEND_GOLD',c.canonical(self.selection))
        self.assertEqual(self.collection['initial_model_calls'],0)
        self.assertEqual(r.audit_capture(self.root/'capture'),self.collection)

    def test_selection_errors(self):
        for ids in [['1','1'],['3'],['../1']]:
            with self.assertRaises(ValueError): r.select(self.dataset,ids)

    def test_query_overflow_retains_denominator(self):
        b=Backend(); b.count_query=lambda q:1025
        collected=r.collect(self.selection,b,self.root/'long')
        self.assertEqual(b.calls,[])
        plan=r.make_plan(collected,PROFILE,'notes')
        client=Client(); summary=r.execute(plan,client,self.root/'skipped')
        self.assertEqual(summary['scheduled'],2); self.assertEqual(client.requests,[])
        self.assertEqual(summary['statuses'],{'skipped_first_search':2})

    def test_search_exception_preserved(self):
        b=Backend()
        def fail(*args): raise RuntimeError('private diagnostic')
        b.search=fail
        collected=r.collect(self.selection,b,self.root/'errors')
        self.assertTrue(all(x['status']=='search_error' for x in collected['cases']))
        self.assertNotIn('private diagnostic',c.canonical(collected))
        r.audit_capture(self.root/'errors')

    def test_malformed_window_stops_capture(self):
        b=Backend(); b.search=lambda *args:[{**window(),'end_char':1}]
        with self.assertRaises(ValueError): r.collect(self.selection,b,self.root/'malformed')
        saved=io.read(self.root/'malformed'/'collection.json')
        self.assertFalse(saved['capture_complete'])
        self.assertEqual(saved['cases'][1]['status'],'not_run')

    def test_capture_journal_tamper_rejected(self):
        p=self.root/'capture'/'1'/'events.jsonl'; p.write_text(p.read_text().replace('Original','Modified'))
        with self.assertRaises(ValueError): r.audit_capture(self.root/'capture')

    def test_empty_observation_is_not_search_error(self):
        b=Backend(); b.search=lambda *args:[]
        collected=r.collect(self.selection,b,self.root/'empty')
        self.assertTrue(all(x['status']=='ok' for x in collected['cases']))

    def test_full_mock_chain_and_paired_inputs(self):
        summary,note_client,prior=self.note_run()
        self.assertEqual(summary['statuses'],{'ok':2})
        plan=r.make_plan(self.collection,PROFILE,'actors',prior=prior)
        for case in ['1','2']:
            pair={j['arm']:j['request'] for j in plan['jobs'] if j['case_id']==case}
            self.assertEqual(pair['A']['messages'],pair['B']['messages'][:-1])
            self.assertEqual(pair['A']['tools'],pair['B']['tools'])
        client=Client(mutate=True); result=r.execute(plan,client,self.root/'actors')
        self.assertEqual(len(client.requests),4); self.assertEqual(result['tool_executions'],0)
        self.assertTrue(result['all_model_jobs_delivered'])
        cards=r.export_review(self.root/'actors',self.root/'review')
        self.assertEqual(cards['scheduled'],4)
        exported=io.read(self.root/'review'/'cards.json')
        self.assertTrue(all(len(x['delivered'][0]['message']['tool_calls'])==2 for x in exported))
        self.assertTrue(all('SDK mutation' not in c.canonical(j['request']) for j in plan['jobs']))
        self.assertTrue(all('"case_id"' not in c.canonical(x['messages']) for x in client.requests))

    def test_invalid_and_empty_notes_produce_exact_A_requests(self):
        summary,client,prior=self.note_run([response('{"notes":[]}'),response('invalid')])
        self.assertEqual(summary['statuses'],{'empty':1,'invalid':1})
        plan=r.make_plan(self.collection,PROFILE,'actors',prior=prior)
        for case in ['1','2']:
            jobs=[j for j in plan['jobs'] if j['case_id']==case]
            self.assertEqual(jobs[0]['request'],jobs[1]['request'])
            self.assertFalse(any(j['memo_injected'] for j in jobs))

    def test_manual_note_edit_rejected(self):
        _,_,prior=self.note_run(); prior['cases']['1']['notes'][0]['statement']='Edited'
        prior=c.seal({k:v for k,v in prior.items() if k!='sha256'})
        with self.assertRaises(ValueError): r.make_plan(self.collection,PROFILE,'actors',prior=prior)

    def test_model_plan_and_source_drift_rejected(self):
        plan=r.make_plan(self.collection,PROFILE,'notes')
        plan['profile']['model']='different'
        plan=c.seal({k:v for k,v in plan.items() if k!='sha256'})
        with self.assertRaises(ValueError): r.validate_plan(plan)
        plan=r.make_plan(self.collection,PROFILE,'notes')
        with patch.object(io,'fingerprint',return_value={'changed':True}), self.assertRaises(ValueError):
            r.execute(plan,Client(),self.root/'no_calls')
        self.assertFalse((self.root/'no_calls').exists())

    def test_reject_reviewer_repeats(self):
        with self.assertRaises(ValueError): r.make_plan(self.collection,PROFILE,'notes',repeats=2)

    def test_profile_byte_guard_no_silent_trimming(self):
        with self.assertRaises(ValueError): r.make_plan(self.collection,{**PROFILE,'max_request_utf8_bytes':10},'notes')

    def test_API_timeout_keeps_cost_unknown_and_all_branches(self):
        error=SimulatedAPIError('simulated timeout, unknown server cost')
        summary,_,prior=self.note_run([error,good_note()])
        self.assertEqual(summary['attempts'],2); self.assertEqual(summary['unknown_usage_requests'],1)
        self.assertFalse(summary['cost_accounting_complete'])
        plan=r.make_plan(self.collection,PROFILE,'actors',prior=prior)
        self.assertEqual(len(plan['jobs']),4)
        self.assertEqual(sum(j['memo_injected'] for j in plan['jobs']),1)

    def test_local_failure_not_model_error(self):
        plan=r.make_plan(self.collection,PROFILE,'notes')
        with self.assertRaises(RuntimeError): r.execute(plan,Client([RuntimeError('local')]),self.root/'bug')
        summary,_=r.audit(self.root/'bug')
        self.assertEqual(summary['scheduled'],2)
        self.assertEqual(summary['statuses']['not_run'],1)
        with self.assertRaises(ValueError): r.note_outputs(self.root/'bug')

    def test_interruption_not_resampled(self):
        plan=r.make_plan(self.collection,PROFILE,'notes')
        with self.assertRaises(KeyboardInterrupt): r.execute(plan,Client([KeyboardInterrupt()]),self.root/'interrupt')
        summary,_=r.audit(self.root/'interrupt')
        self.assertEqual(summary['statuses'],{'incomplete':1,'not_run':1})

    def test_no_overwrite(self):
        self.note_run()
        with self.assertRaises(FileExistsError): r.execute(r.make_plan(self.collection,PROFILE,'notes'),Client(),self.root/'notes')

    def test_damaged_journal_prefix_stays_invalid(self):
        self.note_run()
        path=next((self.root/'notes').glob('*/events.jsonl'))
        with path.open('a') as f:f.write('{broken\n')
        summary,rows=r.audit(self.root/'notes')
        self.assertFalse(summary['all_model_jobs_delivered'])
        self.assertTrue(any(not x['semantic_eligible'] for x in rows))
        with self.assertRaises(ValueError): r.note_outputs(self.root/'notes')

    def test_response_contains_private_reasoning_but_export_does_not(self):
        self.note_run([response('{"notes":[]}',reasoning_content='PRIVATE_DIAGNOSTIC'),good_note()])
        r.export_review(self.root/'notes',self.root/'review')
        self.assertNotIn('PRIVATE_DIAGNOSTIC',(self.root/'review'/'cards.json').read_text())
        self.assertIn('PRIVATE_DIAGNOSTIC',next(p for p in (self.root/'notes').glob('*/events.jsonl') if 'PRIVATE_DIAGNOSTIC' in p.read_text()).read_text())

    def test_actor_requests_cannot_execute_search(self):
        _,_,prior=self.note_run()
        before=len(self.backend.calls)
        plan=r.make_plan(self.collection,PROFILE,'actors',prior=prior,repeats=2)
        summary=r.execute(plan,Client(),self.root/'actors')
        self.assertEqual(summary['scheduled'],8)
        self.assertEqual(len(self.backend.calls),before)
        self.assertEqual(summary['by_arm']['B']['memo_injected'],4)

    def test_note_requests_are_tool_free_and_have_no_semantic_initialization(self):
        plan=r.make_plan(self.collection,PROFILE,'notes')
        for job in plan['jobs']:
            self.assertNotIn('tools',job['request'])
            payload=c.loads(job['request']['messages'][1]['content'])
            self.assertEqual(set(payload),{'question','first_query','observation'})
            self.assertEqual(payload['question'],payload['first_query'])

    def test_other_observation_notes_cannot_be_reused(self):
        _,_,prior=self.note_run()
        other=deepcopy(self.collection)
        other['cases'][0]['observation'][0]['text']='X'*len(other['cases'][0]['observation'][0]['text'])
        other=c.seal({k:v for k,v in other.items() if k!='sha256'})
        with self.assertRaises(ValueError): r.make_plan(other,PROFILE,'actors',prior=prior)

    def test_incomplete_note_capture_blocks_actors_not_semantic_filter(self):
        plan=r.make_plan(self.collection,PROFILE,'notes')
        r.execute(plan,Client(),self.root/'notes')
        path=next((self.root/'notes').glob('*/events.jsonl')); path.unlink()
        with self.assertRaises(ValueError): r.note_outputs(self.root/'notes')

    def test_first_query_unicode_and_whitespace_remain_identical(self):
        dataset=self.root/'unicode.jsonl'
        question='  哪位人物？\nemoji: 😀\t'
        dataset.write_text(json.dumps({'query_id':9,'query':question}),encoding='utf-8')
        selected=r.select(dataset,['9']); backend=Backend()
        data=r.collect(selected,backend,self.root/'unicode')
        self.assertEqual(data['cases'][0]['query'],question)
        self.assertEqual(backend.calls[0]['query'],question)

    def test_CLI_offline_selection_and_plan(self):
        selected=self.root/'selection.json'
        self.assertEqual(r.main(['select','--dataset',str(self.dataset),'--qids','1','2','--output',str(selected)]),0)
        config=self.root/'profile.json'; io.write(config,PROFILE)
        plan=self.root/'notes-plan.json'
        self.assertEqual(r.main(['plan','--collection',str(self.root/'capture'),
            '--profile',str(config),'--stage','notes','--output',str(plan)]),0)
        self.assertEqual(io.read(plan)['max_model_calls'],2)

    def test_mock_not_accepted_as_live(self):
        plan=r.make_plan(self.collection,PROFILE,'notes')
        with self.assertRaises(ValueError): r.execute(plan,Client(),self.root/'live',mode='live')


if __name__=='__main__': unittest.main()
