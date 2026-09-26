"""Read-only integrity checks on recorded experiment artifacts; no API calls."""
import json,hashlib,subprocess,datetime,collections,sqlite3
from pathlib import Path
P=Path(__file__).resolve().parent.parent;ROOT=P.parents[1]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
# Match request hash canonicalizer used by frozen runtime, not an independent guess.
import sys
sys.path.insert(0,str(P))
from runtime import digest as request_digest
h=read(P/'HISTORICAL_HASHES.json');bad=[p for p,s in h.items() if not (ROOT/p).exists() or sha(ROOT/p)!=s];assert not bad,bad
f=read(P/'freeze.json');assert all(sha(ROOT/p)==s for p,s in f['files'].items())
for p,s in f['binary_files'].items():
 st=Path(p).stat();assert (st.st_size,st.st_mtime_ns)==(s['size'],s['mtime_ns']),p
E=P/'exploration';ef=read(E/'freeze.json');assert all(sha(ROOT/p)==s for p,s in ef['files'].items())
counters={};schema_failures=[]
for name,paths in [('primary',sorted(P.glob('round*/*_events.jsonl'))),('exploration',sorted(E.glob('*_events.jsonl')))]:
 calls=0;statuses=collections.Counter();errors=collections.Counter()
 for path in paths:
  if path.name=='tool_events.jsonl':continue
  rows=[json.loads(x) for x in path.read_text().splitlines()];starts=[r for r in rows if r['kind']=='request_started'];ends=[r for r in rows if r['kind']=='completed'];assert len(starts)==len(ends),(path,len(starts),len(ends))
  st={(r['item']['case_id'],r['item']['request_sha256']):r for r in starts};assert len(st)==len(starts),path
  for r in ends:
   event=r['event'];it=event['item'];result=r['result'];assert (it['case_id'],it['request_sha256']) in st
   assert request_digest(it['request'])==it['request_sha256'];assert it['request']['model']=='deepseek-flash';assert event['run_head'] in [read(P/'RUN_STARTED.json')['head'],read(E/'RUN_STARTED.json')['head']]
   statuses[str(event.get('http_status'))]+=1;calls+=1
   if result.get('error'):errors[result['error']['category']]+=1;schema_failures.append({'phase':name,'case_id':it['case_id'],'category':result['error']['category']})
 counters[name]={'calls':calls,'http_statuses':dict(statuses),'errors':dict(errors)}
assert counters['primary']['calls']==404
assert counters['exploration']['calls']<=24
# Same prefix and schema; only appended policy paragraph differs from frozen historical control.
original=read(P/'round2/requests.json');changes=[]
for it in read(E/'REQUESTS.json'):
 old=next(x for x in original if x['case_id']==it['case_id']);a=old['request'];b=it['request']
 assert a['messages'][1:]==b['messages'][1:]
 assert b['messages'][0]['content']==a['messages'][0]['content']+(E/'PROMPT_ADDITION.md').read_text()
 assert {k:v for k,v in a.items() if k!='messages'}=={k:v for k,v in b.items() if k!='messages'}
 changes.append(it['case_id'])
# Every primary returned window and every emitted Claim has a semantic review.
cs=read(P/'RESULTS.json');ww=read(P/'analysis/WINDOW_REVIEW.json');cr=read(P/'analysis/CLAIM_REVIEW.json')
assert len(ww)==sum(len(d['tool']['observations']) for c in cs.values() for d in c['decisions'] if d['tool'])
assert len(cr)==sum(len(u['proposal']['output']['claims_to_add']) for c in cs.values() for u in c['updates'] if u['proposal']['output'])
db=sqlite3.connect(f'file:{ROOT}/BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite?mode=ro',uri=True);cache={};n=0
for cells in [cs,read(E/'RESULTS.json')]:
 for c in cells.values():
  assert len(c['decisions'])<=c['horizon']
  docs={d['doc_ref']:d for d in c['registry']['documents']}
  for w in c['registry']['windows']:
   did=docs[w['doc_ref']]['docid']
   if did not in cache:cache[did]=db.execute('select text from documents where docid=?',(did,)).fetchone()[0]
   assert cache[did][w['offset']:w['offset']+len(w['text'])]==w['text']
   assert hashlib.sha256(w['text'].encode()).hexdigest()==w['text_sha256'];n+=1
  for d in c['decisions']:
   o=d['actor']['output']
   if o:assert len(o['actions'])<=1
  for u in c['updates']:
   o=u['proposal']['output']
   if o:assert len(o['claims_to_add'])<=2
# Scan actual configured credential without ever writing/printing its value.
from dotenv import dotenv_values
key=dotenv_values(ROOT/'.env.deepseek').get('DEEPSEEK_API_KEY');assert key
leaks=[str(p.relative_to(ROOT)) for p in P.rglob('*') if p.is_file() and p.suffix!='.pyc' and key.encode() in p.read_bytes()];assert not leaks,leaks
report={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'historical_files_unchanged':len(h),'primary_frozen_files_unchanged':len(f['files']),'binary_identities_unchanged':len(f['binary_files']),'exploration_frozen_files_unchanged':len(ef['files']),'exact_prefix_policy_only_pairs':changes,'primary_windows_reviewed':len(ww),'primary_claims_reviewed':len(cr),'registered_windows_checked_against_actual_corpus':n,'unique_documents_checked':len(cache),'journals':counters,'retained_failures':schema_failures,'credential_scan':'clean','production_components':'unchanged','all_passed':True}
(P/'analysis/INTEGRITY_CHECK.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,indent=2))
