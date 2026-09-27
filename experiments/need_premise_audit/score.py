"""Deterministic aggregation after a complete single-reviewer semantic audit."""
from collections import Counter
import json
from .common import P, bank, read, write
from .run import OUT, load_rows
from experiments.minimal_need_multiquery.run import accounting_summary

ERRORS = {'missed_premise', 'target_premise_confusion', 'false_premise', 'wrong_anchor', 'subject_error', 'target_identification_error'}

def gate(metrics):
    v0, v1 = metrics['V0'], metrics['V1']
    checks = {
        'V1_invalid_recall85': 100*v1['invalid_detected'] >= 85*v1['invalid_n'],
        'V1_control_specificity85': 100*v1['controls_kept'] >= 85*v1['control_n'],
        'V1_all_binding_correct85': 100*v1['all_binding_correct'] >= 85*v1['n'],
        'V1_target_premise_distinction85': 100*v1['distinction_correct'] >= 85*v1['n'],
        'V1_exact_decision_replicate_agreement80': 100*v1['replicate_agree'] >= 80*v1['replicate_pairs'],
        'valid_schema95_each': all(100*m['valid_output'] >= 95*m['n'] for m in metrics.values()),
        'V1_balanced_accuracy_not_below_V0': v1['balanced_accuracy'] >= v0['balanced_accuracy'],
    }
    return {'status': 'PASS_TO_E2' if all(checks.values()) else 'STOP_E1', 'checks': checks,
            'opens_E3': False, 'prompt_revisions_allowed': 0}

def validate_review(row, review, ref):
    if not isinstance(review['reason'], str) or not review['reason'].strip():
        raise ValueError('Semantic review reason missing')
    if not set(review['errors']) <= ERRORS:
        raise ValueError('Unknown semantic error')
    if not row['valid_output']:
        if review.get('unscorable') is not True:
            raise ValueError('Execution failures have unknown semantics')
        return
    if row['arm'] == 'V0':
        if type(review['issue_correct']) is not bool:
            raise ValueError('V0 issue correctness required')
        return
    for k in ('target_correct', 'subject_correct'):
        if type(review[k]) is not bool:
            raise ValueError('V1 semantic dimension missing')
    bg = row['output']['required_background']
    for k in ('background_matches', 'legitimate_background', 'background_status_correct'):
        if len(review[k]) != len(bg):
            raise ValueError('Every returned background item must be reviewed')
    valid_ids = {b['id'] for b in ref['required_background']}
    for ids in review['background_matches']:
        if not isinstance(ids, list) or not set(ids) <= valid_ids:
            raise ValueError('Invalid reference background alignment')
    for k in ('legitimate_background', 'background_status_correct', 'binding_correct_by_slot'):
        if any(type(x) is not bool for x in review[k]):
            raise ValueError('Expected explicit semantic booleans')
    if len(review['binding_correct_by_slot']) != len(bg)+1:
        raise ValueError('Review subject and every background binding slot')

