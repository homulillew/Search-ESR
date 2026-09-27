"""Zero-network validation, immutable request freeze, and preparation accounting."""
import subprocess,sys
from .common import *
from .inputs import build_schedule

def main():
 assert not (P/'AUTHORIZATION_E1.json').exists() and not (P/'e1_support_alignment/calls').exists()
 for name in ('SELECTION_FREEZE.json','e0_reference/GOLD_FREEZE.json'):
  frozen=read(P/name);committed(P/name)
  for f,h in frozen['files'].items():assert sha(ROOT/f)==h;committed(ROOT/f)
 count=verify_history();schedule=read(P/'e1_support_alignment/SCHEDULE.json');assert schedule==build_schedule() and len(schedule)==96
 tests=subprocess.run([sys.executable,'-m','unittest','experiments.claim_requirement_support_alignment.test_harness','-v'],cwd=ROOT,text=True,capture_output=True)
 assert tests.returncode==0,tests.stdout+tests.stderr
 # Replay measurement only on clearly synthetic fixtures, never report these as real metrics.
 from .test_harness import HarnessTests
 from .score import aggregate
 HarnessTests.setUpClass();fixture=HarnessTests();a=aggregate(fixture.rows(),fixture.refs);b=aggregate(fixture.rows(),fixture.refs);assert a==b
 write(P/'analysis/PREPARATION_VALIDATION.json',{'status':'PASS','head_before_request_freeze_commit':git('rev-parse','HEAD'),'tests_command':'python -m unittest experiments.claim_requirement_support_alignment.test_harness -v','tests_exit':tests.returncode,'test_output':tests.stdout+tests.stderr,'synthetic_only_score_replay_sha256':digest(a),'score_replay_deterministic_on_synthetic_fixture':True,'real_model_score_replay':'NOT_AVAILABLE_NO_CALLS','historical_files_unchanged':count,'schedule_reconstruction_exact':True,'model_calls':0,'network_calls_by_experiment':0})
 write(P/'analysis/PREPARATION_ACCOUNTING.json',{'status':'PREPARED_NOT_EXECUTED','E1_planned':96,'E1_attempted':0,'E2_planned_conditional_slots':192,'E2_requests_frozen':0,'E2_attempted':0,'observed_tokens':0,'cache_hit_rate':None,'cost':None,'paid_model_calls':0,'no_retries':True,'failures':'none attempted; no model performance assessed'})
 # Dynamic post-run artifacts are written later; initial status files are frozen snapshots.
 files=sorted(p for p in P.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name not in ('FREEZE.json','INTEGRITY.json'))
 write(P/'FREEZE.json',{'stage':'E1','base_head':BASE,'gold_commit':git('rev-parse','HEAD'),'head_before_request_freeze_commit':git('rev-parse','HEAD'),'selection_freeze_sha256':sha(P/'SELECTION_FREEZE.json'),'gold_freeze_sha256':sha(P/'e0_reference/GOLD_FREEZE.json'),'schedule_sha256':sha(P/'e1_support_alignment/SCHEDULE.json'),'provider':'deepseek','model':'deepseek-flash','sample_count':24,'replicates':2,'horizon':1,'actual_E1_requests':96,'max_retries':0,'maximum_concurrency':8,'authorization':'NONE: new explicit user approval required under TASK20','E2':'not requested/not authorized; conditional192 planned slots, separate freeze and approval','files':{rel(p):sha(p) for p in files}})
 write(P/'analysis/INTEGRITY.json',{'status':'PASS_PREPARATION_ONLY','historical_files_unchanged':count,'previous_experiments_unchanged':True,'frozen_requests_unchanged':schedule==build_schedule(),'gold_reference_unchanged':True,'selection_unchanged':True,'score_replay_deterministic':'synthetic fixtures only; real-output replay pending E1','freeze_sha256':sha(P/'FREEZE.json'),'all_frozen_files_match':all(sha(ROOT/f)==h for f,h in read(P/'FREEZE.json')['files'].items()),'model_calls':0})
 print(json.dumps({'historical_files_unchanged':count,'E1_actual_frozen_requests':len(schedule),'model_calls':0,'freeze_sha256':sha(P/'FREEZE.json')},indent=2))
if __name__=='__main__':main()
