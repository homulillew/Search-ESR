"""No live calls. Freeze all stage inputs before committing the run."""
import json,subprocess,sys,hashlib
from pathlib import Path
TOP=Path(__file__).resolve().parent;ROOT=TOP.parents[1];sys.path.insert(0,str(ROOT))
from experiments.evidence_scope_localization.runtime import read,write,sha,digest,now,head,prepare
def main():
 labels=read(TOP/'bank/LABELS.json')
 manifest=[{'case_id':r['case_id'],'arm':a,'policy_arm':a,**({'oracle':r['gold_doc_ref']} if a=='A3' else {})} for r in labels for a in (['A0','A1','A2'] if r['bank']=='N' else ['A0','A1','A2','A3'])]
 write(TOP/'r1/MANIFEST.json',manifest);prepare('r1')
 tracked=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0');historical={}
 for p in tracked:
  if p.startswith('experiments/') and not p.startswith('experiments/evidence_scope_localization/') and (ROOT/p).is_file():historical[p]=sha(ROOT/p)
 write(TOP/'HISTORICAL_HASHES.json',historical)
 selected=[p for p in TOP.rglob('*') if p.is_file() and '__pycache__' not in str(p) and p.suffix not in ['.pyc'] and p.name not in ['FREEZE.json','FROZEN_STATE.md']]
 deps=['experiments/model_backend_deepseek/provider.json','experiments/goal_residual_control_v3/capability.py','experiments/bcplus_verification/runtime.py','experiments/deferred_recovery/tools.py','BCPlus/scripts/search_bcplus.py','llm_chat/agent.py','llm_chat/search_find_agent.py','llm_chat/raw_windows.py','llm_chat/window_locator.py','llm_chat/window_units.py','experiments/bcplus_verification/prompts/writer.md']
 selected.extend(ROOT/p for p in deps if (ROOT/p).exists())
 binaries=list((ROOT/'BCPlus/indexes/qwen3-embedding-8b').glob('*.pkl'))+[ROOT/'BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite']+list(Path('/data/model/Qwen3-Embedding-8B').glob('*.safetensors'))
 f={'utc':now(),'parent_head':head(),'remote_base':subprocess.check_output(['git','rev-parse','origin/experiment/bcplus-discovery-verification'],text=True).strip(),'provider_model':read(ROOT/'experiments/model_backend_deepseek/provider.json'),'sample_count':{'K':10,'N':8,'challenge':5,'trajectories':84},'horizon':2,'max_retries':0,'files':{str(p.relative_to(ROOT)):sha(p) for p in selected},'binary_files':{str(p):{'size':p.stat().st_size,'mtime_ns':p.stat().st_mtime_ns} for p in binaries},'integer_gates':{'K_A1_at_least':8,'K_A1_minus_A0_at_least':2,'N_A1_minus_A0_at_least':0,'N_A1_local_lock_at_most':0,'R2_trigger_A3_at_most':7,'A3_gray':8,'A3_usable_at_least':9},'adaptive_request_freeze':'exact bytes and hash saved before every call; frozen deterministic builder'}
 write(TOP/'r1/FREEZE.json',f)
 (TOP/'FROZEN_STATE.md').write_text('# Frozen state\n\n'+f'Base `{f["remote_base"]}`; preregistration parent `{head()}`.\n\n'+'R1 immutable manifest: [r1/FREEZE.json](r1/FREEZE.json). The committed run HEAD is recorded in r1/STARTED.json and every request freeze.\n\n'+'K=10/5 qids, N=8/8 qids, challenge=5; 84 trajectories, horizon=2, max_retries=0. K sampling shortfall is explicit.\n\n'+'All selection, source annotations, Need/query lexicons, rubric, prompts, response/tool schemas and historical prefixes are hashed before API calls. Corpus/index/model binary sizes and nanosecond mtimes are frozen; known documents carry full SHA256. No historical artifact may change.\n')
 print('frozen',len(f['files']),'inputs;',len(historical),'historical files')
if __name__=='__main__':main()
