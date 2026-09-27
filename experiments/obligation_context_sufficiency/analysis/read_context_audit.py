"""Unmasked context-provenance review only after first-pass commit."""
from experiments.obligation_context_sufficiency.common import *
from experiments.obligation_context_sufficiency.run import OUT,load_rows
import argparse,subprocess
assert subprocess.check_output(['git','show','HEAD:'+rel(OUT/'review/FIRST_PASS.json')],cwd=ROOT)==(OUT/'review/FIRST_PASS.json').read_bytes()
a=argparse.ArgumentParser();a.add_argument('start',type=int);a.add_argument('stop',type=int);args=a.parse_args()
rows={r['id']:r for r in load_rows()};cases=bank();eligible=read(P/'analysis/CONTEXT_AVAILABILITY.json')['subsets']['path_eligible']
for cid in eligible[args.start:args.stop]:
 c=cases[cid];ctx=input_for(c,'C2')['Recent Context'];print('\nCASE',cid,c['state_id'])
 print('PATH',json.dumps(ctx['recent_events'],ensure_ascii=False));print('RAW',json.dumps(ctx['recent_observations'],ensure_ascii=False))
 for arm in ARMS:
  for rep in (1,2):
   r=rows[f'{arm}__{cid}__R{rep}'];print(r['id'],json.dumps(r['output'],ensure_ascii=False))
