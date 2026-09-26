"""Offline cache prototype only; no semantic judgments and no production integration."""
import hashlib,json,copy

def progress_key(question,claims):
    return hashlib.sha256(json.dumps({'Original Question':question,'Verified Claims':[c['statement'] for c in claims]},ensure_ascii=False,sort_keys=True).encode()).hexdigest()

class ProgressCache:
    def __init__(self):self.key=None;self.light=None;self.audit=None
    def observe(self,question,claims,**irrelevant):
        key=progress_key(question,claims)
        if key!=self.key:self.key=key;self.light=None;self.audit=None
        return key
    def put(self,kind,value):
        assert kind in ['light','audit'];setattr(self,kind,copy.deepcopy(value))
    def get(self,kind):return copy.deepcopy(getattr(self,kind))
    def audit_needed(self,proposes_stop):return bool(proposes_stop and self.audit is None)

def decision(light,audit):
    # Transport/contract failure cannot authorize STOP; failure is still scored.
    return bool(light and light['resolved'] and audit and audit['confirmed'])
