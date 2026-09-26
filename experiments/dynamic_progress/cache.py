"""Operational ephemeral cache. No semantic checks or persistent research fields."""
import copy,hashlib,json

def canonical(question,claims):
    return json.dumps({'question':question,'claims':claims},sort_keys=True,ensure_ascii=False,separators=(',',':'))

def progress_key(question,claims):
    return hashlib.sha256(canonical(question,claims).encode()).hexdigest()

class ProgressCache:
    def __init__(self):
        self.claims_version=0;self.progress_input_hash=None;self.progress_cache=None;self._claims=None
    def decision(self,question,claims,evaluate,**irrelevant):
        # Caller supplies semantic Claims. Provenance/Workspace/Hypothesis never enter evaluator.
        snap=copy.deepcopy(claims)
        if self._claims is None or self._claims != snap:
            self.claims_version+=1;self._claims=snap
        key=progress_key(question,snap)
        if key!=self.progress_input_hash:
            result=evaluate(question,copy.deepcopy(snap))
            self.progress_cache=copy.deepcopy(result);self.progress_input_hash=key
        return copy.deepcopy(self.progress_cache)
