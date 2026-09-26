"""Explicit single-reviewer judgements, separated from production state."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from runtime import *
b=TOP/'admission_replay'
packets={r['review_id']:r for r in read(b/'OUTPUT_REVIEW_PACKETS.json')};gold={r['packet_id']:r for r in read(b/'GOLD_ADMISSION_ATOMS.json')}
reviews=read(b/'REVIEWS.json') if (b/'REVIEWS.json').exists() else {}
def mark(uid,codes,captured=(),hyp='correct_keep',reason='',scope=()):
    p=packets[uid];o=p['output'];g=gold[p['packet_id']]
    assert o is not None and len(codes)==len(o['claims_to_add']),(uid,codes,o)
    # S=source-supported, R=decision-relevant, N=novel; missing letter is false.
    cl=[]
    for i,(s,c) in enumerate(zip(o['claims_to_add'],codes)):
        cl.append({'statement':s,'source_supported':'S' in c,'decision_relevant':'R' in c,'novel':'N' in c,
          'scope_preserved':i not in scope,'incidental':'R' not in c,
          'reason':reason or g['reason']})
    ids=[f"A{p['packet_index']:02}_{j}" for j in captured]
    assert set(ids)<={a['atom_id'] for a in g['atoms']}
    reviews[uid]={'packet_id':p['packet_id'],'claims':cl,'captured_atoms':ids,'hypothesis_verdict':hyp,
      'hypothesis_reason':reason or g['reason'],'no_claim_expected':g['no_new_claim_expected'],
      'correct_empty_admission':len(cl)==0 and g['no_new_claim_expected'],
      'reviewer':'single Codex; arm-masked output queue; historical familiarity remains'}

def save():write(b/'REVIEWS.json',reviews)
