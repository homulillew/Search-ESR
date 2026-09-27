"""Local append-only artifacts; all historical experiments are read-only."""
import hashlib
import json
import subprocess
from pathlib import Path
P = Path(__file__).resolve().parent
ROOT = P.parents[1]
OLD = ROOT / 'experiments/skeleton_state_alignment'
BASE = 'dd442dd62082e5923c98bd553b38fc4de3ad309d'
F = 'fully_supported'
STATUSES = {F, 'partially_supported', 'unsupported'}
def read(p): return json.loads(Path(p).read_text())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(v): return hashlib.sha256(json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
def rel(p): return str(Path(p).relative_to(ROOT))
def git(*args): return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()
def write(p, value):
    p = Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x') as f: f.write(value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2)+'\n')
def metric(n,d): return {'numerator':n, 'denominator':d, 'value': n/d if d else None}
def project(status):
    if status not in STATUSES: raise ValueError('Unknown status; no default-to-OPEN repair')
    return 'CLOSED' if status == F else 'OPEN'
def committed(p, head=None):
    assert subprocess.check_output(['git','show',(head or git('rev-parse','HEAD'))+':'+rel(p)],cwd=ROOT)==Path(p).read_bytes(), 'Uncommitted '+rel(p)
def verify_sources():
    manifest=read(P/'e0_control_equivalence/SOURCE_MANIFEST.json')
    for name,h in manifest['files'].items(): assert sha(ROOT/name)==h, name
    history=read(P/'analysis/HISTORICAL_HASHES.json')
    for name,h in history.items(): assert sha(ROOT/name)==h, name
    return {'source_files_verified':len(manifest['files']), 'historical_files_unchanged':len(history)}
