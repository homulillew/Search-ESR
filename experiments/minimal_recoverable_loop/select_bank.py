"""Source-only E0 selection. Does not read model answers or reference answers."""
import re
from .common import *
from experiments.ephemeral_obligation_decomposition.source_units import split_units

LEGACY='experiments/evidence_fidelity_loop/evidence_packet/BANK.json'
RECENT='experiments/belief_need_budget_locality_repair/acquisition/trajectories'
# Fixed natural observations covering the task's named risk families; no output-based selection.
RECENT_SLOTS={
    'F07':['2_3','2_5','3_1'],
    'F08':['1_2','1_3','1_4'],
    'F10':['1_2','2_3','2_5'],
    'F11':['2_2'],
    'F13':['1_1','1_2','1_5','2_2','2_3'],
    'F14':['2_1','2_2','2_3','2_4','3_1'],
    'F15':['1_2','2_1','2_2'],
    'F16':['1_4','3_1'],
}
QIDS={'F07':'261','F08':'228','F10':'971','F11':'538','F13':'637','F14':'843','F15':'1259','F16':'922'}

def skeleton(q):
    # Sentence/bullet source spans, never semantic subtraction or rewritten requirements.
    units=split_units(q);merged=[];pending=None
    framing={'I need specific information in one of the research papers.', 'Here are some clues:',
             'I want you to find the name of the series that I am talking about.',
             'Here are various plot points from the series in sequence:',
             "Hey Chat, I'm trying to remember someone's popular name."}
    for u in units:
        if u['text'] in framing:continue
        if re.fullmatch(r'\d+\.',u['text']):
            pending=u['start'];continue
        start=pending if pending is not None else u['start'];pending=None
        merged.append({'source_start':start,'source_end':u['end'],'text':q[start:u['end']]})
    assert pending is None
    return [{'requirement_id':f'R{i+1}',**u} for i,u in enumerate(merged)]

def make_bank():
    bank=[];duplicates=[];seen={}
    for row in read(ROOT/LEGACY):
        o=row['observation'];key=digest([row['qid'],o['url'],o['text']])
        if key in seen:
            duplicates.append({'omitted':row['case_id'],'same_observation_as':seen[key]});continue
        seen[key]=row['case_id']
        source=ROOT/row['historical_origin']['path']
        origin=read(source)
        if row['case_id'].startswith('F1_'):
            old=next(x for x in origin if x['case_id']==row['case_id'][3:])
            assert o['text'] in old['new_observation']['text']
            proof={'path':rel(source),'row_id':old['case_id'],'pointer':'new_observation.text',
                   'relationship':'exact historical window or contiguous historical excerpt','sha256':sha(source)}
        else:
            old=next(x for x in origin if x['review_id']==row['historical_origin']['review_id'])
            matches=[]
            for i,a in enumerate(old['actions']):
                for key_name in ('results','matches'):
                    for j,w in enumerate(a['result'].get(key_name,[])):
                        if w.get('preview',w.get('text'))==o['text']:
                            matches.append({'action_index':i,'collection':key_name,'index':j,'tool':a['name']})
            assert matches,row['case_id']
            proof={'path':rel(source),'row_id':old['review_id'],'sha256':sha(source),'matching_tool_observations':matches}
        bank.append({'observation_id':row['case_id'],'qid':row['qid'],'question':row['raw_question'],
                     'source_observation':{'title':o['title'],'url':o['url'],'text':o['text']},
                     'historical_refs':{'doc_ref':o['doc_ref'],'window_ref':o['window_ref']},
                     'provenance':{'path':LEGACY,'row_id':row['case_id'],'sha256':sha(ROOT/LEGACY),'upstream':proof},
                     'selection_family':'legacy_observation_census'})
    for tag,slots in RECENT_SLOTS.items():
        for slot in slots:
            path=ROOT/RECENT/tag/'calls'/f'writer_{slot}.request.json'
            inp=json.loads(read(path)['request']['messages'][1]['content'])
            o=inp['Observation'];step=int(slot.split('_')[0])
            toolpath=ROOT/RECENT/tag/f'decision{step}_tool.json'
            tool=read(toolpath)
            found=[i for i,z in enumerate(tool['observations']) if all(z.get(k)==v for k,v in o.items())]
            assert len(found)==1,(tag,slot)
            bank.append({'observation_id':f'{tag}_W{slot}','qid':QIDS[tag],'question':inp['Original Question'],
                         'source_observation':{'title':o['title'],'url':o['url'],'text':o['text']},
                         'historical_refs':{'doc_ref':o['doc_ref'],'window_ref':o['window_ref']},
                         'provenance':{'path':rel(path),'sha256':sha(path),'pointer':'request.messages[1].content.Observation',
                                       'upstream':{'path':rel(toolpath),'sha256':sha(toolpath),'observation_index':found[0],'tool':tool['action']['tool']}},
                         'selection_family':'task_named_semantic_risks'})
    assert len(bank)==53 and len({r['qid'] for r in bank})==20
    for i,r in enumerate(bank):
        r['source_id']=f'S{i+1:03d}'
        r['observation_sha256']=text_hash(r['source_observation']['text'])
        r['question_sha256']=text_hash(r['question'])
    write(P/'e0_reference/ADMISSION_BANK.json',bank)
    write(P/'e0_reference/ADMISSION_SELECTION.json',{
        'base':BASE,'rule':'Take all44 legacy evidence_packet observations, collapse exact(qid,url,text) duplicates retaining first historical row; add the25 explicit recent source slots; do not inspect prior writer outcomes to select.',
        'legacy_path':LEGACY,'legacy_raw_count':44,'legacy_unique_observations':28,'recent_slots':RECENT_SLOTS,
        'observations':53,'qids':20,'duplicates_removed':duplicates,
        'notes':'Real historical source text retained byte-for-byte at the selected historical observation boundary. Synthetic examples permitted only in offline invariant tests, never this bank.'})
    questions={r['qid']:r['question'] for r in bank}
    write(P/'e0_reference/QUESTION_SKELETONS.json',[{'qid':q,'Q':text,'R':skeleton(text)} for q,text in sorted(questions.items(),key=lambda x:int(x[0]))])
    print('Admission observations',len(bank),'qids',len(questions))

if __name__=='__main__': make_bank()
