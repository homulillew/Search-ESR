"""Explicit post-hoc reviewer-boundary scenarios; never alter primary labels."""
from copy import deepcopy
from collections import Counter
from ..common import *
from ..evaluate import score,aggregate,gate
from .. import run
def calculate(stage, modified):
    run.STAGE=stage;run.OUT=P/stage
    reviews=deepcopy(read(P/stage/'review/FIRST_PASS.json'));byid={r['review_id']:r for r in reviews}
    for rid,patch in modified.items():
        for k,v in patch.items():
            if isinstance(v,dict):byid[rid][k].update(v)
            else:byid[rid][k]=v
    key=read(P/stage/'review/KEY.json');rs={key[r['review_id']]:r for r in reviews};refs=read(P/'e0_reference/REFERENCE_TASK_STRUCTURE.json')
    rows=[score(r,rs[r['id']],refs[r['qid']]) for r in run.load_rows()]
    pairs=deepcopy(read(P/stage/'review/PAIRS.json'))
    for p in pairs:
        valid=sum(r['strict'] for r in rows if r['arm']==p['arm'] and r['qid']==p['qid'])
        if valid==0:p['label']='both_invalid'
        elif valid==1:p['label']='one_valid_one_invalid'
        elif p['label'] in ('one_valid_one_invalid','both_invalid'):p['label']='compatible_structure'
    arms=aggregate(rows,pairs)
    return {'arms':arms,'gate':gate(arms,stage),'status':'post-hoc counterfactual only, primary labels unchanged'}
def main():
    out={}
    e1=STAGES[0]
    out['E1_accept_elliptical_recipient_R050']=calculate(e1,{'R050':{'coverage':{'M1':True}}})
    out['E1_reject_coarse_founder_group_R018']=calculate(e1,{'R018':{'severe_broadness':True,'harmful_merge':True}})
    out['E1_stricter_fragmentation_R048_R032']=calculate(e1,{r:{'severe_fragmentation':True,'harmful_split':True} for r in ('R048','R032')})
    out['E1_require_unresolved_song_possessive']=calculate(e1,{r:{'critical_violations':[{'invariant':'I2','types':['role_identity'],'reason':'Counterfactual stricter possessive ambiguity interpretation.'}],'coverage':{'M4':False}} for r in ('R013','R020')})
    grouping={}
    for stage in STAGES:
        if not (P/stage/'METRICS.json').exists():continue
        m=read(P/stage/'METRICS.json');pairs=read(P/stage/'review/PAIRS.json')
        grouping[stage]={a:{'pair_labels':dict(Counter(p['label'] for p in pairs if p['arm']==a)),
          'same_structure_only':sum(p['label']=='same_structure' for p in pairs if p['arm']==a)/v['qids'],
          'registered_same_or_compatible_and_both_strict':v['stability'],'raw_both_strict':v['both_strict']} for a,v in m['arms'].items()}
    write(P/'analysis/SENSITIVITY.json',{'semantic_counterfactuals':out,'grouping_definition':grouping,
      'denominator':'All registered primary metrics retain every planned slot; no case deletions or response replacement.',
      'limitations':['Single familiar Codex reviewer; partial style-revealing masking, no inter-rater reliability estimate.','Q922 recipient ellipsis is a high-ambiguity coverage judgment, not established semantic corruption.','Q169 artist possessive is accepted as association rather than invented authorship; stricter reading shown separately.','Any E1 corruption advantage is supported by one question, not a large independent error sample.','E1 and E2 test canonicalization, not historical Dynamic-O selection or downstream state alignment.']})
if __name__=='__main__':main()
