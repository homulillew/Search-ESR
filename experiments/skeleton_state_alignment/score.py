"""Frozen-reference metrics; aggregation only after committed first-pass review."""
import argparse
from collections import Counter
from .common import *
from .run import committed, load_rows, schedule
F='fully_supported'
def rate(n,d):return n/d if d else None
def metric(n,d):return {'numerator':n,'denominator':d,'value':rate(n,d)}

def check_gates(metrics,rules,extra=None):
    values={k:v['value'] for k,v in metrics.items() if isinstance(v,dict) and 'value' in v}
    values.update(extra or {})
    checks={}
    for k,(operator,limit) in rules.items():
        v=values.get(k)
        passed=v is not None and (v>=limit-1e-12 if operator=='>=' else v<=limit+1e-12)
        checks[k]={'value':v,'operator':operator,'threshold':limit,'pass':passed}
    return {'pass':all(c['pass'] for c in checks.values()),'checks':checks}

def e1_counts(row,gold):
    valid=bool(row.get('valid_output'))
    pred={r['requirement_id']:r for r in row['output']['requirements']} if valid else {}
    c=Counter(states=1,schema_valid=int(valid),nodes=len(gold['requirements']))
    exact=valid
    for rid,g in gold['requirements'].items():
        p=pred.get(rid);gs=g['status'];ps=p['status'] if p else None;refs=set(p['supported_by']) if p else set()
        ok=ps==gs;c['status_correct']+=ok;exact=exact and ok
        c['gold_residual']+=gs!=F;c['gold_full']+=gs==F
        c['false_supported']+=gs!=F and ps==F
        c['false_unresolved']+=gs==F and ps in ('partially_supported','unsupported')
        c['missing_on_gold_full']+=gs==F and p is None
        c['pred_residual']+=ps in ('partially_supported','unsupported')
        c['residual_tp']+=gs!=F and ps in ('partially_supported','unsupported')
        c['pred_full']+=ps==F;c['true_full']+=gs==F and ps==F
        c['cited']+=len(refs);c['contributing_cited']+=len(refs & set(g['contributing_claims']))
        sufficient=gs==F and any(set(group)<=refs for group in g['acceptable_full_support_groups'])
        c['full_sufficient']+=ps==F and sufficient
        c['pred_partial']+=ps=='partially_supported'
        c['partial_valid']+=ps=='partially_supported' and gs=='partially_supported' and any(set(group)<=refs for group in g['acceptable_partial_support_groups'])
    c['exact_mask']=int(exact)
    return c

def e1_metrics(rows,golds):
    parts=[e1_counts(row,golds[(row['case_id'],row['arm'])]) for row in rows]
    c=sum(parts,Counter())
    pairs={'node_status_accuracy':('status_correct','nodes'),'fully_supported_precision':('true_full','pred_full'),
      'false_supported_rate':('false_supported','gold_residual'),'false_unresolved_rate':('false_unresolved','gold_full'),
      'residual_recall':('residual_tp','gold_residual'),'residual_precision':('residual_tp','pred_residual'),
      'support_precision':('contributing_cited','cited'),'full_support_sufficiency':('full_sufficient','pred_full'),
      'partial_support_validity':('partial_valid','pred_partial'),'exact_state_mask':('exact_mask','states'),'schema_validity':('schema_valid','states')}
    m={k:metric(c[a],c[b]) for k,(a,b) in pairs.items()}
    precision=m['residual_precision']['value'];recall=m['residual_recall']['value']
    m['residual_f1']={'value':2*precision*recall/(precision+recall) if precision is not None and recall is not None and precision+recall else (0 if precision==0 or recall==0 else None)}
    m['macro_state_node_accuracy']={'value':sum(p['status_correct']/p['nodes'] for p in parts)/len(parts) if parts else None}
    paired={sid:[p['exact_mask'] for row,p in zip(rows,parts) if row['case_id']==sid] for sid in {row['case_id'] for row in rows}}
    m['both_replicates_exact']=metric(sum(len(v)==2 and all(v) for v in paired.values()),len(paired))
    m['counts']=dict(c)
    return m

