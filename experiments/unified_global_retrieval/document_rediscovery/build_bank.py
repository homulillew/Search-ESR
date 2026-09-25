"""Freeze source-grounded checkpoint/Gap cells before query-model calls."""
import hashlib
import json
import sqlite3
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OBS = json.loads((ROOT / 'experiments/minimal_research_loop/verify_necessity/OBSERVATIONS.json').read_text())
BY_ID = {x['case_id']: x for x in OBS}
DB = sqlite3.connect(ROOT / 'BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite')

# (type, qid, frozen-observation checkpoint, sufficient corpus docid,
#  semantic Gap, exact supporting anchor, optional prefix-supported hypothesis)
SPECS = [
 ('A','387','E1_F1_T1_387','5266',"What was the storage capacity of Dean Dodrill's gaming PC?",'5TB of Storage',None),
 ('A','387','E1_F1_T1_387','5266',"How much RAM did Dean Dodrill's gaming PC have?",'8GB RAM',None),
 ('A','517','E1_F1_T1_517','67431',"What year was the actor known as Peter King born?",'25 May 1978',None),
 ('A','435','E1_F1_T1_435','43657',"At what age did Oliver Mtukudzi die?",'age of 66',None),
 ('A','435','E1_F1_T1_435','43657',"Did the retrospective describe Oliver Mtukudzi as having made more than 60 albums?",'more than 60 albums',None),
 ('A','177','E1_F1_T1_177','86819',"How many players did Rangers sign ahead of the 2022/23 NPFL season?",'signed 13 new players',None),
 ('A','580','E1_F1_T1_580','78633',"Which numbered season-four episode has Gretchen visiting home for the baby's birth?",'seventh episode of Season 4',None),
 ('A','1094','E1_F1_T1_1094','17992',"Which two teams played the match with the 95th-minute free kick?",'Paris Saint Germain to a 4-3 win over Lille',None),
 ('A','546','E1_F1_T1_546','84118',"Who did Ding Junhui beat 4-3 in the opening 2023 English Open match?",'4-3 victory over Ma Hailong',None),
 ('A','311','E1_F1_T5_311','20521',"What is the native Argentine title of the cartoon described in the question?",'native_name: Las aventuras de Hijitus',None),
 ('A','186','E1_F1_T5_186','39978',"Which software publisher is listed for the November 1992 DOS game?",'Albino Frog Software',None),
 ('A','1034','E1_F1_T1_1034','24300',"Which person in the 2021 article worked as both singer and model?",'Heart Evangelista',None),

 ('B','517','E1_F1_T1_517','67431',"What exact filmography role did Peter King play in The Constant Gardener?",'Policeman 1','Peter King'),
 ('B','387','E1_F1_T1_387','5266',"What size printing paper did Dean Dodrill use for animation?",'normal 8x11','Dean Dodrill'),
 ('B','435','E1_F1_T1_435','43657',"Which song by Oliver Mtukudzi was interpreted as urging Robert Mugabe to retire?",'Wasakara','Oliver Mtukudzi'),
 ('B','1094','E1_F1_T1_1094','17992',"Which PSG player scored the second goal in the 4-3 Lille match?", "Neymar's goal",'PSG'),
 ('B','311','E1_F1_T5_311','20521',"Which object gives Hijitus his magical powers in the Argentine cartoon?",'sombreritus','Hijitus'),
 ('B','186','E1_F1_T5_186','39978',"What was the planned name of the second Galacta episode?",'Last Stand on Mars','Galacta'),
 ('B','1034','E1_F1_T1_1034','24300',"What role did Heart Evangelista play on the programme mentioned near the end of the article?",'Missy Sandejas','Heart Evangelista'),
 ('B','546','E1_F1_T5_546','38231',"Which youth snooker championship did Ding Junhui reach the semi-finals of in 2003?",'semi-finals of the IBSF World Under-21 Championship','Ding Junhui'),

 ('C','435','E1_F1_T2_435','56154',"How many albums did the May 2017 Forbes Africa feature attribute to the musician in the question?",'65 albums',None),
 ('C','435','E1_F1_T2_435','48151',"Was the age-66 Zimbabwean musician included in Forbes Africa's 2017 richest-musicians list?",'Oliver Tuku Mtukudzi',None),
 ('C','435','E1_F1_T2_435','51535',"How many albums did a 2017 richest-African-musicians report attribute to the musician in the question?",'65 albums',None),
 ('C','177','E1_F1_T4_177','83572',"Where did the club in the question finish in the 2014 NPFL table, and what was its goal difference?",'Enugu Rangers',None),
 ('C','177','E1_F1_T4_177','37053',"Which club won the 2016 Nigeria Professional Football League?",'Enugu Rangers',None),
 ('C','580','F3_P12_W5','35134',"Which season-one episode involved Gretchen's friends convincing Jimmy to take her on a date?",'convinced by Gretchen',None),
 ('C','580','F3_P12_W5','73919',"Which season-three finale involved Edgar's sacrifice?", "Edgar's sacrifice",None),
 ('C','311','E1_F1_T4_311','20521',"What is the native Argentine title of the educational cartoon described in the question?",'native_name: Las aventuras de Hijitus',None),
 ('C','186','E1_F1_T4_186','39978',"What November 1992 DOS shareware game was published by the amphibian-named company?",'Galacta: The Battle for Saturn',None),
 ('C','517','E1_F1_T4_517','67431',"Which actor played Policeman 1 in the 2005 film The Constant Gardener?",'Policeman 1',None),
 ('C','546','E1_F1_T4_546','38231',"When did the candidate snooker player in the question turn professional, and how many maximum breaks did he make?",'professional: 2003',None),
 ('C','1094','E1_F1_T3_1094','24763',"Was Paris Saint-Germain formed by a merger of Paris Football Club and Stade Saint-Germain?",'PSG were formed in 1970 after the merger',None),

 ('D','435','E1_F1_T1_435','56154',"How many albums did the May 2017 Forbes Africa feature attribute to Oliver Mtukudzi?",'65 albums','Oliver Mtukudzi'),
 ('D','435','E1_F1_T1_435','48151',"Was Oliver Mtukudzi included in Forbes Africa's 2017 richest-musicians list?",'Oliver Tuku Mtukudzi','Oliver Mtukudzi'),
 ('D','177','E1_F1_T1_177','83572',"What was Enugu Rangers' position in the 2014 NPFL table?",'Enugu Rangers','Rangers'),
 ('D','177','E1_F1_T1_177','83572',"What was Enugu Rangers' goal difference in the 2014 NPFL table?",'Enugu Rangers','Rangers'),
 ('D','177','E1_F1_T1_177','37053',"Did Enugu Rangers win the 2016 Nigeria Professional Football League?",'winners: Enugu Rangers','Rangers'),
 ('D','580','E1_F1_T1_580','35134',"Which season-one episode involved Gretchen's friends convincing Jimmy to take her on a date?",'convinced by Gretchen',None),
 ('D','580','E1_F1_T1_580','73919',"Which season-three finale involved Edgar's sacrifice?", "Edgar's sacrifice",None),
 ('D','546','E1_F1_T1_546','38231',"In what year did Ding Junhui turn professional?",'professional: 2003','Ding Junhui'),
]

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()

