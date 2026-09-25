"""Summarize immutable online updater calls and offline proposal reviews."""
import sys
from pathlib import Path
BASE=Path(__file__).resolve().parent
TOP=BASE.parent
sys.path.insert(0,str(TOP))
from common import read,write

def metrics(rows):
    p=[v for row in rows for v in row['proposals']]
    n=len(p)
    return {'cases':len(rows),'distinct_qids':len({r['qid'] for r in rows}),
      'proposals':n,'supported':sum(v['source_supported'] for v in p),
      'decision_relevant':sum(v['decision_relevant'] for v in p),
      'supported_and_relevant':sum(v['source_supported'] and v['decision_relevant'] for v in p),
      'incidental_or_marginal':sum(not v['decision_relevant'] for v in p),
      'over_specific':sum(v['over_specific'] for v in p),
      'target_leak_absent_from_observation':sum(v['target_leak'] for v in p),
      'oracle_binding_recovered':sum(r['oracle_binding_recovered'] for r in rows)}

def main():
    r=read(BASE/'REVIEWS.json');o=read(BASE/'corrected/OUTPUTS.json')
    h=sum((x.get('usage') or {}).get('prompt_cache_hit_tokens',0) for x in o)
    m=sum((x.get('usage') or {}).get('prompt_cache_miss_tokens',0) for x in o)
    out={'all':metrics(r),'provisional_upper_bound':metrics([x for x in r if x['case_id'] in
      {'U1_B03','U1_C01','U1_C03','U1_C05'}]),
      'valid_calls':sum(x['output'] is not None for x in o),
      'cache':{'hit_tokens':h,'miss_tokens':m,'hit_rate':round(h/(h+m),4) if h+m else None}}
    write(BASE/'summary.json',out)
    print(out['all'])

if __name__=='__main__':main()
