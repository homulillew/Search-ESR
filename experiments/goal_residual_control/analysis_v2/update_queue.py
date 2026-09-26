from progress import *
def queue():
 b=TOP/'three_round_loop_v2';rows=[];mapping={}
 for p in sorted(b.glob('*updater*_events.jsonl')):
  for line in p.open():
   e=json.loads(line)
   if e['kind']!='completed':continue
   it=e['event'];r=e['result'];v=json.loads(it['request']['messages'][1]['content']);uid=digest([it['request_sha256'],r['output']])[:16]
   rows.append({'review_id':uid,'qid':r['qid'],'claims_before':v['Verified Claims'],'hypothesis_before':v['Working Hypothesis'],'observation':v['Observation'],'proposal':r['output'],'error':r['error']})
   mapping.setdefault(uid,[]).append({'file':p.name,'cell':r['case_id'],'request_sha256':r['request_sha256']})
 write(b/'UPDATER_STREAM_PACKETS.json',rows);write(b/'PRIVATE_STREAM_MAP.json',mapping)
 return rows
if __name__=='__main__':
 rows=queue();reviewed=read(TOP/'analysis_v2/UPDATER_LABELS.json') if (TOP/'analysis_v2/UPDATER_LABELS.json').exists() else {};seen=set()
 known_texts={r['observation']['text'] for r in rows if r['review_id'] in reviewed};substantive_pending=0
 for r in sorted(rows,key=lambda x:x['review_id']):
  uid=r['review_id'];o=r['proposal']
  if uid in reviewed or uid in seen:continue
  seen.add(uid)
  if not o:print(uid,'INVALID',r['error']);continue
  if not o['claims_to_add'] and o['hypothesis_update']['action']=='keep':continue
  substantive_pending+=1
  print('\nID',uid,'Q',r['qid'],'PRIOR_H',r['hypothesis_before'],'PROPOSED',json.dumps(o,ensure_ascii=False),'\nSOURCE',r['observation']['url'],'\n',r['observation']['text'] if r['observation']['text'] not in known_texts else '[Exact observation text already read in a reviewed packet.]')
 print('TOTAL',len(rows),'unique pending substantive',substantive_pending,'unlabelled including empty keep',len(seen))
