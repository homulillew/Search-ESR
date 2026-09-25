"""Freeze S1 and its two controls before any new model or retrieval call."""
import hashlib
import json
import random
import subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parent
TOP = BASE.parent
ROOT = TOP.parents[1]
SC0 = TOP / 'state_bank'
CONTROL_IDS = ['U1_B01','U1_B02','U1_B03','U1_B04','U1_B05','U1_B06',
               'U1_B07','U1_C01','U1_C05','U1_C06','U1_C11','U1_D07']
SEED = 20260926

# Exact support substrings are checked against each cell's source-audited prior W.
# These facts are true, but do not identify the target candidate or resolve its Gap.
NOISE = {
 '517': [
  ('One parent served in the Kenyan Army before the article described the acting career.', 'served in the Kenyan Army'),
  ('The other parent worked at a military hospital, according to the biography.', 'mother worked at the military hospital'),
  ("The person attended Lang'ata High School in Nairobi.", "Lang'ata High School in Nairobi")],
 '387': [
  ('A workstation used an i7 2600k processor.', 'i7 2600k'),
  ('That workstation had 8GB RAM and 5TB storage.', '8GB RAM, 5TB of Storage'),
  ('The office setup included two 24-inch screens.', 'pair of 24" flatscreens')],
 '435': [
  ('The music style included South African mbaqanga influences.', 'Zulu-rooted mbaqanga'),
  ("The style used Zimbabwe's metal-tined mbira instrument.", "Zimbabwe's mbira"),
  ('An independence celebration included the new national anthem in 1980.', "In 1980, Mtukudzi celebrated Zimbabwe's independence")],
 '1094': [
  ('The article opens by mentioning sensational passes and unreal drama.', 'Sensational passes. Unreal drama.'),
  ('Its editor picked one weekend moment from European league action.', "one moment from all the action"),
  ('The writer says football rarely lacks talking points after a weekend.', 'rarely lacks for talking points')],
 '311': [
  ('The animated series lists eight seasons.', 'num_seasons: 8'),
  ('The listed broadcast network was Canal 13.', 'network: Canal 13'),
  ('Its episodes used several short runtime formats.', 'runtime: * 1 minute')],
 '186': [
  ('The DOS game allowed keyboard input.', 'Keyboard'),
  ('It was distributed on two floppy-disk sizes.', '3.5" Floppy Disk, 5.25" Floppy Disk'),
  ('Surviving an enemy wave earned a bonus score.', 'you get a bonus to your score')],
 '1034': [
  ('The article describes ownership of a Hermès Birkin bag.', 'Hermès Birkin bag'),
  ('The maternal family owned a sugar-cane plantation.', 'mother\'s family owns a sugar cane plantation'),
  ('A father gave the first Birkin bag at age 22.', 'Birkin bag from her father at 22 years old')],
 '177': [
  ('A roster article says captain Tope Olusesi had left the club.', 'captain, Tope Olusesi'),
  ('Goalkeeper Seidu Mutawakilu also left the club.', 'Seidu Mutawakilu left'),
  ('Michael Ibe arrived from Abia Warriors.', 'Michael Ibe and Gabriel Innocent linked up')],
 '580': [
  ('Heidi, a friend from eighth grade in the episode backstory, survived leukemia.', 'survived leukemia'),
  ('She later owned the old roller-rink hangout from their school days.', 'owns their old roller rink hangout'),
  ('A police raid interrupted a trip to a derelict mall, and a pickup was abandoned.', 'The police raid the mall')],
 '546': [
  ('A player arrived wearing a brown suit and bow tie.', 'usual brown suit with bow tie'),
  ('A friend bought replacement clothes on Brentwood High Street.', 'Brentwood High Street to buy Ding some new clothes'),
  ('The player forfeited the opening frame after arriving late.', 'forfeited the first frame')],
}

