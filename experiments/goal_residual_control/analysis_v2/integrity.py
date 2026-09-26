from progress import *
import subprocess
ROOT=TOP.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run():
 old=read(TOP/'harness_v2/HISTORICAL_ARTIFACT_HASHES.json');old_bad=[p for p,h in old.items() if sha(ROOT/p)!=h];fs={}
 for s in ['research_decision_v2','one_step_acquisition_v2','transition_replan_v2','three_round_loop_v2']:
  f=read(TOP/s/'freeze.json');fs[s]={'frozen_git_head':f['git_head'],'run_started_head':read(TOP/s/'run_started.json')['head'],'frozen_files':len(f['files']),'mismatches':[p for p,h in f['files'].items() if sha(ROOT/p)!=h],'request_hash_matches':sha(TOP/s/'REQUESTS.json')==f['requests_sha256']}
 dup=[];request_bad=[];calls=0;source_bad=[];models=collections.Counter()
 for stage in ['research_decision_v2','transition_replan_v2','three_round_loop_v2']:
  for p in (TOP/stage).glob('*_events.jsonl'):
   es=[json.loads(l) for l in p.open()];started=collections.Counter((e['item']['case_id'],e['item']['arm']) for e in es if e['kind']=='request_started');dup.extend([str(p)+':'+str(k) for k,v in started.items() if v>1])
   for e in es:
    if e['kind']!='completed' or 'event' not in e:continue
    ev=e['event'];calls+=1;r=ev['request'];h=hashlib.sha256(json.dumps(r,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
    if h!=ev['request_sha256']:request_bad.append(str(p))
    if ev.get('response'):models[ev['response']['model']]+=1
 for stage,fn in [('one_step_acquisition_v2','outputs.json'),('transition_replan_v2','tool_outputs.json')]:
  for r in read(TOP/stage/fn):
   for a in r['actions']:
    for w in a['observations']:
     if not w.get('text') or not w.get('window_ref') or not w.get('doc_ref'):source_bad.append([stage,r['case_id']])
 loop=read(TOP/'three_round_loop_v2/results.json');loop_bad=[];tool_errors=[]
 for key,c in loop.items():
  if len(c['decisions'])>3:loop_bad.append([key,'horizon'])
  for d in c['decisions']:
   if len(d['actions'])>2:loop_bad.append([key,'batch'])
   for a in d['actions']:
    if a.get('error'):tool_errors.append([key,a['error']])
    for w in a['observations']:
     if not w.get('text') or not w.get('window_ref') or not w.get('doc_ref'):source_bad.append(['G5',key])
 report={'historical_files_checked':len(old),'historical_mismatches':old_bad,'stage_freezes':fs,'duplicate_submissions_within_batch':dup,'request_hash_mismatches':request_bad,'model_calls_archived':calls,'response_model_names':dict(models),'observations_missing_provenance_fields':source_bad,'G5_cells':len(loop),'G5_budget_violations':loop_bad,'G5_tool_errors':tool_errors,'branch':subprocess.check_output(['git','branch','--show-current'],text=True).strip(),'scope':'No resampling; adaptive successive rounds may legitimately reuse an identical request. No claim of stochastic output reproducibility. Old G1/G2/FINAL and all frozen backend files must match exact bytes.'}
 assert not old_bad and not dup and not request_bad and not source_bad
 assert len(loop)==30 and not loop_bad
 assert all(not x['mismatches'] and x['request_hash_matches'] for x in fs.values())
 write(TOP/'INTEGRITY_CHECKS_V2.json',report);return report
if __name__=='__main__':print(json.dumps(run(),indent=2))
