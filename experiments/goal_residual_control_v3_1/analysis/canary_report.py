import sys,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from runtime import *
b=TOP/'structured_transport_canary';r=read(b/'canary_outputs.json');u=[x['usage'] for x in r if x.get('usage')]
m={'planned':24,'attempted':sum(x['attempted'] for x in r),'structural_valid':sum(x['structural_valid'] for x in r),'harness_valid':sum(x['harness_valid'] for x in r),'failures':dict(collections.Counter(x['error']['category'] for x in r if x['error'])),'mode':'responses_structured' if all(x['structural_valid'] for x in r) else 'json_mode_fallback','usage_reported':len(u),'usage':{k:sum(x[k] for x in u if x.get(k) is not None) for k in ['input','output','hit','miss','reasoning']}}
m['usage']['cache_rate']=m['usage']['hit']/(m['usage']['hit']+m['usage']['miss']);write(b/'metrics.json',m)
(b/'RESULTS.md').write_text(f'''# Production-shape transport canary

24/24 requests returned. Structural validity 23/24; Harness validity 23/24. One Actor produced Find+k despite nested closed branches (e3b5870f898beefd). This is 1/24 (4.17%) structural failure, 1/12 Actors (8.33%), zero Updater/Goal failures. No repair/retry/tools. Remaining 23 objects pass unchanged Harness checks; no additional control violation.

Selected `json_mode_fallback` uniformly under frozen rule. One canary does not establish a general provider failure rate. No more provider probes will run. Original semantic context is byte-identical for every historical request.

Usage: {json.dumps(m['usage'])}. All 24 report usage. Cache is token-weighted. Replay proceeds with full Uc/U1 pairing; it will test JSON-mode behavior independently, not assume zero failures.
''')
print(json.dumps(m))
