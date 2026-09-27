"""Exclusive new-study artifacts; immutable source history."""
import hashlib
import json
import subprocess
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
BASE = '01895c849a064e9659f121fd05c9af3d4f23bf85'

def read(p):
    return json.loads(Path(p).read_text())

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

def rel(p):
    return str(Path(p).relative_to(ROOT))

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()

def write(p, value):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x') as stream:
        stream.write(value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2)+'\n')

def committed(p):
    assert subprocess.check_output(['git', 'show', 'HEAD:'+rel(p)], cwd=ROOT) == Path(p).read_bytes(), rel(p)

def metric(n, d):
    return {'numerator': n, 'denominator': d, 'value': n/d if d else None}

def verify_history():
    expected = read(P/'analysis/HISTORICAL_HASHES.json')
    for path, value in expected.items():
        assert sha(ROOT/path) == value, path
    return len(expected)
