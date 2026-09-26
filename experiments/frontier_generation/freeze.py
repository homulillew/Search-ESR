"""Build pre-call manifest; run once before committing it and submitting any request."""
from runtime import *

def main():
    base=TOP/'f1_state_sufficiency';assert not (base/'freeze.json').exists()
    bank=rd(TOP/'bank/CHECKPOINT_BANK.json')
    items=[item(c,a,r) for c in bank for a in ['H','S','SH'] for r in [1,2]]
    items.sort(key=lambda x:dg(['frontier-f1-order-20260926',x['id']]))
    wr(base/'requests.json',items)
    paths=[p for p in TOP.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
    # Historical source, prompts, validation and retrieval code pins. No tools execute in F1.
    old=['experiments/goal_residual_control/three_round_loop_v2/results.json',
         'experiments/goal_residual_control/transition_replan_v2/state_updates.json',
         'experiments/goal_residual_control/bank/SNAPSHOTS.json',
         'experiments/model_backend_deepseek/provider.json',
         'experiments/goal_residual_control_v3_1/prompts/state_updater_gap_conditioned.md']
    paths += [ROOT/p for p in old]
    paths += [p for d in ['llm_chat','search_engine','experiments/goal_residual_control/harness_v2'] if (ROOT/d).exists() for p in (ROOT/d).rglob('*.py')]
    files={str(p.relative_to(ROOT)):sha(p) for p in sorted(set(paths))}
    historical=subprocess.check_output(['git','ls-tree','-r','--name-only','9e4b48c'],cwd=ROOT,text=True).splitlines()
    hist={p:sha(ROOT/p) for p in historical if (ROOT/p).is_file()}
    wr(TOP/'historical_baseline_hashes.json',hist)
    files[str((TOP/'historical_baseline_hashes.json').relative_to(ROOT))]=sha(TOP/'historical_baseline_hashes.json')
    wr(base/'freeze.json',{'created_utc':now(),'construction_head':head(),
        'base_head':'9e4b48c197d4248e2ccf34850948761706252cfd',
        'execution_head_policy':'Freeze and all input files must be committed and match HEAD; each request journals exact run_head.',
        'provider':CONFIG,'transport':'chat/completions JSON mode; no schema sent to provider',
        'sample_count':144,'checkpoint_count':24,'qid_count':10,'arms':['H','S','SH'],'replicates':2,
        'horizon':1,'tool_calls':0,'max_retries':0,'workers':4,'timeout_seconds':240,
        'failure_policy':'All planned slots in denominator; no retry or replacement; auth latch; no existing journal overwrite.',
        'order':'sha256(frontier-f1-order-20260926,id)','file_hashes':files,
        'request_hashes':{x['id']:x['request_sha256'] for x in items},
        'binary_policy':'No retrieval in F1–F3. Frozen unchanged Deferred Recovery full corpus/index manifest remains authoritative; reverify before F4 if reached.'})
    print('Frozen',len(items),'requests;',len(hist),'historical files;',len(files),'input/code pins')

if __name__=='__main__':main()
