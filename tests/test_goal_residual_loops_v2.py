"""Offline controller checks with mock model/tool boundaries, never live calls."""
import copy,json,sys,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'experiments/goal_residual_control/harness_v2'))
import adaptive as runner
from contracts import validate_object

class FakeTools:
    def __init__(self,state):self.state=copy.deepcopy(state)
    def close(self):pass

class LoopTests(unittest.TestCase):
    def exercise(self,stage):
        real=runner.TOP;requests=[]
        with tempfile.TemporaryDirectory() as tmp:
            top=Path(tmp);(top/'bank').mkdir()
            for name in ['SNAPSHOTS.json','TRANSITIONS.json','SOURCE_WINDOWS.json']:
                (top/'bank'/name).write_bytes((real/'bank'/name).read_bytes())
            for folder in ['transition_replan_v2','three_round_loop_v2']:(top/folder).mkdir()
            (top/'three_round_loop_v2/selection.json').write_bytes((real/'three_round_loop_v2/selection.json').read_bytes())
            def mock_batch(base,tag,items):
                outputs=[]
                for it in items:
                    requests.append(copy.deepcopy(it));v=json.loads(it['request']['messages'][1]['content']);kind=it['kind']
                    if kind=='goal_reviewer':
                        self.assertEqual(set(v),{'Original Question','Verified Claims'})
                        resolved='mock source fact' in v['Verified Claims'];obj={'resolved':resolved,'residual':'' if resolved else 'mock unresolved relation'}
                    elif kind=='state_updater':obj={'claims_to_add':['mock source fact'],'hypothesis_update':{'action':'clear','statement':''}}
                    else:
                        self.assertNotIn('gold_residual',v)
                        obj={'decision':'act','gap':'mock current gap','actions':[{'tool':'search','query':'mock query','k':5}]}
                    validate_object(obj,kind)
                    outputs.append({k:it[k] for k in ['case_id','qid','arm','kind']}|{'output':obj,'error':None})
                return outputs
            def mock_execute(tools,out):
                return {'decision':out,'actions':[{'action':out['actions'][0],'result':{'status':'ok'},'error':None,
                  'observations':[{'window_ref':'W900','doc_ref':'D900','title':'Mock source','url':'https://example.test','text':'mock source fact'}]}], 'error':None}
            with patch.object(runner,'TOP',top),patch.object(runner,'gate',lambda p:None),patch.object(runner,'journal_batch',mock_batch),\
                 patch.object(runner,'create_searcher',lambda:SimpleNamespace(close=lambda:None)),\
                 patch.object(runner,'restore',lambda state,searcher:FakeTools(state)),patch.object(runner,'execute_batch',mock_execute),\
                 patch.object(runner,'workspace',lambda tools:copy.deepcopy(tools.state['available_workspace'])):
                getattr(runner,stage)()
            if stage=='g4':
                states=json.loads((top/'transition_replan_v2/actor_states.json').read_text())
                self.assertEqual(len(states),80)
                for tid in [f'T{i:02}' for i in range(1,21)]:
                    self.assertIn('mock source fact',[c['statement'] for c in states[tid+':R3']['verified_claims']])
                    self.assertNotIn('mock source fact',[c['statement'] for c in states[tid+':R2']['verified_claims']])
            else:
                cells=json.loads((top/'three_round_loop_v2/results.json').read_text());self.assertEqual(len(cells),30)
                for c in cells.values():
                    self.assertEqual(len(c['decisions']),1 if c['arm']=='L2' else 3)
                    self.assertEqual(c['status'],'goal_stop' if c['arm']=='L2' else 'horizon_exhausted')
                    self.assertEqual(c['state']['working_hypothesis'],None)
                    for u in c['updates']:self.assertEqual(u['post_state']['verified_claims'][-1]['support_refs'],['W900'])
                for it in requests:
                    if it['kind']=='research_actor':
                        view=json.loads(it['request']['messages'][1]['content'])
                        self.assertEqual('Persisted historical Gap' in view,it['arm']=='L0')
                        self.assertEqual('Goal Residual' in view,it['arm']=='L2')
    def test_g4_oracle_online_separation_and_all_arms(self):self.exercise('g4')
    def test_g5_horizon_mutation_and_immediate_resolved_stop(self):self.exercise('g5')

if __name__=='__main__':unittest.main()
