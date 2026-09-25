"""SC0: construct a small, temporally audited State ladder without model/Search calls."""
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
U1 = ROOT / 'experiments/unified_global_retrieval/document_rediscovery'
OBS_PATH = ROOT / 'experiments/minimal_research_loop/verify_necessity/OBSERVATIONS.json'
F3_PATH = ROOT / 'experiments/gap_evidence_claim_loop/single_gap_rollout/REVIEW_PACKETS.json'

# Selected before S1 requests. Every cell has three supported, nonanswer facts.
SELECTED = [
    'U1_B01','U1_B02','U1_B03','U1_B04','U1_B05','U1_B06','U1_B07','U1_B08',
    'U1_C01','U1_C02','U1_C03','U1_C05','U1_C06','U1_C07','U1_C11','U1_C12',
    'U1_D01','U1_D02','U1_D03','U1_D04','U1_D05','U1_D06','U1_D07','U1_D08',
]
SOURCE = {
    '517': 'E1_F1_T1_517', '387': 'E1_F1_T1_387', '435': 'E1_F1_T1_435',
    '1094': 'E1_F1_T1_1094', '311': 'E1_F1_T5_311', '186': 'E1_F1_T5_186',
    '1034': 'E1_F1_T1_1034', '177': 'E1_F1_T1_177', '580': 'E1_F1_T1_580',
    '546': 'E1_F1_T1_546',
}

# (statement, exact substring in the historical prior W, analysis-only fact kind)
FACTS = {
 '517': [
  ('The candidate actor is Peter King Nzioki Mwania, known as Peter King.', 'popularly known as Peter King, is a Kenyan actor', 'candidate_grounding'),
  ('Peter King was born on 25 May 1978.', 'born 25 May 1978', 'constraint_resolution'),
  ('Peter King made his film debut in The Constant Gardener in 2005.', 'In 2005, he made his film debut with a minor role in The Constant Gardener', 'relation_grounding')],
 '387': [
  ('The candidate animator is Dean Dodrill.', 'My name is Dean Dodrill and I\'m a self-taught illustrator and animator', 'candidate_grounding'),
  ('Dean Dodrill worked on Dust: An Elysian Tail.', 'Dust: An Elysian Tail', 'relation_grounding'),
  ('Dean Dodrill used an animation light-table in his office.', 'I have an animation light-table', 'constraint_resolution')],
 '435': [
  ('The candidate musician is Oliver Mtukudzi.', 'musician Oliver "Tuku" Mtukudzi', 'candidate_grounding'),
  ('Oliver Mtukudzi died at age 66.', 'died on Wednesday at the age of 66', 'constraint_resolution'),
  ('The retrospective described Oliver Mtukudzi as having more than 60 albums.', 'more than 60 albums under his belt', 'relation_grounding')],
 '1094': [
  ('The relevant football match was Paris Saint-Germain versus Lille.', 'Paris Saint Germain to a 4-3 win over Lille', 'candidate_grounding'),
  ('The PSG–Lille match ended 4-3.', '4-3 win over Lille', 'constraint_resolution'),
  ('Lionel Messi took a last-gasp free kick in the 95th minute of PSG’s home match.', "It was the 95th minute of PSG's home game vs Lille", 'relation_grounding')],
 '311': [
  ('The candidate cartoon is The Adventures of Hijitus.', 'title: The Adventures of Hijitus', 'candidate_grounding'),
  ('The series is Argentine and first aired in 1967.', 'The Adventures of Hijitus () is an Argentine animated series created in 1967', 'constraint_resolution'),
  ('Manuel García Ferré created the series.', 'created in 1967 by Spanish cartoonist Manuel García Ferré', 'relation_grounding')],
 '186': [
  ('The candidate game is Galacta: The Battle for Saturn.', 'title: Galacta: The Battle for Saturn', 'candidate_grounding'),
  ('Galacta was released for DOS in November 1992.', 'November 1992 on DOS', 'constraint_resolution'),
  ('The game page identifies Galacta as shareware.', 'Business Model\nShareware', 'relation_grounding')],
 '1034': [
  ('The candidate person is Heart Evangelista.', 'Heart Evangelista is no spoiled rich kid', 'candidate_grounding'),
  ('The article describes Heart Evangelista as both singer and model.', 'TV host, singer, model', 'constraint_resolution'),
  ('Her early career included the programme G-mik.', 'First spotted acting on a kid-friendly show called G-mik', 'relation_grounding')],
 '546_wikipedia': [
  ('The candidate snooker player is Ding Junhui.', 'Ding Junhui (; born 1 April 1987)', 'candidate_grounding'),
  ('Ding Junhui turned professional in 2003.', 'In 2003, Ding turned professional', 'constraint_resolution'),
  ('The source attributes seven maximum breaks to Ding Junhui.', 'including seven maximum breaks', 'relation_grounding')],
 '546_guardian': [
  ('The candidate snooker player is Ding Junhui.', 'Ding Junhui needed a quick change', 'candidate_grounding'),
  ('Ding won his opening 2023 English Open match 4-3.', '4-3 victory over Ma Hailong', 'constraint_resolution'),
  ('That opening win was against Ma Hailong.', 'victory over Ma Hailong', 'relation_grounding')],
 '177': [
  ('The candidate team is Rangers in the Nigeria Professional Football League.', 'Nigeria Professional Football League outfit Rangers', 'candidate_grounding'),
  ('The club is based in Enugu.', 'The Enugu- based club', 'constraint_resolution'),
  ('Rangers signed 13 players ahead of the 2022/23 season.', 'Rangers have signed 13 new players ahead of the 2022/23', 'relation_grounding')],
 '580': [
  ("The candidate series is You're the Worst, identified by the observed episode page.", 'youretheworst.fandom.com/wiki/Not_a_Great_Bet', 'candidate_grounding'),
  ('Not a Great Bet is the seventh episode of Season 4.', 'seventh episode of Season 4', 'constraint_resolution'),
  ('In that episode, Gretchen goes home for her brother’s baby’s birth.', 'Gretchen goes home for the birth of her brother\'s baby', 'relation_grounding')],
}