def main():
    assert len(SPECS) == 40
    assert Counter(s[0] for s in SPECS) == {'A':12,'B':8,'C':12,'D':8}
    assert len({s[1] for s in SPECS}) >= 10
    required_urls={BY_ID[s[2]]['observation']['url'] for s in SPECS}
    url_to_ids={u:[] for u in required_urls}
    for docid,url in DB.execute('SELECT docid,url FROM documents'):
        if url in url_to_ids:url_to_ids[url].append(docid)
    docs = {}
    def get(docid):
        if docid not in docs:
            row = DB.execute('SELECT text,url FROM documents WHERE docid=?',(docid,)).fetchone()
            assert row, docid
            docs[docid] = row
        return docs[docid]
    bank=[]; truth=[]
    for n,(kind,qid,source,target,gap,anchor,hypothesis) in enumerate(SPECS,1):
        obs=BY_ID[source]; assert obs['qid']==qid, (qid,source)
        old_url=obs['observation']['url']; old_text=obs['observation']['text']
        oldids=url_to_ids[old_url]
        assert len(oldids)==1, (source,oldids)
        oldid=oldids[0];full,url=get(oldid)
        assert old_text in full,(source,'window not in corpus')
        target_text,target_url=get(target)
        assert anchor.lower() in target_text.lower(),(source,target,anchor)
        assert (kind in ('A','B')) == (oldid==target),(kind,source,oldid,target)
        if kind=='A':assert anchor.lower() in old_text.lower(),(source,anchor)
        if kind=='B':assert anchor.lower() not in old_text.lower(),(source,anchor)
        if kind in ('C','D'):assert anchor.lower() not in full.lower(),(source,anchor)
        if hypothesis:assert hypothesis.lower() in old_text.lower(),(source,hypothesis)
        case_id=f'U1_{kind}{sum(x["primary_type"]==kind for x in bank)+1:02d}'
        checkpoint={'historical_observation_case':source,'historical_observation_path':'experiments/minimal_research_loop/verify_necessity/OBSERVATIONS.json','observed_window_sha256':hashlib.sha256(old_text.encode()).hexdigest(),'kind':'single_observation_diagnostic_prefix'}
        writer={'raw_question':obs['raw_question'],'current_gap':gap,'relevant_committed_claims':[],'working_hypothesis':hypothesis}
        bank.append({'case_id':case_id,'qid':qid,'primary_type':kind,'writer_input':writer,'historical_checkpoint':checkpoint,'writer_input_sha256':digest(writer)})
        sufficient=[target]
        if qid=='435' and target in {'56154','48151','51535'}:
            sufficient=['56154','48151','51535'] if 'How many albums' in gap else ['48151','51535']
        if qid=='177' and target in {'37053','914'}:
            sufficient=['37053','914']
        truth.append({'case_id':case_id,'qid':qid,'primary_type':kind,'sufficient_doc_ids':sufficient, 'historically_seen_doc_ids':[oldid], 'historically_seen_sufficient_doc_ids':[d for d in sufficient if d==oldid], 'misleading_seen_doc_ids':[oldid] if kind=='D' else [],'evidence_location':{'doc_id':target,'historical_window_seen':kind=='A','anchor':anchor,'anchor_offset':target_text.lower().find(anchor.lower()),'source_text_sha256':hashlib.sha256(target_text.encode()).hexdigest()},'historical_checkpoint_sha256':digest(checkpoint)})
    assert len({(x['writer_input_sha256'],x['historical_checkpoint']['observed_window_sha256']) for x in bank})==40,'duplicate semantic cells'
    (HERE/'BANK.json').write_text(json.dumps(bank,indent=2,ensure_ascii=False)+'\n')
    (HERE/'PRIVATE_TRUTH.json').write_text(json.dumps(truth,indent=2,ensure_ascii=False)+'\n')
    print('frozen',len(bank),'qids',len({x['qid'] for x in bank}),'types',Counter(x['primary_type'] for x in bank))

if __name__=='__main__':main()
