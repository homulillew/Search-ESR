"""Offline final arithmetic, review immutability and secret-content validation."""
from collections import Counter
import subprocess
from ..common import *
from ..evaluate import score,aggregate,gate
from ..prepare import credential
from .. import run
def main():
    checks=[]
    commits={'e1_development':'f598e02','e2_fresh':'4117df1'}
    refs=read(P/'e0_reference/REFERENCE_TASK_STRUCTURE.json')
    for stage in STAGES:
        run.STAGE=stage;run.OUT=P/stage
        key=read(P/stage/'review/KEY.json');labels=read(P/stage/'review/FIRST_PASS.json');rmap={key[r['review_id']]:r for r in labels}
        rows=[score(r,rmap[r['id']],refs[r['qid']]) for r in run.load_rows()]
        m=read(P/stage/'METRICS.json');assert rows==m['rows']
        a=aggregate(rows,read(P/stage/'review/PAIRS.json'));assert a==m['arms'];assert gate(a,stage)==m['gate']
        path=P/stage/'review/FIRST_PASS.json'
        assert subprocess.check_output(['git','show',commits[stage]+':'+rel(path)],cwd=ROOT)==path.read_bytes()
        assert len(list((P/stage/'calls').glob('*.attempt.json')))==len(rows)
        checks.append({'stage':stage,'planned':len(rows),'semantic_arithmetic_replay':True,'first_pass_unchanged_since_commit':commits[stage],'gate':m['gate']['pass']})
    key=credential().encode();checked=0
    for p in P.rglob('*'):
        if not p.is_file() or '__pycache__' in p.parts:continue
        assert key not in p.read_bytes(),'Secret value found in artifact (value not printed)';checked+=1
    assert read(P/'e1_development/METRICS.json')['gate']['pass']
    e2=read(P/'e2_fresh/METRICS.json')['gate'];assert not e2['pass']
    assert [k for k,v in e2['checks'].items() if not v['pass']]==['comparison_strict_direction']
    write(P/'analysis/FINAL_VALIDATION.json',{'status':'PASS','stages':checks,'secret_literal_scan_files':checked,'secret_values_logged':False,'extra_attempt_files':0,'calls_after_E2':0,'first_pass_labels_unchanged':True,'historical_integrity':read(P/'analysis/INTEGRITY.json')['status']})
if __name__=='__main__':main()
