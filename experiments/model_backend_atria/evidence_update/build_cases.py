"""Materialize exact raw diagnostic evidence; no model call."""

import hashlib
import json
from pathlib import Path
import sqlite3
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'experiments/search_find_v3b/orthogonal_search'))
from run_partial import checkpoint

HERE=Path(__file__).resolve().parent
DB=ROOT/'BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite'
STATE_EVENTS=ROOT/'experiments/search_find_v3b/verification_state/events.jsonl'

SPECS=[
 ('546_mark_professional_refute','546',9,'D5',
  'Mark Williams turned professional between 1995 and 2006.',
  'refutes','Professional\t1992–present',95,120),
 ('546_mark_maximum_refute','546',9,'D5',
  'Mark Williams had scored the maximum break more than three times.',
  'refutes','Maximum breaks\t3',80,90),
 ('546_ding_professional_support','546',33,'D17',
  'Ding Junhui turned professional between 1995 and 2006.',
  'supports','In 2003, Ding turned professional',100,130),
 ('546_ding_breaks_support','546',33,'D17',
  'Ding Junhui had more than 300 century breaks and more than three maximum breaks.',
  'supports','more than 600 century breaks, including seven maximum breaks',100,100),
 ('546_mark_result_non_support','546',9,'D5',
  'A Mark Williams result source establishes the stated 2023 decider, 4-3, 4-0, then loss sequence.',
  'inconclusive','2021 | Championship League Invitational',150,220),
 ('1094_inter_split_support','1094',45,'D37',
  'Inter Milan was formed after internal disagreements at AC Milan.',
  'supports','In 1908, Milan experienced a split',100,180),
 ('1094_inter_page_irrelevant','1094',69,'D38',
  'A general Inter Milan page identifies the player who took the 95th-minute free kick in the described match.',
  'irrelevant','Inter Milan',0,450),
 ('1094_totti_penalty_refute','1094',45,'D14',
  'The listed 95th-minute Francesco Totti event was a free kick.',
  'refutes','95th-minute penalty from Francesco Totti',100,100),
]


def main():
    target=HERE/'cases.json'
    if target.exists():raise FileExistsError(target)
    con=sqlite3.connect(f'{DB.as_uri()}?mode=ro',uri=True)
    cases=[]
    try:
      for index,(case_id,qid,seq,ref,claim,relation,anchor,left,right) in enumerate(SPECS,1):
        _,prior,_=checkpoint(qid,seq)
        snap=[e['audit']['handles'] for e in prior if e['kind']=='tool_internal'][-1]
        doc=next(x for x in snap['documents'] if x['doc_ref']==ref)
        docid=str(doc['docid'])
        text,url=con.execute('select text,url from documents where docid=?',(docid,)).fetchone()
        sha=hashlib.sha256(text.encode()).hexdigest()
        assert sha==doc['document_sha256']
        pos=text.find(anchor)
        if pos<0:raise ValueError((case_id,anchor))
        start=max(0,pos-left);end=min(len(text),pos+len(anchor)+right)
        span=text[start:end]
        # A duplicate in the original prefix would fail this new-evidence test.
        request,_,_=checkpoint(qid,seq)
        assert span not in json.dumps(request['messages'],ensure_ascii=False)
        cases.append({'case_id':case_id,'qid':qid,'seq':seq,'tentative_claim':claim,
                      'expected_relation':relation,'evidence_kind':'diagnostic_oracle_evidence',
                      'evidence_ref':f'W{900+index}','doc_ref':ref,'docid_private':docid,
                      'document_sha256_private':sha,'url':url,
                      'offset':start,'end_char':end,'evidence_text':span,
                      'evidence_sha256':hashlib.sha256(span.encode()).hexdigest()})
    finally:con.close()
    target.write_text(json.dumps({'purpose':'EvidenceUtilizationUpperBound, not acquisition',
                   'cases':cases},ensure_ascii=False,indent=2)+'\n')
    print('cases',len(cases),'relations',{r:sum(c['expected_relation']==r for c in cases)
                                       for r in ('supports','refutes','inconclusive','irrelevant')})


if __name__=='__main__':main()
