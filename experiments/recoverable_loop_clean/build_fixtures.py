"""Offline extraction from immutable Stage 4 ancestry; never imports later runners.

Review annotations are human-authored expectations, not model evaluations.
Only selected prefix claims/windows enter fixtures; no gold/future/answer fields.
"""
import hashlib
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).parent / 'fixtures'
BASE = 'experiments/belief_need_budget_locality_repair'
provenance = {}


def sha(data): return hashlib.sha256(data).hexdigest()
def read(path):
    data = (ROOT/path).read_bytes(); provenance[path] = sha(data)
    return json.loads(data)


SPECS = [
 ('euler', '538', 'F11', 'S01', [0], 'Verify whether the target book references Euler.',
  'Locate where the target book references Euler.', 'Biography does not establish the book-to-Euler reference.'),
 ('book_article', '971', 'F10', 'S01', [0,1], 'Locate the later article and verify its date.',
  'Find the 2016 article.', 'Book publication is not later article publication.'),
 ('memo_letter', '922', 'F16', 'S01', [0,1], 'Verify the actual date of the enclosed letter.',
  'Inspect the March 5, 1945 letter.', 'The covering memorandum date does not date the enclosed letter.'),
 ('patient_country', '637', 'F13', 'S06', [6], 'Verify both reports’ locations and publication dates from their sources.',
  'The Pakistani patient proves both reports were published in Pakistan.',
  'Patient nationality alone is insufficient. This actual full window ALSO explicitly locates the clinic in Pakistan; preserve that narrower positive evidence. It does not establish both reports’ publication country/dates.'),
 ('teammates', '1259', 'F15', 'S01', [0,1], 'Verify each teammate’s country.',
  'Find the two Chinese teammates’ home cities.', 'Team membership and one member’s nationality do not establish the other two members’ same-country condition.'),
 ('dlc', '843', 'F14', 'S06', [2,3,4,5,6], 'Verify the candidate DLC’s European-nation qualifier.',
  'Find the name of the established European-nation mechanic.', 'Technology/government changes do not establish the question’s European-nation condition.'),
 ('q637_local_global', '637', 'F13', 'S06', list(range(11)), 'Check the two reports’ dates and shared candidate binding.',
  'Name the disease since all clinical clues match.', 'Keep grounded local clinical facts; global candidate and both report conditions remain unestablished.'),
 ('ding2019', '228', 'F08', 'S01', [0,1], 'Test whether Ding satisfies the 2019 childlessness condition.',
  'Verify the gift made by Ding, who had no children as of 2019.', 'Ding is a tentative candidate injected for this offline regression; no selected Claim establishes Ding’s 2019 family status.'),
]


def build():
    review = read(BASE+'/bank/CLAIM_SUPPORT_REVIEW.json')
    supported = {r['statement']: r['review'] for r in review if r['review']['status']=='supported'}
    result = []
    for ident,qid,case,checkpoint,indices,good,bad,reason in SPECS:
        path = f'{BASE}/acquisition/trajectories/{case}/{checkpoint}.json'
        row = read(path)['state']; claims = []; obs = {}
        for i in indices:
            c = row['claims'][i]
            assert c['statement'] in supported, c['statement']
            tool = read(c['source_observation_path'])
            w = tool['observations'][c['source_observation_index']]
            assert sha(w['text'].encode()) == w['text_sha256']
            obs[w['window_ref']] = w
            claims.append({'statement': c['statement'], 'evidence_refs': c['support_refs'],
                           'historical_review': supported[c['statement']]})
        rpath = f'experiments/ephemeral_obligation_decomposition/e1_development/calls/D2__Q{qid}__R1.result.json'
        reqs = read(rpath)['output']['requirements']
        hypothesis = row['hypothesis']
        if ident == 'ding2019': hypothesis = 'Ding may be the founder candidate; his task conditions still require verification.'
        result.append(dict(case_id=ident, qid=qid, question=row['question'], requirements=reqs,
                           claims=claims, observations=list(obs.values()), hypothesis=hypothesis,
                           source_snapshot=path, skeleton_source=rpath,
                           derivation='Selected reviewed C and their observed windows; H from snapshot except explicit Ding injection. Not an exact full historical checkpoint.',
                           review=dict(acceptable_one_gap=good, hardened_or_completion_error=bad,
                                       expected_closure='CONTINUE', reason=reason, model_tested=False)))
    bank = read('experiments/gap_evidence_claim_loop/single_gap_rollout/BANK.json')
    for qid in ['546','1094']:
        cell = next(c for c in bank if c['qid']==qid)
        w = cell['relevant_observed_window']
        observations = [dict(window_ref=w['ref'], doc_ref=w['doc_ref'], title=w['title'], text=w['text'],
                             url='', text_sha256=sha(w['text'].encode()))]
        extra = None
        if qid=='546':
            path = 'experiments/runs/v003a_search_find/qid_546/20260922T121742.932067Z/events.jsonl'
            data = (ROOT/path).read_bytes(); provenance[path] = sha(data)
            prefix = [json.loads(line) for line in data.splitlines() if line]
            # Prefix boundary, no future source content is used.
            for event in prefix:
                if event['seq'] > cell['checkpoint_seq']: break
                if event['kind'] == 'tool_result' and event.get('name') == 'search':
                    for hit in event['result']['results']:
                        if hit['doc_ref']=='D17':
                            extra = dict(window_ref=hit['preview_ref'],doc_ref='D17',title=hit['title'],
                                         text=hit['preview'],url=hit['url'],text_sha256=sha(hit['preview'].encode()),
                                         observed_seq=event['seq'])
            assert extra and extra['observed_seq'] <= cell['checkpoint_seq']
            observations.append(extra)
        result.append(dict(case_id='q'+qid, qid=qid, question=cell['raw_question'],
            requirements=[{'source_spans':[{'text':cell['raw_question']}]}],
            claims=cell['initial_claims'], observations=observations, hypothesis=cell['working_hypothesis'],
            source_snapshot='experiments/gap_evidence_claim_loop/single_gap_rollout/BANK.json',
            skeleton_source='Mechanical whole-question R1 for this control fixture, not a new model skeleton.',
            derivation='Reviewed seed C/window from historical bank; q546 adds a real uninspected prefix source.',
            pending_historical_source=extra['doc_ref'] if extra else None,
            review=dict(acceptable_one_gap=cell['active_gap'], hardened_or_completion_error='Treat the partial match as the globally identified answer.',
                        expected_closure='CONTINUE',model_tested=False,
                        reason='The seed match result does not establish the remaining ordered sequence/history conditions.')))
    OUT.mkdir(exist_ok=True)
    for item in result:
        (OUT/(item['case_id']+'.json')).write_text(json.dumps(item,ensure_ascii=False,indent=2)+'\n')
    (OUT/'MANIFEST.json').write_text(json.dumps({'stage4_head':'7fdb048e856545facd4acfb590e8cf28c46f1013',
        'source_files_sha256':provenance,'fixture_files_sha256':{x.name:sha(x.read_bytes()) for x in sorted(OUT.glob('*.json')) if x.name!='MANIFEST.json'},
        'selection':'Ten required historical regression mechanisms; selected C all source-relative supported, no new model selection.',
        'limitations':'Scripted expectations, not new semantic measurements. Selected projections are not full prefix replays. No historical result modified.'},ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__': build()
