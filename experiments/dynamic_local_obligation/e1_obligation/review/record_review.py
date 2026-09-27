"""Transcribe explicit masked single-reviewer judgments only."""
from experiments.dynamic_local_obligation.common import *
from experiments.dynamic_local_obligation.score import DIMENSIONS,ERRORS

def record(part,judgments):
 packets={p['review_id']:p for p in read(P/'e1_obligation/review/PACKETS.json')};labels=[]
 for n,spec in judgments.items():
  rid=f'R{n:03d}';r=packets[rid];failed=spec.get('fails',[])
  assert set(failed)<=set(DIMENSIONS) and set(spec.get('errors',[]))<=set(ERRORS)
  labels.append({'review_id':rid,'dimensions':{k:(k not in failed and r['valid_output']) for k in DIMENSIONS},
   'errors':spec.get('errors',[]),'reason':spec['reason'],'ambiguity':spec.get('ambiguity','low')})
 write(P/f'e1_obligation/review/PART{part}.json',labels)