# Actual later target windows in the same F3 replay when available. None is read by S1.
TARGET_EVENTS = {
 'U1_B01': ('P11','W12'), 'U1_B03': ('P05','W9'),
 'U1_C01': ('P05','W10'), 'U1_C02': ('P05','W6'), 'U1_C03': ('P05','W6'),
 'U1_C05': ('P07','W12'), 'U1_C06': ('P12','W2'), 'U1_C07': ('P12','W4'),
 'U1_C11': ('P06','W35'), 'U1_D01': ('P05','W10'), 'U1_D02': ('P05','W6'),
 'U1_D03': ('P07','W17'), 'U1_D04': ('P07','W17'), 'U1_D05': ('P07','W12'),
 'U1_D06': ('P12','W2'), 'U1_D07': ('P12','W4'), 'U1_D08': ('P06','W35'),
}
F3_PRIOR = {'435':'P05:seed:W1','177':'P07:seed:W1','517':'P11:seed:W1',
            '580':'P12:seed:W1','546':'P06:decision3:W13','1094':'R1:69:W38'}

# Canonical U1 anchors sometimes identify the already-known candidate rather than
# the target answer (for example, an Enugu Rangers table row). These exact strings
# are answer-bearing material forbidden in the prior W, reviewed before S1.
LEAKAGE_DENY = {
    'U1_C02':'Forbes', 'U1_D02':'Forbes',
    'U1_D03':'2014', 'U1_D04':'2014', 'U1_D05':'2016',
}
TARGET_EVENT_QUOTES = {
    'U1_C02':'#10 – Oliver Mtukudzi (Zimbabwe)',
    'U1_D02':'#10 – Oliver Mtukudzi (Zimbabwe)',
    'U1_C11':'In 2003, Ding turned professional',
    'U1_D08':'In 2003, Ding turned professional',
}


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def digest(s):
    return hashlib.sha256(s.encode()).hexdigest()


