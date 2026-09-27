"""Restore only real prefix observations; pin full source bytes locally, never upload them."""
import copy
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import sqlite3
from .common import *
from llm_chat.raw_windows import RawWindowBuilder, Window
from llm_chat.search_find_v3b_agent import OrthogonalSearchFindTools
from llm_chat.recoverable_loop.tools import ToolBridge
from llm_chat.recoverable_loop.state import State, Claim, Hypothesis, skeleton, append_event, state_from_dict
from llm_chat.recoverable_loop.contracts import validate_decision

SOURCES={}
def load(path):
    SOURCES[str(path)]=sha(ROOT/path);return read(ROOT/path)


def from_audits(audits):
    raw_windows={};discovery={};attempts=[]
    for action,a in audits:
        raw=a['raw_result'];raw=raw if isinstance(raw,list) else [raw]
        ds={(d['docid'],d['document_sha256']):d['doc_ref'] for d in a['handles']['documents']}
        ws={w['source_window_ref']:w['window_ref'] for w in a['handles']['windows']}
        observed=[]
        for raw_w in raw:
            if 'text' not in raw_w:continue
            w=copy.deepcopy(raw_w);w['source_window_ref']=w.pop('window_ref')
            w['window_ref']=ws[w['source_window_ref']];w['doc_ref']=ds[(w['docid'],w['document_sha256'])]
            if w['window_ref'] in raw_windows:
                old=raw_windows[w['window_ref']]
                for key in ['text','offset','end_char','doc_ref','document_sha256']:assert old[key]==w[key]
            raw_windows[w['window_ref']]=w;observed.append(w['window_ref'])
            if action['tool']=='search':discovery.setdefault(w['doc_ref'],w['window_ref'])
        attempts.append({'action':action,'observed_handles':observed,'feedback':'unassessed_historical',
                         'family':None,'inspected_sources':[],'new_source_opportunities':[]})
    reg=audits[-1][1]['handles']
    assert set(raw_windows)=={w['window_ref'] for w in reg['windows']}
    return {'documents':reg['documents'],'windows':[raw_windows[w['window_ref']] for w in reg['windows']],
            'discovery_previews':discovery},attempts


def restore(packet,tokenizer,searcher=None):
    t=OrthogonalSearchFindTools();t.searcher=searcher;t.window_builder=RawWindowBuilder(tokenizer)
    b=ToolBridge(t);reg=packet['registry']
    with sqlite3.connect(f"file:{ROOT/'BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite'}?mode=ro",uri=True) as db:
        for d in reg['documents']:
            text,url=db.execute('select text,url from documents where docid=?',(d['docid'],)).fetchone()
            key=t.window_builder.register(d['docid'],text,url)
            assert key[1]==d['document_sha256'],('changed original document',d['docid'])
            assert t.handles.document(key)[0]==d['doc_ref']
        for w in reg['windows']:
            key=t.handles.resolve_document(w['doc_ref']);doc=t.window_builder.documents[key]
            assert doc['text'][w['offset']:w['end_char']]==w['text']
            t.window_builder.windows[w['source_window_ref']]=Window(key[0],key[1],w['offset'],w['end_char'])
            assert t.handles.window(w['source_window_ref'])[0]==w['window_ref']
        for w in reg['windows']:
            raw={**w,'window_ref':w['source_window_ref']}
            b.evidence.add(b._normalize({'tool':'open','raw_result':raw,'handles':t.handles.snapshot()}))
    t.discovery_previews=copy.deepcopy(reg['discovery_previews'])
    assert set(t.discovery_previews)=={d['doc_ref'] for d in reg['documents']}
    s=state_from_dict(packet['state'])
    for c in s.C:b.evidence.select(c.evidence_refs)
    for h in s.H:b.evidence.select(h.basis_refs)
    return s,b


