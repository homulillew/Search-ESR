"""Render frozen-denominator descriptive tables from reviewed observations."""
import collections,json
from pathlib import Path
P=Path(__file__).resolve().parents[1]
def rd(n):return json.loads((P/n).read_text())
def frac(v):return f"{v['n']}/{v['d']}" if v['d'] else '—'
def num(v):return f'{v:.2f}' if v is not None else '—'
m=rd('analysis/METRICS.json');cells=rd('analysis/CELL_REVIEW.json');actions=rd('analysis/ACTION_REVIEW.json');integ=rd('analysis/INTEGRITY.json')
lines=['# R1 reviewed results','',
'Primary: exact support or refutation actually returned within at most two decisions. One model sample per case/arm. No Writer or evaluator-controlled early stopping. Fresh K has ten Need families but only five qids; N has eight families/eight qids. Challenge is separate. No population significance or equivalence claim.','',
'## Evidence and access','',
'| Bank | Arm | Exact | First action | Recovery after no first evidence | First existing exact D use | Mean actions | Mean actions to evidence, successes only |','|---|---|---:|---:|---:|---:|---:|---:|']
for bank,g in m['groups'].items():
 for arm,r in g.items():lines.append(f"| {bank} | {arm} | {frac(r['exact_evidence'])} | {frac(r['action1_success'])} | {frac(r['action2_recovery'])} | {frac(r['first_known_source_direct_use'])} | {num(r['mean_actions'])} | {num(r['mean_actions_to_evidence_successes'])} |")
