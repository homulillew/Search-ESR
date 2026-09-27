"""Read-only historical/freeze/raw-response/scoring integrity, no API calls."""
import json
import subprocess
from experiments.need_premise_audit.common import P,ROOT,bank,digest,read,rel,sha,write
from experiments.need_premise_audit.run import OUT,load_rows,parse_response
from experiments.need_premise_audit.score import summarize
from experiments.minimal_need_multiquery.run import accounting_summary

def inspect():
    freeze=read(P/'FREEZE.json'); record=read(OUT/'RUN.json'); head=record['head']
    if record['manifest_sha256']!=sha(P/'FREEZE.json'):raise ValueError('Manifest drift')
    for name,expected in freeze['files'].items():
        if sha(ROOT/name)!=expected:raise ValueError('Frozen mutation: '+name)
        if subprocess.check_output(['git','show',head+':'+name],cwd=ROOT)!=(ROOT/name).read_bytes():
            raise ValueError('Uncommitted request input: '+name)
    for name,expected in read(P/'analysis/HISTORICAL_HASHES.json').items():
        if sha(ROOT/name)!=expected:raise ValueError('Historical mutation: '+name)
    jobs=read(OUT/'SCHEDULE.json'); rows=load_rows(); candidates=bank()
    for job,row in zip(jobs,rows):
        path=OUT/'calls'/job['id']
        request=read(path.with_suffix('.request.json'))
        if request['head']!=head or request['request']!=job['request'] or request['request_sha256']!=digest(job['request']):
            raise ValueError('Sent request mismatch')
        response=read(path.with_suffix('.response.json'))
        parsed=parse_response(response['status'],response['body'],job,candidates[job['candidate_id']])
        for key,value in parsed.items():
            if row.get(key)!=value:raise ValueError('Raw/result mismatch: '+job['id']+':'+key)
    for suffix in ('.attempt.json','.request.json','.response.json','.result.json'):
        if {f.name[:-len(suffix)] for f in (OUT/'calls').glob('*'+suffix)}!={j['id'] for j in jobs}:
            raise ValueError('Missing or extra archive files')
    key=read(OUT/'review/KEY.json');review=read(OUT/'review/REVIEW.json')
    if summarize(rows,{key[k]:v for k,v in review.items()})!=read(OUT/'METRICS.json'):
        raise ValueError('Review/metrics inconsistency')
    attest=read(OUT/'review/REVIEW_ATTESTATION.json')
    if attest['review_sha256']!=sha(OUT/'review/REVIEW.json'):raise ValueError('Review changed after attestation')
    return {'status':'PASS','execution_head':head,'manifest_sha256':sha(P/'FREEZE.json'),
            'frozen_files_unchanged':len(freeze['files']),'historical_files_unchanged':len(read(P/'analysis/HISTORICAL_HASHES.json')),
            'planned_attempted_archived':len(jobs),'complete_review_records':len(review),
            'accounting':accounting_summary(rows),'reference_labels_unchanged':True,'tool_calls':0,'retries':0,
            'interpretation_limit':'Mechanical preservation PASS does not mean successful E1 execution. V0 was rejected by provider; its capability/comparative effect is unavailable. V1 independently fails absolute semantic gates.'}

if __name__=='__main__':
    import sys
    result=inspect()
    if '--save' in sys.argv:write(P/'analysis/INTEGRITY.json',result)
    print(json.dumps({k:v for k,v in result.items() if k!='accounting'},indent=2))
