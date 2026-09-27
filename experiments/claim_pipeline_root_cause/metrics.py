"""Review-driven metrics: never use lexical similarity as an entailment judge."""
from collections import defaultdict
from .harness import normalize, choose_components

def fraction(num,den):return {'numerator':num,'denominator':den,'rate':num/den if den else None}
def mean(xs):return sum(xs)/len(xs) if xs else None
def error_reduction(old,new):return (old-new)/old if old is not None and old>0 and new is not None else None

def e1(packets,results,reviewed,annotations):
    by={p['packet_id']:p for p in packets};anns={a['packet_id']:a for a in annotations}
    cs=defaultdict(list)
    for c in reviewed:cs[(c['packet_id'],c['arm'])].append(c)
    rows=[]
    if len({(r['packet_id'],r['arm']) for r in results})!=len(results):raise ValueError('duplicate arm/packet result')
    for r in results:
        p=by[r['packet_id']];a=anns[r['packet_id']];cands=sorted(cs[(r['packet_id'],r['arm'])],key=lambda c:c['index'])
        if r['status']=='ok' and len(cands)!=len(r['findings']):raise ValueError('missing candidate review')
        allowed={x['atom_id'] for x in a['required_atoms']};seen={normalize(c['statement']) for c in p['C']};groups=set();kept=[]
        for c in cands:
            if not set(c['covered_atom_ids'])<=allowed:raise ValueError('foreign/future atom')
            s=normalize(c['candidate']['statement']);group=c.get('duplicate_group') or 'single:'+str(c['index'])
            if c['duplicate_with_C'] or s in seen or group in groups:continue
            kept.append(c);seen.add(s);groups.add(group)
        covered=set().union(*(set(c['covered_atom_ids']) for c in kept if c['source_supported'] and c['gap_relevant'])) if kept else set()
        rows.append({'packet_id':p['packet_id'],'qid':p['qid'],'split':p['split'],'arm':r['arm'],'status':r['status'],
            'context_kind':p['context_kind'],'families':a['families'],'C_nonempty':bool(p['C']),'stratum':a.get('stratum','synthetic_test'),
            'raw_count':len(cands),'raw_strengthened':sum(c['semantic_strengthening'] and not c['source_supported'] for c in cands),
            'raw_supported':sum(c['source_supported'] for c in cands),'raw_relevant':sum(c['gap_relevant'] for c in cands),
            'dedup_count':len(kept),'dedup_supported':sum(c['source_supported'] for c in kept),
            'dedup_strengthened':sum(c['semantic_strengthening'] and not c['source_supported'] for c in kept),
            'covered_atoms':len(covered),'required_atoms':len(allowed),'silence_eligible':a['correct_silence_primary_eligible'],
            'raw_silent':r['status']=='ok' and not cands,'dedup_silent':r['status']=='ok' and not kept})
    def aggregate(rs):
        valid=[r for r in rs if r['status']=='ok'];total=sum(r['raw_count'] for r in valid);dedup=sum(r['dedup_count'] for r in valid)
        metrics={'packets':len(rs),'failures':len(rs)-len(valid),
            'FSSR':fraction(sum(r['raw_strengthened'] for r in valid),total),
            'SSP':fraction(sum(r['raw_supported'] for r in valid),total),
            'gap_relevance_precision':fraction(sum(r['raw_relevant'] for r in valid),total),
            'GRSR':fraction(sum(r['covered_atoms'] for r in valid),sum(r['required_atoms'] for r in rs)),
            'correct_silence_raw':fraction(sum(r['raw_silent'] and r['silence_eligible'] for r in valid),sum(r['silence_eligible'] for r in rs)),
            'correct_silence_dedup':fraction(sum(r['dedup_silent'] and r['silence_eligible'] for r in valid),sum(r['silence_eligible'] for r in rs)),
            'claim_bloat':fraction(total,len(valid)),'dedup_claim_bloat':fraction(dedup,len(valid)),
            'dedup_FSSR':fraction(sum(r['dedup_strengthened'] for r in valid),dedup),
            'dedup_SSP':fraction(sum(r['dedup_supported'] for r in valid),dedup)}
        if metrics['failures']:
            for v in metrics.values():
                if isinstance(v,dict):v.update(rate=None,incomplete=True)
        return metrics
    tables={s:{a:aggregate([r for r in rows if r['arm']==a and (s=='pooled' or r['split']==s)]) for a in ['A0','A1','A2']} for s in ['pooled','D','H_diagnostic']}
    sensitivity={field:{str(value):{a:aggregate([r for r in rows if r['arm']==a and (value in r[field] if field=='families' else r[field]==value)]) for a in ['A0','A1','A2']} for value in sorted({v for r in rows for v in (r[field] if field=='families' else [r[field]])})} for field in ['context_kind','families','C_nonempty','stratum']}
    contrasts={}
    complete={(r['packet_id'],r['arm']) for r in rows}=={(p['packet_id'],a) for p in packets for a in ['A0','A1','A2']} and all(r['status']=='ok' for r in rows)
    for h,old,new in [('H1','A0','A1'),('H2','A1','A2')]:
        pairs=[]
        for p in packets:
            sub={r['arm']:r for r in rows if r['packet_id']==p['packet_id']}
            if old in sub and new in sub and sub[old]['status']==sub[new]['status']=='ok':
                pairs.append({'packet_id':p['packet_id'],'qid':p['qid'],'split':p['split'],
                    'strengthened_count_delta':sub[new]['raw_strengthened']-sub[old]['raw_strengthened'],
                    'covered_atom_delta':sub[new]['covered_atoms']-sub[old]['covered_atoms'],
                    'candidate_count_delta':sub[new]['raw_count']-sub[old]['raw_count']})
        clustered={q:mean([r['strengthened_count_delta'] for r in pairs if r['qid']==q]) for q in sorted({r['qid'] for r in pairs})}
        gate=complete;details={}
        for split in ['pooled','H_diagnostic']:
            b=tables[split][old];v=tables[split][new];reduction=error_reduction(b['FSSR']['rate'],v['FSSR']['rate'])
            recall_ok=b['GRSR']['rate'] is not None and v['GRSR']['rate'] is not None and v['GRSR']['rate']>=b['GRSR']['rate']-.10
            rel_ok=h!='H2' or (b['gap_relevance_precision']['rate'] is not None and v['gap_relevance_precision']['rate'] is not None and v['gap_relevance_precision']['rate']>=b['gap_relevance_precision']['rate']-.10)
            pp=[r for r in pairs if split=='pooled' or r['split']==split];qs={r['qid'] for r in pp}
            qdelta=mean([clustered[q] for q in qs]);pdelta=mean([r['strengthened_count_delta'] for r in pp])
            passed=reduction is not None and reduction>=(.30 if split=='pooled' else 0) and reduction>0 and recall_ok and rel_ok and qdelta is not None and qdelta<0 and pdelta<0
            details[split]={'relative_FSSR_reduction':reduction,'recall_guard':recall_ok,'relevance_guard':rel_ok,'qid_mean_delta':qdelta,'packet_mean_delta':pdelta,'pass':passed};gate &= passed
        contrasts[h]={'supported':bool(gate),'paired_packets':pairs,'qid_mean_deltas':clustered,'gate_details':details}
    return {'complete':complete,'tables':tables,'sensitivity':sensitivity,'packet_rows':rows,'hypotheses':contrasts}

