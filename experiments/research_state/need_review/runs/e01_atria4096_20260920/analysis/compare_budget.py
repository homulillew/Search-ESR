"""Audit the one-setting change against the immediately prior frozen batch."""
import pathlib,json,datetime,hashlib
r=pathlib.Path(__file__).resolve().parents[1]
prior=r.parent/'e01_atria_20260920'
def read(p):return json.loads(p.read_text())
m=read(r/'manifest.json');old=read(prior/'manifest.json')
assert m['schedule']==old['schedule']
assert m['prompt_sha256']==old['prompt_sha256']
assert m['approved_plan']['implementation_sha256']==old['approved_plan']['implementation_sha256']
a=dict(m['settings']);b=dict(old['settings']);diff={k:{'prior':b.get(k),'current':a.get(k)} for k in set(a)|set(b) if a.get(k)!=b.get(k)}
assert diff=={'review_max_tokens':{'prior':512,'current':4096}},diff
for f in (r/'checkpoints').glob('*.json'):assert read(f)==read(prior/'checkpoints'/f.name)
paired={};rows=[]
for s in m['schedule']:
    sid=s['sample_id'];d=read(r/'branches'/sid/'result.json');p=read(prior/'branches'/sid/'result.json')
    a=dict(d['review']['request']);b=dict(p['review']['request'])
    assert a.pop('max_tokens')==4096;assert b.pop('max_tokens')==512;assert a==b
    key=(s['checkpoint_id'],s['repeat_id']);paired.setdefault(key,{})[s['review_contract']]=d
    rows.append({'sample_id':sid,'review_request_only_cap_changed':True,
      'actor_request_identical_to_prior':d['actor']['request']==p['actor']['request'],
      'prior_memo_injected':p['memo_injected'],'current_memo_injected':d['memo_injected']})
out={'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
     'prior_run':prior.name,'current_run':r.name,'settings_diff':diff,
     'same_schedule_checkpoints_prompts_implementation':True,
     'prior_plan_sha256':old['plan_sha256'],'current_plan_sha256':m['plan_sha256'],
     'cross_batch_requests':rows,'within_batch_actor_pairs':[]}
for (cid,rid),ds in sorted(paired.items()):
    a=ds['baseline'];b=ds['source_grounded_v1']
    out['within_batch_actor_pairs'].append({'checkpoint_id':cid,'repeat_id':rid,
      'both_fallback':not a['memo_injected'] and not b['memo_injected'],
      'actor_requests_identical':a['actor']['request']==b['actor']['request']})
(r/'budget_comparison.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(out,ensure_ascii=False,indent=2))
