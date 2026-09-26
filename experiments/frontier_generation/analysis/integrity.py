"""Verify historical immutability, committed freeze and every one-shot request."""
import sys,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from runtime import *

def main():
    base=TOP/'f1_state_sufficiency';f=verify_freeze(base/'freeze.json')
    hist=rd(TOP/'historical_baseline_hashes.json')
    changed=[p for p,h in hist.items() if not (ROOT/p).exists() or sha(ROOT/p)!=h]
    assert not changed,changed
    reqs={r['id']:r for r in rd(base/'requests.json')}
    rows=rd(base/'frontier_outputs.json');events=[json.loads(l) for l in (base/'frontier_events.jsonl').read_text().splitlines()]
    starts=[e for e in events if e['kind']=='request_started'];ends=[e for e in events if e['kind']=='completed']
    assert len(rows)==len(reqs)==144 and len(ends)==144
    assert len({r['id'] for r in rows})==144
    assert max(collections.Counter(e['item']['id'] for e in starts).values())==1
    assert set(e['item']['id'] for e in starts)=={r['id'] for r in rows if r['attempted']}
    for e in starts:
        it=e['item'];assert it==reqs[it['id']]
        assert dg(it['request'])==it['request_sha256']==f['request_hashes'][it['id']]
        assert 'tools' not in it['request']
        for p,h in f['file_hashes'].items():
            # HEAD pins already verified; one shared committed run HEAD suffices below.
            pass
    heads=sorted({e['run_head'] for e in starts})
    for h in heads:
        for p,expected in f['file_hashes'].items():
            data=subprocess.check_output(['git','show',h+':'+p],cwd=ROOT)
            assert hashlib.sha256(data).hexdigest()==expected,(h,p)
    assert set(rd(base/'semantic_review.json'))==set(rd(base/'private_review_key.json'))
    models=collections.Counter(e['event'].get('response',{}).get('model') for e in ends)
    result={'checked_utc':now(),'historical_files':len(hist),'changed_historical_files':changed,
        'planned_calls':len(reqs),'attempted_calls':len(starts),'completion_records':len(ends),
        'duplicate_submissions':0,'tool_calls':0,'run_heads':heads,'returned_model_ids':dict(models),
        'frozen_input_pins':len(f['file_hashes']),'all_request_hashes_match':True,'all_semantic_labels_present':True,
        'limitations':['Single masked reviewer; treatment inferable from input format.',
          'Archived-episode history boundary and inherited legacy States, not full ancestral chronology or fresh U1 State.',
          'No F1 statistical independence across checkpoints/replicates of same qid.']}
    wr(TOP/'INTEGRITY.json',result);print(json.dumps(result,indent=2))

if __name__=='__main__':main()
