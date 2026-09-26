"""Offline regression of the concrete failure against every actual input shape."""
import copy, difflib, json
from pathlib import Path
from attempts_compat import append_attempt
P=Path(__file__).resolve().parents[1]
inputs=json.loads((P/'bank/RUNTIME_INPUTS.json').read_text())
rows=[]
for c in inputs:
    before=copy.deepcopy(c['attempts']);ctx=before
    actions=[{'action':{'tool':'find','doc_ref':'D1','query':'relation'},'status':'ok','returned_windows':['W_new1']},
             {'action':{'tool':'open','window_ref':'W_new1','direction':'after'},'status':'ok','returned_windows':['W_new2']}]
    for a in actions:ctx=append_attempt(ctx,a)
    assert before==c['attempts']
    if isinstance(before,list):assert ctx==before+actions
    else:
        assert {k:v for k,v in ctx.items() if k!='current_run_attempts'}==before
        assert ctx['current_run_attempts']==actions
    rows.append({'case_id':c['case_id'],'input_type':type(before).__name__,'two_appends_preserve_prior_context':True})
source=(P/'runtime.py').read_text()
old="     c['attempts'].append("
assert source.count(old)==1
patched=source.replace('def contract(', 'from experiments.evidence_scope_localization.engineering.attempts_compat import append_attempt\n\ndef contract(',1).replace(old,"     c['attempts']=append_attempt(c['attempts'],",1)
compile(patched,'future_runtime.py','exec')
(P/'engineering/FUTURE_RUNTIME.patch').write_text(''.join(difflib.unified_diff(source.splitlines(True),patched.splitlines(True),fromfile='a/experiments/evidence_scope_localization/runtime.py',tofile='b/experiments/evidence_scope_localization/runtime.py')))
(P/'engineering/TEST_RESULTS.json').write_text(json.dumps({'cases':rows,'passed':len(rows),'model_calls':0,'retrieval_calls':0,'patch_compiles':True,'applied_to_r1':False},indent=2)+'\n')
print('23 real contexts: preserved and appended twice; proposed patch compiles; R1 unmodified.')
