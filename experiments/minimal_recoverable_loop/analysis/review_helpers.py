"""Serialize manually reviewed candidate judgments; never call a model or infer labels."""
from experiments.minimal_recoverable_loop.common import *
from experiments.minimal_recoverable_loop.run import OUT

def packet(start,end,rep=None):
    bank={b['source_id']:b for b in read(P/'e0_reference/ADMISSION_BANK.json')}
    for number in range(start,end+1):
        sid=f'S{number:03d}'
        paths=sorted((OUT/'writer/calls').glob(f'W_{sid}_r*.result.json'))
        if rep is not None:paths=[p for p in paths if f'_r{rep}.' in p.name]
        if not paths:continue
        print('\nSOURCE',sid,json.dumps(bank[sid]['source_observation'],ensure_ascii=False))
        for path in paths:
            row=read(path)
            print(row['id'],'valid',row['valid_output'])
            if not row['valid_output']:continue
            for i,c in enumerate(row['output']['candidate_claims'],1):
                print(i,c['statement'],'\n E:',c['supporting_excerpt'])

def save(sid,rep,n,errors=None,useful=(),obs_proofs=None,excerpt_proofs=None):
    """Caller has manually reviewed all n actual candidates against source and quote."""
    if isinstance(sid,int):sid=f'S{sid:03d}'
    row=read(OUT/'writer/calls'/f'W_{sid}_r{rep}.result.json')
    assert row['valid_output'] and len(row['output']['candidate_claims'])==n
    errors=errors or {};obs_proofs=obs_proofs or {};excerpt_proofs=excerpt_proofs or {}
    assert set(errors)<=set(range(1,n+1))
    records=[]
    for i,c in enumerate(row['output']['candidate_claims'],1):
        error=errors.get(i)
        # Error tuple: observation-entails, excerpt-entails, tags, hardening, reason.
        record={'candidate_id':f"{row['id']}_C{i}",'claim_entailed_by_observation':True,
                'claim_entailed_by_excerpt':True,'error_tags':[],'high_risk':False,
                'candidate_hardening':False,'useful':i in useful,'matched_atom_ids':[],
                'reason':'Manually checked the quoted text and complete observed source: this narrow statement is directly supported; no additional identity, relation or scope was supplied.'}
        if error:
            o,e,t,h,reason=error
            record.update(claim_entailed_by_observation=o,claim_entailed_by_excerpt=e,error_tags=t,
                          high_risk=bool(set(t)-{'other','excerpt_mismatch'}) or h,candidate_hardening=h,reason=reason)
        for atom,groups in obs_proofs.items():
            if any(i in g for g in groups):record['matched_atom_ids'].append(f'{sid}_F{atom}')
        records.append(record)
    atoms=next(r for r in read(P/'e0_reference/ADMISSION_REFERENCE.json') if r['source_id']==sid)['acceptable_claim_atoms']
    proofs=[]
    for atom in atoms:
        num=int(atom['atom_id'].rsplit('F',1)[1]);proof={'atom_id':atom['atom_id'],'replicate':rep}
        for key,groups in [('sufficient_candidate_sets',excerpt_proofs.get(num,[])),('observation_sufficient_candidate_sets',obs_proofs.get(num,[]))]:
            assert all(g and all(1<=i<=n for i in g) for g in groups)
            proof[key]=[[f"{row['id']}_C{i}" for i in g] for g in groups]
        proofs.append(proof)
    write(P/'analysis/candidate_review_parts'/f'{row["id"]}.json',{
        'reviewer':'single task-familiar Codex; content-only, before Admission outcomes',
        'writer_result_sha256':sha(OUT/'writer/calls'/f'{row["id"]}.result.json'),
        'records':records,'atom_support_sets':proofs})

def binding(reason='The complete observation establishes the named referent, but the chosen excerpt omits its antecedent; metadata cannot replace the missing participant proof.'):
    return (True,False,['entity_binding_unproven'],False,reason)

def second_parts(sid):
    if isinstance(sid,int):sid=f'S{sid:03d}'
    a=read(OUT/'writer/calls'/f'W_{sid}_r1.result.json')['output']['candidate_claims']
    b=read(OUT/'writer/calls'/f'W_{sid}_r2.result.json')['output']['candidate_claims']
    review=read(P/'analysis/candidate_review_parts'/f'W_{sid}_r1.json')
    return sid,a,b,review

def delta_packet(start,end):
    for s in range(start,end+1):
        sid,a,b,rev=second_parts(s);lookup={digest(c):i for i,c in enumerate(a,1)}
        print('\n'+sid,'replicate2',len(b),'candidates')
        for i,c in enumerate(b,1):
            old=lookup.get(digest(c))
            if old:print(i,'EXACT_REUSE r1_C'+str(old))
            else:print(i,c['statement'],'\n E:',c['supporting_excerpt'])

def save_second(sid,n,errors=None,useful=None,obs_proofs=None,excerpt_proofs=None):
    from itertools import product
    sid,a,b,rev=second_parts(sid);assert len(b)==n
    lookup={digest(c):i for i,c in enumerate(a,1)}
    inherited={};use=set();mapping={}
    for i,c in enumerate(b,1):
        old=lookup.get(digest(c))
        if not old:continue
        r=rev['records'][old-1];mapping.setdefault(old,[]).append(i)
        if r['useful']:use.add(i)
        if not r['claim_entailed_by_excerpt']:
            inherited[i]=(r['claim_entailed_by_observation'],r['claim_entailed_by_excerpt'],r['error_tags'],r['candidate_hardening'],r['reason'])
    inherit_proofs={k:{} for k in ('sufficient_candidate_sets','observation_sufficient_candidate_sets')}
    for p in rev['atom_support_sets']:
        for field in inherit_proofs:
            groups=[]
            for g in p[field]:
                nums=[int(cid.rsplit('_C',1)[1]) for cid in g]
                if all(i in mapping for i in nums):groups.extend([list(x) for x in product(*(mapping[i] for i in nums))])
            inherit_proofs[field][int(p['atom_id'].rsplit('F',1)[1])]=groups
    inherited.update(errors or {})
    save(sid,2,n,inherited,use if useful is None else useful,
         inherit_proofs['observation_sufficient_candidate_sets'] if obs_proofs is None else obs_proofs,
         inherit_proofs['sufficient_candidate_sets'] if excerpt_proofs is None else excerpt_proofs)

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('start',type=int);ap.add_argument('end',type=int);ap.add_argument('--rep',type=int);ap.add_argument('--delta',action='store_true')
    a=ap.parse_args();delta_packet(a.start,a.end) if a.delta else packet(a.start,a.end,a.rep)
