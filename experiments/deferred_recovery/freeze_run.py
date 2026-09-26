import hashlib,json,subprocess
from pathlib import Path
from run import TOP,ROOT,initial,actor_items
from runtime import write,read,sha,now,head,CONFIG

def bigsha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def main():
 assert not (TOP/'freeze.json').exists()
 for p,h in read(TOP/'analysis/HISTORICAL_HASHES.json').items():assert sha(ROOT/p)==h,p
 assert read(TOP/'tool_audit/RESULTS.json')['status']=='PASS'
 req=actor_items(initial(),0);write(TOP/'r1/requests.json',req)
 binaries=sorted((ROOT/'BCPlus/indexes/qwen3-embedding-8b').glob('*.pkl'))+[ROOT/'BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite']+sorted(Path('/data/model/Qwen3-Embedding-8B').glob('*.safetensors'))+sorted(Path('/data/model/Qwen3-Embedding-8B').glob('*.json'))
 big={}
 for p in binaries:
  st=p.stat();big[str(p)]={'sha256':bigsha(p),'size':st.st_size,'mtime_ns':st.st_mtime_ns};print('hashed',p.name,flush=True)
 paths=list(TOP.glob('*.py'))+list(TOP.glob('*.md'))+list((TOP/'prompts').glob('*'))+list((TOP/'schemas').glob('*'))
 paths+=list((TOP/'bank').glob('*.json'))+list((TOP/'bank').glob('*.md'))+[TOP/'tool_audit/run.py',TOP/'tool_audit/RESULTS.json',TOP/'r1/requests.json',TOP/'analysis/HISTORICAL_HASHES.json']
 paths+=[ROOT/p for p in ['llm_chat/search_find_agent.py','llm_chat/search_find_v3b_agent.py','llm_chat/agent.py','llm_chat/raw_windows.py','llm_chat/window_locator.py','llm_chat/window_units.py','BCPlus/scripts/search_bcplus.py','experiments/model_backend_deepseek/provider.json','experiments/goal_residual_control/harness_v2/contracts.py','experiments/goal_residual_control/harness_v2/UPDATER_RESPONSE_SCHEMA.json','experiments/goal_residual_control_v3/capability.py']]
 f={'git_head':head(),'utc':now(),'model':CONFIG['model'],'base_url':CONFIG['base_url'],'transport':'json_object','timeout_seconds':240,'max_retries':0,'workers':4,'actor_requests_first':14,'max_actor_total':28,'max_decisions':2,'max_actions_per_decision':1,'k':5,'device':'cuda:1','embedding_dtype':'float16','bank_gate':'INSUFFICIENT_BANK','label':'limited diagnostic, not confirmatory','files':{str(p.relative_to(ROOT)):sha(p) for p in paths},'binary_files':big,'request_sha256':{r['case_id']+':'+r['arm']:r['request_sha256'] for r in req}}
 write(TOP/'freeze.json',f)
 print('frozen14 first decisions; all adaptive code pinned',flush=True)
if __name__=='__main__':main()
