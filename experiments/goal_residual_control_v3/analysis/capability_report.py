"""Deterministic capability accounting; no provider calls, no output mutation."""
import hashlib,json,sys
from pathlib import Path
TOP=Path(__file__).resolve().parents[1];ROOT=TOP.parents[1]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')

def main():
 b=TOP/'structured_output_preflight';groups=[('responses_initial',b/'CAPABILITY_REQUESTS.json',b/'primary_outputs.json'),
 ('strict_initial',b/'CAPABILITY_REQUESTS.json',b/'fallback_outputs.json'),
 ('equivalent_schema',b/'equivalent_schema_probe/REQUESTS.json',b/'equivalent_schema_probe/outputs.json')]
 rows=[]
 for phase,rp,op in groups:
  req={r['id']:r for r in read(rp)}
  for e in read(op):
   r=req[e['id']];assert e['request_sha256']==r['request_sha256'];u=e.get('usage');cache=None;inp=None;out=None;reasoning=None;total=None
   if u:
    if r['surface']=='responses':inp=u['input_tokens'];cache=(u.get('input_tokens_details') or {}).get('cached_tokens');out=u['output_tokens'];reasoning=(u.get('output_tokens_details') or {}).get('reasoning_tokens');total=u['total_tokens']
    else:inp=u['prompt_tokens'];cache=u.get('prompt_cache_hit_tokens');out=u['completion_tokens'];reasoning=(u.get('completion_tokens_details') or {}).get('reasoning_tokens');total=u['total_tokens']
   semantic=None
   if e['id']=='compiled_updater_responses' and e.get('parsed_output'):
    x=e['parsed_output'];semantic=not (x['hypothesis_update']['action']=='set' and not x['hypothesis_update']['statement'].strip())
   rows.append({'id':e['id'],'phase':phase,'surface':r['surface'],'request_sha256':e['request_sha256'],
    'http_status':e.get('http_status'),'attempted':e['attempted'],'schema_valid':bool(e.get('schema_valid')),
    'is_impossible_schema_negative_control':e['id']=='impossible_array_responses',
    'parsed_output':e.get('parsed_output'),'known_local_semantic_consistency':semantic,'error_type':e.get('error',{}).get('type'),
    'provider_error':json.loads(e['response_text']).get('error') if e.get('http_status')!=200 else None,
    'response_model':e.get('response',{}).get('model'),'input_tokens':inp,'cache_hit_tokens':cache,
    'cache_miss_tokens':inp-cache if inp is not None and cache is not None else None,
    'output_tokens':out,'reasoning_tokens':reasoning,'total_tokens':total})
 assert len(rows)==13 and len({r['id'] for r in rows})==13
 hit=sum(r['cache_hit_tokens'] or 0 for r in rows);miss=sum(r['cache_miss_tokens'] or 0 for r in rows)
 summary={'capability_gate':'FAIL_REQUIRED_EXACT_SCHEMA','diagnostic_calls':13,'responses_calls':sum(r['surface']=='responses' for r in rows),
  'strict_function_calls':sum(r['surface']=='strict_function' for r in rows),'http_200':sum(r['http_status']==200 for r in rows),
  'http_400':sum(r['http_status']==400 for r in rows),'schema_valid_outputs':sum(r['schema_valid'] for r in rows),
  'completed_schema_violations':sum(r['http_status']==200 and not r['schema_valid'] for r in rows),
  'usage_reported':sum(r['input_tokens'] is not None for r in rows),'usage_unreported':sum(r['input_tokens'] is None for r in rows),
  'reported_input_tokens':sum(r['input_tokens'] or 0 for r in rows),'reported_output_tokens':sum(r['output_tokens'] or 0 for r in rows),
  'reported_total_tokens':sum(r['total_tokens'] or 0 for r in rows),'reported_reasoning_tokens':sum(r['reasoning_tokens'] or 0 for r in rows),
  'reported_cache_hit_tokens':hit,'reported_cache_miss_tokens':miss,'reported_weighted_cache_hit_rate':hit/(hit+miss) if hit+miss else None,
  'historical_preflight_frozen':24,'historical_preflight_attempted':0,'admission_attempted':0,'G4_attempted':0,'G5_attempted':0,
  'interpretation':'Diagnostic schemas include one deliberate impossible language; these counts are not research-node serialization rates. Unreported usage is unknown, not proven zero cost.',
  'rows':rows}
 write(b/'CAPABILITY_METRICS.json',summary)
 old=read(TOP/'analysis/HISTORICAL_HASHES.json');bad=[p for p,h in old['files'].items() if sha(ROOT/p)!=h]
 freezes={}
 for p in [b/'freeze.json',b/'equivalent_schema_probe/freeze.json']:
  f=read(p);freezes[str(p.relative_to(TOP))]=[k for k,h in f['files'].items() if sha(ROOT/k)!=h]
 starts=[]
 for p in [b/'primary_events.jsonl',b/'fallback_events.jsonl',b/'equivalent_schema_probe/events.jsonl']:
  for line in p.open():
   e=json.loads(line)
   if e['kind']=='request_started':starts.append(e['id'])
 assert len(starts)==13 and len(set(starts))==13
 assert not bad and not any(freezes.values())
 integrity={'historical_files_checked':len(old['files']),'historical_mismatches':bad,'freeze_mismatches':freezes,
  'unique_attempts':len(starts),'duplicate_probe_ids':False,'zero_retries':True,'research_calls':0,
  'scope':'Exact local artifact/request integrity; does not certify provider constrained decoding.'}
 write(TOP/'analysis/INTEGRITY.json',integrity)
 print(json.dumps({k:v for k,v in summary.items() if k!='rows'},indent=2));print(json.dumps(integrity,indent=2))

if __name__=='__main__':main()