RELATION_TERMS = {
 'U1_B01':['filmography','role'], 'U1_B02':['printing','paper'],
 'U1_B03':['song','retire'], 'U1_B04':['second','goal'],
 'U1_B05':['object','magical powers'], 'U1_B06':['second','episode'],
 'U1_B07':['role','programme'], 'U1_B08':['youth','semi-finals'],
 'U1_C01':['Forbes','albums'], 'U1_C02':['Forbes','richest'],
 'U1_C03':['richest','albums'], 'U1_C05':['2016','champion'],
 'U1_C06':['season one','episode'], 'U1_C07':['season three','sacrifice'],
 'U1_C11':['professional','maximum breaks'], 'U1_C12':['merger','club'],
 'U1_D01':['Forbes','albums'], 'U1_D02':['Forbes','richest'],
 'U1_D03':['2014','position'], 'U1_D04':['2014','goal difference'],
 'U1_D05':['2016','champion'], 'U1_D06':['season one','episode'],
 'U1_D07':['season three','sacrifice'], 'U1_D08':['professional','year'],
}
CANDIDATES = {
 '517':['Peter King','Peter Nzioki'], '387':['Dean Dodrill'],
 '435':['Oliver Mtukudzi','Oliver Tuku Mtukudzi'], '1094':['PSG','Paris Saint Germain','Paris Saint-Germain'],
 '311':['Hijitus'], '186':['Galacta'], '1034':['Heart Evangelista'],
 '546':['Ding Junhui'], '177':['Rangers','Enugu Rangers'],
 '580':["You're the Worst","Youre the Worst"],
}


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def request(case, arm, claims, prompt, model, raw=None):
    state = {'Claims':claims, 'Optional Working Hypothesis':None} if raw is None else {'Raw Prior Evidence':raw}
    content = {'Question':case['raw_question'], 'Current Target Gap':case['target_gap'],
               'Current Research State':state}
    return {'model':model, 'messages':[{'role':'system','content':prompt},
            {'role':'user','content':json.dumps(content,ensure_ascii=False)}], 'stream':False}


