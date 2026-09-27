"""Commit inputs first, then create exclusive phase hash freeze. No consent creation."""
import argparse
from .common import *
from .run import jobs

def freeze(phase):
    assert phase in ('writer','admission')
    path=P/'e1_admission'/f'{phase.upper()}_FREEZE.json'
    if path.exists():raise FileExistsError(path)
    paths=git('ls-files','--',rel(P)).splitlines()
    assert paths and rel(P/'e1_admission'/f'{phase.upper()}_REQUESTS.json') in paths
    manifest={}
    for name in paths:
        p=ROOT/name;committed(p);manifest[name]=sha(p)
    extra=['llm_chat/search_find_agent.py','experiments/deferred_recovery/tools.py',
           'experiments/skeleton_state_alignment/prepare.py','experiments/contextual_subtraction_qualification/run.py',
           'experiments/minimal_need_multiquery/run.py','experiments/ephemeral_obligation_decomposition/source_units.py']
    for name in extra:committed(ROOT/name);manifest[name]=sha(ROOT/name)
    write(path,{'base':BASE,'phase':phase,'request_commit':git('rev-parse','HEAD'),'actual_requests':len(jobs(phase)),
                'provider':'deepseek','model':'deepseek-flash','max_retries':0,'max_concurrency':8,
                'files':manifest,'authorized_calls_at_freeze':0,'task_sha256':sha(P/'TASK.md'),
                'execution_condition':'TASK47: separate fresh explicit user authorization after exact requests committed/hash-frozen. No old approval reused.'})
    print('Freeze',rel(path),'sha256',sha(path),'actual_requests',len(jobs(phase)))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('phase',choices=['writer','admission']);freeze(p.parse_args().phase)