def e2_metrics(rows,refs):
    c=Counter(planned=len(rows));per_case={};jobs={j['id']:j for j in schedule(STAGES[1])}
    for r in rows:
        g=refs[r['case_id']];valid=bool(r.get('valid_output'));v=r['output']['selection'] if valid else None
        c['schema_valid']+=valid;c['valid_selection']+=v in g['acceptable_active_ids'] or (v=='STOP' and g['stop_allowed'])
        c['selected_supported']+=v in g['invalid_supported_ids'];c['downstream']+=v in g['blocked_or_downstream_ids']
        c['low_value']+=v in g['other_invalid_ids'];c['false_stop']+=v=='STOP' and not g['stop_allowed']
        c['stop_controls']+=g['stop_allowed'];c['missed_stop']+=g['stop_allowed'] and v!='STOP'
        job=jobs[r['id']]
        if job['request']:
            mask=json.loads(job['request']['messages'][1]['content'])['Coverage Mask']['requirements']
            c['selected_input_mask_supported']+=any(x['requirement_id']==v and x['status']==F for x in mask)
            c['stop_against_input_mask']+=v=='STOP' and any(x['status']!=F for x in mask)
        per_case.setdefault(r['case_id'],[]).append((v,v in g['acceptable_active_ids'] or (v=='STOP' and g['stop_allowed'])))
    stability=Counter()
    for entries in per_case.values():
        if len(entries)!=2:stability['incomplete_pair']+=1;continue
        (v1,ok1),(v2,ok2)=entries
        if ok1 and ok2:stability['same_acceptable_ID' if v1==v2 else 'compatible_different_valid_IDs']+=1
        elif ok1 or ok2:stability['one_valid_one_invalid']+=1
        else:stability['both_invalid']+=1
    m={k:metric(c[n],c['planned']) for k,n in [('valid_selection','valid_selection'),('selected_supported','selected_supported'),
       ('downstream_selection','downstream'),('low_value_selection','low_value'),('false_stop','false_stop'),('schema_validity','schema_valid'),
       ('selected_input_mask_supported','selected_input_mask_supported'),('stop_against_input_mask','stop_against_input_mask')]}
    m['missed_stop']=metric(c['missed_stop'],c['stop_controls']);m['stability']=dict(stability);m['counts']=dict(c)
    return m

def strata(rows,measure):
    cases=bank()
    return {field:{str(v):measure([r for r in rows if getter(r)==v]) for v in sorted({getter(r) for r in rows},key=str)}
      for field,getter in [('qid',lambda r:r['qid']),('historical_type',lambda r:cases[r['case_id']]['type']),
        ('claims_empty',lambda r:not cases[r['case_id']]['claims']),('replicate',lambda r:r['replicate'])]}

def monotonic(rows):
    by={(r['case_id'],r['arm'],r['replicate']):r for r in rows};cases=bank();events=[]
    frozen=read(P/'analysis/MONOTONIC_PAIRS.json')
    rank={'unsupported':0,'partially_supported':1,F:2}
    for pair in frozen:
        if not pair['eligible']:continue
        for arm in ('A0','A1'):
            for rep in (1,2):
                x=by[(pair['from'],arm,rep)];y=by[(pair['to'],arm,rep)]
                event={**pair,'arm':arm,'replicate':rep,'evaluable':bool(x.get('valid_output') and y.get('valid_output'))}
                if event['evaluable']:
                    a={r['requirement_id']:r['status'] for r in x['output']['requirements']};b={r['requirement_id']:r['status'] for r in y['output']['requirements']}
                    event.update(full_to_unsupported=[i for i in a if a[i]==F and b[i]=='unsupported'],
                      any_regression=[i for i in a if rank[b[i]]<rank[a[i]]],any_progress=[i for i in a if rank[b[i]]>rank[a[i]]])
                events.append(event)
    return {'descriptive_only':True,'frozen_eligible_pairs':sum(p['eligible'] for p in frozen),'events':events}

