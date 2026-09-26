import sys,collections,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from runtime import *

stages={}
for stage,planned in [('f1_state_sufficiency',144),('exploration',18)]:
    b=TOP/stage;f=verify_freeze(b/'freeze.json');req={x['id']:x for x in rd(b/'requests.json')};rows=rd(b/'frontier_outputs.json')
    ev=[json.loads(l) for l in (b/'frontier_events.jsonl').read_text().splitlines()];starts=[e for e in ev if e['kind']=='request_started'];ends=[e for e in ev if e['kind']=='completed']
    assert len(req)==len(rows)==len(starts)==len(ends)==planned
    assert len({x['item']['id'] for x in starts})==planned
    heads=sorted({x['run_head'] for x in starts})
    for e in starts:
        it=e['item'];assert it==req[it['id']];assert dg(it['request'])==f['request_hashes'][it['id']]
        assert set(it['request'])=={'model','messages','stream','response_format'}
    for h in heads:
        for p,sha_expected in f['file_hashes'].items():
            assert hashlib.sha256(subprocess.check_output(['git','show',h+':'+p],cwd=ROOT)).hexdigest()==sha_expected,(h,p)
    assert set(rd(b/'semantic_review.json'))==set(rd(b/'private_review_key.json'))
    stages[stage]={'planned':planned,'attempted':len(starts),'completed':len(ends),'run_heads':heads,
        'failures':dict(collections.Counter(x['error']['category'] for x in rows if x['error'])),
        'returned_models':dict(collections.Counter(e['event']['response'].get('model') for e in ends)),
        'input_tokens':sum(x['usage']['input'] for x in rows),'cache_hit_tokens':sum(x['usage']['hit'] for x in rows)}
old={x['id']:x for x in rd(TOP/'f1_state_sufficiency/requests.json')}
for it in rd(TOP/'exploration/requests.json'):
    p=old[it['parent_id']];r=copy.deepcopy(p['request'])
    if it['arm']=='A1':r['messages'][0]['content']+='\nChoose the smallest currently useful unresolved research question.\n'
    assert r==it['request'];assert p['view_sha256']==it['view_sha256']
hist=rd(TOP/'historical_baseline_hashes.json');assert all((ROOT/p).exists() and sha(ROOT/p)==h for p,h in hist.items())
from dotenv import dotenv_values
secret=dotenv_values(ROOT/CONFIG['credential_file']).get(CONFIG['credential_field'])
assert secret
leaks=[str(p.relative_to(ROOT)) for p in TOP.rglob('*') if p.is_file() and '__pycache__' not in p.parts and secret.encode() in p.read_bytes()]
assert not leaks,leaks
result={'checked_utc':now(),'base_head':'9e4b48c197d4248e2ccf34850948761706252cfd','historical_files_verified_unchanged':len(hist),
    'exact_state_provenance':rd(TOP/'analysis/PROVENANCE_CHECK.json'),'stages':stages,'total_submissions':162,'tool_calls':0,'writer_calls':0,'retries':0,
    'request_hashes_and_committed_freezes_match':True,'all_labels_present':True,'exploration_only_one_sentence_diff':True,
    'credential_leaks_in_artifacts':False,'future_stages':'F2/F3/F4 unmeasured; failed F1 gate',
    'cache_hit_tokens':sum(x['cache_hit_tokens'] for x in stages.values()),'input_tokens':sum(x['input_tokens'] for x in stages.values())}
result['cache_hit_rate']=result['cache_hit_tokens']/result['input_tokens']
wr(TOP/'analysis/INTEGRITY.json',result);print(json.dumps(result,indent=2))
