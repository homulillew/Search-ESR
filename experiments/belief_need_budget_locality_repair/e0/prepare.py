"""Mechanical selection from actual old length failures; no new model calls."""
import json,hashlib,itertools,subprocess,collections
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];OLD=ROOT/'experiments/belief_need_convergence'
def rd(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dg(x):return hashlib.sha256(json.dumps(x,sort_keys=True).encode()).hexdigest()
def wr(p,x):
 with p.open('x') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
labels={r['case_id']:r for r in rd(OLD/'bank/LABELS.json')};rows=[]
for arm,folder in [('P1','round_0'),('P5','round_1')]:
 pool=[]
 for path in sorted((OLD/folder/'calls').glob(f'*_{arm}.result.json')):
  r=rd(path)
  if not r.get('error') or r['error']['category']!='length':continue
  cid=r['case_id'];l=labels[cid];group='no_H' if 'U1' in l['strata'] else 'strong_H' if any(s in l['strata'] for s in ['U3','U4']) else 'weak_H'
  reqpath=path.with_name(path.name.replace('.result.json','.request.json'));req=rd(reqpath)['request'];rawpath=path.with_name(path.name.replace('.result.json','.response.json'));raw=json.loads(rd(rawpath)['body']);assert raw['choices'][0]['finish_reason']=='length';assert req['max_tokens']==4096
  pool.append({'case_id':cid,'qid':l['qid'],'old_arm':arm,'group':group,'strata':l['strata'],'request':req,'old_result_path':str(path.relative_to(ROOT)),'old_request_path':str(reqpath.relative_to(ROOT)),'old_response_path':str(rawpath.relative_to(ROOT)),'old_hashes':{str(p.relative_to(ROOT)):sha(p) for p in [path,reqpath,rawpath]}})
 eligible=[c for c in itertools.combinations(pool,6) if collections.Counter(r['group'] for r in c)=={'no_H':2,'weak_H':2,'strong_H':2} and len({r['qid'] for r in c})>=4]
 assert eligible
 chosen=min(eligible,key=lambda c:(-len({r['qid'] for r in c}),dg(['budget-locality-repair-v1',arm,[r['case_id'] for r in c]])))
 rows.extend(chosen)
for i,r in enumerate(rows,1):r['calibration_id']=f'C{i:02}'
wr(P/'e0/CASES.json',rows)
subsets=[c for c in itertools.combinations(rows,3) if len({r['old_arm'] for r in c})==2 and len({r['group'] for r in c})==3 and len({r['qid'] for r in c})==3]
sub=min(subsets,key=lambda c:dg(['default-preflight-v1',[r['calibration_id'] for r in c]]))
wr(P/'e0/SELECTION.json',{'rule':'Exactly 6 previous P1 and 6 previous P5 actual length failures. Each arm: two No-H, two weak-H, two strong-H; at least four qids, maximize qids then fixed-seed SHA256 tie break. No expected/new answer or outcome used.','cases':[r['calibration_id'] for r in rows],'qids':sorted({r['qid'] for r in rows}),'default_preflight':[r['calibration_id'] for r in sub],'preflight_rule':'Three fixed representatives, three qids, one each H group, both old prompts represented. They are also the mandatory historical-default control. Same default output is reused if EDEFAULT expands to all12.'})
wr(P/'CONFIG.json',{'provider':'deepseek','model':'deepseek-flash','base_url':'https://api.deepseek.com','credential_file':'.env.deepseek','credential_field':'DEEPSEEK_API_KEY','timeout_seconds':240,'max_retries':0,'max_workers':8,'temperature_need':0,'stream':False,'response_format':{'type':'json_object'},'primary_budget_preference':'omit max_tokens; validate before selecting','semantic_retries':0,'tool_calls_in_need_evaluation':0})
paths=subprocess.check_output(['git','ls-files','experiments'],cwd=ROOT,text=True).splitlines();wr(P/'HISTORICAL_HASHES.json',{f:sha(ROOT/f) for f in paths if (ROOT/f).is_file()})
# Read historical request metadata and one documented cap-reaching response only.
proof={}
for line in (ROOT/'experiments/bcplus_verification/round2/actor_events.jsonl').open():
 e=json.loads(line)
 if e.get('kind')=='completed' and e['result']['case_id']=='D10':
  proof={'path':'experiments/bcplus_verification/round2/actor_events.jsonl','request_keys':list(e['event']['item']['request']),'request_has_max_tokens':'max_tokens' in e['event']['item']['request'],'usage':e['result']['usage'],'finish_reason':e['event']['response']['choices'][0]['finish_reason'],'elapsed_seconds':e['result']['elapsed_seconds']}
wr(P/'e0/HISTORICAL_BUDGET_PROOF.json',proof)
print([(r['calibration_id'],r['case_id'],r['old_arm'],r['qid'],r['group']) for r in rows]);print('default preflight',[r['calibration_id'] for r in sub])
