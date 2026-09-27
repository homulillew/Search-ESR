"""Offline outcome analysis; refuses to run before a complete frozen source-only review."""
import json
from collections import Counter
from .contracts import HERE, ROOT, read, save, digest, file_hash
from .. import metrics
from ..runner import check_inventory_review

def fraction(n,d):return {'numerator':n,'denominator':d,'rate':n/d if d else None,'defined':bool(d)}

def freeze_review():
    labels=read(HERE/'review/inventory_labels.json');mapping=read(HERE/'review/private_mapping.json')
    check_inventory_review(mapping,labels)
    for m in mapping:
        l=labels[m['review_id']]
        if [f['index'] for f in l['facts']]!=list(range(m['facts'])):raise ValueError('fact review coverage/order')
        for k in ['attribution_loss','modality_loss','relation_loss']:
            if not isinstance(l[k],list):raise ValueError('missing loss review: '+k)
        if type(l['severe_verdict_uninterpretability']) is not bool:raise ValueError('missing severity review')
    save(HERE/'review/INVENTORY_REVIEW_FREEZE.json',{'review_method':'single Codex source-only packet review; labels frozen before G0/G1 outcome analysis',
        'labels_sha256':file_hash(HERE/'review/inventory_labels.json'),
        'packets':{str(p.relative_to(ROOT)):file_hash(p) for p in sorted((HERE/'review/inventory_source').glob('*.json'))},
        'inventories':len(mapping),'facts':sum(m['facts'] for m in mapping),
        'limitation':'Reviewer knows prior task examples; no linked candidate or arm verdict is displayed in inventory review packets.'})

def analyze():
    frozen=read(HERE/'review/INVENTORY_REVIEW_FREEZE.json')
    if frozen['labels_sha256']!=file_hash(HERE/'review/inventory_labels.json'):raise ValueError('source review changed')
    for p,h in frozen['packets'].items():
        if file_hash(ROOT/p)!=h:raise ValueError('review packet changed')
    labels=read(HERE/'review/inventory_labels.json');mapping=read(HERE/'review/private_mapping.json')
    b=read(HERE/'CANDIDATE_BANK.json');pairs=b['pairs'];results=read(HERE/'run001/RESULTS.json')
    transport=read(HERE/'run001/TRANSPORT_SUMMARY.json');complete=read(HERE/'run001/COMPLETENESS_GATE.json')['complete']
    report=metrics.e2(pairs,results)
    report['transport_complete']=complete
    review={'inventories':len(labels),'facts':sum(len(l['facts']) for l in labels.values()),
        'unsupported_facts':sum(not f['source_supported'] for l in labels.values() for f in l['facts']),
        'inventories_with_omissions':sum(bool(l['omitted_observed_commitments']) for l in labels.values()),
        'inventories_with_attribution_loss':sum(bool(l['attribution_loss']) for l in labels.values()),
        'inventories_with_modality_loss':sum(bool(l['modality_loss']) for l in labels.values()),
        'inventories_with_relation_loss':sum(bool(l['relation_loss']) for l in labels.values()),
        'severe_verdict_uninterpretability':any(l['severe_verdict_uninterpretability'] for l in labels.values()),
        'labels_sha256':frozen['labels_sha256']}
    report['inventory_review']=review
    if not complete:status='H3_INCONCLUSIVE_INCOMPLETE_EXECUTION'
    elif report['tables']['pooled']['G0']['FAR']['numerator']==0:status='H3_INCONCLUSIVE_NO_BASELINE_FALSE_ADMISSION'
    elif review['severe_verdict_uninterpretability']:status='H3_INCONCLUSIVE_INVENTORY_UNRELIABILITY'
    elif report['supported']:status='H3_SUPPORTED'
    else:status='H3_NOT_SUPPORTED'
    report['final_status']=status;report['original_numeric_gate']=report['supported']
    if status!='H3_SUPPORTED':report['supported']=False
    if not complete:
        report['survivor_only_analysis']=False
        save(HERE/'review/E2_METRICS.json',report)
        return
    by={(r['pair_id'],r['arm']):r for r in results};families={p['pair_id']:p['family_prestratum'] for p in read(HERE/'BANK_FREEZE.json')['pairs']}
    invs={m['evidence_key']:m for m in mapping}
    rescue=[];harm=[];negative=[];errors=[];allcases=[]
    for p in pairs:
        a,c=(by[(p['pair_id'],x)] for x in ('G0','G1'))
        bad=not p['label']['source_supported'] and p['label']['semantic_strengthening']
        key=digest(p['Evidence']);m=invs[key];frozen_inv=read(ROOT/m['inventory_path'])
        case={'pair_id':p['pair_id'],'qid':p['qid'],'split':p['split'],'family':families[p['pair_id']],
            'ambiguity':p['label']['ambiguous_relation'],'truth':p['label'],'source_review_reason':p['source_review_reason'],
            'Candidate':p['candidate'],'Evidence':p['Evidence'],'Inventory':frozen_inv['inventory'],
            'G0':{'verdict':a['verdict'],'reason':a['reason']},'G1':{'verdict':c['verdict'],'reason':c['reason']},
            'inventory_review_id':m['review_id'],'inventory_review':labels[m['review_id']]}
        case['rescue']=bad and a['verdict']=='supported' and c['verdict']=='insufficient'
        case['recall_harm']=p['label']['source_supported'] and a['verdict']=='supported' and c['verdict']=='insufficient'
        case['errors']=[arm+('_false_admit' if bad else '_false_reject') for arm,row in [('G0',a),('G1',c)] if (row['verdict']=='supported')!=p['label']['source_supported']]
        allcases.append(case)
        if bad:negative.append(case)
        if case['rescue']:rescue.append(case)
        if case['recall_harm']:harm.append(case)
        if case['errors']:errors.append(case)
    report['rescue_count']=len(rescue);report['recall_harm_count']=len(harm)
    report['negative_qids']=sorted({p['qid'] for p in negative});report['negative_families']=dict(Counter(p['family'] for p in negative))
    report['negative_ambiguity_strata']={}
    for s in ['all','ambiguous','nonambiguous']:
        pp=[p for p in pairs if not p['label']['source_supported'] and p['label']['semantic_strengthening'] and (s=='all' or p['label']['ambiguous_relation']==(s=='ambiguous'))]
        report['negative_ambiguity_strata'][s]={arm:fraction(sum(by[p['pair_id'],arm]['verdict']=='supported' for p in pp),len(pp)) for arm in ['G0','G1']}
    report['transport_summary']=transport
    report['STOP_AFTER_E2']=True;report['E3_calls']=0;report['production_changed']=False
    save(HERE/'review/E2_METRICS.json',report)
    save(HERE/'review/ERROR_CATALOG.json',{'rescue_cases':rescue,'recall_harm_cases':harm,'all_negative_cases':negative,'all_error_cases':errors})
    save(HERE/'review/ALL_CASES.json',allcases)
    print(json.dumps({k:report[k] for k in ['final_status','tables','gate_details','rescue_count','recall_harm_count','inventory_review']},indent=2))

if __name__=='__main__':
    import sys
    if sys.argv[1:] == ['freeze-review']:freeze_review()
    elif sys.argv[1:] == ['analyze']:analyze()
    else:raise SystemExit('choose freeze-review or analyze')
