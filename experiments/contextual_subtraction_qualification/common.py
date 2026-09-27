"""New-stage artifacts only. Historical experiments and frozen inputs are immutable."""
import hashlib,json,subprocess
from pathlib import Path
P=Path(__file__).resolve().parent
ROOT=P.parents[1]
OLD=ROOT/'experiments/claim_requirement_support_alignment'
BASE='50f11b58a554223d8c2ac91a2d0ec8ad41dc1289'
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def rel(p):return str(Path(p).relative_to(ROOT))
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def write(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x') as f:f.write(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def metric(n,d):return {'numerator':n,'denominator':d,'value':n/d if d else None}
def committed(p):assert subprocess.check_output(['git','show','HEAD:'+rel(p)],cwd=ROOT)==Path(p).read_bytes(),rel(p)
def verify_history():
 h=read(P/'analysis/HISTORICAL_HASHES.json')
 for p,s in h.items():assert sha(ROOT/p)==s,p
 return len(h)