def calculate_stage(stage):
    rows=load_rows(stage);rules=read(P/'GATES.json');result={'stage':stage,'planned_slots':len(rows),'arms':{}}
    if stage==STAGES[0]:
        golds={(r['case_id'],r['skeleton_arm']):r for r in read(P/'e1_alignment/GOLD_MASKS.json')}
        for arm in ('A0','A1'):
            subset=[r for r in rows if r['arm']==arm]
            result['arms'][arm]={'metrics':e1_metrics(subset,golds),'strata':strata(subset,lambda r:e1_metrics(r,golds))}
        a0=result['arms']['A0']['metrics'];a1=result['arms']['A1']['metrics']
        losses={k:a0[src]['value']-a1[src]['value'] for k,src in [('alignment_loss','exact_state_mask'),('node_accuracy_loss','node_status_accuracy')]}
        result['losses']=losses
        for arm in ('A0','A1'):result['arms'][arm]['gate']=check_gates(result['arms'][arm]['metrics'],rules[arm],losses)
        result['monotonic_progress']=monotonic(rows)
    else:
        refs={r['case_id']:r for r in read(P/'e2_selection/SELECTION_REFERENCE.json')}
        for arm in ('S0','S1'):
            subset=[r for r in rows if r['arm']==arm]
            result['arms'][arm]={'metrics':e2_metrics(subset,refs),'strata':strata(subset,lambda r:e2_metrics(r,refs))}
        losses={'selection_loss':result['arms']['S0']['metrics']['valid_selection']['value']-result['arms']['S1']['metrics']['valid_selection']['value']}
        result['losses']=losses
        for arm in ('S0','S1'):result['arms'][arm]['gate']=check_gates(result['arms'][arm]['metrics'],rules[arm],losses)
        result['stop_control_note']='No natural positive STOP controls in this bank.'
    result['joint_gate_pass']=all(v['gate']['pass'] for v in result['arms'].values())
    return result

def seal_review(stage):
    out=P/stage/'review';packets=read(out/'PACKETS.json');labels=read(out/'JUDGMENTS.json')
    assert set(labels)=={p['review_id'] for p in packets}
    taxonomy=read(P/'SCHEMAS.json')['error_taxonomy'][stage]
    for p in packets:
        label=labels[p['review_id']]
        assert isinstance(label['reason'],str) and label['reason'].strip()
        assert set(label['error_codes'])<=set(taxonomy)
        if stage==STAGES[0]:
            expected={n['requirement_id'] for n in p['input']['Task Skeleton']}
            assert set(label['node_judgments'])==expected
            for node in label['node_judgments'].values():
                assert all(node[k] is None or isinstance(node[k],bool) for k in ('status_correct','support_correct'))
                assert isinstance(node['reason'],str) and node['reason'].strip()
        else:assert label['selection_appropriate_under_visible_mask'] is None or isinstance(label['selection_appropriate_under_visible_mask'],bool)
    # Packet, key and judgments must already be a committed first pass. No aggregate file yet.
    assert not (P/stage/'METRICS.json').exists()
    head=git('rev-parse','HEAD')
    for filename in ('PACKETS.json','KEY.json','JUDGMENTS.json'):committed(out/filename,head)
    write(out/'REVIEW_SEAL.json',{'judgment_commit':head,'files':{rel(out/n):sha(out/n) for n in ('PACKETS.json','KEY.json','JUDGMENTS.json')},
      'scope':'One familiar Codex reviewer; packet-masked first pass, not independent reviewers or erased memory. No aggregate inspected before this commit.'})

def assert_review_sealed(stage):
    seal=read(P/stage/'review/REVIEW_SEAL.json')
    for name,h in seal['files'].items():
        assert sha(ROOT/name)==h
        assert __import__('hashlib').sha256(subprocess.check_output(['git','show',seal['judgment_commit']+':'+name],cwd=ROOT)).hexdigest()==h
    labels=read(P/stage/'review/JUDGMENTS.json')
    assert len(labels)==108

def aggregate(stage):
    assert_review_sealed(stage)
    from .run import audit
    audit(stage)
    value=calculate_stage(stage);write(P/stage/'METRICS.json',value)
    report=f"# {stage}\n\nPlanned slots:108. Single-reviewer exposed historical development bank.\n\n"
    for arm,v in value['arms'].items():
        report+=f"## {arm}: {'PASS' if v['gate']['pass'] else 'FAIL'}\n\n| Metric | Value | Threshold | Pass |\n|---|---:|---:|---|\n"
        for k,c in v['gate']['checks'].items():
            val='NA' if c['value'] is None else f"{c['value']:.4f}"
            report+=f"| {k} | {val} | {c['operator']} {c['threshold']} | {c['pass']} |\n"
        report+='\n'
    report+='Joint gate: '+('PASS' if value['joint_gate_pass'] else 'FAIL')+'.\n\n'
    report+='See METRICS.json for qid/type/empty-Claims/replicate strata, denominators and paired metrics.\n'
    report+='E1 failure stops E2. E2 completion stops this experiment regardless of outcome.\n'
    write(P/stage/'REPORT.md',report)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['seal_review','aggregate']);parser.add_argument('stage',choices=STAGES)
    args=parser.parse_args();globals()[args.mode](args.stage)
