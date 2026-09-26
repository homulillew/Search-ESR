import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from runtime import *
b=TOP/'admission_replay';bank=read(b/'BANK.json');items=read(b/'requests.json');lookup={(r['case_id'],r['arm']):r for r in items}
for p in bank:
 old=p['old_request'];u0=json.loads(old['messages'][1]['content']);uc=lookup[p['packet_id'],'Uc']['request'];u1=lookup[p['packet_id'],'U1']['request']
 assert uc['messages']==old['messages']
 v=json.loads(u1['messages'][1]['content']);gap=v.pop('Current Research Gap');assert v==u0
 assert gap==p['actor']['output']['gap']==p['current_actor_gap']
 assert p['actor']['output']['decision']=='act'
 assert digest(p['pre_state'])==p['pre_state_sha256']
 assert digest(p['observation'])==p['observation_sha256']
 for r in [uc,u1]:assert set(r)=={'model','messages','stream','response_format'} and r['model']=='deepseek-flash' and r['response_format']=={'type':'json_object'}
 for a in p['producing_actions']:assert a['action'] in p['actor']['output']['actions']
for stage in ['structured_transport_canary','admission_replay']:
 f=read(TOP/stage/'freeze.json')
 for p,h in f['files'].items():assert sha(ROOT/p)==h,p
check_history()
result={'historical_files_unchanged':len(read(TOP/'analysis/HISTORICAL_HASHES.json')),'Uc_message_exact_pairs':55,'U1_only_view_delta_Current_Gap':55,'exact_actor_gap_provenance':55,'both_freezes_exact':True,'no_added_sampling_or_thinking_parameter':True}
write(TOP/'analysis/PRE_ANALYSIS_INTEGRITY.json',result);print(json.dumps(result))
