import sys,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from runtime import *
check_history();ledger=[];usage_rows=[]
for stage,tag in [('structured_transport_canary','canary'),('admission_replay','paired'),('admission_exploration','U2')]:
 b=TOP/stage;f=read(b/'freeze.json')
 for p,h in f['files'].items():assert sha(ROOT/p)==h,p
 planned=read(b/'requests.json');events=[json.loads(l) for l in (b/(tag+'_events.jsonl')).open()]
 starts=[e for e in events if e['kind']=='request_started'];ends=[e for e in events if e['kind']=='completed']
 assert len(starts)==len(ends)==len(planned)
 keyed={(r['case_id'],r['arm']):r for r in planned};assert len(keyed)==len(planned)
 assert len({(e['item']['case_id'],e['item']['arm']) for e in starts})==len(planned)
 for e in ends:
  it=e['event']['item'];r=e['result'];assert it==keyed[it['case_id'],it['arm']]
  assert digest(it['request'])==it['request_sha256']==r['request_sha256']
  assert e['event']['response']['model']=='deepseek-flash'
  assert json.loads(e['event']['response_text'])==e['event']['response']
  if r['output'] is not None:
   assert decode(e['event']['response'],it['mode'])==r['output']
   messages=it['request'].get('input',it['request'].get('messages'));validate(r['output'],it['kind'],json.loads(messages[1]['content']))
  usage_rows.append(r['usage'])
 ledger.append({'stage':stage,'planned':len(planned),'attempted_once':len(starts),'raw_responses':len(ends),'structural_valid':sum(e['result']['structural_valid'] for e in ends),'harness_valid':sum(e['result']['harness_valid'] for e in ends),'failures':dict(collections.Counter(e['result']['error']['category'] for e in ends if e['result']['error'])),'freeze_head':f['git_head'],'freeze_sha256':sha(b/'freeze.json')})
u={k:sum(v[k] for v in usage_rows) for k in ['input','output','hit','miss','reasoning']};assert u['hit']+u['miss']==u['input'];u['cache_rate']=u['hit']/u['input'];u['total']=u['input']+u['output']
# Confirm complete original and exploratory semantic review coverage, without modifying either.
for stage,arms in [('admission_replay',['Uc','U1']),('admission_exploration',['U2'])]:
 b=TOP/stage;reviews=read(b/'REVIEWS.json')
 rows=[r for arm in arms for r in read(b/(arm+'_outputs.json'))]
 for r in rows:
  if r['output'] is not None:
   uid=digest(['admission-review',r['case_id'],r['output']])[:16];assert uid in reviews
   assert [c['statement'] for c in reviews[uid]['claims']]==r['output']['claims_to_add']
report={'status':'PASS','protected_baseline_files':len(read(TOP/'analysis/HISTORICAL_HASHES.json')),'stages':ledger,'calls':len(usage_rows),'usage':u,'research_tools':0,'G4_G5':'not_run_original_gate_failed','semantic_review':'single Codex; not independently replicated','no_retry_no_repair_raw_identity':True}
write(TOP/'analysis/FINAL_INTEGRITY.json',report);print(json.dumps(report,indent=2))
write(TOP/'RUN_STATUS.json',{'status':'complete_with_failed_confirmatory_admission_gate','canary':'completed_json_fallback_selected','admission':'completed_FAIL_RECALL_TRADEOFF','exploration':'completed_mixed_positive','G4':'not_run','G5':'not_run','pending_model_calls':0})
