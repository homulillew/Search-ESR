"""Experiment-local artifact operations; historical experiments are read-only."""
import hashlib
import json
from pathlib import Path
import subprocess

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
OLD = ROOT / 'experiments/minimal_need_multiquery'

def read(path):
    return json.loads(Path(path).read_text())

def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as f:
        f.write(value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

def rel(path):
    return str(Path(path).relative_to(ROOT))

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()

def bank():
    return {c['candidate_id']: c for c in read(P / 'e0_reference/CANDIDATES.json')}

def refs(candidate):
    return {'Q'} | {c['id'] for c in candidate['claims']}

def input_for(candidate):
    return {'Original Question': candidate['question'], 'Verified Claims': candidate['claims'],
            'Working Hypothesis': candidate['hypothesis'], 'Candidate Need': candidate['candidate_need']}
