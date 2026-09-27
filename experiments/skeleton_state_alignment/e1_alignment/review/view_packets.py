"""Render masked packet groups only. No key/reference/result/aggregate access."""
import json
from pathlib import Path
import sys
p=Path(__file__).resolve().parent
rows=json.loads((p/'VIEW_GROUPS.json').read_text())
for g in rows[int(sys.argv[1])-1:int(sys.argv[2])]:
 print('\nGROUP',g['group'])
 print('Q:',g['input']['Original Question'])
 print('CLAIMS:',json.dumps(g['input']['Verified Claims'],ensure_ascii=False))
 for n in g['input']['Task Skeleton']:
  print(n['requirement_id'],n.get('label',''),':',' | '.join(s['text'] for s in n['source_spans']))
 for o in g['outputs']:
  print(o['review_id'],json.dumps(o['output'],ensure_ascii=False))
