"""Read-only historical inputs and exclusive experiment artifacts."""
import hashlib,json,subprocess
from pathlib import Path
P=Path(__file__).resolve().parent
ROOT=P.parents[1]
OLD=ROOT/'experiments/skeleton_state_alignment'
PREV=ROOT/'experiments/recoverable_control_equivalence'
BASE='1f5536d54bc963e27583368dbed1d8356e012ee9'
F='fully_supported'
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def rel(p):return str(Path(p).relative_to(ROOT))
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def write(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x') as f:f.write(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def metric(n,d):return {'numerator':n,'denominator':d,'value':n/d if d else None}
def committed(p,head=None):assert subprocess.check_output(['git','show',(head or git('rev-parse','HEAD'))+':'+rel(p)],cwd=ROOT)==Path(p).read_bytes(),rel(p)
def verify_history():
 history=read(P/'analysis/HISTORICAL_HASHES.json')
 for name,h in history.items():assert sha(ROOT/name)==h,name
 return len(history)
