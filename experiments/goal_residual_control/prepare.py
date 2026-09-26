"""Stage inputs, committed before execution; no outcome-based selection."""
import sys,json,copy
from common import *

def g2():
    states=read(TOP/'bank/SNAPSHOTS.json');goals={x['case_id']:x for x in read(TOP/'goal_review/outputs.json')}
    items=[];blocked=[]
    for i,s in enumerate(states):
        order=['A0','A1','A2'];order=order[i%3:]+order[:i%3]
        for arm in order:
            if arm=='A1' and goals[s['case_id']]['output'] is None:
                blocked.append({'case_id':s['case_id'],'qid':s['qid'],'arm':arm,'reason':'G1 failure'});continue
            view=actor_view(s,residual=goals[s['case_id']]['output'] if arm=='A1' else None,
                             gap=s['historical_active_gap'] if arm=='A2' else None)
            items.append(item(s['case_id'],s['qid'],arm,'research_actor',view))
    base=TOP/'research_decision';write(base/'inherited_failures.json',blocked)
    (base/'PROTOCOL.md').write_text('# G2 research decisions\n\n40 snapshots × three arms. Counterbalanced cyclic arm order; one call each, no tools yet. All common inputs identical; only actual G1 residual or historical gap differs. Strict JSON and unchanged argument schema; ≤2 independent actions. See root protocol/rubric. No performance gate.\n')
    freeze_stage(base,items,{'g1_outputs_sha256':sha(TOP/'goal_review/outputs.json'),'prepare_sha256':sha(__file__),
                           'planned_cells':120,'inherited_failures':blocked,'horizon':1})

def g3():
    base=TOP/'one_step_acquisition';base.mkdir(exist_ok=True)
    assert not (base/'freeze.json').exists()
    out=read(TOP/'research_decision/outputs.json')
    write(base/'freeze.json',{'git_head':head(),'time':now(),'actor_outputs_sha256':sha(TOP/'research_decision/outputs.json'),
      'bank_freeze_sha256':sha(TOP/'bank/freeze.json'),'runner_sha256':sha(TOP/'tools_runner.py'),
      'common_sha256':sha(TOP/'common.py'),'rubric_sha256':sha(TOP/'REVIEW_RUBRIC.md'),
      'tool_schema_sha256':digest(SEARCH_FIND_TOOLS),'device':'cuda:1','order':[(x['case_id'],x['arm']) for x in out],
      'max_actions':2,'horizon':1,'max_retries':0,'policy':'validate all references against pre-batch handles; execute as-is, no retry; archive all real observations and failures'})
    (base/'PROTOCOL.md').write_text('# G3 one-step real acquisition\n\nExecute frozen G2 outputs in original counterbalanced order. Stops have zero actions. Actor-invalid and pre-batch-reference-invalid cells remain failures. Every real observation is archived. Source/arm-blind packets evaluate actual original-goal progress, with primary frozen pool and alternative-source sensitivity. No model calls in this stage. Backend unchanged.\n')

if __name__=='__main__':{'g2':g2,'g3':g3}[sys.argv[1]]()