def e2(pairs,results):
    by={(r['pair_id'],r['arm']):r for r in results}
    if len(by)!=len(results):raise ValueError('duplicate pair result')
    complete=set(by)=={(p['pair_id'],a) for p in pairs for a in ['G0','G1']} and all(r['status']=='ok' for r in results)
    tables={};paired=[]
    for s in ['pooled','D','H_diagnostic']:
        pp=[p for p in pairs if s=='pooled' or p['split']==s];tables[s]={}
        for arm in ['G0','G1']:
            def admit(p):
                r=by.get((p['pair_id'],arm),{});return r.get('status')=='ok' and r.get('verdict')=='supported'
            neg=[p for p in pp if p['label']['semantic_strengthening'] and not p['label']['source_supported']]
            pos=[p for p in pp if p['label']['source_supported']];amb=[p for p in pp if p['label']['ambiguous_relation']]
            tables[s][arm]={'FAR':fraction(sum(admit(p) for p in neg),len(neg)),
                'TPR':fraction(sum(admit(p) for p in pos),len(pos)),
                'ambiguous_admit':fraction(sum(admit(p) for p in amb),len(amb))}
    for p in pairs:
        a,b=(by.get((p['pair_id'],arm),{}) for arm in ['G0','G1'])
        if a.get('status')==b.get('status')=='ok':
            bad=not p['label']['source_supported'] and p['label']['semantic_strengthening']
            delta=int(b['verdict']=='supported')-int(a['verdict']=='supported')
            paired.append({'pair_id':p['pair_id'],'qid':p['qid'],'split':p['split'],'negative':bad,
                'admit_delta':delta,'anchoring_rescue':bad and delta==-1})
    details={};gate=complete
    for s in ['pooled','H_diagnostic']:
        a=tables[s]['G0'];b=tables[s]['G1'];reduction=error_reduction(a['FAR']['rate'],b['FAR']['rate'])
        pp=[r for r in paired if r['negative'] and (s=='pooled' or r['split']==s)]
        qs={r['qid'] for r in pp};qd={q:mean([r['admit_delta'] for r in pp if r['qid']==q]) for q in qs}
        qdelta=mean(list(qd.values()));pdelta=mean([r['admit_delta'] for r in pp])
        passed=reduction is not None and reduction>=(.5 if s=='pooled' else 0) and reduction>0 and b['TPR']['rate'] is not None and b['TPR']['rate']>=.85 and qdelta is not None and qdelta<0 and pdelta<0
        details[s]={'relative_FAR_reduction':reduction,'qid_mean_deltas':qd,'qid_mean_delta':qdelta,'packet_pair_mean_delta':pdelta,'pass':passed};gate &= passed
    if not complete:
        for arms in tables.values():
            for metrics in arms.values():
                for v in metrics.values():v.update(rate=None,incomplete=True)
    return {'complete':complete,'tables':tables,'paired_candidates':paired,'anchoring_rescue':sum(r['anchoring_rescue'] for r in paired),'supported':bool(gate),'gate_details':details}

