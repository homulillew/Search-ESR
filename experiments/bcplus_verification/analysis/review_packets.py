"""Offline, read-only live-result packet builder. Never imported by runtime."""
import json,sys,re
from pathlib import Path
P=Path(__file__).resolve().parent.parent
cells=json.loads((P/sys.argv[1]).read_text())
for cid in sys.argv[2:]:
 c=next(v for v in cells.values() if v['case_id']==cid)
 print('\n###',cid,c['qid'],c['constraint'] or 'DISCOVERY')
 for d in c['decisions']:
  r=d['round']
  m=re.match(r'round(\d+)/',sys.argv[1])
  if m and r+1!=int(m[1]):continue
  a=d['actor']['output'];print('ROUND',r+1,'ACTOR',a)
  if not d['tool']:continue
  for k,w in enumerate(d['tool']['observations']):
   print('OBS',f'{r+1}.{k}',w['window_ref'],w['doc_ref'],w['url']);print(' '.join(w['text'].split()))
   u=next((u for u in c['updates'] if u['round']==r and u['wave']==k),None)
   if u:print('WRITER',u['proposal']['output'],'PRE H',u['pre_state']['hypothesis'])
 print('FINAL H',c['hypothesis'])
