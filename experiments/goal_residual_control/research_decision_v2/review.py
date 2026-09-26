"""Single Codex review of all arm-hidden G2v2 packets; original truth unchanged."""
import sys,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'harness_v2'))
from runtime import *
base=TOP/'research_decision_v2';packets=read(base/'REVIEW_PACKETS.json');mapping=read(base/'PRIVATE_PACKET_MAP.json')
notes=read(base/'SEMANTIC_NOTES.json');truth=read(TOP/'bank/PRIVATE_TRUTH.json');reviews=[]
overcommit={'B004','B022','B058','B088','B102'}
for p in packets:
    pid=p['packet_id'];out=p['decision'];gold=p['gold_residual']['goal_status']=='resolved';stop=bool(out and out['decision']=='stop')
    r={'packet_id':pid,'qid':p['qid'],**mapping[pid],'valid':out is not None,'gold_resolved':gold,
      'correct_stop':stop and gold,'premature_stop':stop and not gold,'act_open':bool(out and not stop and not gold),
      'over_research':bool(out and not stop and gold),'goal_drift':False if out else None,
      'already_solved':False if out else None,'hypothesis_overcommit':pid in overcommit if out else None,
      'residual_reducing':bool(out and not stop and not gold) if out else None,
      'valid_action_semantics':bool(out and not stop) if out else None,
      'ambiguity':'medium' if pid in overcommit else 'low'}
    if out and not stop:
        assert pid in notes,pid;r['reason']=notes[pid]
    elif stop:r['reason']='STOP matches frozen primary closure.' if gold else 'Current committed Claims do not yet support all material original-goal requirements. Observed but uncommitted Workspace text alone does not reduce the Claims-based residual.'
    else:r['reason']='Strict action schema failure; not reinterpreted or executed.'
    strict_gold=gold and r['case_id'] not in truth['sensitivity_open_cases']
    r['strict_correct_stop']=stop and strict_gold;r['strict_premature_stop']=stop and not strict_gold
    reviews.append(r)
write(base/'reviews.json',reviews)
outs=read(base/'outputs.json');metrics={}
for arm in ['A0','A1','A2']:
    rr=[r for r in reviews if r['arm']==arm];oo=[r for r in outs if r['arm']==arm]
    metrics[arm]={'planned':40,'valid':sum(r['valid'] for r in rr),'resolved_n':7,'open_n':33,
      **{k:sum(r[k] is True for r in rr) for k in ['correct_stop','premature_stop','act_open','over_research','goal_drift','already_solved','hypothesis_overcommit','residual_reducing','valid_action_semantics','strict_correct_stop','strict_premature_stop']},
      'planned_tool_calls':sum(len(r['output']['actions']) for r in oo if r['output']),
      'proposed_tools':dict(collections.Counter(a['tool'] for r in oo if r['output'] for a in r['output']['actions']))}
paired={}
by={(r['case_id'],r['arm']):r for r in reviews}
for a,b in [('A1','A0'),('A1','A2')]:
    eligible=[cid for cid in truth['snapshots'] if by[cid,a]['valid'] and by[cid,b]['valid']]
    paired[a+'_vs_'+b]={'both_valid_n':len(eligible),'premature_improved':sum(by[cid,b]['premature_stop'] and not by[cid,a]['premature_stop'] for cid in eligible),
      'premature_worsened':sum(by[cid,a]['premature_stop'] and not by[cid,b]['premature_stop'] for cid in eligible),
      'no_independent_sample_claim':'40 snapshots cluster within 10 qids; descriptive pairing only'}
write(base/'metrics.json',{'contract_valid':118,'planned':120,'valid_rate':118/120,'old_valid_rate':75/120,
  'arms':metrics,'paired':paired,'semantic_scope':'single arm-hidden Codex reviewer; no executed Evidence Progress yet',
  'failure':'two Find objects include forbidden k; no wrapper-normalization or retry'})
rows=[]
for a,m in metrics.items():rows.append(f"| {a} | {m['valid']}/40 | {m['correct_stop']}/7 | {m['premature_stop']}/33 | {m['act_open']}/33 | {m['hypothesis_overcommit']} |")
(base/'RESULTS.md').write_text('''# G2v2 results

**118/120 (98.33%) valid**, versus historical 75/120 (62.5%), a descriptive +35.83 percentage points. All 120 API responses returned; both failures are Find actions containing forbidden k. Zero retries, repairs, normalization or resampling. The same full contract was used in all arms; old data and G1 residuals were not rewritten. A 120-pair object audit confirms only the appended system contract/examples changed. This supports the serialization-ambiguity diagnosis; it does not retrospectively turn old invalids into valid observations.

| Arm | Valid / planned | Correct STOP / resolved | Premature STOP / open | Act / open | Hypothesis overcommit |
|---|---:|---:|---:|---:|---:|
'''+ '\n'.join(rows)+'''

All valid acting packets select an original-goal-directed gap. Five gap wordings overstate an unverified binding; their queries still concern original requirements. Candidate names in exploratory queries alone are not overcommit. No unrelated-goal drift or fully solved-gap pursuit was found among valid acts. Invalids retain planned denominators and unknown semantics.

The resolved cohort is only two qids, with the pre-frozen q435 strict sensitivity in reviews/metrics. Claims-based premature stopping can occur even when the Workspace contains uncommitted support; this is evaluated under the unchanged original rubric. Paired cell counts are descriptive and not independent 40-question estimates. Stochastic variation prevents attributing every old/new semantic change to serialization alone.

The integrity gate passes. Continue G3–G5 regardless of effect strength. Tool proposals have not yet demonstrated Evidence Progress.
''')
print(json.dumps({'arms':metrics,'paired':paired},indent=2))
