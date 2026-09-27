"""Post-review execution integrity, costing, and diagnostic provenance."""
from collections import Counter,defaultdict
from .common import *
from .run import OUT,load_rows,schedule,audit
from .score import assert_review,calculate
from experiments.skeleton_state_alignment.run import parse_response,accounting

def execute():
    assert_review();check=audit();rows=load_rows();jobs={j['id']:j for j in schedule()};run=read(OUT/'RUN.json')
    for row in rows:
        assert row['head']==run['head']
        stem=OUT/'calls'/row['id'];request=read(stem.with_suffix('.request.json'))
        assert request['request']==jobs[row['id']]['request'] and request['request_sha256']==row['request_sha256']
        if row.get('http_status') is not None:
            raw=read(stem.with_suffix('.response.json'));parsed=parse_response(raw['status'],raw['body'],jobs[row['id']])
            for key,value in parsed.items():assert row[key]==value,(row['id'],key)
    saved=read(OUT/'ACCOUNTING.json');replay=accounting(rows)
    for k,v in replay.items():assert saved[k]==v,k
    metrics=read(OUT/'METRICS.json');assert metrics==calculate()
    assert len(list((OUT/'calls').glob('*.attempt.json')))==saved['sent_or_send_intent']
    judged=read(OUT/'review/JUDGMENTS.json');key=read(OUT/'review/KEY.json');reverse={v:k for k,v in key.items()}
    disagreements=[];errors=[]
    details={d['id']:d for arm in metrics['arms'].values() for d in arm['details']}
    for row in rows:
        d=details[row['id']];j=judged[reverse[row['id']]]
        if not d['valid_selection']:
            errors.append({**{k:row[k] for k in ('id','qid','case_id','arm','replicate')},**d,'visible_mask_review':j})
        if j['selection_appropriate_under_visible_mask'] is not None and j['selection_appropriate_under_visible_mask']!=d['valid_selection']:
            disagreements.append({'id':row['id'],'review_id':reverse[row['id']],'blind_visible_mask_judgment':j,'frozen_reference_valid':d['valid_selection'],
               'scope':'Visible-mask judgments are not the same estimand as hidden-state frozen-reference validity. No reference edits.'})
    write(P/'analysis/E1_ERROR_LEDGER.json',errors)
    write(P/'analysis/E1_REVIEW_DISAGREEMENTS.json',disagreements)
    # Identical payloads can span states with different unresolved subconditions.
    refs={r['case_id']:r for r in read(OUT/'SELECTION_REFERENCE.json')};groups=defaultdict(list)
    for job in jobs.values():groups[job['request_sha256']].append(job)
    collisions=[]
    for request_hash,group in groups.items():
        cases=sorted({j['case_id'] for j in group})
        if len(cases)<2:continue
        sets={c:refs[c]['acceptable_active_ids'] for c in cases}
        if len({tuple(v) for v in sets.values()})>1:
            collisions.append({'request_sha256':request_hash,'cases':cases,'acceptable_ids_by_state':sets,
             'common_acceptable_ids':sorted(set.intersection(*(set(v) for v in sets.values()))),
             'reason':'Same Q/Skeleton/binary Mask omits residual subconditions. Descriptive identifiability diagnostic, not a new primary metric.'})
    write(P/'analysis/E1_INPUT_COLLISIONS.json',collisions)
    pair=[]
    for case in sorted({r['case_id'] for r in rows}):
        cs=[r for r in rows if r['case_id']==case]
        pair.append({'case_id':case,'qid':cs[0]['qid'],
            'same_payload_across_arms':len({r['request_sha256'] for r in cs})==1,
            'S0':[details[r['id']] for r in cs if r['arm']=='S0'],
            'S1':[details[r['id']] for r in cs if r['arm']=='S1']})
    write(P/'analysis/E1_PAIRED_SELECTION.json',pair)
    write(P/'analysis/E1_EXECUTED_FILES.json',{rel(p):sha(p) for p in sorted(OUT.rglob('*')) if p.is_file() and '__pycache__' not in p.parts})
    write(P/'analysis/E1_INTEGRITY.json',{'status':'PASS',**check,'raw_responses_and_requests_replayed':len(rows),
       'metrics_exact_replay':True,'accounting_exact_replay':True,'review_sealed':True,
       'attempts':saved['sent_or_send_intent'],'max_retries':0,'historical_preservation':True,
       'visible_review_reference_disagreements':len(disagreements),'identical_input_reference_collisions':len(collisions)})
    print(json.dumps({'status':'PASS','attempts':saved['sent_or_send_intent'],'review_disagreements':len(disagreements),'input_collisions':len(collisions)},indent=2))
if __name__=='__main__':execute()
