"""Serialization helper for explicit manual judgments, not an automatic reviewer."""
from ..common import *
def judgment(rid, nodes, reason, *, missing=(), violations=(), invented=(), dependency=True,
             broad=False, fragmented=False, merge=False, split=False, ambiguity='low', notes=None):
    # Each nodes position corresponds to the manually read frozen M1, M2, ... .
    mapping={f'M{i+1}':([n] if isinstance(n,int) else n) for i,n in enumerate(nodes)}
    return {'review_id':rid,'coverage':{m:bool(ns) and m not in missing for m,ns in mapping.items()},
     'coverage_nodes':mapping,'coverage_notes':notes or {},'critical_violations':list(violations),
     'dependency':{'K1':dependency},'invented_semantics':list(invented),
     'granularity':'mixed' if broad and fragmented else 'too_broad' if broad else 'over_fragmented' if fragmented else 'acceptable',
     'severe_broadness':broad,'severe_fragmentation':fragmented,'harmful_merge':merge,'harmful_split':split,
     'ambiguity':ambiguity,'reason':reason}
def violation(invariant,types,nodes,reason):
    return dict(invariant=invariant,types=types,nodes=nodes,reason=reason)
def record(stage,part,rows):write(P/stage/'review'/f'PART_{part}.json',rows)
