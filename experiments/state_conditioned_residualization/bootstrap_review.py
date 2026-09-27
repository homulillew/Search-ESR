"""Masked visible-window review export. Does not export oracle evidence."""
from .common import *
from .bootstrap_runtime import load_rows

def export(directory):
 d=P/directory;parents={s['case_id']:s['parent'] for s in read(P/'e0_reference/PARENT_REQUIREMENTS.json')};states={s['case_id']:s for s in read(P/'e0_reference/STATES.json')}
 jobs={j['id']:j for j in read(d/'SCHEDULE.json')};rows=load_rows(directory);packets=[];key={};windows={}
 for i,r in enumerate(sorted(rows,key=lambda r:digest(['bootstrap-blind-v1',r['id']]))):
  bid=f'E{i+1:03}';key[bid]=r['id'];s=states[r['case_id']];j=jobs[r['id']];t=read(d/'retrieval'/f"{r['id']}.json");view=[]
  if t['tool']:
   for w in t['tool']['observations']:
    h=digest([w['title'],w['text']]);wid='T'+h[:10];windows[wid]={'title':w['title'],'text':w['text']}
    view.append({'text_id':wid,'doc_ref':w['doc_ref'],'window_ref':w['window_ref'],'title':w['title']})
  packets.append({'review_id':bid,'question':s['question'],'parent':parents[s['case_id']],'claims':s['claims'],'model_input':json.loads(j['request']['messages'][1]['content']) if j['request'] else None,'query':r['output'].get('query') if r['valid_output'] else None,'query_contract':r['valid_output'],'retrieval_attempted':t['attempted'],'tool_error':t['error'],'visible_windows':view})
 write(d/'review/PACKETS.json',packets);write(d/'review/KEY.json',key);write(d/'review/WINDOWS.json',windows)
 print('packets',len(packets),'unique visible texts',len(windows))
if __name__=='__main__':
 import sys
 export(sys.argv[1])