def main():
    assert not (BASE/'query_events.jsonl').exists() and not (BASE/'QUERIES.json').exists()
    bank = json.loads((SC0/'BANK.json').read_text())
    truth = {x['case_id']:x for x in json.loads((SC0/'PRIVATE_TRUTH.json').read_text())}
    assert len(bank)==24 and len(CONTROL_IDS)==12 and len(RELATION_TERMS)==24
    provider = json.loads((ROOT/'experiments/model_backend_deepseek/provider.json').read_text())
    assert provider['model']=='deepseek-flash' and provider['max_retries']==0
    prompt_path = TOP/'prompts/state_conditioned_query_writer.md'
    prompt = prompt_path.read_text().rstrip()
    noise_rows, history_rows = [], []
    for case in bank:
        cid=case['case_id']; qid=case['qid']; prior=truth[cid]
        if cid not in CONTROL_IDS:
            continue
        specs=NOISE[qid]
        for statement, quote in specs:
            assert quote in prior['prior_window_text'], (cid,quote)
            assert prior['prior_answer_bearing_text_excluded'].lower() not in statement.lower()
        noise_claims=[x[0] for x in specs]
        s3=case['state_arms']['S3']['claims']
        wc=lambda v:len(' '.join(v).split())
        ratio=wc(noise_claims)/wc(s3)
        assert .65 <= ratio <= 1.55,(cid,ratio)
        noise_rows.append({'case_id':cid,'qid':qid,'claims':noise_claims,
            'support':[{'statement':s,'source_observation_case':prior['source_observation_case'],
                        'prior_ref':prior['prior_evidence_ref'],'quote':q} for s,q in specs],
            'noise_word_count':wc(noise_claims),'s3_word_count':wc(s3),
            'word_count_ratio':ratio,'review_decision':'true prior facts; no target candidate, core constraint, or answer relation'})
        history_rows.append({'case_id':cid,'qid':qid,'prior_source_observation':prior['source_observation_case'],
            'prior_window_sha256':prior['prior_window_text_sha256'],'raw_prior_evidence':prior['prior_window_text']})
    write(TOP/'controls/noise/BANK.json',noise_rows)
    write(TOP/'controls/raw_history/BANK.json',history_rows)
    noise={x['case_id']:x for x in noise_rows}; history={x['case_id']:x for x in history_rows}
    rows=[]
    for c in bank:
        for arm in ['S0','S1','S2','S3']:
            req=request(c,arm,c['state_arms'][arm]['claims'],prompt,provider['model'])
            rows.append({'case_id':c['case_id'],'qid':c['qid'],'arm':arm,
                         'request_sha256':digest(req),'request':req})
        if c['case_id'] in noise:
            for arm,claims,raw in [('S_noise',noise[c['case_id']]['claims'],None),
                                   ('S_history',[],history[c['case_id']]['raw_prior_evidence'])]:
                req=request(c,arm,claims,prompt,provider['model'],raw)
                rows.append({'case_id':c['case_id'],'qid':c['qid'],'arm':arm,
                             'request_sha256':digest(req),'request':req})
    assert len(rows)==120
    random.Random(SEED).shuffle(rows)
    write(BASE/'REQUESTS.json',rows)
    prev=json.loads((ROOT/'experiments/global_retrieval_robustness/rank_depth/freeze.json').read_text())
    assert sha(ROOT/'BCPlus/scripts/search_bcplus.py')==prev['retriever_sha256']
    for name,h in prev['index_sha256'].items():
        assert sha(ROOT/name)==h,name
    freeze={'sc0_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'sc0_bank_sha256':sha(SC0/'BANK.json'),'sc0_truth_sha256':sha(SC0/'PRIVATE_TRUTH.json'),
        'prompt_sha256':sha(prompt_path),'requests_sha256':sha(BASE/'REQUESTS.json'),
        'noise_bank_sha256':sha(TOP/'controls/noise/BANK.json'),
        'history_bank_sha256':sha(TOP/'controls/raw_history/BANK.json'),
        'provider':{k:provider[k] for k in ['model','base_url','timeout_seconds','max_retries']},
        'generation_config':'SDK defaults; no temperature or max_tokens override; same across all 120 requests',
        'random_seed':SEED,'call_order':[(x['case_id'],x['arm'],x['request_sha256']) for x in rows],
        'sample_counts':{'main':96,'noise':12,'raw_history':12},
        'retriever_sha256':prev['retriever_sha256'],'index_sha256':prev['index_sha256'],
        'sqlite_sha256':prev['sqlite_sha256'],'embedding_model':prev['model'],
        'device':'cuda:1','corpus_documents':100195,'retrieval_depth':50,
        'k_values':[1,3,5,10,20,50],
        'candidate_aliases':CANDIDATES,'relation_terms':RELATION_TERMS,
        'metrics':{'direct_hit':'any frozen sufficient doc in top k','progress_hit':'direct or frozen bridge doc in top k',
            'rank_miss_value':51,'MRR_miss_value':0,'clue_load':'fraction of query content tokens also in raw Question after excluding Current Gap tokens, candidate aliases and stop words'},
        'gates':{'recall5_pp':15,'ceiling_pair_improved_fraction':.5,'ceiling_pair_worsened_fraction_max':.15,
            'improved_qids_min':4,'noise_fraction_of_s3_gain_max':.5,'history_advantage_pp_max':5},
        'failure_policy':'one call per request, max_retries=0, no repair, failures scored as retrieval misses'}
    write(BASE/'freeze.json',freeze)
    print('prepared',len(rows),'requests, controls',len(noise_rows),'noise word ratios',
          min(x['word_count_ratio'] for x in noise_rows),max(x['word_count_ratio'] for x in noise_rows))


if __name__=='__main__':main()
