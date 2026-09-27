"""Display Q/C/O only, grouped by canonical input to make repeated ratings consistent."""
import argparse
from collections import defaultdict
from experiments.obligation_context_sufficiency.common import *
a=argparse.ArgumentParser();a.add_argument('start',type=int);a.add_argument('stop',type=int);args=a.parse_args()
groups=defaultdict(list)
for r in read(P/'e1_context/review/PACKETS.json'):groups[digest([r['question'],r['claims']])].append(r)
for idx,(sig,rows) in enumerate(sorted(groups.items())):
 if not args.start<=idx<args.stop:continue
 print('\nGROUP',idx,'INPUT',sig[:12]);print('Q:',rows[0]['question']);print('C:',json.dumps(rows[0]['claims'],ensure_ascii=False))
 for r in rows:
  print(r['review_id'],json.dumps(r['output'],ensure_ascii=False))
  if not r['valid_output']:print('mechanical_failure:',r['failure'])
