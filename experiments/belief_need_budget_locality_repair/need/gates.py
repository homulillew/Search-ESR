"""Report gates without rounding fractions or treating zero activation as success."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from transport import P,rd,save
stage=sys.argv[1];D=P/'need'/stage;confirm=stage.startswith('confirmation');settings=rd(P/'need/SETTINGS.json');g=settings['confirmation_gate' if confirm else 'development_gate'];m=rd(D/'METRICS.json')
bank=rd(P/'bank'/('CONFIRMATION.json' if confirm else 'DEVELOPMENT.json'));out={}
for arm,x in m.items():
 if arm=='ORACLE':continue
 s=x['primary'];n=s['n'];e=s['errors'];d=x['delta'];gap=[s for s in bank if s['label']['strong_h_one_gap']];adequate=len(gap)>=8 and len({s['qid'] for s in gap})>=3
 checks={'completion':s['FinalJSONCompletionRate']>=g['completion'],'strict':s['ITT_strict']>=g['strict'],'premise':e['P']/n<=g['premise_max'],'stale':e['S']/n<=g['stale_max'],'broad':e['W']/n<=g['broad_max'],'no_h':x['no_h']['ITT_strict']>=g['no_h'],
 'B_validity_in_delta':d['B_strict_rate']>=g['delta'],'activated_retirement':d['retirement_given_A_valid_activation'] is not None and d['retirement_given_A_valid_activation']>=g['delta']}
 if adequate:checks['strong_h_one_gap']=x['strong_h_one_gap']['ITT_strict']>=g['one_gap']
 if confirm:checks.update({'state_count':n>=g['states_min'],'fresh_qid_count':len({s['qid'] for s in bank})>=g['qids_min']})
 passed=all(checks.values());near_numeric=s['FinalJSONCompletionRate']>=.95 and s['ITT_strict']>=.85 and e['P']/n<=.05 and e['S']/n<=.075 and x['no_h']['ITT_strict']>=.80
 out[arm]={'checks':checks,'failed':[k for k,v in checks.items() if not v],'PASS':passed,'NEAR_PASS_numeric_eligible':near_numeric,'NEAR_PASS_additional_review_required':'Single clear long-tail mechanism; no systemic collapse, promotion or closure. Numeric eligibility alone never declares NEAR_PASS.','one_gap_adequately_sampled':adequate,'one_gap_count':len(gap),'activated_delta_n':d['A_activated_g_and_valid'],'claim':'Within-cohort semantic diagnostic; not end-to-end accuracy or iid population estimate.'}
save(D/'GATES.json',out);print(out)
