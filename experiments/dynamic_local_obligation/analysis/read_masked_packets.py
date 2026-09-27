"""Show only first-pass-authorized fields; suppress repeated identical Q/C text."""
import argparse
from experiments.dynamic_local_obligation.common import *
def main():
 arg=argparse.ArgumentParser();arg.add_argument('start',type=int);arg.add_argument('stop',type=int);a=arg.parse_args()
 rows=read(P/'e1_obligation/review/PACKETS.json');seen={digest([r['question'],r['claims']]) for r in rows[:a.start]}
 for r in rows[a.start:a.stop]:
  sig=digest([r['question'],r['claims']]);print('\n'+r['review_id']+' input '+sig[:10])
  if sig not in seen:
   print('Q:',r['question']);print('C:',json.dumps(r['claims'],ensure_ascii=False));seen.add(sig)
  print('O:',json.dumps(r['output'],ensure_ascii=False))
  if not r['valid_output']:print('mechanical_failure:',r['failure'])
if __name__=='__main__':main()
