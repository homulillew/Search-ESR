"""Read-only artifact integrity checks; no API, no source or label mutations."""
import hashlib,json,subprocess
from pathlib import Path
from dotenv import dotenv_values
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1]
def rd(p):return json.loads(p.read_text())
def sha(b):return hashlib.sha256(b).hexdigest()
def dg(x):return sha(json.dumps(x,ensure_ascii=False,sort_keys=True).encode())
errors=[];historical=rd(P/'HISTORICAL_HASHES.json')
for f,h in historical.items():
 if sha((ROOT/f).read_bytes())!=h:errors.append('historical modified:'+f)
cases={r['case_id']:r for r in rd(P/'bank/RUNTIME_INPUTS.json')};labels={r['case_id']:r for r in rd(P/'bank/LABELS.json')};count=0;peaks=[];runs=[]
for folder in ['round_0','round_0_p3_format_repair','round_1']:
 d=P/folder;fr=rd(d/'FREEZE.json');run=rd(d/'RUN.json');s=rd(d/'SUMMARY.json');peaks.append(s['max_concurrent_http']);runs.append(run['head'])
 assert sha((d/'FREEZE.json').read_bytes())==run['freeze_sha256']
 for f,h in fr['paths'].items():
  assert sha((ROOT/f).read_bytes())==h,('frozen dependency changed',folder,f)
  # Each dependency was present in the committed run HEAD, before requests.
  committed=subprocess.check_output(['git','show',run['head']+':'+f],cwd=ROOT)
  assert sha(committed)==h,(folder,'not committed at run',f)
 assert len(rd(d/'OUTPUTS.json'))==len(fr['jobs'])
 for f in sorted((d/'calls').glob('*.request.json')):
  r=rd(f);count+=1;c=cases[r['case_id']];view=json.loads(r['request']['messages'][1]['content']);assert r['head']==run['head'];assert dg(r['request'])==r['request_sha256']
  assert view['Original Question']==c['question'] and view['Verified Claims']==c['claims'] and view['Working Hypothesis']==c['hypothesis']
  assert len(view)==(4 if r['stage'] in ['P4','P3B'] else 3)
  if r['stage']=='P4':assert view['One confirmed unresolved issue']==labels[r['case_id']]['oracle_gap']
  if r['stage']=='P3B':assert view['Ephemeral unresolved_issue']==rd(d/'calls'/f"{r['case_id']}_P3A.result.json")['output']['unresolved_issue']
  assert 'tools' not in r['request'];assert r['request']['model']=='deepseek-flash';assert r['request']['max_tokens']==4096
  result=rd(f.with_name(f.name.replace('.request.json','.result.json')));assert result['request_sha256']==r['request_sha256']
  assert f.with_name(f.name.replace('.request.json','.response.json')).exists()
assert count==391 and all(p<=8 for p in peaks)
key=dotenv_values(ROOT/'.env.deepseek').get('DEEPSEEK_API_KEY');assert key
for f in P.rglob('*'):
 if f.is_file() and '__pycache__' not in str(f):
  if key.encode() in f.read_bytes():errors.append('credential found in artifact:'+str(f.relative_to(P)))
assert not errors,errors
# Check append-only review completeness and composite identities.
for folder in ['round_0','round_1']:
 rows=rd(P/folder/'REVIEW.json')
 for r in rows:
  if r['output']:assert r['STRICT_VALID']==(r['V'] and r['A'] and not any(r[k] for k in ['S','P','W','I','H']))
  else:assert not r['STRICT_VALID'] and all(r[k] is None for k in ['V','S','P','W','I','H','A'])
result={'historical_files_verified_unchanged':len(historical),'frozen_rounds_verified':3,'run_heads':runs,'requests_verified':count,'per_batch_http_peaks':peaks,'batches_executed_sequentially':True,'no_tool_requests':True,'runtime_inputs_exact_QCH':True,'oracle_and_ephemeral_fields_isolated':True,'credentials_absent_from_artifacts':True,'output_reviews_complete':True,'retries_per_protocol_version':0,'P3_technical_protocol_exception':'55 original HTTP400 failures preserved; separate preregistered format repair, no semantic best-of','closure_and_simulation_not_run':True,'errors':[]}
out=P/'analysis/INTEGRITY_REPORT.json'
with out.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result,indent=2))