def put(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def main():
    assert len(SELECTED) == len(set(SELECTED)) == 24
    u1 = {x['case_id']: x for x in json.loads((U1 / 'BANK.json').read_text())}
    truths = {x['case_id']: x for x in json.loads((U1 / 'PRIVATE_TRUTH.json').read_text())}
    obs = {x['case_id']: x for x in json.loads(OBS_PATH.read_text())}
    e1 = {x['case_id']: x for x in json.loads((ROOT / 'experiments/evidence_fidelity_loop/evidence_packet/BANK.json').read_text())}
    f3 = {x['review_id']: x for x in json.loads(F3_PATH.read_text())}
    by_source = {}
    for case in u1.values():
        key = case['historical_checkpoint']['historical_observation_case']
        by_source.setdefault(key, truths[case['case_id']]['historically_seen_doc_ids'][0])
    public, private = [], []
    for cid in SELECTED:
        case = u1[cid]; truth = truths[cid]; qid = case['qid']
        source_id = SOURCE[qid]
        if qid == '546' and cid == 'U1_B08':
            source_id = 'E1_F1_T5_546'
        source = obs[source_id]
        w = source['observation']; text = w['text']
        prior_doc = by_source[source_id]
        anchor = truth['evidence_location']['anchor']
        deny = LEAKAGE_DENY.get(cid, anchor)
        assert deny.lower() not in text.lower(), (cid, 'target answer-bearing text already in prior W', deny)
        profile = '546_wikipedia' if source_id.endswith('T5_546') else ('546_guardian' if qid=='546' else qid)
        specs = FACTS[profile]
        facts = []
        for n, (statement, quote, kind) in enumerate(specs, 1):
            assert quote in text or quote in w['url'], (cid, quote)
            assert deny.lower() not in statement.lower(), (cid, statement)
            facts.append({'fact_id':f'F{n}', 'statement':statement,
                          'prior_evidence_ref':w['window_ref'], 'historical_source_key':source_id,
                          'support_quote':quote, 'support_location':'url' if quote in w['url'] else 'text',
                          'first_seen_before_target':True,
                          'source_supported':True, 'analysis_kind':kind})
        states = {'S0':[], 'S1':[facts[0]['statement']],
                  'S2':[x['statement'] for x in facts[:2]],
                  'S3':[x['statement'] for x in facts]}
        question = case['writer_input']['raw_question']; gap = case['writer_input']['current_gap']
        target_event = TARGET_EVENTS.get(cid)
        if target_event:
            packet = f3[target_event[0]]
            observed = [x for x in packet['observations'] if x['ref'] == target_event[1]]
            assert observed, (cid, target_event)
            target_quote = TARGET_EVENT_QUOTES.get(cid, anchor)
            assert target_quote.lower() in observed[0]['text'].lower(), (cid, 'target event lacks support')
            first_seen = f'{target_event[0]}:decision{observed[0]["decision"]}:{target_event[1]}'
            assert observed[0]['decision'] >= 1
            censored = False
        else:
            first_seen = None
            censored = True
            target_quote = None
        origin = e1[source['historical_origin']['case_id']]['historical_origin']
        prior_event = F3_PRIOR.get(qid) if source_id == SOURCE[qid] else None
        prior_event = prior_event or origin.get('checkpoint')
        if isinstance(prior_event, dict):
            prior_event = prior_event.get('checkpoint') or f"{prior_event.get('source')}#event_seq={prior_event.get('event_seq')}"
        if cid == 'U1_B08':
            prior_event = 'prior_stage_D_real_tool:C_location_546_bio:W32'
        bridge = [] if prior_doc in truth['sufficient_doc_ids'] else [prior_doc]
        public.append({'case_id':cid, 'qid':qid, 'primary_type':case['primary_type'],
                       'raw_question':question, 'target_gap':gap, 'question_sha256':digest(question),
                       'target_gap_sha256':digest(gap),
                       'state_arms':{arm:{'claims':statements,'working_hypothesis':None}
                                     for arm,statements in states.items()}})
        private.append({'case_id':cid, 'qid':qid, 'primary_type':case['primary_type'],
                        'source_observation_case':source_id, 'prior_evidence_ref':w['window_ref'],
                        'prior_source_docid':prior_doc, 'prior_source_url':w['url'],
                        'prior_window_text_sha256':digest(text), 'prior_window_text':text,
                        'prior_event':prior_event,
                        'prior_facts':facts, 'target_evidence_first_seen_event':first_seen,
                        'target_first_seen_right_censored_after_prior':censored,
                        'target_evidence_anchor_private':anchor,
                        'target_observation_support_quote_private':target_quote,
                        'prior_answer_bearing_text_excluded':deny,
                        'sufficient_doc_ids':truth['sufficient_doc_ids'],
                        'bridge_claim':facts[0]['statement'] if bridge else None,
                        'bridge_doc_ids':bridge,
                        'why_bridge_changes_next_decision':'Grounds the candidate or event referent before targeting the unresolved relation.' if bridge else None,
                        'dependency_annotation':{'required_referents':['candidate/entity','event/constraint','target relation'],
                          'coverage_by_arm':{'S0':[], 'S1':['candidate/entity'],
                                             'S2':['candidate/entity','event/constraint'],
                                             'S3':['candidate/entity','event/constraint','relation context']}},
                        'review_decision':'admit: three source-supported pre-target facts; no target answer-bearing text in prior W'})
    assert len({x['qid'] for x in public}) == 10
    put(HERE / 'BANK.json', public)
    put(HERE / 'PRIVATE_TRUTH.json', private)
    head = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    put(HERE / 'freeze.json', {'base_head':head,'case_order':SELECTED,
        'qid_count':len({x['qid'] for x in public}), 'sample_count':24,
        'input_sha256':{str(p.relative_to(ROOT)):sha(p) for p in
          [U1/'BANK.json',U1/'PRIVATE_TRUTH.json',OBS_PATH,F3_PATH,ROOT/'experiments/evidence_fidelity_loop/evidence_packet/BANK.json']},
        'bank_sha256':sha(HERE/'BANK.json'),'private_truth_sha256':sha(HERE/'PRIVATE_TRUTH.json'),
        'question_hashes':{x['case_id']:x['question_sha256'] for x in public},
        'gap_hashes':{x['case_id']:x['target_gap_sha256'] for x in public},
        'source_window_hashes':{x['case_id']:x['prior_window_text_sha256'] for x in private},
        'temporal_policy':'Prior W must lack target answer-bearing text; explicit later event must contain reviewed target support. Null target event is right-censored, never imputed.',
        'no_model_or_retrieval_calls':True})
    print('SC0',len(public),'cases',Counter(x['qid'] for x in public))


if __name__ == '__main__':main()
