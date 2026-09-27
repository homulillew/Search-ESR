"""Replay frozen experiment/raw usage and provenance without paid calls."""
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from .common import *
from . import run as e1
from . import bootstrap_runtime as br
from .score import calculate,assert_review
from experiments.skeleton_state_alignment.run import accounting

def main():
 historical=verify_history();assert_review();assert read(P/'e1_residualization/METRICS.json')==calculate()
 for path in [P/'FREEZE.json',P/'e2_bootstrap/FREEZE.json',P/'e2b_escalation/probe_generation/FREEZE.json',P/'e2b_escalation/FREEZE.json',P/'analysis/oracle_diagnostic/FREEZE.json']:
  committed(path)
  for p,h in read(path)['files'].items():assert sha(ROOT/p)==h,p
 for p,h in read(P/'analysis/E1_EXECUTED_FILES.json').items():assert sha(ROOT/p)==h,p
 stages=['e1_residualization','e2_bootstrap','e2b_escalation/probe_generation','e2b_escalation'];allrows=[];accounts={}
 for stage in stages:
  d=P/stage;jobs=read(d/'SCHEDULE.json');rs=e1.load_rows() if stage==stages[0] else br.load_rows(stage);mapping={j['id']:j for j in jobs}
  for r in rs:
   j=mapping[r['id']];stem=d/'calls'/r['id'];assert r['request_sha256']==j['request_sha256']
   if r['attempted']:
    actual=read(stem.with_suffix('.request.json'));assert actual['request']==j['request'];assert 'max_tokens' not in actual['request']
    raw=read(stem.with_suffix('.response.json'));parsed=(e1.parse if stage==stages[0] else br.parse)(raw['status'],raw['body'],j)
    for k,v in parsed.items():assert r[k]==v,(stage,r['id'],k)
   else:assert not stem.with_suffix('.attempt.json').exists()
  acc=read(d/'ACCOUNTING.json')
  for k,v in accounting(rs).items():assert acc[k]==v,(stage,k)
  assert len(list((d/'calls').glob('*.attempt.json')))==sum(r['attempted'] for r in rs)
  accounts[stage]=acc;allrows+=rs
 assert read(P/'e2_bootstrap/SCHEDULE.json')==br.build_e2()
 # No future/Gold fields in requests; exact input constructors and stage hashes bound above.
 for j in read(P/'e2b_escalation/probe_generation/SCHEDULE.json'):
  v=json.loads(j['request']['messages'][1]['content']);assert set(v)=={'Original Question','Parent Requirement','Previous probe objective','Previous query','Mechanical result summary'}
  s=v['Mechanical result summary'];assert set(s)=={'returned documents','any new claim admitted','new binding found'}
  assert s['any new claim admitted']==s['new binding found']=='no'
  assert all(set(x)=={'doc_ref','title'} for x in s['returned documents'])
 backend=read(P/'e2_bootstrap/BACKEND.json')
 for p,h in backend['code_sha256'].items():assert sha(ROOT/p)==h,p
 def check_asset(item):
  p,expected=item;s=Path(p).stat();assert (s.st_size,s.st_mtime_ns)==(expected['size'],expected['mtime_ns']);assert sha(p)==expected['sha256'],p
 with ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(check_asset,backend['assets'].items()))
 db=sqlite3.connect(f'file:{ROOT}/BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite?mode=ro',uri=True);cache={};searches=0;windows=0
 for stage in ['e2_bootstrap','e2b_escalation']:
  d=P/stage;rs={r['id']:r for r in br.load_rows(stage)};m=read(d/'METRICS.json');key=read(d/'review/KEY.json');judgments={key[r['review_id']]:r for r in read(d/'review/JUDGMENTS.json')}
  seal=read(d/'review/SEAL.json')
  for p,h in seal['files'].items():assert sha(ROOT/p)==h,p
  for scored in m['rows']:
   for k,v in judgments[scored['id']].items():assert scored[k]==v
  for arm,vals in m['arms'].items():
   ar=[r for r in m['rows'] if r['arm']==arm]
   for k in ['new_material','binding','direct','bridge','real_no_gain','query_drift','candidate_commitment','objective_only_rule_violation','retrieval_valid']:
    assert vals[k]==metric(sum(bool(r[k]) for r in ar),len(ar))
  for ident,r in rs.items():
   ret=read(d/'retrieval'/f'{ident}.json')
   if not ret['attempted']:assert not r['valid_output'];continue
   searches+=1;t=ret['tool'];assert t['action']=={'tool':'search','query':r['output']['query'],'k':5};assert not ret['error'];assert len(t['observations'])==5
   for w in t['audit']['raw_result']:
    docid=w['docid']
    if docid not in cache:cache[docid]=db.execute('select text,url from documents where docid=?',(docid,)).fetchone()
    txt,url=cache[docid];assert hashlib.sha256(txt.encode()).hexdigest()==w['document_sha256'];assert txt[w['offset']:w['end_char']]==w['text'];assert url==w['url'];assert w['text_tokens']+w['title_tokens']<=400;windows+=1
 db.close()
 assert searches==21 and windows==105 and sum(r['attempted'] for r in allrows)==138
 assert read(P/'analysis/oracle_diagnostic/COMPLETED.json')=={'searches':2,'known_source_previews':2,'model_calls':0,'errors':0}
 combined=accounting(allrows);write(P/'analysis/EXECUTION_ACCOUNTING.json',{'stages':accounts,'combined':combined,'primary_searches':21,'oracle_searches':2,'oracle_known_document_previews':2,'find_open_calls':0,'writer_calls':0,'model_calls':138,'max_retries':0,'reasoning_included_in_completion':True,'currency_cost':'Unavailable; no guessed price or double-counted reasoning tokens.'})
 write(P/'analysis/INTEGRITY.json',{'status':'PASS','head_before_final_audit_commit':git('rev-parse','HEAD'),'historical_tracked_files_unchanged':historical,'all_stage_freezes_unchanged':True,'E1_scores_exact_replay':True,'all_model_raw_parse_and_usage_exact_replay':True,'model_attempts':138,'new_model_retry_attempts':0,'original_retrieval_code_unchanged':True,'binary_assets_full_sha256_rechecked':len(backend['assets']),'primary_searches':searches,'primary_raw_windows_substring_hash_budget_verified':windows,'oracle_separate':True,'persistent_fields_added':0,'future_gold_input_fields':0,'automatic_rollout':False})
 print(json.dumps({'status':'PASS','attempts':138,'historical_unchanged':historical,'combined':combined},indent=2))
if __name__=='__main__':main()
