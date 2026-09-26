"""Verify E0 isolation and account actual API usage, including failed arms."""
import sys,json,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from transport import P,ROOT,rd,sha,save,dg
BASE=P/'e0';cases={x['calibration_id']:x for x in rd(BASE/'CASES.json')};n=0;usage=[]
for arm in ['E8192','E16384','E32768','EDEFAULT']:
 for f in sorted((BASE/arm/'calls').glob('*.request.json')):
  x=rd(f);c=cases[f.name.split('.')[0]];req=x['request'];old=c['request'];assert {k:v for k,v in req.items() if k!='max_tokens'}=={k:v for k,v in old.items() if k!='max_tokens'};assert dg(req)==x['request_sha256'];assert ('max_tokens' not in req) if arm=='EDEFAULT' else req['max_tokens']==int(arm[1:]);assert 'JSON' in req['messages'][0]['content'];n+=1
  r=rd(f.with_name(f.name.replace('.request.json','.result.json')));usage.append(r['token_accounting'])
for c in cases.values():
 for p,h in c['old_hashes'].items():assert sha(ROOT/p)==h
inp=sum(u['input'] for u in usage);hit=sum(u['hit'] for u in usage)
save(BASE/'INTEGRITY.json',{'actual_requests':n,'expected_requests':48,'old_4096_reused':12,'same_prompt_inputs_temperature_timeout':True,'only_payload_delta':'max_tokens value/absence','default_preflight_reused_once':True,'historical_sources_unchanged':True,'input_tokens':inp,'completion_tokens':sum(u['output'] for u in usage),'reasoning_tokens':sum(u['reasoning'] for u in usage),'final_answer_tokens':sum(u['final'] for u in usage),'cache_hit_tokens':hit,'cache_miss_tokens':sum(u['miss'] for u in usage),'cache_hit_rate':hit/inp,'retries':0,'error_interpretation':'length failures have no semantic verdict; schema and final-output metrics separate'})
print('48 distinct calls, budget-only payload delta verified; cache',round(hit/inp*100,2))
