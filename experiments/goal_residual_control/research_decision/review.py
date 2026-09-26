"""Single Codex packet review; invalid action serialization is never repaired."""
import sys,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import *
base=TOP/'research_decision';packets=read(base/'REVIEW_PACKETS.json');mapping=read(base/'PRIVATE_PACKET_MAP.json')
notes=read(base/'semantic_notes.json');truth=read(TOP/'bank/PRIVATE_TRUTH.json');reviews=[]
overcommit={'B022','B056','B080','B113'}
for p in packets:
    pid=p['packet_id'];out=p['decision'];gold=p['gold_residual']['goal_status']=='resolved'
    r={'packet_id':pid,'qid':p['qid'],'valid':out is not None,'gold_resolved':gold,
      'residual_reducing':None,'already_solved':None,'goal_drift':None,'hypothesis_overcommit':None,
      'unnecessary_bridge':None,'reasonable_direct_attack':None,'actionable':None,
      'correct_stop':False,'premature_stop':False,'over_research':False,'reason':'Frozen-parser invalid; no semantic action accepted or executed.'}
    if out:
        stop=out['decision']=='stop';r.update(correct_stop=stop and gold,premature_stop=stop and not gold,
          over_research=not stop and gold,goal_drift=False,already_solved=False,hypothesis_overcommit=False,
          unnecessary_bridge=False,reasonable_direct_attack=False,actionable=not stop,residual_reducing=not stop and not gold)
        if stop:r['reason']='STOP matches frozen primary resolved Claims.' if gold else 'STOP while original-goal requirements remain unsupported by the current Claims. Workspace visibility alone is not committed closure.'
        else:
            assert pid in notes,pid
            r['reason']=notes[pid];r['hypothesis_overcommit']=pid in overcommit
            r['reasonable_direct_attack']=p['qid'] in ('435','177','387') or pid=='B009'
            docs={d['doc_ref'] for d in p['workspace']['known_documents']};wins={w['window_ref'] for w in p['workspace']['observed_windows']}
            r['actionable']=all(a.get('doc_ref') in docs if a['tool']=='find' else a.get('window_ref') in wins if a['tool']=='open' else True for a in out['actions'])
    r.update(mapping[pid]);strict_gold=gold and r['case_id'] not in truth['sensitivity_open_cases']
    r['strict_correct_stop']=bool(out and out['decision']=='stop' and strict_gold)
    r['strict_premature_stop']=bool(out and out['decision']=='stop' and not strict_gold)
    reviews.append(r)
write(base/'reviews.json',reviews)
outs=read(base/'outputs.json')
def stats(arm):
    rr=[r for r in reviews if r['arm']==arm];valid=[r for r in rr if r['valid']]
    acts=[p['decision'] for p in packets if mapping[p['packet_id']]['arm']==arm and p['decision'] and p['decision']['decision']=='act']
    return {'planned':len(rr),'valid':len(valid),'invalid':len(rr)-len(valid),'valid_rate':len(valid)/len(rr),
      'resolved_n':sum(r['gold_resolved'] for r in rr),'open_n':sum(not r['gold_resolved'] for r in rr),
      'act_decisions':len(acts),'planned_tool_calls':sum(len(x['actions']) for x in acts),'executed_tool_calls':0,
      **{k:sum(r[k] is True for r in rr) for k in ['correct_stop','premature_stop','over_research','goal_drift','already_solved','residual_reducing','hypothesis_overcommit','actionable','strict_correct_stop','strict_premature_stop']}}
metrics={'arms':{a:stats(a) for a in ['A0','A1','A2']},'valid':sum(r['valid'] for r in reviews),'planned':120,
 'comparison_status':'not interpretable: frozen action serialization validity 62.5% <80%, treatment-dependent missingness',
 'error_types':dict(collections.Counter(x['error']['message'].split('\n')[0] for x in outs if x['error'])),
 'blindness':'packet arm labels withheld during single-reviewer reading; same-session Codex not independent human replication',
 'execution_gate':'stop after G2; G3/G4/G5 not run; no effect-size stopping'}
write(base/'metrics.json',metrics)
rows=[]
for a,s in metrics['arms'].items():rows.append(f"| {a} | {s['valid']}/40 | {s['correct_stop']}/7 | {s['premature_stop']}/33 | {s['act_decisions']} | {s['hypothesis_overcommit']} |")
(base/'RESULTS.md').write_text('''# G2: execution integrity failure

120/120 API responses returned, but only **75/120 (62.5%)** satisfy the frozen Actor JSON contract. All 45 failures are action serialization: 38 discriminator/wrapper failures and 7 missing top-level query failures. No retry, repair, relaxed parser or rejected-action execution was performed. This is a harness contract omission, documented in INTERFACE_FAILURE.md, not negative evidence about the architecture.

The <80% integrity gate stops G3–G5. The frozen batch was allowed to finish so the full planned denominator and failures remain available. Primary comparisons are not interpretable because missingness differs by arm and valid STOP uses no action object.

## Diagnostic only

| Arm | Valid | Correct STOP / resolved | Premature STOP / open | Valid act decisions | Hypothesis overcommit |
|---|---:|---:|---:|---:|---:|
'''+ '\n'.join(rows)+'''

All denominators above retain planned snapshots; 40 snapshots are only 10 qids. Invalids have unknown semantic outcomes, not zero drift. No valid acting packet pursued a fully resolved original goal or an unrelated new objective; four overstate a candidate identity/binding. Valid-query relevance does not establish evidence progress. No tools ran, so source precision, evidence yield and efficiency are unmeasured. q435 strict closure sensitivity is retained in reviews/metrics.

A1's diagnostic premature stops cannot be attributed solely to G1: Actor can independently stop despite a nonempty residual, while G1's two empty residual errors can also propagate. These failure examples warrant study under a corrected explicit response contract, not a selected valid-only arm ranking.
''')
print(json.dumps(metrics,ensure_ascii=False,indent=2))
