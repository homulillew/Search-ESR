"""Join condition metadata after first-pass labels; compare all scheduled pairs."""
import pathlib,json,hashlib,datetime,collections
r=pathlib.Path(__file__).resolve().parents[1];v=r/'review'
mapping={c['card_id']:c for c in json.loads((v/'private_key.json').read_text())['cards']}
rows=[json.loads(x) for x in (v/'annotations_first_pass.jsonl').read_text().splitlines()]
pair_lookup={}
for c in rows:
    k=mapping[c['card_id']];c['condition']={f:k[f] for f in ['sample_id','checkpoint_id','repeat_id','review_contract']}
    pair_lookup.setdefault((k['checkpoint_id'],k['repeat_id']),{})[k['review_contract']]=c
for c in rows:
    k=c['condition'];labels=c['labels']
    if k['review_contract']=='baseline':reg='not_applicable';note='同期C0不对自身作退化判断。'
    else:
        base=pair_lookup[(k['checkpoint_id'],k['repeat_id'])]['baseline']
        if 'unknown' in [labels['action_acceptable'],base['labels']['action_acceptable']]:
            reg='unknown';note='C1 Actor超时，不能比较语义动作好坏；运行可靠性失败另行保留。C1有memo、C0无memo，无法补造反事实动作。'
        else:
            reg='yes' if base['labels']['action_acceptable']=='yes' and labels['action_acceptable']=='no' else 'no'
            note=('本批C1完整动作不合格，配对C0为较弱通过，因此本口径出现退化；C0若降级则不成立。' if reg=='yes' else '按完整响应标签，本批C1没有比配对C0更差。')
            note+='双方都无备忘回退，实际Actor请求相同；行为差异不能归因于来源合同。'
    labels['regression']=reg;c['label_evidence']['regression']={'supporting_refs':['question'],'notes':note}
(v/'annotations_final.jsonl').write_text(''.join(json.dumps(c,ensure_ascii=False)+'\n' for c in rows))
s={'reviewer':'single Codex-assisted; prior outputs/card order known, not blind or independent human gold',
   'scheduled':12,'valid_review_semantic_denominator':1,'source_correct_valid_reviews':1,
   'source_rate_among_valid':1.0,'caveat':'1/1 describes the sole available review, not 100% end-to-end success or a population accuracy estimate.',
   'by_contract':{},'by_checkpoint':{},'cross_budget_descriptive':{},'sensitivity':{}}
for contract in ['baseline','source_grounded_v1']:
    cs=[c for c in rows if c['condition']['review_contract']==contract]
    valid=[c for c in cs if c['execution_status']['review_status']=='ok']
    correct=sum(c['labels']['review_source_attribution_correct']=='yes' for c in valid)
    s['by_contract'][contract]={'scheduled':len(cs),'valid_reviews':len(valid),'source_correct':correct,
      'source_rate_among_valid':correct/len(valid) if valid else None,
      'labels':{k:dict(collections.Counter(c['labels'][k] for c in cs)) for k in cs[0]['labels']},
      'acceptable_actions_after_valid_review':sum(c['labels']['action_acceptable']=='yes' for c in valid),
      'observable_actor_after_valid_review':sum(c['actor_response'] is not None for c in valid)}
for cid in sorted({c['condition']['checkpoint_id'] for c in rows}):
    cs=[c for c in rows if c['condition']['checkpoint_id']==cid]
    s['by_checkpoint'][cid]={'scheduled':len(cs),'acceptable':sum(c['labels']['action_acceptable']=='yes' for c in cs),
      'unknown':sum(c['labels']['action_acceptable']=='unknown' for c in cs)}
prior=[json.loads(x) for x in (r.parent/'e01_atria_20260920/review/annotations_final.jsonl').read_text().splitlines()]
prior_by={x['condition']['sample_id']:x for x in prior}
comparison=json.loads((r/'budget_comparison.json').read_text())
same={x['sample_id'] for x in comparison['cross_batch_requests'] if x['actor_request_identical_to_prior']}
transitions=collections.Counter()
for c in rows:
    sid=c['condition']['sample_id']
    if sid in same:transitions[f"{prior_by[sid]['labels']['action_acceptable']}->{c['labels']['action_acceptable']}"]+=1
s['cross_budget_descriptive']={'prior_review_cap':512,'current_review_cap':4096,
  'prior_valid_reviews':0,'current_valid_reviews':1,'prior_acceptable':7,'current_acceptable':3,
  'current_unacceptable':8,'current_unknown':1,'scheduled_each':12,
  'identical_actor_request_count':len(same),'transitions_on_identical_actor_requests':dict(transitions),
  'caveat':'Every observed current Actor used exact fallback and matches the prior request; differences do not show that a larger Reviewer cap caused better/worse Actor reasoning. Repeated development cases and variable service/sampling, no rollout accuracy.'}
s['sensitivity']={'weak_pass_cards':['card_0002','card_0012'],
  'main_acceptable_count':3,'if_both_weak_passes_downgraded_acceptable_count':1,
  'fixed_denominator':12,'reason':'OR query may repeat an old branch; unverified Championship League format may warrant checking first. Main delivery/attribution conclusions unchanged.'}
(r/'semantic_summary.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
(v/'unmask_attestation.json').write_text(json.dumps({'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
  'first_pass_sha256':hashlib.sha256((v/'annotations_first_pass.jsonl').read_bytes()).hexdigest(),
  'changes':'Only regression labels/evidence changed; condition metadata appended.'},indent=2)+'\n')
print(json.dumps(s,ensure_ascii=False,indent=2))
