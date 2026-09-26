"""Render actual frozen inputs and archived outputs for single-reviewer coding."""
import json,sys
from pathlib import Path
P=Path(__file__).resolve().parents[1]
def rd(p):return json.loads(p.read_text())
C={x['case_id']:x for x in rd(P/'bank/RUNTIME_INPUTS.json')};L={x['case_id']:x for x in rd(P/'bank/LABELS.json')}
start=int(sys.argv[1]) if len(sys.argv)>1 else 1;end=int(sys.argv[2]) if len(sys.argv)>2 else 55
for n in range(start,end+1):
 cid=f'N{n:03}';c=C[cid];l=L[cid];print('\n###',cid,l['qid'],l['source_inventory_id'],l['strata']);print('Q',c['question']);print('H',c['hypothesis']);print('\n'.join(f'C{i+1}: {s}' for i,s in enumerate(c['claims'])));print('ORACLE',l['oracle_gap'])
 for arm in ['P0','P1','P2','P3','P4']:
  p=P/'round_0'/f'{cid}_{arm}.json'
  if arm=='P3' and (P/'round_0_p3_format_repair'/f'{cid}_P3.json').exists():p=P/'round_0_p3_format_repair'/f'{cid}_P3.json'
  if not p.exists():continue
  r=rd(p);print(arm,r['output'] or r['errors'])
  if arm=='P3':
   a=rd(p.parent/'calls'/f'{cid}_P3A.result.json');print('P3A',a['output'])