def prepare():
    target=BASE/'prefixes';target.mkdir(exist_ok=False)
    support=load('experiments/belief_need_budget_locality_repair/bank/CLAIM_SUPPORT_REVIEW.json')
    reviewed={r['statement'] for r in support if r['review']['status']=='supported'}
    packets=[]
    for family,qid,case in [('R2','637','F13'),('R2','228','F08'),('R3','538','F11'),('R3','922','F16')]:
        directory=f'experiments/belief_need_budget_locality_repair/acquisition/trajectories/{case}'
        snap=load(directory+'/S01.json');state=snap['state'];last=int(snap['transition'].split('_')[1]);audits=[]
        for n in range(1,last+1):
            tool=load(directory+f'/decision{n}_tool.json')
            a=tool['action'];audits.append(({'tool':a['tool'],'arguments':{k:v for k,v in a.items() if k!='tool'}},tool['audit']))
        reg,attempts=from_audits(audits)
        rpath=f'experiments/ephemeral_obligation_decomposition/e1_development/calls/D2__Q{qid}__R1.result.json'
        rs=load(rpath)['output']['requirements']
        assert all(c['statement'] in reviewed for c in state['claims'])
        cs=tuple(Claim(f'C{i}',c['statement'],tuple(c['support_refs'])) for i,c in enumerate(state['claims'],1))
        hs=(Hypothesis('H1',state['hypothesis'],'active',()),) if state['hypothesis'] else ()
        s=State(state['question'],skeleton(state['question'],rs),cs,hs)
        for a in attempts[-3:]:s=append_event(s,'step_outcome',a)
        packets.append({'cell_id':family+'_Q'+qid,'family':family,'qid':qid,'state':asdict(s),'registry':reg,
            'forced_first':{'decision':'request_closure'} if family=='R3' else None,
            'provenance':{'snapshot':directory+'/S01.json','transition':snap['transition'],'skeleton':rpath,
              'observation_boundary':'Entire acquisition result already returned before this intra-Writer snapshot; only Claims/H through this snapshot are selected.',
              'seed_claims':'Every statement has historical supported source-relative review; H preserved literally with low authority.'}})
    bank=load('experiments/gap_evidence_claim_loop/single_gap_rollout/BANK.json')
    for qid,ts,limit in [('546','20260922T121742.932067Z',33),('1094','20260922T113202.256169Z',69)]:
        old=next(x for x in bank if x['qid']==qid)
        path=f'experiments/runs/v003a_search_find/qid_{qid}/{ts}/events.jsonl';SOURCES[path]=sha(ROOT/path)
        audits=[];action=None
        with (ROOT/path).open() as f:
            for line in f:
                e=json.loads(line)
                if e['seq']>limit:break
                if e['kind']=='tool_start':action={'tool':e['name'],'arguments':e['arguments']}
                if e['kind']=='tool_internal':audits.append((action,e['audit']))
        reg,attempts=from_audits(audits)
        cs=tuple(Claim(c['claim_id'],c['statement'],tuple(c['evidence_refs'])) for c in old['initial_claims'])
        assert old['prefix_review']['seed_claims_supported']
        s=State(old['raw_question'],skeleton(old['raw_question'],[{'source_spans':[{'text':old['raw_question']}]}]),cs)
        for a in attempts[-3:]:s=append_event(s,'step_outcome',a)
        # A prefix-only, predeclared opportunity, identical across replicates.
        if qid=='546':
            w=next(w for w in reg['windows'] if w['window_ref']=='W31')
            assert w['doc_ref']=='D17'
            p={'doc_ref':'D17','window_ref':'W31','title':w['title'],'preview':w['text'],'uninspected':True}
            s=append_event(s,'step_outcome',{'family':None,'feedback':'unassessed_historical','inspected_sources':[],
                                           'new_source_opportunities':[p],'annotation':'Prefix-only D17 opportunity; not model nomination.'})
        forced={'decision':'acquire','focus_requirement_id':'R1','one_gap':old['active_gap'],'strategy':'LOCATE_SOURCE',
                'hypothesis_ids_under_test':[],'action':copy.deepcopy(audits[-1][0])}
        packets.append({'cell_id':'R1_Q'+qid,'family':'R1','qid':qid,'state':asdict(s),'registry':reg,'forced_first':forced,
            'provenance':{'events':path,'last_seq':limit,'seed_claims':'Source-relative reviewed historical single-gap bank; not a historical C runtime.',
                          'skeleton':'Mechanical whole-Q R1, no new model call','intervention':'Repeat last prefix Search with existing reviewed active gap. No claim that the gap itself is false.'}})
    from transformers import AutoTokenizer
    tokenizer=AutoTokenizer.from_pretrained('/data/model/Qwen3-Embedding-8B',local_files_only=True,use_fast=True)
    reports=[]
    for p in sorted(packets,key=lambda p:p['cell_id']):
        s,b=restore(p,tokenizer)
        if p['forced_first']:validate_decision(p['forced_first'],s,b.tools.handles)
        seed_support=[]
        for c in s.C:
            seed_support.append({'claim':asdict(c),'evidence':[asdict(b.evidence.get(w)) for w in c.evidence_refs]})
        p['prefix_sha256']=digest({'state':p['state'],'registry':p['registry']})
        save(target/(p['cell_id']+'.json'),p)
        save(target/(p['cell_id']+'.seed_review.json'),{'claims':seed_support,'judgment':'Existing source-relative supported labels reused; global closure not asserted.'})
        reports.append({'cell_id':p['cell_id'],'documents':len(p['registry']['documents']),'windows':len(p['registry']['windows']),
                        'claims':len(s.C),'hypotheses':len(s.H),'all_document_hashes_and_raw_spans_verified':True})
    save(BASE/'PREFIX_PREFLIGHT.json',{'sources':SOURCES,'cells':reports,'new_model_calls':0,'new_search_calls':0,
        'no_future_visibility':'Only tool_internal and tool_start events through cutoff; only snapshot C/H. Full source bytes remain local and unavailable to roles until real acquisition.'})
    save(BASE/'SCHEDULE.json',[{'trajectory_id':p['cell_id']+f'__rep{rep}','cell_id':p['cell_id'],'family':p['family'],'replicate':rep}
                               for p in sorted(packets,key=lambda p:p['cell_id']) for rep in [1,2]])
    print(json.dumps(reports,indent=2))

if __name__=='__main__':prepare()
