"""G3v2 freeze and unchanged Orthogonal execution of valid G2v2 actions."""
from runtime import *
from tools_runner import run_one_step

def freeze():
    base=TOP/'one_step_acquisition_v2';base.mkdir(exist_ok=True)
    g=read(TOP/'research_decision_v2/ENGINEERING_GATE.json');assert g['continue_G3']
    outputs=read(TOP/'research_decision_v2/outputs.json')
    freeze_stage(base,[],{'phase':'G3v2','G2_outputs_sha256':sha(TOP/'research_decision_v2/outputs.json'),
      'G2_gate_sha256':sha(TOP/'research_decision_v2/ENGINEERING_GATE.json'),'case_arm_order':[(x['case_id'],x['arm']) for x in outputs],
      'planned_decisions':120,'valid_decisions':sum(x['output'] is not None for x in outputs),'max_actions':2,'horizon':1,
      'device':'cuda:1','backend':'unchanged OrthogonalSearchFindTools / BCPlusSearcher','retry':False,
      'progress':'Original Question + Claims + frozen residual rubric + exact Observation; arm hidden; primary and alternative-source sensitivity'})
    (base/'PROTOCOL.md').write_text('# G3v2 real acquisition\n\nExecute all valid G2v2 actions using unchanged Search/Find/Open semantics. All 120 planned decisions remain in the denominator, including stops and failures. At most two independent actions; no post-result rewriting. Source/arm-hidden semantic review uses Original Question, not local Gap alone. Frozen primary source pool and separate post-retrieval sensitivity remain unchanged.\n')

def run():
    base=TOP/'one_step_acquisition_v2';gate(base)
    f=read(base/'freeze.json');assert sha(TOP/'research_decision_v2/outputs.json')==f['extra']['G2_outputs_sha256']
    states={s['case_id']:s for s in read(TOP/'bank/SNAPSHOTS.json')}
    run_one_step(base,states,read(TOP/'research_decision_v2/outputs.json'))

if __name__=='__main__':{'freeze':freeze,'run':run}[sys.argv[1]]()
