import hashlib
import json
import subprocess
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
BASE = '1e5b426b037eda91395664b820ce64cd4f12c708'

def read(p): return json.loads(Path(p).read_text())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(v): return hashlib.sha256(json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
def text_hash(v): return hashlib.sha256(v.encode()).hexdigest()
def rel(p): return str(Path(p).relative_to(ROOT))
def git(*args): return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()
def write(p, v):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x') as f: f.write(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def committed(p):
    assert subprocess.check_output(['git','show','HEAD:'+rel(p)],cwd=ROOT)==Path(p).read_bytes(),rel(p)
def metric(n,d): return {'numerator':n,'denominator':d,'value':n/d if d else None}
def verify_history():
    hs=read(P/'analysis/HISTORICAL_HASHES.json')
    for path,h in hs.items(): assert sha(ROOT/path)==h,path
    return len(hs)
