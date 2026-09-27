"""Exclusive experiment artifacts and explicit model-input boundaries."""
import hashlib
import json
from pathlib import Path
import subprocess
P=Path(__file__).resolve().parent
ROOT=P.parents[1]
PREV=ROOT/'experiments/ephemeral_obligation_decomposition'
HIST=ROOT/'experiments/dynamic_local_obligation'
STATUSES=('fully_supported','partially_supported','unsupported')
STAGES=('e1_alignment','e2_selection')
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def rel(p):return str(Path(p).relative_to(ROOT))
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def write(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x') as f:f.write(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def questions():return {c['qid']:c for c in read(PREV/'e0_reference/DEV_QUESTIONS.json')}
def skeletons(arm):
 name={'A0':'ORACLE_RUNTIME_SKELETON','A1':'RUNTIME_SKELETON_D2','D1':'RUNTIME_SKELETON_D1','D2':'RUNTIME_SKELETON_D2'}[arm]
 return read(P/f'e0_addressability/{name}.json')
def bank():return {s['case_id']:s for s in read(P/'e0_reference/STATES.json')}
def runtime_nodes(qid,arm):
 return [{k:v for k,v in n.items() if k in ('requirement_id','source_spans','label')} for n in skeletons(arm)[qid]['requirements']]
