"""Local, exclusive artifact I/O; no semantic state or retrieval changes."""
import hashlib
import json
from pathlib import Path
import subprocess
P = Path(__file__).resolve().parent
ROOT = P.parents[1]
def read(p): return json.loads(Path(p).read_text())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(v): return hashlib.sha256(json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
def rel(p): return str(Path(p).relative_to(ROOT))
def git(*args): return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()
def write(p, v):
 p = Path(p); p.parent.mkdir(parents=True, exist_ok=True)
 with p.open('x') as f:
  f.write(v if isinstance(v, str) else json.dumps(v, ensure_ascii=False, indent=2) + '\n')
def bank(): return {c['case_id']:c for c in read(P/'e0_reference/CASES.json')}
def input_for(c, arm):
 value = {'Local Obligation':c['gold_obligation'], 'Verified Claims':c['claims']}
 if arm == 'G1': value['Working Hypothesis'] = c['belief']['hypothesis']
 return value
