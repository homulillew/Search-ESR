"""Exclusive experiment artifacts; Q-only input boundary."""
import hashlib
import json
from pathlib import Path
import subprocess
P = Path(__file__).resolve().parent
ROOT = P.parents[1]
ARMS = ('D0', 'D1', 'D2')
STAGES = ('e1_development', 'e2_fresh')
PROMPTS = dict(zip(ARMS, ('d0_freeform.txt', 'd1_source_anchored.txt', 'd2_extractive_grouping.txt')))
def read(p): return json.loads(Path(p).read_text())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(v): return hashlib.sha256(json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
def rel(p): return str(Path(p).relative_to(ROOT))
def git(*args): return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()
def write(p, v):
    p = Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x') as f:
        f.write(v if isinstance(v, str) else json.dumps(v, ensure_ascii=False, indent=2) + '\n')
def bank(stage=None):
    names = ['DEV_QUESTIONS', 'FRESH_QUESTIONS'] if stage is None else ['DEV_QUESTIONS' if stage == STAGES[0] else 'FRESH_QUESTIONS']
    return {c['qid']: c for n in names for c in read(P/f'e0_reference/{n}.json')}
def input_for(c):
    return {'Original Question': c['question'], 'Addressable Source Units': [dict(unit=u['unit'], text=u['text']) for u in c['source_units']]}
