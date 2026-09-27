"""Deterministic reanalysis; no network, no new alignment, no Gold edits."""
from collections import Counter
import statistics
from .common import *
from experiments.skeleton_state_alignment.contracts import alignment_errors

def projection_rows():
    golds={(g['case_id'],g['skeleton_arm']):g for g in read(OLD/'e1_alignment/GOLD_MASKS.json')}
    states={s['case_id']:s for s in read(OLD/'e0_reference/STATES.json')}
    refs={r['case_id']:r for r in read(OLD/'e2_selection/SELECTION_REFERENCE.json')}
    rows=[]
    for job in read(OLD/'e1_alignment/SCHEDULE.json'):
        source=OLD/'e1_alignment/calls'/f"{job['id']}.result.json"
        result=read(source); payload=json.loads(job['request']['messages'][1]['content'])
        valid=result['valid_output'] and not alignment_errors(result['output'],payload['Task Skeleton'],payload['Verified Claims'])
        gold=golds[job['case_id'],job['arm']]['requirements']; state=states[job['case_id']]
        pred={n['requirement_id']:n for n in result['output']['requirements']} if valid else {}
        nodes=[]
        for rid,g in gold.items():
            gs=g['status']; ps=pred[rid]['status'] if valid else None
            gc=project(gs); pc=project(ps) if valid else None
            nodes.append({'requirement_id':rid,'gold_status':gs,'predicted_status':ps,'gold_control':gc,'predicted_control':pc,
                'supported_by':pred[rid]['supported_by'] if valid else None,'gold_reason':g['reason'],
                'false_close':gc=='OPEN' and pc=='CLOSED','false_open':gc=='CLOSED' and pc=='OPEN',
                'semantic_error':gs!=ps,'binary_error':gc!=pc,'collapsed_U_P_error':gs!=ps and gc==pc=='OPEN'})
        row={k:job[k] for k in ('id','case_id','state_id','qid','arm','replicate')}
        row.update(source=rel(source),source_sha256=sha(source),schema_valid=valid,claims_empty=not state['claims'],nodes=nodes,
            gold_open_ids=[n['requirement_id'] for n in nodes if n['gold_control']=='OPEN'],
            predicted_open_ids=[n['requirement_id'] for n in nodes if n['predicted_control']=='OPEN'],
            false_close_ids=[n['requirement_id'] for n in nodes if n['false_close']],
            exact_three_way=valid and all(not n['semantic_error'] for n in nodes),
            exact_binary=valid and all(not n['binary_error'] for n in nodes))
        row['false_empty_open_set']=bool(valid and row['gold_open_ids'] and not row['predicted_open_ids'])
        # A0 has different node meanings. Never transfer a D2 R# by numeric ID.
        if row['arm']=='A1':
            ref=refs[row['case_id']]; acceptable=set(ref['acceptable_active_ids']); open_ids=set(row['predicted_open_ids'])
            assert acceptable<=set(row['gold_open_ids'])
            assert set(ref['invalid_supported_ids'])=={n['requirement_id'] for n in nodes if n['gold_control']=='CLOSED'}
            available=sorted(acceptable & open_ids)
            row.update(acceptable_active_ids=sorted(acceptable),remaining_acceptable_ids=available,
                frontier_evaluable=bool(acceptable),lost_all_acceptable_frontier=bool(valid and acceptable and not available),
                still_has_recovery_frontier=bool(valid and row['false_close_ids'] and available),
                representation_addressability_limit=ref['no_admissible_single_id'],
                false_stop_hazard=bool(valid and not open_ids and not ref['stop_allowed']))
            if row['false_close_ids']:
                row['false_close_frontier_category']=('D_empty_OpenSet' if not open_ids else 'A_acceptable_frontier_remains' if available
                    else 'B_only_blocked_downstream' if open_ids<=set(ref['blocked_or_downstream_ids']) else 'C_no_acceptable_frontier')
            else: row['false_close_frontier_category']=None
        else:
            row.update(acceptable_active_ids=None,remaining_acceptable_ids=None,frontier_evaluable=False,
                lost_all_acceptable_frontier=None,still_has_recovery_frontier=None,representation_addressability_limit=None,
                false_stop_hazard=row['false_empty_open_set'],false_close_frontier_category='UNAVAILABLE_NO_FROZEN_A0_SELECTION_REFERENCE' if row['false_close_ids'] else None)
        rows.append(row)
    return rows

