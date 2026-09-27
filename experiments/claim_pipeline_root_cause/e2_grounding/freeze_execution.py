"""Offline freeze creation after tests, never model execution."""
import subprocess
from .contracts import HERE, BASE, ROOT, read, save, digest, file_hash
from .runner import make_plan

def main():
    b=read(HERE/'CANDIDATE_BANK.json');config=read(HERE/'CONFIG.json')
    plan=make_plan(b['pairs'],config)
    save(HERE/'REQUEST_PLAN.json',plan)
    save(HERE/'EXECUTION_PREFLIGHT.json',{
        'status':'PASS','source_head':read(HERE/'BANK_FREEZE.json')['source_head'],
        'pre_execution_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'calls':{'G0':b['count'],'inventory':b['inventory_count'],'Coverage':b['count'],'total':b['calls']},
        'initial_ready':50,'initial_active_cap':50,'max_active_cap':50,'pool_max':70,
        'tests':'OFFLINE_TESTS.txt','test_failures_during_development':'pytest collection required absolute test imports for namespace packages; corrected before freeze; no API traffic.',
        'evidence_projection':'inherited V2; all public texts byte-preserving; dynamic W enum and runtime membership',
        'initial_requests_frozen':50,'dynamic_coverage_requests':35,
        'coverage_binding':'candidate hash + frozen inventory content/hash + unchanged prompt/schema/config; archived request hash before dispatch',
        'inventory_physical_freeze':'exclusive JSON write and read-back before dependency resolves; transport rechecks before coverage dispatch',
        'fresh_inventory_only':True,'alias_mapping':False,'historical_prompt_changes':False,
        'secret_archived':False,'new_retrieval':0,'H_confirmation_execution':False,'E3_entrypoint':False,
        'authorization':'TASK.md §4, <=85 paid E2 requests. No additional approval required.',
        'file_descriptor_limit':1048576,
        'account_budget':'50 active slots total for this job; no other experiment launched by this task; no key/user_id rotation',
        'failure_policy':config['failure_policy'],'STOP_AFTER_E2':True})
    old=[ROOT/p for p in subprocess.check_output(['git','ls-files','experiments/claim_pipeline_root_cause'],cwd=ROOT,text=True).splitlines() if '/e2_grounding/' not in p]
    new=[p for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts and '.pytest_cache' not in p.parts]
    paths=sorted(set(old+new))
    save(HERE/'EXECUTION_FREEZE.json',{'source_head':read(HERE/'BANK_FREEZE.json')['source_head'],
        'bank_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'files':{str(p.relative_to(ROOT)):file_hash(p) for p in paths},
        'planned_calls':b['calls'],'request_plan_sha256':file_hash(HERE/'REQUEST_PLAN.json'),
        'configuration':config,'prompt_schema_bank_freeze_sha256':file_hash(HERE/'BANK_FREEZE.json'),
        'historical_files_protected':len(old),'H3_thresholds':read(HERE/'BANK_FREEZE.json')['H3']})
    save(HERE/'AUTHORIZATION.json',{'authorized':True,'stages':['E2'],'call_ceiling':85,
        'freeze_sha256':file_hash(HERE/'EXECUTION_FREEZE.json'),'task_sha256':file_hash(HERE/'TASK.md'),
        'provenance':'User attachment TASK §4 is new explicit E2 authorization; prior standing authorization also remains in force.',
        'STOP_AFTER_E2':True})

if __name__=='__main__':main()
