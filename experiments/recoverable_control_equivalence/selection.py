"""Prospective selector input/contract/scoring. No model call at import."""
from collections import Counter
from .common import *
from experiments.skeleton_state_alignment.contracts import selection_errors

def nodes_for(qid):
    raw=read(OLD/'e0_addressability/RUNTIME_SKELETON_D2.json')[qid]['requirements']
    return [{k:v for k,v in n.items() if k in ('requirement_id','source_spans','label')} for n in raw]

def build_schedule():
    rows=[]; gold={(g['case_id'],g['skeleton_arm']):g for g in read(OLD/'e1_alignment/GOLD_MASKS.json')}
    for state in read(OLD/'e0_reference/STATES.json'):
        nodes=nodes_for(state['qid'])
        for arm in ('S0','S1'):
            source=OLD/('e1_alignment/GOLD_MASKS.json' if arm=='S0' else f"e1_alignment/calls/A1__{state['case_id']}__R1.result.json")
            if arm=='S0':mask={r:project(n['status']) for r,n in gold[state['case_id'],'A1']['requirements'].items()}
            else:
                source_result=read(source)
                assert source_result['valid_output'], 'No fallback for invalid historical mask'
                mask={n['requirement_id']:project(n['status']) for n in source_result['output']['requirements']}
            assert set(mask)=={n['requirement_id'] for n in nodes}
            payload={'Original Question':state['question'],'Task Skeleton':nodes,'Control Mask':mask}
            request={'model':'deepseek-flash','temperature':0,'stream':False,'response_format':{'type':'json_object'},
                'messages':[{'role':'system','content':(P/'prompts/selection.txt').read_text()},
                    {'role':'user','content':json.dumps(payload,ensure_ascii=False)}]}
            for rep in (1,2):
                row={k:state[k] for k in ('case_id','state_id','qid')}
                row.update(id=f"{arm}__{state['case_id']}__R{rep}",stage='e1_selection',arm=arm,replicate=rep,
                    mask_source=rel(source),mask_source_sha256=sha(source),source_replicate=1 if arm=='S1' else None,
                    request=request,request_sha256=digest(request))
                rows.append(row)
    return sorted(rows,key=lambda r:digest(['recoverable-control-selection-v1',r['id']]))

def selection_metrics(rows,jobs,refs):
    c=Counter(planned=len(rows)); pairs={};details=[]
    for row in rows:
        job=jobs[row['id']];payload=json.loads(job['request']['messages'][1]['content']);ref=refs[row['case_id']]
        valid=bool(row.get('valid_output')) and not selection_errors(row.get('output'),payload['Task Skeleton'])
        v=row['output']['selection'] if valid else None
        flags={'schema_validity':valid,
            'valid_selection':v in ref['acceptable_active_ids'] or (v=='STOP' and ref['stop_allowed']),
            'selected_closed':v in ref['invalid_supported_ids'],
            'selected_input_closed':payload['Control Mask'].get(v)=='CLOSED',
            'downstream_selection':v in ref['blocked_or_downstream_ids'],
            'false_stop':v=='STOP' and not ref['stop_allowed'],
            'input_mask_false_stop':v=='STOP' and 'OPEN' in payload['Control Mask'].values(),
            'other_invalid_selection':v in ref['other_invalid_ids']}
        c.update({k:int(b) for k,b in flags.items()})
        pairs.setdefault(row['case_id'],[]).append((v,flags['valid_selection']))
        details.append({'id':row['id'],'case_id':row['case_id'],'selection':v,**flags})
    stable=Counter()
    for values in pairs.values():
        if len(values)!=2:stable['incomplete_pair']+=1;continue
        (a,va),(b,vb)=values
        stable['same_valid_ID' if va and vb and a==b else 'different_both_valid' if va and vb else 'one_valid_one_invalid' if va or vb else 'both_invalid']+=1
    keys=('valid_selection','selected_closed','selected_input_closed','downstream_selection','false_stop','input_mask_false_stop','schema_validity','other_invalid_selection')
    return {'metrics':{k:metric(c[k],len(rows)) for k in keys},'counts':dict(c),'stability':dict(stable),'details':details}

def evaluate_gates(metrics,rules,loss=None):
    checks={}
    for name,(op,limit) in rules.items():
        value=loss if name=='selection_loss' else metrics[name]['value']
        checks[name]={'value':value,'operator':op,'threshold':limit,'pass':value is not None and (value>=limit-1e-12 if op=='>=' else value<=limit+1e-12)}
    return {'pass':all(c['pass'] for c in checks.values()),'checks':checks}
