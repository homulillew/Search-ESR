import sys,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from runtime import *
base=TOP/'transport_correction';assert not (base/'freeze.json').exists()
original=rd(TOP/'p1_progress/progress_outputs.json');assert len(original)==216
requests={x['id']:x for x in rd(TOP/'p1_progress/requests.json')};events={e['result']['id']:e for e in [json.loads(l) for l in (TOP/'p1_progress/progress_events.jsonl').read_text().splitlines()] if e['kind']=='completed'}
items=[]
for r in original:
 e=events[r['id']]['event'];body=e.get('response_text','')
 if e.get('http_status')!=400 or "Prompt must contain the word 'json'" not in body:continue
 assert r['output'] is None and r['usage'] is None and r['arm'] in ['R','FULL']
 assert 'choices' not in json.loads(body)
 it=copy.deepcopy(requests[r['id']]);it['id']='TC_'+it['id'];it['request']['messages'][1]['content']+='\n\nReturn JSON.';it['request_sha256']=dg(it['request']);items.append(it)
items.sort(key=lambda x:dg(['dynamic-progress-transport-correction',x['id']]))
wr(base/'requests.json',items)
files=[base/'PLAN.md',base/'requests.json',base/'freeze_correction.py',base/'run.py',TOP/'runtime.py',TOP/'p1_progress/freeze.json',TOP/'p1_progress/progress_outputs.json',TOP/'analysis/RUBRIC.md',TOP/'bank/PRIMARY_LABELS.json',TOP/'bank/CHALLENGE_LABELS.json']
wr(base/'freeze.json',{'created_utc':now(),'construction_head':head(),'sample_count':len(items),'provider':CONFIG,'max_retries':0,'best_of':0,'workers':4,'timeout_seconds':240,'horizon':1,'tool_calls':0,'eligibility':'Only originalHTTP400missingJSON/nochoices/nousage. No successful model inference resampled. Original denominators retained.','primary_gate_override':False,'file_hashes':{str(p.relative_to(ROOT)):sha(p) for p in files},'request_hashes':{i['id']:i['request_sha256'] for i in items}})
print('Correction frozen',len(items))
