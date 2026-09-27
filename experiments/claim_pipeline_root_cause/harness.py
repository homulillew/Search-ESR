"""Diagnostic information-flow DAGs. No imports of production engine or state mutation."""
import asyncio
import copy
import hashlib
import json
from pathlib import Path
import jsonschema

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def canonical(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def digest(x):return hashlib.sha256(canonical(x).encode()).hexdigest()
def file_hash(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def save(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
def normalize(s):return ' '.join(s.split()).casefold()

def bank(split=None):
    rows=read(HERE/'bank/diagnostic.json')+read(HERE/'bank/heldout.json')
    return [p for p in rows if split is None or p['split'] in split]

def evidence(packet,refs=None):
    ws=copy.deepcopy(packet['Observation'])
    if refs is None:return ws
    if len(set(refs))!=len(refs):raise ValueError('duplicate selection/reference')
    existing={w['window_ref'] for w in ws}
    if not set(refs)<=existing:raise ValueError('unobserved window ref')
    return [w for w in ws if w['window_ref'] in refs]

def inputs(role,packet=None,candidate=None,selected=None,inventory=None,windows=None):
    # Allowlists are the treatment. Do not serialize whole packet/provenance/review.
    if role in ['a0_current_reader','a2_selector']:
        return copy.deepcopy({k:packet[k] for k in ['OneGap','C','Observation']})
    if role=='a1_no_c_reader':return copy.deepcopy({k:packet[k] for k in ['OneGap','Observation']})
    if role=='a2_evidence_formulator':
        return {'Evidence':evidence(packet,[s['window_ref'] for s in selected['selections']])}
    if role=='g0_current_grounding':return {'candidate':copy.deepcopy(candidate),'Evidence':copy.deepcopy(windows)}
    if role=='g1_evidence_inventory':return {'Evidence':copy.deepcopy(windows)}
    if role=='g1_candidate_coverage':return {'candidate':copy.deepcopy(candidate),'SourceCommitmentInventory':copy.deepcopy(inventory)}
    raise ValueError(role)

def request(role,payload,config):
    schema=read(HERE/'schemas'/f'{role}.json');prompt=(HERE/'prompts'/f'{role}.txt').read_text()
    return {'model':config['model'],'temperature':config['temperature'],'thinking':config['thinking'],
        'reasoning_effort':config['reasoning_effort'],'max_tokens':config['max_tokens'],
        'stream':False,'response_format':{'type':'json_object'},
        'messages':[{'role':'system','content':prompt+'\nReturn one JSON object matching this schema:\n'+canonical(schema)},
                    {'role':'user','content':canonical(payload)}]}

def validate(role,value,payload):
    jsonschema.Draft202012Validator(read(HERE/'schemas'/f'{role}.json')).validate(value)
    ws=payload.get('Observation',payload.get('Evidence',[]));available={w['window_ref'] for w in ws}
    if role=='a2_selector':
        refs=[s['window_ref'] for s in value['selections']]
        if len(refs)!=len(set(refs)) or not set(refs)<=available:raise ValueError('invalid selections')
    for field in ['findings','facts']:
        for c in value.get(field,[]):
            if not c['statement'].strip() or not set(c['evidence_refs'])<=available:raise ValueError('invalid factual refs/statement')
    return value

async def construct(port,p,arm,stage='E1'):
    meta={'packet_id':p['packet_id'],'qid':p['qid'],'split':p['split'],'arm':arm,'stage':stage,
          'source_hashes':[digest(w) for w in p['Observation']]}
    ident=f"{stage}_{p['packet_id']}_{arm}"
    try:
        role={'A0':'a0_current_reader','A1':'a1_no_c_reader','A2':'a2_selector'}[arm]
        first=await port.call(ident+'_1',role,inputs(role,p),meta)
        if arm=='A2':
            if not first['selections']:return {**meta,'status':'ok','findings':[],'selections':[],'formulator_skipped':True}
            final=await port.call(ident+'_2','a2_evidence_formulator',inputs('a2_evidence_formulator',p,selected=first),meta)
            return {**meta,'status':'ok',**final,'selections':first['selections'],'formulator_skipped':False}
        return {**meta,'status':'ok',**first}
    except Exception as exc:
        return {**meta,'status':'failed','error':type(exc).__name__+': '+str(exc)}

async def run_e1(port,packets):
    if any(p['split']=='H_confirmation' for p in packets):raise ValueError('E3 holdout leakage')
    return await asyncio.gather(*(construct(port,p,a) for p in packets for a in ['A0','A1','A2']))

def export_review(packets,results,out):
    """Display one candidate at a time; archive mapping separately from review."""
    out=Path(out);by={p['packet_id']:p for p in packets};mapping=[]
    for r in results:
        if r['status']!='ok':continue
        p=by[r['packet_id']]
        for i,c in enumerate(r['findings']):
            rid='B_'+digest(['blind-v1',r['packet_id'],r['arm'],i,c])[:24]
            source={'review_id':rid,'Candidate':c,'Observation':evidence(p,c['evidence_refs'])}
            save(out/'source'/f'{rid}.json',source)
            save(out/'relevance'/f'{rid}.json',{**source,'OneGap':p['OneGap'],'C':p['C']})
            mapping.append({'review_id':rid,'packet_id':p['packet_id'],'arm':r['arm'],'index':i})
    save(out/'private_mapping.json',mapping)
    return mapping

def review_candidates(packets,results,mapping,labels):
    by={p['packet_id']:p for p in packets};ms={x['review_id']:x for x in mapping}
    if set(labels)!=set(ms):raise ValueError('incomplete candidate review')
    outputs={(r['packet_id'],r['arm']):r for r in results}
    rows=[]
    for rid,m in ms.items():
        p=by[m['packet_id']];c=outputs[(m['packet_id'],m['arm'])]['findings'][m['index']];l=labels[rid]
        for key in ['source_supported','semantic_strengthening','gap_relevant','duplicate_with_C','gap_useful_if_supported','ambiguous_relation']:
            if type(l.get(key)) is not bool:raise ValueError('missing boolean '+key)
        if l['source_supported'] and l['semantic_strengthening']:raise ValueError('contradictory source labels')
        families={'temporal','identity_entity','source_document','cross_entity','qualifier_quantifier','conjunction_sequence','attribution_modality','role'}
        if not isinstance(l.get('strengthening_type'),list) or not set(l['strengthening_type'])<=families:raise ValueError('invalid strengthening family review')
        if l['semantic_strengthening'] and not l['strengthening_type']:raise ValueError('strengthening type required')
        if l['gap_useful_if_supported'] and not l['gap_relevant']:raise ValueError('useful but irrelevant label conflict')
        if not isinstance(l.get('covered_atom_ids'),list) or not l.get('reason'):raise ValueError('incomplete atom/reason review')
        rows.append({**m,**l,'qid':p['qid'],'split':p['split'],'candidate':c,'Evidence':evidence(p,c['evidence_refs'])})
    return rows

def freeze_e2_candidates(reviewed,historical):
    pools={};unused=[]
    for c in sorted(reviewed+historical,key=digest):
        if c['split']=='H_confirmation':continue
        if not c['source_supported'] and not c['semantic_strengthening']:
            unused.append({'candidate':c['candidate'],'reason':'unsupported non-strengthening; outside primary FAR stratum'});continue
        key=digest([normalize(c['candidate']['statement']),sorted(c['candidate']['evidence_refs']),c['Evidence']])
        label={k:c[k] for k in ['source_supported','semantic_strengthening','ambiguous_relation']}
        if key in pools:
            if label!=pools[key]['label']:raise ValueError('conflicting duplicate source reviews')
            pools[key]['origins'].append({k:c[k] for k in ['packet_id','qid','split']})
        else:pools[key]={'pair_id':'E2_'+key[:24],'candidate':c['candidate'],'Evidence':c['Evidence'],
                'qid':c['qid'],'split':c['split'],'label':label,'origins':[{k:c[k] for k in ['packet_id','qid','split']}],
                'source_review_reason':c['reason']}
    chosen=[]
    # <=15 supported and <=15 strengthened per split. No new negatives or backfill.
    for s in ['D','H_diagnostic']:
        for supported in [True,False]:
            group=sorted((r for r in pools.values() if r['split']==s and r['label']['source_supported']==supported),key=lambda r:r['pair_id'])
            if not group:raise ValueError(f'insufficient E2 source-label stratum: {s} supported={supported}')
            chosen+=group[:15]
    return {'pairs':chosen,'all_unique_pairs':sorted(pools.values(),key=lambda r:r['pair_id']),'excluded':unused,
        'count':len(chosen),'inventory_count':len({digest(r['Evidence']) for r in chosen}),
        'calls':2*len(chosen)+len({digest(r['Evidence']) for r in chosen})}

async def run_e2(port,pairs):
    inventories={}
    async def inventory(pair):
        key=digest(pair['Evidence'])
        if key not in inventories:
            linked=[p for p in pairs if digest(p['Evidence'])==key]
            meta={'stage':'E2','arm':'G1_inventory','evidence_key':key,
                'pair_ids':[p['pair_id'] for p in linked],
                'packet_ids':sorted({o['packet_id'] for p in linked for o in p['origins']}),
                'source_hashes':[digest(w) for w in pair['Evidence']]}
            inventories[key]=asyncio.create_task(port.call('E2_I_'+key[:24],'g1_evidence_inventory',
                inputs('g1_evidence_inventory',windows=pair['Evidence']),meta))
        return await inventories[key]
    async def one(pair,arm):
        meta={'stage':'E2','pair_id':pair['pair_id'],'qid':pair['qid'],'split':pair['split'],'arm':arm,
              'source_hashes':[digest(w) for w in pair['Evidence']]}
        try:
            if arm=='G0':
                role='g0_current_grounding';payload=inputs(role,candidate=pair['candidate'],windows=pair['Evidence'])
            else:
                inv=await inventory(pair);role='g1_candidate_coverage';payload=inputs(role,candidate=pair['candidate'],inventory=inv)
            val=await port.call(pair['pair_id']+'_'+arm,role,payload,meta)
            return {**meta,'status':'ok',**val}
        except Exception as exc:return {**meta,'status':'failed','error':type(exc).__name__+': '+str(exc)}
    return await asyncio.gather(*(one(p,a) for p in pairs for a in ['G0','G1']))

def exact_dedup(findings,claims):
    seen={normalize(c['statement']) for c in claims};kept=[]
    for c in findings:
        n=normalize(c['statement'])
        if n not in seen:kept.append(c);seen.add(n)
    return kept

async def run_e3(port,packets,decision):
    if not decision.get('eligible') or not any(decision['supported'].values()):raise ValueError('E3 gate closed')
    if any(p['split']!='H_confirmation' for p in packets):raise ValueError('E3 requires reserved holdout')
    expected=choose_components(decision['supported'])
    if decision['construction']!=expected['construction'] or decision['grounding']!=expected['grounding']:raise ValueError('components inconsistent with gates')
    async def one(p,pipeline):
        arm='A0' if pipeline=='current' else decision['construction']
        admission='G0' if pipeline=='current' else decision['grounding']
        row=await construct(port,p,arm,'E3_'+pipeline)
        row.update(pipeline=pipeline,grounding=admission)
        if row['status']!='ok':return row
        try:
            # Match production exact-duplicate skip; blinded semantic dedup is an
            # offline endpoint for both arms, not a new runtime mutation policy.
            candidates=exact_dedup(row['findings'],p['C']);admitted=[];decisions=[]
            inventory=None
            if candidates and admission=='G1':
                inventory=await port.call(f"E3_{pipeline}_{p['packet_id']}_inventory",'g1_evidence_inventory',
                    inputs('g1_evidence_inventory',windows=evidence(p)),row_meta(row))
            for i,c in enumerate(candidates):
                role='g0_current_grounding' if admission=='G0' else 'g1_candidate_coverage'
                inp=inputs(role,candidate=c,windows=evidence(p,c['evidence_refs']),inventory=inventory)
                verdict=await port.call(f"E3_{pipeline}_{p['packet_id']}_ground_{i}",role,inp,row_meta(row))
                decisions.append({'candidate':c,**verdict})
                if verdict['verdict']=='supported':admitted.append(c)
            return {**row,'candidate_C':admitted,'admission_decisions':decisions}
        except Exception as exc:return {**row,'status':'failed','error':type(exc).__name__+': '+str(exc)}
    return await asyncio.gather(*(one(p,a) for p in packets for a in ['current','repaired']))

def row_meta(r):return {k:r[k] for k in ['stage','packet_id','qid','split','arm','source_hashes']}
def choose_components(supported):
    return {'construction':'A2' if supported.get('H2') else 'A1' if supported.get('H1') else 'A0',
            'grounding':'G1' if supported.get('H3') else 'G0'}