def summarize(rows):
    nodes=[n for r in rows for n in r['nodes']]; valid=[r for r in rows if r['schema_valid']]
    ns=len(nodes); m={
      'binary_node_accuracy':metric(sum(not n['binary_error'] for n in nodes),ns),
      'three_way_node_accuracy':metric(sum(not n['semantic_error'] for n in nodes),ns),
      'open_requirement_recall':metric(sum(n['gold_control']==n['predicted_control']=='OPEN' for n in nodes),sum(n['gold_control']=='OPEN' for n in nodes)),
      'open_requirement_precision':metric(sum(n['gold_control']==n['predicted_control']=='OPEN' for n in nodes),sum(n['predicted_control']=='OPEN' for n in nodes)),
      'closure_precision':metric(sum(n['gold_control']==n['predicted_control']=='CLOSED' for n in nodes),sum(n['predicted_control']=='CLOSED' for n in nodes)),
      'false_close_rate':metric(sum(n['false_close'] for n in nodes),sum(n['gold_control']=='OPEN' for n in nodes)),
      'exact_binary_mask':metric(sum(r['exact_binary'] for r in rows),len(rows)),
      'exact_three_way_mask':metric(sum(r['exact_three_way'] for r in rows),len(rows)),
      'schema_validity':metric(len(valid),len(rows)),
      'false_empty_open_set':metric(sum(r['false_empty_open_set'] for r in rows),len(rows)),
      'false_stop_hazard':metric(sum(r['false_stop_hazard'] for r in rows),len(rows))}
    m['control_equivalent_gain']={'value':m['exact_binary_mask']['value']-m['exact_three_way_mask']['value'] if rows else None,'unit':'proportion_difference'}
    m['counts']={'responses':len(rows),'nodes':ns,'three_way_status_errors':sum(n['semantic_error'] for n in nodes),
       'binary_control_errors':sum(n['binary_error'] for n in nodes),'U_P_errors_collapsed':sum(n['collapsed_U_P_error'] for n in nodes),
       'remaining_false_close_errors':sum(n['false_close'] for n in nodes),'remaining_false_open_errors':sum(n['false_open'] for n in nodes),
       'false_close_responses':sum(bool(r['false_close_ids']) for r in rows),'semantically_wrong_but_binary_exact':sum(r['exact_binary'] and not r['exact_three_way'] for r in rows)}
    d2=[r for r in rows if r['arm']=='A1']; eligible=[r for r in d2 if r['frontier_evaluable']]
    fc=[r for r in d2 if r['false_close_ids']]
    m['lost_all_acceptable_frontier']=metric(sum(r['lost_all_acceptable_frontier'] for r in eligible),len(eligible))
    m['still_has_recovery_frontier']=metric(sum(r['still_has_recovery_frontier'] for r in fc),len(fc))
    m['representation_addressability_limit']=metric(sum(r['representation_addressability_limit'] for r in d2),len(d2))
    m['false_close_frontier_categories']=dict(Counter(r['false_close_frontier_category'] for r in rows if r['false_close_ids']))
    m['frontier_reference_scope']='A1 D2 only; A0 unavailable, never mapped by matching numeric IDs'
    return m

def temporal(rows):
    pairs=read(OLD/'analysis/MONOTONIC_PAIRS.json'); edges={p['from']:p['to'] for p in pairs if p['eligible']}
    lookup={(r['arm'],r['case_id'],r['replicate']):r for r in rows}; events=[]
    for row in rows:
        for rid in row['false_close_ids']:
            e={k:row[k] for k in ('id','arm','qid','case_id','replicate')}; e['requirement_id']=rid
            nxt=edges.get(row['case_id']); e['next_eligible_state']=nxt
            nr=lookup.get((row['arm'],nxt,row['replicate']))
            if nr and nr['schema_valid']:
                node=next(n for n in nr['nodes'] if n['requirement_id']==rid)
                e['outcome']={('OPEN','OPEN'):'recovered_open',('CLOSED','CLOSED'):'became_justified',('OPEN','CLOSED'):'persistent_false_close',('CLOSED','OPEN'):'reopened_incorrectly'}[node['gold_control'],node['predicted_control']]
                e['next_gold_control']=node['gold_control'];e['next_predicted_control']=node['predicted_control']
            else:e['outcome']='right_censored_no_eligible_successor' if nxt is None else 'unevaluable_successor'
            e['consecutive_false_close_observed_states']=1; e['safe_resolution_steps']=None; e['recovered_open_steps']=None
            current=row['case_id'];steps=0
            while current in edges:
                current=edges[current];steps+=1;nrow=lookup.get((row['arm'],current,row['replicate']))
                if not nrow or not nrow['schema_valid']:break
                node=next(n for n in nrow['nodes'] if n['requirement_id']==rid)
                if node['false_close']:e['consecutive_false_close_observed_states']+=1;continue
                if node['gold_control']==node['predicted_control']:
                    e['safe_resolution_steps']=steps
                    if node['gold_control']=='OPEN':e['recovered_open_steps']=steps
                break
            events.append(e)
    return {'eligible_literal_claim_addition_pairs':sum(p['eligible'] for p in pairs),
        'excluded_pairs':[p for p in pairs if not p['eligible']], 'events':events,
        'scope':'Historical independently sampled masks along observed Claims additions. No closed-loop counterfactual, no causal recovery claim.'}

