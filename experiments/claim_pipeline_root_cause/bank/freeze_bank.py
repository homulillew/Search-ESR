"""Validate original bytes, exact observed payloads and all selected provenance."""
import json, subprocess, hashlib
from collections import Counter
from pathlib import Path
from build_inventory import ROOT, BASE_HEAD, save, sha, digest
B=Path(__file__).resolve().parent

def normalized(w):
    w=dict(w)
    if 'ref' in w:w['window_ref']=w.pop('ref')
    w['text_sha256']=hashlib.sha256(w['text'].encode()).hexdigest()
    return w

def texts(x):
    if isinstance(x,dict):
        for k,v in x.items():
            if k=='text' and isinstance(v,str):yield v
            else:yield from texts(v)
    elif isinstance(x,list):
        for v in x:yield from texts(v)

def main():
    inv=json.loads((B/'inventory.json').read_text())
    packets=json.loads((B/'selection.json').read_text())['packets']
    labels=json.loads((B/'annotations.json').read_text())['packets']
    source_hashes=dict(inv['sources']);edges=[];history=[]
    def original(path):
        p=ROOT/path;raw=p.read_bytes()
        assert raw==subprocess.check_output(['git','show',BASE_HEAD+':'+path],cwd=ROOT),path
        source_hashes[path]=sha(p)
        return json.loads(raw)
    for path,h in inv['sources'].items():assert sha(ROOT/path)==h
    for p in packets:
        o=p['origin'];src=original(o['path'])
        if o['path'].endswith('OBSERVATIONS.json'):
            x=src[int(o['pointer'][1:])]
            assert p['OneGap']==x['active_gap'] and p['C']==x['relevant_committed_claims']
            assert p['Observation']==[normalized(x['observation'])]
            old=o['historical_origin'];up=original(old['path'])
            case=next(r for r in up if r['case_id']==old['case_id'])
            upstream_w=normalized(case['observation'])
            # The archived verify-necessity preparation added `date` (text header
            # or corpus registry). It was already visible in that Reader context.
            assert upstream_w=={k:v for k,v in p['Observation'][0].items() if k!='date'}
            prep='experiments/minimal_research_loop/verify_necessity/prepare_bank.py'
            source_hashes[prep]=sha(ROOT/prep)
            older=case['historical_origin'];upstream=original(older['path'])
            assert any(t==p['Observation'][0]['text'] for t in texts(upstream))
            edges.append({'packet_id':p['packet_id'],'context_archive':o,'evidence_archive':old,
                'upstream_observed_text':older,'context_exact':True,'metadata_exact_at_context_archive':True,
                'text_exact_through_upstream':True,'legacy_metadata_derivation':{'path':prep,'added_field':'date','value':p['Observation'][0].get('date')},
                'note':'legacy evidence-fidelity bank may supply corpus-resolved metadata; visible in archived review context, not asserted as original live prefix metadata'})
        else:
            body=json.loads(src['request']['messages'][-1]['content'])
            index=int(o['pointer'].rsplit('/',1)[1])
            assert p['OneGap']==body['OneGap'] and p['C']==body['C']
            assert p['Observation']==[normalized(body['Observation'][index])]
            edges.append({'packet_id':p['packet_id'],'context_archive':o,'context_exact':True,
                'metadata_exact_at_context_archive':True,'text_exact_through_upstream':True})
        assert p['content_sha256']==digest({k:p[k] for k in ['qid','OneGap','C','Observation']})
        for c in p['historical_candidates']:
            raw=original(o['response_path']);findings=json.loads(raw['choices'][0]['message']['content'])['findings']
            assert c in findings
            # Review of actual historical output only; no manufactured negative.
            negative=p['packet_id']=='P_37c827530a066a86'
            history.append({'candidate_id':'HC_'+digest([p['packet_id'],c])[:16],
                'packet_id':p['packet_id'],'qid':p['qid'],'split':p['split'],'candidate':c,
                'Evidence':p['Observation'],'origin':{'commit':BASE_HEAD,'path':o['response_path'],'finding_index':findings.index(c)},
                'source_supported':not negative,'semantic_strengthening':negative,
                'ambiguous_relation':negative,'reason':next(a['reason'] for a in labels if a['packet_id']==p['packet_id'])})
    counts=Counter(p['qid'] for p in packets);assert max(counts.values())<=2
    assert len(packets)==36 and len(counts)>=18
    families=sorted({f for a in labels for f in a['families']});assert len(families)>=6
    splits={s:{'packets':sum(p['split']==s for p in packets),'qids':sorted({p['qid'] for p in packets if p['split']==s},key=int)} for s in ['D','H_diagnostic','H_confirmation']}
    for s,st in splits.items():
        ids={p['packet_id'] for p in packets if p['split']==s};ls=[a for a in labels if a['packet_id'] in ids]
        st['strata']=dict(Counter(a['stratum'] for a in ls));st['useful_atoms']=sum(len(a['required_atoms']) for a in ls)
        st['primary_silence_packets']=sum(a['correct_silence_primary_eligible'] for a in ls)
        assert st['useful_atoms'] and st['primary_silence_packets']
    assert not(set(splits['D']['qids'])&set(splits['H_diagnostic']['qids']))
    assert not(set(splits['H_confirmation']['qids'])&(set(splits['D']['qids'])|set(splits['H_diagnostic']['qids'])))
    save(B/'provenance.json',{'base':BASE_HEAD,'source_file_hashes':source_hashes,'edges':edges})
    save(B/'historical_candidates.json',history)
    save(B/'diagnostic.json',[p for p in packets if p['split']=='D'])
    save(B/'heldout.json',[p for p in packets if p['split']!='D'])
    save(B/'manifest.json',{'base':BASE_HEAD,'audit_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'count':len(packets),'qids':len(counts),'splits':splits,'verified_relation_families':families,
        'context_kinds':dict(Counter(p['context_kind'] for p in packets)),
        'historical_candidates':len(history),'historical_supported':sum(c['source_supported'] for c in history),
        'historical_strengthened':sum(c['semantic_strengthening'] for c in history),
        'files':{str(p.relative_to(B.parent)):sha(p) for p in sorted(B.glob('*')) if p.is_file()},
        'rubric_sha256':sha(B.parent/'REVIEW_RUBRIC.md'),'new_semantic_calls':0,'new_retrieval_calls':0})
    print(json.dumps(splits,indent=2))

if __name__=='__main__':main()