def integrated_decision(e1_report,e2_report):
    supported={h:r['supported'] for h,r in e1_report['hypotheses'].items()}
    supported['H3']=e2_report['supported']
    return {'eligible':e1_report['complete'] and e2_report['complete'] and any(supported.values()),
            'supported':supported,**choose_components(supported),
            'interpretation':'structural intervention evidence; no factorial interaction inference'}

def e3(packets,results,reviewed,annotations):
    # All admitted candidates count for false-authority before semantic dedup.
    mapped=[]
    for r in results:
        mapped.append({**r,'arm':{'current':'A0','repaired':'A1'}[r['pipeline']]})
    reviews=[{**c,'arm':{'current':'A0','repaired':'A1'}[c['arm']]} for c in reviewed]
    admitted_reviews=[];admitted_results=[]
    for r in mapped:
        candidates=r.get('candidate_C',[])
        pool=sorted([c for c in reviews if c['packet_id']==r['packet_id'] and c['arm']==r['arm']],key=lambda c:c['index'])
        cs=[]
        for candidate in candidates:
            match=next((c for c in pool if c['candidate']==candidate),None)
            if match is not None:cs.append(match);pool.remove(match)
        if r['status']=='ok' and len(cs)!=len(candidates):raise ValueError('missing authoritative candidate review')
        admitted_reviews += [{**c,'index':i} for i,c in enumerate(cs)]
        admitted_results.append({**r,'findings':candidates})
    report=e1(packets,admitted_results,admitted_reviews,annotations)
    # E1 helper's three-arm completeness is not used for this two-pipeline stage.
    complete=len(results)==2*len(packets) and {(r['packet_id'],r['pipeline']) for r in results}=={(p['packet_id'],a) for p in packets for a in ['current','repaired']} and all(r['status']=='ok' for r in results)
    false={arm:sum(not c['source_supported'] for c in admitted_reviews if c['arm']==arm) for arm in ['A0','A1']}
    stats=report['tables']['pooled']['A1'];vals=[stats[k]['rate'] for k in ['SSP','GRSR','correct_silence_dedup']]
    passed=complete and false['A1']==0 and all(v is not None for v in vals) and vals[0]>=.95 and vals[1]>=.80 and vals[2]>=.80
    return {'complete':complete,'pass':passed,'false_authoritative_C':{'current':false['A0'],'repaired':false['A1']},
        'tables':{'current':report['tables']['pooled']['A0'],'repaired':stats},'packet_rows':report['packet_rows'],
        'scope':'diagnostic candidate C only; no production state mutation'}