def temporal_summary(events):
    counts=Counter(e['outcome'] for e in events)
    denom=sum(counts[k] for k in ('recovered_open','became_justified','persistent_false_close','reopened_incorrectly'))
    safe=counts['recovered_open']+counts['became_justified']
    recovery=[e['recovered_open_steps'] for e in events if e['recovered_open_steps'] is not None]
    resolution=[e['safe_resolution_steps'] for e in events if e['safe_resolution_steps'] is not None]
    return {'natural_false_close_nodes':len(events),'outcome_counts':dict(counts),
        'safe_resolution_rate':metric(safe,denom),
        'recoverability_status':'EVALUABLE' if denom>=4 else 'INSUFFICIENT_NATURAL_DENOMINATOR',
        'persistent_false_close_count':counts['persistent_false_close'],
        'maximum_consecutive_false_close_observed_states':max((e['consecutive_false_close_observed_states'] for e in events),default=0),
        'median_recovery_steps':statistics.median(recovery) if recovery else None,
        'median_safe_resolution_steps':statistics.median(resolution) if resolution else None,
        'censoring_note':'End-of-chain events are not successes or failures in safe-resolution denominator; max run is a lower bound. Events/replicates share qids.'}

def gate(m,t):
    rules=read(P/'GATES.json')['E0_A1']; checks={}
    for k,(op,limit) in rules.items():
        value=m[k]['value']; checks[k]={'value':value,'operator':op,'threshold':limit,
            'pass':value is not None and (value>=limit-1e-12 if op=='>=' else value<=limit+1e-12)}
    sr=t['safe_resolution_rate']; required=sr['denominator']>=4
    checks['safe_resolution_rate']={'value':sr['value'],'denominator':sr['denominator'],'required':required,
        'threshold':.75,'pass':not required or sr['value']>=.75,'status':t['recoverability_status']}
    return {'pass':all(c['pass'] for c in checks.values()),'checks':checks,'primary_arm':'A1','A0':'diagnostic only; old joint failure unchanged'}

def compute():
    rows=projection_rows(); times=temporal(rows); arms={}
    for arm in ('A0','A1'):
        sub=[r for r in rows if r['arm']==arm]; ev=[e for e in times['events'] if e['arm']==arm]
        strata={}
        for field in ('qid','replicate','claims_empty'):
            strata[field]={}
            for value in sorted({r[field] for r in sub},key=str):
                sr=[r for r in sub if r[field]==value]; ids={r['id'] for r in sr}
                strata[field][str(value)]={'metrics':summarize(sr),'recoverability':temporal_summary([e for e in ev if e['id'] in ids])}
        arms[arm]={'metrics':summarize(sub),'recoverability':temporal_summary(ev),'strata':strata}
    result={'arms':arms,'gate':gate(arms['A1']['metrics'],arms['A1']['recoverability']),
        'exposed_development_bank':True,'natural_states':27,'qids':10,'source_responses':108,'new_model_calls':0}
    return rows,times,result

def execute():
    integrity=verify_sources(); freeze=read(P/'E0_FREEZE.json')
    for name,h in freeze['files'].items(): assert sha(ROOT/name)==h; committed(ROOT/name)
    committed(P/'E0_FREEZE.json')
    rows,times,result=compute(); out=P/'e0_control_equivalence'
    write(out/'CONTROL_EQUIVALENT_MASKS.json',rows);write(out/'RECOVERABILITY.json',times);write(out/'METRICS.json',result)
    keys=('id','case_id','qid','arm','replicate','gold_open_ids','predicted_open_ids','false_close_ids','false_empty_open_set','false_stop_hazard','acceptable_active_ids','remaining_acceptable_ids','lost_all_acceptable_frontier','still_has_recovery_frontier','representation_addressability_limit','false_close_frontier_category')
    write(out/'ABSORBING_ERROR_AUDIT.json',[{k:r[k] for k in keys} for r in rows])
    ledger=[]
    for row in rows:
        for node in row['nodes']:
            if node['semantic_error']:ledger.append({**{k:row[k] for k in ('id','qid','case_id','arm','replicate')},**node})
    write(P/'analysis/ERROR_LEDGER.json',ledger)
    sensitivity={}
    for arm in ('A0','A1'):
        sensitivity[arm]={}
        sub=[r for r in rows if r['arm']==arm]
        for qid in sorted({r['qid'] for r in sub}):
            left=[r for r in sub if r['qid']!=qid];m=summarize(left);t=temporal_summary([e for e in times['events'] if e['arm']==arm and e['qid']!=qid])
            sensitivity[arm][qid]={'metrics':m,'recoverability':t,'runtime_gate_if_A1':gate(m,t) if arm=='A1' else None}
    write(P/'analysis/SENSITIVITY.json',{'status':'DESCRIPTIVE_NO_GATE_OVERRIDE','leave_one_qid_out':sensitivity})
    write(out/'EXECUTION.json',{'head':git('rev-parse','HEAD'),'freeze_sha256':sha(P/'E0_FREEZE.json'),**integrity,'new_model_calls':0})
    print(json.dumps({a:result['arms'][a]['metrics'] for a in ('A0','A1')},indent=2));print('E0_GATE',result['gate']['pass'])
if __name__=='__main__': execute()
