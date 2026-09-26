from pathlib import Path
import json,statistics,collections
TOP=Path(__file__).resolve().parents[1]
s=json.load(open(TOP/'f1_state_sufficiency/summary.json'))
def fmt(r):return f"{r['n']}/{r['d']} ({r['rate']:.1%})" if r['rate'] is not None else 'unmeasured'
def table(headers,rows):return '\n'.join(['| '+' | '.join(headers)+' |','|'+'|'.join(['---']*len(headers))+'|']+['| '+' | '.join(map(str,r))+' |' for r in rows])
lines=['# F1 results','', 'All planned outputs are retained; gate uses valid decisions including correct STOP. Two replicates are correlated samples, not best-of. Primary closure and coverage were frozen before calls.','',
 table(['Metric','H','S','SH'],[[k]+[fmt(s['arms'][a][k]) for a in ['H','S','SH']] for k in ['valid','valid_act','correct_stop','stale','drift','unsupported_premise','over_broad','premature_stop','missed_stop','belief_error','critical','provider_or_contract_failure']]),'',
 '## Gate','', '```json',json.dumps(s['gate'],indent=2),'```','',
 'Critical repairs count checkpoints once, requiring an S critical failure and both SH replicates valid. Cases: '+str(s['critical_repairs'])+'. Long-term blocking omission is unmeasured in static F1.','',
 '## Per-question valid decisions','',table(['qid','H','S','SH'],[[q]+[fmt(v[a]['valid']) for a in ['H','S','SH']] for q,v in s['per_qid'].items()]),'',
 '## Actual H input token quartiles','',
 'Four equal groups of six checkpoints; same memberships for every arm. Table cells valid / stale / drift / premature-stop counts, each denominator12.','',
 table(['Quartile','H','S','SH'],[[q]+[' / '.join(str(v[a][k]['n']) for k in ['valid','stale','drift','premature_stop']) for a in ['H','S','SH']] for q,v in s['quartiles'].items()]),'',
 'Quartile failures are confounded by question, checkpoint phase and closure opportunities; no causal long-history or significance claim.','',
 '## Replicate stability','',table(['Category','H','S','SH'],[[k]+[s['stability'][a].get(k,0) for a in ['H','S','SH']] for k in ['same_valid_requirement','different_both_valid','one_valid','both_invalid']]),'',
 'Each arm has24pairs. Shared requirement IDs may encompass different subrelations; exact narrow focuses are preserved in replicate_stability.json.','',
 '## Measured usage and elapsed time','',
 table(['Arm','Input total / mean','Output total / mean','Reasoning proxy total / mean','Mean sec','Median sec','Cache hit tokens/input'],[[a]+[str(v[k]['sum'])+' / '+str(round(v[k]['mean'],1) if v[k]['mean'] is not None else None) for k in ['input','output','reasoning']]+[round(v['elapsed']['mean'],2),round(v['elapsed']['median'],2),fmt(v['cache_hit_rate'])] for a,v in s['arms'].items()]),'',
 'Reasoning tokens are an inference-burden proxy, not cognitive load. Provider elapsed is per-call wall time including provider/network, with four concurrent requests and shared cache warmth. No monetary estimate was made.','',
 '## Deferred reactivation','', '```json',json.dumps(s['deferred'],indent=2),'```','',
 'Failure to select a deferred requirement immediately is not scored wrong if another valid Need exists. Subrelation reactivation is separately annotated and not counted as full-composite recovery. No tools or Writer executed.','',
 '## Predeclared closure sensitivity','',table(['Arm','Valid with F24 discriminative-identity closure'],[[a,fmt(r)] for a,r in s['closure_sensitivity'].items()]),'',
 'Only the predeclared F24 policy changes. The primary coverage and gate are not overwritten.','',
 '## Audit trail','', 'Exact requests and committed freeze; append-only raw events; masked_contexts/packets; individual semantic_review; private unmask key; reviewed_outputs; replicate_stability and summary. STOP is mechanically scored against the human-reviewed frozen closure label. ACT Needs are individually semantically reviewed. The reviewer can infer treatment from view content; this is not perfect blinding.','',
 'The bank is24archived checkpoints/10qids with complete recorded-episode history, but unrecovered ancestral chronology and inherited legacy Writer States. It is not a fresh minimal-U1 cohort.']
(TOP/'f1_state_sufficiency/RESULTS.md').write_text('\n'.join(lines)+'\n')
print('wrote F1 results tables')
