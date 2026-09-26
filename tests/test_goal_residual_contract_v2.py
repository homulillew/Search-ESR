"""Offline interface tests; no API, model loading, Search, Find or Open calls."""
import copy,json,sys,unittest
import tempfile
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'experiments/goal_residual_control/harness_v2'))
import contracts as v2
from llm_chat.auth_guard import AuthFailureLatch

class AuthRejected(Exception):pass
class OtherError(Exception):pass

class ContractTests(unittest.TestCase):
    ws={'known_documents':[{'doc_ref':'D1'},{'doc_ref':'D2'}],'observed_windows':[{'window_ref':'W1'}]}
    def act(self,*actions):return {'decision':'act','gap':'A research question','actions':list(actions)}
    def check(self,obj,kind='research_actor'):return v2.validate_object(obj,kind,self.ws if kind=='research_actor' else None)
    def reject(self,obj,kind='research_actor'):
        with self.assertRaises(Exception):self.check(obj,kind)
    def test_stop(self):self.check({'decision':'stop','gap':'','actions':[]})
    def test_search(self):self.check(self.act({'tool':'search','query':'q','k':5}))
    def test_find(self):self.check(self.act({'tool':'find','doc_ref':'D1','query':'q'}))
    def test_open(self):
        for direction in ['before','after','around']:self.check(self.act({'tool':'open','window_ref':'W1','direction':direction}))
    def test_two_independent(self):self.check(self.act({'tool':'find','doc_ref':'D1','query':'a'},{'tool':'find','doc_ref':'D2','query':'b'}))
    def test_two_searches(self):self.check(self.act({'tool':'search','query':'a','k':5},{'tool':'search','query':'b','k':5}))
    def test_type_discriminator(self):self.reject(self.act({'type':'search','query':'q','k':5}))
    def test_name_arguments(self):self.reject(self.act({'name':'search','arguments':{'query':'q','k':5}}))
    def test_nested_arguments(self):self.reject(self.act({'tool':'search','arguments':{'query':'q','k':5}}))
    def test_missing_query(self):self.reject(self.act({'tool':'search','k':5}))
    def test_missing_k(self):self.reject(self.act({'tool':'search','query':'q'}))
    def test_dependent_batch(self):self.reject(self.act({'tool':'search','query':'q','k':5},{'tool':'find','doc_ref':'D3','query':'q'}))
    def test_unknown_window(self):self.reject(self.act({'tool':'open','window_ref':'W2','direction':'around'}))
    def test_illegal_tool(self):self.reject(self.act({'tool':'get_document','docid':'1'}))
    def test_extras(self):
        for k in ['name','type','arguments','doc_ref','window_ref']:
            self.reject(self.act({'tool':'search','query':'q','k':5,k:'x'}))
    def test_top_extras(self):self.reject({'decision':'stop','gap':'','actions':[],'answer':'x'})
    def test_bad_stop(self):
        self.reject({'decision':'stop','gap':'g','actions':[]})
        self.reject({'decision':'stop','gap':'','actions':[{'tool':'search','query':'q','k':5}]})
    def test_empty_act(self):
        self.reject(self.act());self.reject({'decision':'act','gap':'  ','actions':[{'tool':'search','query':'q','k':5}]})
    def test_too_many(self):self.reject(self.act(*[{'tool':'search','query':'q','k':5}]*3))
    def test_k_range(self):
        for k in [0,11,True,'5']:self.reject(self.act({'tool':'search','query':'q','k':k}))
    def test_goal_forms(self):
        for x in [{'resolved':True,'residual':''},{'resolved':False,'residual':'Missing relation'}]:self.check(x,'goal_reviewer')
    def test_goal_inconsistency(self):
        for x in [{'resolved':True,'residual':'missing'},{'resolved':False,'residual':''},{'resolved':'true','residual':''},{'resolved':True,'residual':'','confidence':1}]:self.reject(x,'goal_reviewer')
    def test_updater_all_actions(self):
        for a,s in [('keep',''),('set','Candidate may fit'),('clear','')]:self.check({'claims_to_add':['Observed atomic fact'],'hypothesis_update':{'action':a,'statement':s}},'state_updater')
    def test_updater_invalid(self):
        self.reject({'claims_to_add':['a','b','c'],'hypothesis_update':{'action':'keep','statement':''}},'state_updater')
        self.reject({'claims_to_add':[],'hypothesis_update':{'action':'set','statement':''}},'state_updater')
        self.reject({'claims_to_add':[],'hypothesis_update':{'action':'replace','statement':'x'}},'state_updater')
    def test_bad_finish(self):
        with self.assertRaises(ValueError):v2.parse({'choices':[{'finish_reason':'length','message':{'content':'{}'}}]},'research_actor')
    def test_prompt_append_only(self):
        base=v2.STUDY
        self.assertEqual((v2.HERE/'research_actor.md').read_text(),(base/'prompts/research_actor.md').read_text()+(v2.HERE/'actor_contract.md').read_text())
    def test_closed_tool_registry(self):
        self.assertEqual([a['function']['name'] for a in v2.SEARCH_FIND_TOOLS],['search','find','open'])
    def test_typed_auth_latch(self):
        g=AuthFailureLatch((AuthRejected,));self.assertIsNone(g.observe(OtherError()))
        self.assertEqual(g.observe(AuthRejected()),'AuthRejected');self.assertEqual(g.observe(OtherError()),'AuthRejected')
        self.assertIsNone(AuthFailureLatch().observe(AuthRejected()))
    def test_main_runner_uses_same_latch(self):
        from experiments.research_state.first_observation import run
        self.assertIs(run.AuthFailureLatch,AuthFailureLatch)
    def test_v2_auth_stops_queued_requests(self):
        import httpx
        from openai import OpenAI,AuthenticationError
        import runtime
        calls=[]
        def handler(req):
            calls.append(req)
            return httpx.Response(401,json={'error':{'message':'invalid fixture credential','type':'authentication_error'}})
        def make_client():return OpenAI(api_key='fixture',base_url='https://example.test',max_retries=0,http_client=httpx.Client(transport=httpx.MockTransport(handler)))
        with tempfile.TemporaryDirectory() as tmp,patch.object(runtime,'client',make_client),patch.object(runtime,'AUTH',AuthFailureLatch((AuthenticationError,))):
            items=[runtime.item(str(i),'0','mock','goal_reviewer',{'Original Question':'Q','Verified Claims':[]}) for i in range(12)]
            rows=runtime.batch(Path(tmp),'offline',items)
        self.assertLessEqual(len(calls),4)
        self.assertEqual(sum(r['attempted'] for r in rows),len(calls))
        self.assertGreaterEqual(sum(r['error']['type']=='blocked_by_auth' for r in rows),8)
    def test_request_only_changes_system_appendix(self):
        import runtime
        old=runtime.read(runtime.TOP/'research_decision/REQUESTS.json')
        appendix=(v2.HERE/'actor_contract.md').read_text()
        for it in old:
            original=it['request'];view=json.loads(original['messages'][1]['content'])
            new=runtime.request('research_actor',view)
            self.assertEqual(new['messages'][0]['content'],original['messages'][0]['content']+appendix)
            new['messages'][0]['content']=original['messages'][0]['content']
            self.assertEqual(new,original)

if __name__=='__main__':unittest.main()