lines+=['','Recovery denominator includes early STOP/schema failures; it is not conditional on an attempted second tool. Mean actions to evidence excludes failures and is selection-sensitive. It should be read alongside exact success. Runtime failures truncated nine trajectories after their successful first tool; costs and second decisions are therefore incomplete for those cases.','',
'## Tools and cost','',
'| Bank | Arm | Search | Find | Open | Input | Output | Reasoning (included in output) | API calls | Cache hit/input | Model seconds sum | Tool seconds sum |','|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
for bank,g in m['groups'].items():
 for arm,r in g.items():
  t=r['tools'];c=r['cost'];lines.append(f"| {bank} | {arm} | {t.get('search',0)} | {t.get('find',0)} | {t.get('open',0)} | {c['input']} | {c['output']} | {c['reasoning']} | {c['api_calls']} | {100*c['cache_hit_rate']['rate']:.1f}% | {c['model_elapsed_seconds_sum']:.2f} | {c['tool_elapsed_seconds_sum']:.2f} |")
c=m['all']['cost']
lines += ['',f"Total: {c['api_calls']} API calls, **zero Writer calls**, 53 Search / 42 Find / 5 Open; {c['input']:,} input, {c['output']:,} output, {c['reasoning']:,} reasoning tokens. Weighted cache hit **{c['hit']:,}/{c['input']:,} = {100*c['cache_hit_rate']['rate']:.2f}%**; miss {c['miss']:,}; nonzero-cache requests {frac(c['cache_occurrence'])}. Cache depends on concurrency/order and is a cost observation, not a semantic outcome.",
f"Run wall time **{m['wall_time']['wall_seconds']:.2f}s**, including retrieval initialization; model elapsed sum {c['model_elapsed_seconds_sum']:.2f}s, tool elapsed sum {c['tool_elapsed_seconds_sum']:.2f}s. Overlapping sums are not additive wall time. Recorded HTTP concurrency peak {integ['api_concurrency']['peak_active']}, tool peak {integ['tool_concurrency']['peak_active']}; GPU forwards alone were locked. No monetary cost is inferred.",
'', '## Paired fresh cells', '', '| Case | QID | Structure | A0 | A1 | A2 | A3 |','|---|---|---|---:|---:|---:|---:|']
for bank in ['K','N','challenge']:
 for cid in sorted({c['case_id'] for c in cells if c['bank']==bank}):
  cr=[c for c in cells if c['case_id']==cid];v={c['arm']:c for c in cr};vals=[]
  for arm in ['A0','A1','A2','A3']:
   r=v.get(arm)
   vals.append('—' if r is None else ('✓' if r['exact_evidence'] else '×')+('*' if r['status'].endswith('failure') else ''))
  lines.append(f"| {cid} | {cr[0]['qid']} | {cr[0]['structure']} | "+' | '.join(vals)+' |')
lines+=['','* Retained schema/runtime failure; a ✓* means actual exact evidence preceded the runtime error. See engineering/INCIDENT.md for the independent failure-free sensitivity.','',
'## Source-hit versus window-hit','',
'Action denominator: Search calls returning any audited exact source; numerator: none of their windows provides exact evidence. Window denominator: returned windows from exact sources; numerator: that particular window omits the relation. A Search can include a missed window and another successful one.','',
'| Bank | Arm | Failed exact-source Search actions | Exact-source Search windows missing relation |','|---|---|---:|---:|']
for bank,g in m['groups'].items():
 for arm,r in g.items():
  if arm=='A3':continue
  lines.append(f"| {bank} | {arm} | {frac(r['search_source_hit_window_miss_actions'])} | {frac(r['search_exact_source_window_miss'])} |")
lines+=['','Overall: **11/48 (22.9%)** source-hit Search actions fail at window access, and **19/69 (27.5%)** correct-source windows miss the relation. Five of 53 Search calls return no audited exact source. K alone: 0/16 failed source-hit Search actions despite 6/25 missed individual windows; other returned windows recover the relation. Challenge drives most action-level misses.','',
'## Structure sensitivity (fresh K only)','',
'| Relation region | Cases | A0 | A1 | A2 | A3 |','|---|---:|---:|---:|---:|---:|']
for st,g in m['by_structure'].items():lines.append(f"| {st} | {g['A0']['n']} | "+' | '.join(frac(g[a]['exact_evidence']) for a in ['A0','A1','A2','A3'])+' |')
lines+=['','Structure labels describe the relation region. No fresh pure-table case survived eligibility; three table/infobox challenges are not a fresh structural comparison. K_VP14 A1 repeats the start of the correct WPBSA table, but K_VN06 A3 misses the Class-of-92 relation in prose. Table-specific superiority or failure is not established.','',
'## Failures, including nonsemantic incidents','',
'| Cell | Final status | Labels | Explanation |','|---|---|---|---|']
for c in cells:
 if not c['exact_evidence'] or c['status'].endswith('failure'):
  why=(str(c['runtime_error']) if c['runtime_error'] else c['reason']).replace('|','/')
  lines.append(f"| {c['cell']} | {c['status']} | {', '.join(c['failure_labels'])} | {why} |")
lines+=['','S1–S8 are multi-label descriptions, not mutually exclusive causal estimates. N_VP03 A0/A1 stops after one local inspection; A2 stops immediately. This is S8/overinterpretation, not S3, which requires two unsuccessful inspections of the same wrong source. K_VP14 A1 selects a correct source twice; its repeated query is S6, not wrong-source local lock.','',
'## Query attributes','',
'Exact repetition means the same tool, same local target (if any), and identical query bytes. Entity/relation presence is a frozen lexical annotation, not a subjective good-query score.','',
'| Tool | Actions | Repeated query | Entity terms | Relation terms | Same-document rediscoveries (windows) |','|---|---:|---:|---:|---:|---:|']
for t in ['search','find','open']:
 a=[a for a in actions if a['tool']==t]
 lines.append(f"| {t} | {len(a)} | {sum(x['repeated_query'] for x in a)} | {sum(x['entity_terms_present'] for x in a)} | {sum(x['relation_terms_present'] for x in a)} | {sum(x['same_document_rediscovery_count'] for x in a)} |")
lines+=['','Local query wording can choose a wrong occurrence even in the gold document (Class of92; production credits; WPBSA table start). Global queries can repeatedly retrieve a correct source with the same unsuitable preview (paper setup challenge). This bank does not identify a single universal query defect.','']
(P/'analysis/RESULTS_REPORT.md').write_text('\n'.join(lines))
print('Wrote analysis/RESULTS_REPORT.md')
