"""Post-review integrity and preregistered descriptive sensitivity. No calls."""
import argparse
import copy
from collections import Counter
from .common import *
from .run import audit, load_rows, schedule, parse_response, accounting
from .score import assert_review_sealed, calculate_stage, e1_metrics, e2_metrics, check_gates
F='fully_supported'
def status_metrics(metrics):
    return {k:v for k,v in metrics.items() if k in ('node_status_accuracy','false_supported_rate','false_unresolved_rate','residual_recall','exact_state_mask')}

def sensitivity(stage,rows):
    plan=read(P/'analysis/SENSITIVITY.json');analyses={v['name']:v for v in plan['analyses']};result={'primary_gates_unchanged':True,'analyses':{}}
    if stage==STAGES[0]:
        gold={(r['case_id'],r['skeleton_arm']):r for r in read(P/'e1_alignment/GOLD_MASKS.json')}
        for name in ('low_ambiguity_nodes','strict_citation_context','unqualified_author_list','writing_vs_publication','tribute_partner_scope'):
            g=copy.deepcopy(gold)
            if name=='low_ambiguity_nodes':
                for ref in g.values():ref['requirements']={rid:n for rid,n in ref['requirements'].items() if n['ambiguity']=='low'}
            elif name=='strict_citation_context':
                for ref in g.values():
                    for node in ref['requirements'].values():
                        node['acceptable_full_support_groups']=[sorted(set(v)|set(node['reference_binding_context'])) for v in node['acceptable_full_support_groups']]
            else:
                for item in analyses[name]['overrides']:g[item['case_id'],item['arm']]['requirements'][item['id']]['status']=item['status']
            results={}
            for arm in ('A0','A1'):
                subset=[r for r in rows if r['arm']==arm and g[r['case_id'],arm]['requirements']]
                m=e1_metrics(subset,g)
                if name=='low_ambiguity_nodes':m={k:m[k] for k in ('node_status_accuracy','false_supported_rate','residual_recall','support_precision','full_support_sufficiency')}
                elif name=='strict_citation_context':m={'full_support_sufficiency':m['full_support_sufficiency']}
                else:m=status_metrics(m)
                results[arm]=m
            result['analyses'][name]=results
        leave={};rules=read(P/'GATES.json')
        for q in sorted({r['qid'] for r in rows}):
            ms={a:e1_metrics([r for r in rows if r['arm']==a and r['qid']!=q],gold) for a in ('A0','A1')}
            losses={'alignment_loss':ms['A0']['exact_state_mask']['value']-ms['A1']['exact_state_mask']['value'],
                    'node_accuracy_loss':ms['A0']['node_status_accuracy']['value']-ms['A1']['node_status_accuracy']['value']}
            leave[q]={a:{'metrics':status_metrics(ms[a]),'descriptive_gate':check_gates(ms[a],rules[a],losses)} for a in ms}
        result['analyses']['leave_one_qid_out']=leave
    else:
        refs={r['case_id']:r for r in read(P/'e2_selection/SELECTION_REFERENCE.json')}
        for name in ('relaxed_selection_locality','strict_selection_locality'):
            refs2=copy.deepcopy(refs)
            for sid,r in refs2.items():
                if name=='relaxed_selection_locality':r['acceptable_active_ids']+=analyses[name]['add_acceptable'].get(sid,[])
                else:r['acceptable_active_ids']=[i for i in r['acceptable_active_ids'] if i not in analyses[name]['remove_acceptable_by_qid'].get(str(r['qid']),[])]
            result['analyses'][name]={a:e2_metrics([r for r in rows if r['arm']==a],refs2)['valid_selection'] for a in ('S0','S1')}
        leave={};rules=read(P/'GATES.json')
        for q in sorted({r['qid'] for r in rows}):
            ms={a:e2_metrics([r for r in rows if r['arm']==a and r['qid']!=q],refs) for a in ('S0','S1')}
            loss={'selection_loss':ms['S0']['valid_selection']['value']-ms['S1']['valid_selection']['value']}
            leave[q]={a:{'valid_selection':ms[a]['valid_selection'],'descriptive_gate':check_gates(ms[a],rules[a],loss)} for a in ms}
        result['analyses']['leave_one_qid_out']=leave
    return result

def analyze(stage):
    assert_review_sealed(stage);checked=audit(stage);rows=load_rows(stage);jobs={j['id']:j for j in schedule(stage)}
    metrics=read(P/stage/'METRICS.json');assert metrics==calculate_stage(stage),'Metric replay drift'
    archive=P/stage;run=read(archive/'RUN.json')
    assert run['manifest_sha256']==sha(P/'FREEZE.json')
    assert __import__('hashlib').sha256(subprocess.check_output(['git','show',run['head']+':'+rel(P/'FREEZE.json')],cwd=ROOT)).hexdigest()==sha(P/'FREEZE.json')
    for row in rows:
        stem=archive/'calls'/row['id'];job=jobs[row['id']]
        if row['attempted']:
            assert stem.with_suffix('.attempt.json').exists()
            req=read(stem.with_suffix('.request.json'));assert req['request']==job['request'] and req['request_sha256']==job['request_sha256']
        if stem.with_suffix('.response.json').exists():
            raw=read(stem.with_suffix('.response.json'));parsed=parse_response(raw['status'],raw['body'],job)
            assert all(row[k]==v for k,v in parsed.items()),'Raw response replay drift'
        elif row.get('valid_output'):raise AssertionError('Valid output without raw response')
    recorded=read(archive/'ACCOUNTING.json');replayed=accounting(rows)
    assert all(recorded[k]==v for k,v in replayed.items())
    assert recorded['peak_concurrency']<=8
    labels=read(archive/'review/JUDGMENTS.json');key=read(archive/'review/KEY.json')
    counts=Counter(code for label in labels.values() for code in set(label['error_codes']))
    disagreements=[]
    if stage==STAGES[0]:
        gold={(g['case_id'],g['skeleton_arm']):g for g in read(P/'e1_alignment/GOLD_MASKS.json')};byid={r['id']:r for r in rows}
        for rid,label in labels.items():
            row=byid[key[rid]]
            if not row['valid_output']:continue
            pred={n['requirement_id']:n for n in row['output']['requirements']}
            for nid,judgment in label['node_judgments'].items():
                expected=pred[nid]['status']==gold[row['case_id'],row['arm']]['requirements'][nid]['status']
                if judgment['status_correct'] is not None and judgment['status_correct']!=expected:
                    disagreements.append({'review_id':rid,'call_id':row['id'],'node':nid,'blind_status_correct':judgment['status_correct'],'frozen_reference_status_correct':expected,'reason':judgment['reason']})
    write(P/f'analysis/{stage}_INTEGRITY.json',{**checked,'raw_and_request_replay':True,'metrics_and_accounting_replay':True,
       'first_pass_labels_sealed':True,'error_taxonomy_response_counts':dict(counts),'blind_reference_status_disagreements':disagreements,
       'all_planned_slots_retained':len(rows),'history_unchanged':True,'primary_labels_not_revised':True})
    write(P/f'analysis/{stage}_SENSITIVITY.json',sensitivity(stage,rows))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=STAGES);analyze(parser.parse_args().stage)