def summarize(rows, reviews):
    candidates = bank(); reference = {r['candidate_id']: r for r in read(P / 'e0_reference/REFERENCE_AUDIT.json')}
    if set(reviews) != {r['id'] for r in rows}:
        raise ValueError('Review must cover the planned denominator')
    scored = []
    for row in rows:
        c = candidates[row['candidate_id']]; ref = reference[row['candidate_id']]; v = reviews[row['id']]
        validate_review(row, v, ref)
        valid = row['valid_output']; decision = row['output']['decision'] if valid else None
        invalid = ref['reference_decision'] != 'keep'
        binary_correct = valid and ((decision != 'keep') == invalid)
        sr = {**row, 'reference_decision': ref['reference_decision'], 'reference_invalid': invalid, 'no_h': c['no_h'],
              'binary_correct': binary_correct, 'decision_correct': valid and (decision == ref['reference_decision'] if row['arm']=='V1' else binary_correct),
              'errors': v['errors'], 'semantic_review': v}
        if row['arm'] == 'V1':
            matched = set(x for ids in v.get('background_matches', []) for x in ids) if valid else set()
            unsupported = {b['id'] for b in ref['required_background'] if b['status']=='unsupported'}
            detected = set()
            if valid:
                for item, ids, legitimate in zip(row['output']['required_background'],v['background_matches'],v['legitimate_background']):
                    if item['status']=='unsupported' and legitimate:
                        detected.update(set(ids) & unsupported)
            sr.update(target_correct=valid and v.get('target_correct',False), subject_correct=valid and v.get('subject_correct',False),
                      distinction_correct=valid and v.get('target_correct',False) and 'target_premise_confusion' not in v['errors'],
                      all_binding_correct=valid and all(v.get('binding_correct_by_slot',[])),
                      background_reference_n=len(ref['required_background']), background_matched=len(matched),
                      background_returned=len(row['output']['required_background']) if valid else 0,
                      background_legitimate=sum(v.get('legitimate_background',[])) if valid else 0,
                      unsupported_reference_n=len(unsupported), unsupported_detected=len(detected))
        scored.append(sr)
    metrics = {}
    for arm in ('V0','V1'):
        rs=[r for r in scored if r['arm']==arm]
        invalid=[r for r in rs if r['reference_invalid']]; control=[r for r in rs if not r['reference_invalid']]
        recall=sum(r['binary_correct'] for r in invalid)/len(invalid)
        specificity=sum(r['binary_correct'] for r in control)/len(control)
        pair_agree=pair_binary_agree=0
        for cid in candidates:
            pair=sorted([r for r in rs if r['candidate_id']==cid],key=lambda r:r['replicate'])
            if len(pair)!=2:raise ValueError('Missing replicate slot')
            if all(r['valid_output'] for r in pair):
                ds=[r['output']['decision'] for r in pair]
                pair_agree+=ds[0]==ds[1]; pair_binary_agree+=(ds[0]=='keep')==(ds[1]=='keep')
        m={'n':len(rs),'invalid_n':len(invalid),'control_n':len(control),
           'invalid_detected':sum(r['binary_correct'] for r in invalid),'controls_kept':sum(r['binary_correct'] for r in control),
           'recall':recall,'specificity':specificity,'balanced_accuracy':(recall+specificity)/2,
           'valid_json':sum(r.get('valid_json',False) for r in rs),'valid_output':sum(r['valid_output'] for r in rs),
           'decision_correct':sum(r['decision_correct'] for r in rs),
           'replicate_pairs':len(candidates),'replicate_agree':pair_agree,'replicate_agreement':pair_agree/len(candidates),
           'binary_replicate_agreement':pair_binary_agree/len(candidates),
           'errors':dict(Counter(e for r in rs for e in r['errors'])),
           'by_replicate':{str(rep):{'n':sum(r['replicate']==rep for r in rs),
                                    'binary_correct':sum(r['binary_correct'] for r in rs if r['replicate']==rep)} for rep in (1,2)},
           'no_h':{'n':sum(r['no_h'] for r in rs),'binary_correct':sum(r['binary_correct'] for r in rs if r['no_h'])}}
        if arm=='V1':
            for k in ('target_correct','subject_correct','distinction_correct','all_binding_correct','background_reference_n',
                      'background_matched','background_returned','background_legitimate','unsupported_reference_n','unsupported_detected'):
                m[k]=sum(r[k] for r in rs)
            m['required_background_recall']=m['background_matched']/m['background_reference_n']
            m['required_background_precision']=m['background_legitimate']/m['background_returned'] if m['background_returned'] else None
            m['unsupported_background_recall']=m['unsupported_detected']/m['unsupported_reference_n']
            units=[b for r in rs if r['valid_output'] for b in r['semantic_review']['binding_correct_by_slot']]
            m['binding_slot_n']=len(units);m['binding_slots_correct']=sum(units)
            m['binding_slot_accuracy']=sum(units)/len(units) if units else None
        metrics[arm]=m
    return {'metrics':metrics,'gate':gate(metrics),'candidate_instances':len(candidates),
            'unique_states':len({c['state_id'] for c in candidates.values()}),'unique_qids':len({c['qid'] for c in candidates.values()}),
            'accounting':accounting_summary(rows),'scored':scored}

if __name__=='__main__':
    key=read(OUT/'review/KEY.json'); review=read(OUT/'review/REVIEW.json')
    result=summarize(load_rows(),{key[k]:v for k,v in review.items()})
    write(OUT/'METRICS.json',result)
    print(json.dumps({'metrics':result['metrics'],'gate':result['gate']},indent=2))
